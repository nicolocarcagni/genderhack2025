import pandas as pd
import numpy as np

# Nomi dei file
FILE_INPUT_DATI = 'DNF.csv'
DELIMITATORE = ';'
FILE_OUTPUT_REPORT = 'gender_gap_dnf_filatrato.csv'

# Colonne del Gender Gap da trasformare in righe (usiamo i nomi originali)
COLONNE_GENDER_GAP = [
    'Aziende_nel_Database',
    'N_uomini_dipendenti',
    'N_donne_dipendenti',
    'Donne_nel_CdA_(%)',
    'Donne_in_posizioni_manageriali_di_vertice_(%)',
    'Disuguaglianza_salariale_di_genere_(%)',
    'Eta_media_dipendenti_(%)',
    'Dipendenti_con_eta_30_per',
    'Dipendenti_con_eta_30_50_per',
    'Dipendenti_con_eta_50_per',
    'Eta_media_in_CdA_(%)',
    'Membri_del_CdA_con_eta_30_per',
    'Membri_del_CdA_con_eta_30_50_per',
    'Membri_del_CdA_con_eta_50_per'
]

# --- 1. Caricamento Dati e Lookup ---

try:
    # a. Carica i dati originali
    df_raw = pd.read_csv(FILE_INPUT_DATI, delimiter=DELIMITATORE)
    
    # Rinomina la colonna azienda PRIMA di qualsiasi operazione di filtering
    df_raw.rename(columns={'Aziende_nel_Database': 'nome_azienda'}, inplace=True)
    
    # 🛠️ CORREZIONE 1: Aggiorna la lista COLONNE_GENDER_GAP con il nuovo nome
    # Indentazione corretta: la riga è dentro il blocco try
    COLONNE_GENDER_GAP[0] = 'nome_azienda' 
    
    # b. Carica le tabelle di lookup generate precedentemente
    aziende_lookup = pd.read_csv('aziende_import.csv')
    anno_lookup = pd.read_csv('anno_import.csv')

except Exception as e:
    print(f"ERRORE nel caricamento dei file. Dettagli: {e}")
    print("Assicurati che DNF.csv, aziende_import.csv e anno_import.csv esistano nella stessa cartella.")
    exit()


# --- 2. Pulizia e Preparazione all'Unpivot ---

# Filtra solo le colonne di interesse (ora la lista COLONNE_GENDER_GAP è corretta)
df_gender = df_raw[COLONNE_GENDER_GAP].copy()

# Rimuovi le righe di aziende non standard
df_gender = df_gender[df_gender['nome_azienda'] != 'KIKO SPA']
df_gender = df_gender[df_gender['nome_azienda'] != 'COFIDE ']

# Pulisci i valori non numerici e i placeholder ('N.R.', '') in NaN
colonne_valori = COLONNE_GENDER_GAP[1:]
for col in colonne_valori:
    df_gender[col] = df_gender[col].replace(['', 'N.R.'], np.nan)
    df_gender[col] = pd.to_numeric(df_gender[col], errors='coerce')


# --- 3. Esecuzione dell'Unpivot (Wide -> Long) ---

# Usa pd.melt per trasformare le 13 colonne di metriche in righe
# Le colonne risultanti saranno 'nome_azienda', 'nome_metrica_temporanea', 'valore'
df_unpivoted = pd.melt(
    df_gender,
    id_vars=['nome_azienda'],
    value_vars=colonne_valori,
    var_name='nome_metrica',       # Usiamo un nome temporaneo per la metrica
    value_name='valore'            # Valore metrica
)

# Rimuovi le righe dove il dato era NaN (metrica non disponibile)
df_unpivoted.dropna(subset=['valore'], inplace=True)


# --- 4. Mapping delle Chiavi Esterne (FK) ---

# Mappa l'ID azienda (FK)
# 🛠️ CORREZIONE 2: Risoluzione del conflitto di nomi nella merge (Passo 4 & 5)
df_final = df_unpivoted.merge(
    aziende_lookup[['id_azienda', 'nome']],
    left_on='nome_azienda',
    right_on='nome',
    how='left',
    # Poiché 'nome' esiste in entrambe le tabelle dopo l'unpivot, 
    # Pandas aggiunge un suffisso, che ci aspettiamo sia '_y' per la colonna aziendale non utilizzata.
    # L'output sarà: ['nome_azienda', 'nome_metrica', 'valore', 'id_azienda', 'nome']
    suffixes=('_metrica', '_azienda')
)

# Mappa l'ID anno (FK)
id_anno_val = anno_lookup['id_anno'].iloc[0]
df_final['cod_anno'] = id_anno_val


# --- 5. Finalizzazione del DataFrame report_dnf ---

# Seleziona le colonne usando i nomi corretti: 
# 'nome_metrica' contiene il nome della metrica (che diventerà report_dnf.nome)
# 'valore' contiene il valore della metrica (che diventerà report_dnf.valore)
report_dnf_final_df = df_final[[
    'nome_metrica',       # Nome della metrica (corrisponde al DB)
    'id_azienda',
    'valore',
    'cod_anno'
]].copy()

# Rinomina le colonne per rispettare lo schema DB
report_dnf_final_df.columns = ['nome', 'cod_azienda', 'valore', 'cod_anno']

# Assegna la chiave primaria sequenziale (id_report)
report_dnf_final_df['id_report'] = range(1, len(report_dnf_final_df) + 1)

# Riorganizza le colonne come nel tuo schema DB
report_dnf_final_df = report_dnf_final_df[['id_report', 'nome', 'cod_azienda', 'valore', 'cod_anno']]

# 6. Salvataggio del Risultato
report_dnf_final_df.to_csv(FILE_OUTPUT_REPORT, index=False)

print(f"\n✅ File dei Fatti per report_dnf generato con successo: {FILE_OUTPUT_REPORT}")
