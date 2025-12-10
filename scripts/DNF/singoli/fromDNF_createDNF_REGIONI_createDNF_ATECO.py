import pandas as pd
import numpy as np


file_di_origine='DNF.csv'
delimitatore=';'
try:
    df=pd.read_csv(file_di_origine,delimiter=delimitatore)
except EXCEPTION as E:
    print(f"Impossibile leggere il file {file_di_origine}")
    print(f"Dettagli errore:{E}")
ANNO=2019
anno_df=pd.DataFrame({'valore':[ANNO]})#crea un dataframe
anno_df['id_anno'] = range(1, len(anno_df) + 1)
anno_df = anno_df[['id_anno', 'valore']]
#-------------------------------------------------------------------------------------------------------
#------------CREAZIONE TABELLA REGIONI------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------
regione_df = df[['Regioni']].drop_duplicates().sort_values(by='Regioni').reset_index(drop=True)
regione_df.columns = ['nome']
regione_df['id_regione'] = range(1, len(regione_df) + 1)
regione_df = regione_df[['id_regione', 'nome']]
#-------------------------------------------------------------------------------------------------------
#------------CREAZIONE TABELLA ATECO------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------
ateco_df = df[['Settore']].drop_duplicates().sort_values(by='Settore').reset_index(drop=True)
ateco_df.columns = ['settore']
ateco_df['id_ateco'] = range(1, len(ateco_df) + 1)
ateco_df = ateco_df[['id_ateco', 'settore']] # Riorganizza le colonne
anno_df.to_csv('anno_import.csv', index=False)
regione_df.to_csv('regione_import.csv', index=False)
ateco_df.to_csv('ateco_import.csv', index=False)
print("✅ File CSV per le dimensioni base generati con successo:")
print("- anno_import.csv (per la tabella 'anno')")
print("- regione_import.csv (per la tabella 'regione')")
print("- ateco_import.csv (per la tabella 'ateco')")