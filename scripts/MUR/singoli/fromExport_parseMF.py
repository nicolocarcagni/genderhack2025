import pandas as pd
import re
import numpy as np

# Nomi dei file
FILE_ISCRITTI = 'bdg_serie_iscritti.csv'
FILE_ANNO_ALL = 'anno_all_import_definitivo.csv'
FILE_FACOLTA_LOOKUP = 'facolta_import.csv'
FILE_OUTPUT = 'analisi_import_nuovo.csv'

DELIMITATORE = ';'
ENCODING_CORRETTO = 'latin-1' # Correzione per l'errore 0xe0

# --- 1. Caricamento Dati e Preparazione (Correzione Encoding) ---
print(f"Tentativo di caricamento di {FILE_ISCRITTI} con encoding '{ENCODING_CORRETTO}'...")

try:
    df_iscritti = pd.read_csv(FILE_ISCRITTI, delimiter=DELIMITATORE, encoding=ENCODING_CORRETTO)
    print("Caricamento riuscito.")
except Exception as e:
    print(f"ERRORE: Impossibile leggere il file {FILE_ISCRITTI}. Dettagli: {e}")
    exit()

# --- 2. Diagnosi e Identificazione della Colonna Sesso ---

# Tenta di identificare automaticamente il nome della colonna sesso
colonne_sesso_sospette = ['SEX', 'Sesso', 'Genere', 'sesso', 'sesso_agg']
colonna_sesso_reale = None

for col in colonne_sesso_sospette:
    if col in df_iscritti.columns:
        colonna_sesso_reale = col
        break

if colonna_sesso_reale is None:
    print("\n🛑 ERRORE DI CHIAVE: Impossibile trovare la colonna del Sesso.")
    print("Nomi delle colonne disponibili:")
    print(df_iscritti.columns.tolist())
    print("\nPer favore, identifica il nome esatto della colonna che contiene 'M' e 'F' e aggiorna lo script.")
    exit()
else:
    print(f"Colonna Sesso identificata: '{colonna_sesso_reale}'")


# --- 3. Ridenominazione e Filtro ---

# Rinomina e Filtra (solo TOTALE ATENEI)
df_iscritti.rename(columns={
    'DESC_FoET2013': 'nome_facolta', 
    'ISC': 'num_iscritti',
    colonna_sesso_reale: 'sesso_agg' # Rinomina la colonna trovata
}, inplace=True)

df_iscritti_filtered = df_iscritti[df_iscritti['AteneoNOME'] == 'TOTALE ATENEI'].copy()
df_iscritti_filtered['ANNO_valore'] = df_iscritti_filtered['ANNO'].apply(lambda x: int(re.search(r'^\d{4}', x).group(0)))


# --- 4. Caricamento Chiavi Dimensionali ---

try:
    anno_all_df = pd.read_csv(FILE_ANNO_ALL)
    anno_all_df['valore'] = anno_all_df['valore'].astype(int)
except FileNotFoundError:
    print(f"ERRORE: File degli anni {FILE_ANNO_ALL} non trovato.")
    exit()

try:
    facolta_lookup = pd.read_csv(FILE_FACOLTA_LOOKUP)
except FileNotFoundError:
    print(f"ERRORE: File '{FILE_FACOLTA_LOOKUP}' non trovato. Assicurati di averlo generato.")
    exit()


# --- 5. Esecuzione del PIVOT (Separazione M/F) ---

print("Esecuzione del PIVOT per separare Iscritti M e Iscritti F...")

# Esegue il pivot usando 'sesso_agg'
df_pivot = df_iscritti_filtered.pivot_table(
    index=['ANNO_valore', 'nome_facolta'],
    columns='sesso_agg', 
    values='num_iscritti',
    aggfunc='sum'
).reset_index()

# Rinomina le colonne pivot (assumendo che le chiavi siano M e F)
df_pivot.rename(columns={'M': 'num_iscritti_m', 'F': 'num_iscritti_f'}, inplace=True)

# Sostituisce NaN (valori mancanti) con 0
df_pivot[['num_iscritti_m', 'num_iscritti_f']] = df_pivot[['num_iscritti_m', 'num_iscritti_f']].fillna(0)


# --- 6. Generazione della Tabella ANALISI (Fatti) ---

print("Inizio mappatura FK e generazione file...")

# Mappa cod_anno (FK)
df_final = df_pivot.merge(
    anno_all_df[['id_anno', 'valore']],
    left_on='ANNO_valore',
    right_on='valore',
    how='left'
)

# Mappa cod_facolta (FK)

# 🛑 CORREZIONE DEL VALUERROR: Forziamo i tipi di dato a stringa prima del merge
df_final['nome_facolta'] = df_final['nome_facolta'].astype(str)
facolta_lookup['nome'] = facolta_lookup['nome'].astype(str)


df_final = df_final.merge(
    facolta_lookup[['id_facolta', 'nome']],
    left_on='nome_facolta',
    right_on='nome',
    how='left'
)

# Finalizzazione
analisi_final_df = df_final[[
    'num_iscritti_m', 
    'num_iscritti_f', 
    'id_facolta', 
    'id_anno'
]].copy()

# Rinomina per lo schema finale e aggiunge ID
analisi_final_df.columns = ['num_iscritti_m', 'num_iscritti_f', 'cod_facolta', 'cod_anno'] 
analisi_final_df['id_analisi'] = range(1, len(analisi_final_df) + 1)
analisi_final_df = analisi_final_df[['id_analisi', 'num_iscritti_m', 'num_iscritti_f', 'cod_facolta', 'cod_anno']]
analisi_final_df.to_csv(FILE_OUTPUT, index=False)


print(f"\n✅ File generato per la nuova tabella analisi (con Iscritti M/F): {FILE_OUTPUT}")
print(f"Righe generate: {len(analisi_final_df)}")