import pandas as pd
import numpy as np
import os
import re
import sys
import time

# --- CONFIGURAZIONE ---
FILE_ISCRITTI = 'bdg_serie_iscritti.csv'
FILE_OUTPUT_ANNO = 'anno_export.csv'
FILE_OUTPUT_FACOLTA = 'facolta_export.csv'
FILE_OUTPUT_ANALISI = 'analisi_export.csv'

DELIMITATORE = ';'
ENCODING_INPUT = 'latin-1'

# Anno base per inizializzazione (se non presente)
ANNO_BASE_DF = pd.DataFrame({'id_anno': [1], 'valore': [2019]})

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# --- UTILS ---

def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}=== {text} ==={Colors.ENDC}\n")

def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.ENDC}")

def print_error(text):
    print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}")

def print_info(text):
    print(f"{Colors.CYAN}ℹ️  {text}{Colors.ENDC}")

def print_warning(text):
    print(f"{Colors.WARNING}⚠️  {text}{Colors.ENDC}")

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def check_file_exists(filepath):
    if not os.path.exists(filepath):
        print_error(f"File non trovato: {filepath}")
        return False
    return True

def confirm_action(prompt):
    while True:
        response = input(f"{Colors.WARNING}{prompt} [S/n]: {Colors.ENDC}").strip().lower()
        if response in ('', 's', 'si', 'y', 'yes'):
            return True
        elif response in ('n', 'no'):
            return False

def save_csv(df, filename):
    try:
        df.to_csv(filename, index=False, lineterminator='\n')
        print_success(f"File salvato correttamente: {filename} ({len(df)} righe)")
        return True
    except Exception as e:
        print_error(f"Errore durante il salvataggio di {filename}: {e}")
        return False

def load_data(filepath, encoding=ENCODING_INPUT, delimiter=DELIMITATORE):
    print_info(f"Caricamento dati da {filepath}...")
    try:
        df = pd.read_csv(filepath, delimiter=delimiter, encoding=encoding)
        return df
    except Exception as e:
        print_error(f"Impossibile leggere il file {filepath}. Dettagli: {e}")
        return None

# --- FUNZIONI CORE ---

def step_1_generazione_anni():
    print_header("1. Generazione Tabella ANNI")
    
    if not check_file_exists(FILE_ISCRITTI):
        return False

    df_iscritti = load_data(FILE_ISCRITTI)
    if df_iscritti is None:
        return False

    # Filtro iniziale
    df_filtered = df_iscritti[df_iscritti['AteneoNOME'] == 'TOTALE ATENEI'].copy()
    
    # Estrazione anno
    print_info("Estrazione valori anno...")
    try:
        df_filtered['ANNO_valore'] = df_filtered['ANNO'].apply(
            lambda x: int(re.search(r'^\d{4}', x).group(0))
        )
    except Exception as e:
        print_error(f"Errore durante il parsing degli anni: {e}")
        return False

    # Logica incrementale
    existing_years = set(ANNO_BASE_DF['valore'])
    new_years_values = df_filtered['ANNO_valore'].unique()
    new_years_to_add = sorted([y for y in new_years_values if y not in existing_years])

    if new_years_to_add:
        print_info(f"Trovati {len(new_years_to_add)} nuovi anni da aggiungere.")
        max_old_id = ANNO_BASE_DF['id_anno'].max()
        anno_new_df = pd.DataFrame({'valore': new_years_to_add})
        anno_new_df['id_anno'] = range(max_old_id + 1, max_old_id + 1 + len(anno_new_df))
        anno_all_df = pd.concat([ANNO_BASE_DF, anno_new_df], ignore_index=True)
    else:
        print_info("Nessun nuovo anno da aggiungere rispetto alla base.")
        anno_all_df = ANNO_BASE_DF.copy()

    # Ordina per id_anno
    anno_all_df = anno_all_df.sort_values(by='id_anno')
    return save_csv(anno_all_df, FILE_OUTPUT_ANNO)

