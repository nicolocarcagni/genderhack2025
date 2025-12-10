import pandas as pd
import numpy as np
file_input='DNF.csv'
delimitatore=';'
file_output='gender_gap_dnf_filatrato.csv'
colonne_gender_gap=[
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
try:
    df=pd.read_csv(file_input,delimiter=delimitatore,usecols=colonne_gender_gap)
except Exception as E:
    print(f"ERRORE: Impossibile leggere il file {FILE_INPUT}.")
    print(f"Assicurati che il file esista e che il delimitatore sia corretto ('{DELIMITATORE}').")
    print(f"Dettagli errore: {e}")
    exit()
df_pulito = df.copy()
df_pulito = df_pulito[df_pulito['Aziende_nel_Database'] != 'KIKO SPA']
df_pulito = df_pulito[df_pulito['Aziende_nel_Database'] != 'COFIDE ']
colonne_valori = colonne_gender_gap[1:]
for col in colonne_valori:
    df_pulito[col] = df_pulito[col].replace(['', 'N.R.'], np.nan)
    df_pulito[col] = pd.to_numeric(df_pulito[col], errors='coerce')
df_pulito.to_csv(file_output, index=False)
print(f"\n✅ Estrazione e pulizia completate.")
print(f"I dati grezzi e puliti sul gender gap sono stati salvati in: {file_output}")
print(f"Righe totali estratte: {len(df_pulito)}")