import pandas as pd
FILE_INPUT_DATI = 'DNF.csv'
DELIMITATORE = ';'
FILE_OUTPUT_AZIENDE = 'aziende_import.csv'

try:
    df_raw = pd.read_csv(FILE_INPUT_DATI, delimiter=DELIMITATORE)
    df_raw.rename(columns={'Aziende_nel_Database': 'nome_azienda'}, inplace=True)
except Exception as e:
    print(f"ERRORE: Impossibile leggere il file {FILE_INPUT_DATI}.")
    exit()
regione_df = pd.read_csv('regione_import.csv')
ateco_df = pd.read_csv('ateco_import.csv')


# 1. Filtra i dati base necessari e pulisci le righe non standard
aziende_df = df_raw[['nome_azienda', 'Settore', 'Regioni']].drop_duplicates()
aziende_df = aziende_df[aziende_df['nome_azienda'] != 'KIKO SPA']
aziende_df = aziende_df[aziende_df['nome_azienda'] != 'COFIDE ']

# 2. Merge con le tabelle di lookup per ottenere gli ID (FK)
aziende_df = aziende_df.merge(regione_df, left_on='Regioni', right_on='nome', how='left')
aziende_df = aziende_df.merge(ateco_df, left_on='Settore', right_on='settore', how='left')

# 3. Finalizzazione della tabella aziende
aziende_final_df = aziende_df[['nome_azienda', 'id_ateco', 'id_regione']].copy()
aziende_final_df.columns = ['nome', 'cod_ateco', 'cod_regione']
aziende_final_df['id_azienda'] = range(1, len(aziende_final_df) + 1)
aziende_final_df = aziende_final_df[['id_azienda', 'nome', 'cod_ateco', 'cod_regione']]

# 4. Salvataggio
aziende_final_df.to_csv(FILE_OUTPUT_AZIENDE, index=False)
print(f"✅ File CSV per la tabella aziende generato con successo: {FILE_OUTPUT_AZIENDE}")