def step_2_generazione_facolta():
    print_header("2. Generazione Tabella FACOLTA'")
    
    if not check_file_exists(FILE_ISCRITTI):
        return False

    df_iscritti = load_data(FILE_ISCRITTI)
    if df_iscritti is None:
        return False

    df_filtered = df_iscritti[df_iscritti['AteneoNOME'] == 'TOTALE ATENEI'].copy()
    
    print_info("Estrazione nomi facoltà univoci...")
    # Identificazione colonna facolta
    col_facolta = None
    if 'DESC_FoET2013' in df_filtered.columns:
        col_facolta = 'DESC_FoET2013'
    elif 'nome_facolta' in df_filtered.columns:
        col_facolta = 'nome_facolta'
        
    if not col_facolta:
        print_error("Colonna facoltà (es. 'DESC_FoET2013') non trovata nel dataset.")
        print_info(f"Colonne disponibili: {list(df_filtered.columns)}")
        return False

    facolta_df = df_filtered[[col_facolta]].drop_duplicates().sort_values(by=col_facolta).reset_index(drop=True)
    facolta_df.columns = ['nome']
    
    # Assegnazione ID
    facolta_df['id_facolta'] = range(1, len(facolta_df) + 1)
    facolta_df = facolta_df[['id_facolta', 'nome']]
    
    return save_csv(facolta_df, FILE_OUTPUT_FACOLTA)

def step_3_generazione_analisi():
    print_header("3. Generazione Tabella ANALISI (M/F Split)")
    
    # Verifica prerequisiti
    if not check_file_exists(FILE_ISCRITTI): return False
    
    if not os.path.exists(FILE_OUTPUT_ANNO): 
        print_warning(f"File {FILE_OUTPUT_ANNO} mancante. Provo a generarlo...")
        if not step_1_generazione_anni(): return False
        
    if not os.path.exists(FILE_OUTPUT_FACOLTA):
        print_warning(f"File {FILE_OUTPUT_FACOLTA} mancante. Provo a generarlo...")
        if not step_2_generazione_facolta(): return False

    # Caricamento dati
    df_iscritti = load_data(FILE_ISCRITTI)
    anno_all_df = pd.read_csv(FILE_OUTPUT_ANNO)
    facolta_lookup = pd.read_csv(FILE_OUTPUT_FACOLTA)
    
    # Identificazione colonna sesso
    colonne_sesso_sospette = ['SEX', 'Sesso', 'Genere', 'sesso', 'sesso_agg']
    colonna_sesso_reale = None
    for col in colonne_sesso_sospette:
        if col in df_iscritti.columns:
            colonna_sesso_reale = col
            break
            
    if not colonna_sesso_reale:
        print_error("Impossibile trovare la colonna del Sesso (es. SEX, Sesso).")
        return False
    
    print_info(f"Colonna Sesso identificata: '{colonna_sesso_reale}'")

    # Filtri e Rinomine
    df_filtered = df_iscritti[df_iscritti['AteneoNOME'] == 'TOTALE ATENEI'].copy()
    
    col_facolta_orig = 'DESC_FoET2013' if 'DESC_FoET2013' in df_filtered.columns else 'nome_facolta'
    col_isc_orig = 'ISC' if 'ISC' in df_filtered.columns else 'num_iscritti'
    
    try:
        df_filtered.rename(columns={
            col_facolta_orig: 'nome_facolta', 
            col_isc_orig: 'num_iscritti',
            colonna_sesso_reale: 'sesso_agg'
        }, inplace=True)
        
        df_filtered['ANNO_valore'] = df_filtered['ANNO'].apply(lambda x: int(re.search(r'^\d{4}', x).group(0)))
    except KeyError as e:
        print_error(f"Colonna mancante durante la rinomina: {e}")
        return False

    # Pivot Data
    print_info("Esecuzione PIVOT per separare M/F...")
    try:
        df_pivot = df_filtered.pivot_table(
            index=['ANNO_valore', 'nome_facolta'],
            columns='sesso_agg', 
            values='num_iscritti',
            aggfunc='sum'
        ).reset_index()
    except Exception as e:
        print_error(f"Errore durante il pivot: {e}")
        return False

    # Standardizzazione colonne pivot (gestione M/F)
    # Converti colonne in lista per check case-insensitive se necessario, ma qui assumiamo M/F standard
    for col in df_pivot.columns:
        if str(col).strip().upper() == 'M':
            df_pivot.rename(columns={col: 'num_iscritti_m'}, inplace=True)
        elif str(col).strip().upper() == 'F':
            df_pivot.rename(columns={col: 'num_iscritti_f'}, inplace=True)
            
    if 'num_iscritti_m' not in df_pivot.columns:
        print_warning("Colonna M non trovata dopo il pivot. Inserisco 0.")
        df_pivot['num_iscritti_m'] = 0
    if 'num_iscritti_f' not in df_pivot.columns:
        print_warning("Colonna F non trovata dopo il pivot. Inserisco 0.")
        df_pivot['num_iscritti_f'] = 0

    df_pivot[['num_iscritti_m', 'num_iscritti_f']] = df_pivot[['num_iscritti_m', 'num_iscritti_f']].fillna(0)

    # Merge FK Anno
    anno_all_df['valore'] = anno_all_df['valore'].astype(int)
    df_final = df_pivot.merge(
        anno_all_df[['id_anno', 'valore']],
        left_on='ANNO_valore',
        right_on='valore',
        how='left'
    )

    # Merge FK Facolta
    df_final['nome_facolta'] = df_final['nome_facolta'].astype(str)
    facolta_lookup['nome'] = facolta_lookup['nome'].astype(str)
    
    df_final = df_final.merge(
        facolta_lookup[['id_facolta', 'nome']],
        left_on='nome_facolta',
        right_on='nome',
        how='left'
    )

    # Check integrità
    missing_facolta = df_final[df_final['id_facolta'].isnull()]
    if not missing_facolta.empty:
        print_warning(f"{len(missing_facolta)} righe hanno facoltà non mappate!")

    # Selezione finale
    analisi_final_df = df_final[['num_iscritti_m', 'num_iscritti_f', 'id_facolta', 'id_anno']].copy()
    analisi_final_df.columns = ['num_iscritti_m', 'num_iscritti_f', 'cod_facolta', 'cod_anno']
    
    # Generazione PK
    analisi_final_df['id_analisi'] = range(1, len(analisi_final_df) + 1)
    
    # Riordino colonne
    output_cols = ['id_analisi', 'num_iscritti_m', 'num_iscritti_f', 'cod_facolta', 'cod_anno']
    analisi_final_df = analisi_final_df[output_cols]
    
    return save_csv(analisi_final_df, FILE_OUTPUT_ANALISI)

