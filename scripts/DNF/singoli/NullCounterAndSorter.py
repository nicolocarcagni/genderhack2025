import pandas as pd
import numpy as np

file='DNF.csv'
separatore='[;,]'
valori_nulli=['N.A.', 'n.d.', 'ND', '-', '..', 'n.q.', 'N/A', 'NaN', 'None', '', ' ']
try:
    df=pd.read_csv(
        file,
        sep=separatore, 
        # Obbligatorio per usare espressioni regolari complesse nel separatore
        engine='python', 
        # Continua a saltare le righe che non riescono a essere analizzate (utile per i dati sporchi)
        on_bad_lines='skip',
        na_values=valori_nulli)
except FileNotFoundError:
    print(f"ERRORE: File {file} non trovato")
    print("Assicurati che il file sia nella directory corrente")
    exit()
except  Exception as E:
    print(f"Exception:{E}")
    exit()
print(f"Dataset '{file}' caricato con {len(df)} righe e {len(df.columns)} colonne.")
df.columns = df.columns.str.replace('"', '') 
for col in df.columns:
    if df[col].dtype == 'object': 
        df[col] = df[col].str.replace('"', '').str.strip()
df = df.replace(valori_nulli, np.nan)
print("\n --1.Analisi NULL (requisito 1.1)--")
null_value=df.isnull().sum()#crea un dataframe  di valori BOOLEANI (true per NULL, false per NOT NULL) e fa il conteggio dei valori TRUE per ogni colonna
null_value_sorted = null_value[null_value>0].sort_values(ascending=False) #Ordina le colonne in modo da avere le colonne con più valori null a quelle con meno valori
if not null_value_sorted.empty:
    print(null_value_sorted)#stampa il conteggio delle colonne da quella che contiene più NULL a quella che ne contiene meno
else:
    print("Il dataset non ha valori NULL da ripulire.")
print("\n--Analisi dominio e range (requisito 1.2)--")
for col in df.columns:
    val_distinti=df[col].unique()
    print(f"Attributo:'{col}',Valori distinti:'{val_distinti}'")
    if len(val_distinti) > 1 and len(val_distinti) < 10:
        print(f"Categorie:{df[col].unique()}")
    elif pd.api.types.is_numeric_dtype(df[col]):
        print(f"Range:[{df[col].min()},{df[col].max()}]")
