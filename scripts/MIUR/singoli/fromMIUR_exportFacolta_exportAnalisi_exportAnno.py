import pandas as pd
import re

# Nomi dei file
FILE_ISCRITTI = 'bdg_serie_iscritti.csv'
DELIMITATORE = ';'

# Definizione dello stato attuale di ANNO nel DB (2019 = ID 1)
ANNO_BASE = pd.DataFrame({'id_anno': [1], 'valore': [2019]})

# --- 1. Caricamento Dati e Pulizia ---
try:
    # 🛠️ CORREZIONE: Aggiunto encoding='latin1' per risolvere l'errore di codifica
    df_iscritti = pd.read_csv(FILE_ISCRITTI, delimiter=DELIMITATORE, encoding='latin1')
except Exception as e:
    print(f"ERRORE: Impossibile leggere il file {FILE_ISCRITTI}. Dettagli: {e}")
    exit()

# Filtriamo i dati a livello nazionale e rinominiamo le colonne per chiarezza
df_iscritti_filtered = df_iscritti[df_iscritti['AteneoNOME'] == 'TOTALE ATENEI'].copy()
df_iscritti_filtered.rename(columns={'DESC_FoET2013': 'nome_facolta', 'ISC': 'num_iscritti'}, inplace=True)


# --- 2. Generazione della tabella ANNO (Aggiornamento da 2019) ---

# Estrai solo l'anno iniziale (es. '2023/2024' -> 2023) e converti in INT
df_iscritti_filtered['ANNO_valore'] = df_iscritti_filtered['ANNO'].apply(
    lambda x: int(re.search(r'^\d{4}', x).group(0))
)

# Identifica i nuovi anni da aggiungere
existing_years = set(ANNO_BASE['valore'])
new_years_values = df_iscritti_filtered['ANNO_valore'].unique()
new_years_to_add = sorted([y for y in new_years_values if y not in existing_years])

# Crea DataFrame per i nuovi anni e assegna ID sequenziali
if new_years_to_add:
    max_old_id = ANNO_BASE['id_anno'].max()
    anno_new_df = pd.DataFrame({'valore': new_years_to_add})
    anno_new_df['id_anno'] = range(max_old_id + 1, max_old_id + 1 + len(anno_new_df))
    # Unisci l'anno base (2019) e i nuovi anni
    anno_all_df = pd.concat([ANNO_BASE, anno_new_df], ignore_index=True)
else:
    anno_all_df = ANNO_BASE

# Salva la lista aggiornata di TUTTI gli anni. La re-importeremo nel DB.
anno_all_df.to_csv('anno_all_import.csv', index=False)


# --- 3. Generazione della tabella FACOLTA' ---

# Estrai i valori distinti da 'nome_facolta'
facolta_df = df_iscritti_filtered[['nome_facolta']].drop_duplicates().sort_values(by='nome_facolta').reset_index(drop=True)
facolta_df.columns = ['nome']

# Assegna un ID (PK) sequenziale
facolta_df['id_facolta'] = range(1, len(facolta_df) + 1)
facolta_df = facolta_df[['id_facolta', 'nome']]
facolta_df.to_csv('facolta_import.csv', index=False)


# --- 4. Generazione della tabella ANALISI (Fatti) ---

# Prepara il DataFrame di partenza per i join
analisi_raw_df = df_iscritti_filtered[['num_iscritti', 'nome_facolta', 'ANNO_valore']].copy()

# 🛠️ CORREZIONE: Inizia il merge da analisi_raw_df e salva in analisi_df
# Aggiungi cod_facolta (FK)
analisi_df = analisi_raw_df.merge(facolta_df, left_on='nome_facolta', right_on='nome', how='left')

# Aggiungi cod_anno (FK)
analisi_df = analisi_df.merge(anno_all_df[['id_anno', 'valore']], left_on='ANNO_valore', right_on='valore', how='left')

# Finalizzazione di analisi_import.csv

# 1. Seleziona solo le colonne che esistono e contengono i dati/FK (PK esclusa)
# 🛠️ CORREZIONE: Rimossa la selezione di 'id_analisi'
analisi_final_df = analisi_df[['num_iscritti', 'id_facolta', 'id_anno']].copy()

# 2. Rinomina le colonne per rispettare lo schema DB
analisi_final_df.columns = ['num_iscritti', 'cod_facolta', 'cod_anno']

# 3. Genera la Primary Key 'id_analisi'
analisi_final_df['id_analisi'] = range(1, len(analisi_final_df) + 1)

# 4. Riorganizza le colonne come nel tuo schema DB (PK in testa)
analisi_final_df = analisi_final_df[['id_analisi', 'num_iscritti', 'cod_facolta', 'cod_anno']]
analisi_final_df.to_csv('analisi_import.csv', index=False)


print("✅ File generati per bdg_serie_iscritti.csv:")
print("- anno_all_export.csv (Contiene tutti gli anni: 2019 + nuovi anni. Ricorda di usarlo per ripopolare la tabella 'anno')")
print("- facolta_export.csv (Per la tabella 'facolta')")
print("- analisi_export.csv (Per la tabella dei fatti 'analisi')")