def run_full_pipeline():
    print_header("ESEGUENDO PIPELINE COMPLETA")
    if step_1_generazione_anni():
        time.sleep(1)
        if step_2_generazione_facolta():
            time.sleep(1)
            step_3_generazione_analisi()

# --- MENU ---

def main_menu():
    while True:
        clear_screen()
        print(f"{Colors.HEADER}======================================{Colors.ENDC}")
        print(f"{Colors.HEADER}        AnalyzeMUR    |   byNC&AM    {Colors.ENDC}")
        print(f"{Colors.HEADER}======================================{Colors.ENDC}")
        print(f"\n{Colors.BOLD}Scegli un'operazione:{Colors.ENDC}\n")
        print(f" {Colors.CYAN}1.{Colors.ENDC} Genera Tabella ANNI")
        print(f" {Colors.CYAN}2.{Colors.ENDC} Genera Tabella FACOLTA'")
        print(f" {Colors.CYAN}3.{Colors.ENDC} Genera Tabella ANALISI (M/F)")
        print("-" * 38)
        print(f" {Colors.GREEN}{Colors.BOLD}9. ESEGUI PIPELINE COMPLETA{Colors.ENDC}")
        print(f" {Colors.FAIL}0. Esci{Colors.ENDC}")
        print("-" * 38)
        
        choice = input(f"\n{Colors.BOLD}Selection > {Colors.ENDC}").strip()
        
        if choice == '1':
            step_1_generazione_anni()
        elif choice == '2':
            step_2_generazione_facolta()
        elif choice == '3':
            step_3_generazione_analisi()
        elif choice == '9':
            if confirm_action("Sei sicuro di voler rigenerare TUTTI i file?"):
                run_full_pipeline()
        elif choice == '0':
            print(f"\n{Colors.CYAN}Chiudo l'applicazione. A presto! 👋{Colors.ENDC}")
            sys.exit()
        else:
            print_error("Opzione non valida. Riprova.")
        
        input(f"\n{Colors.CYAN}Premi INVIO per tornare al menu...{Colors.ENDC}")

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\n\nOperazione annullata dall'utente.")
        sys.exit()
