import pandas as pd
import numpy as np
import os
import sys
import time

# --- CONFIGURAZIONE ---
FILE_INPUT_DATI = 'DNF.csv'
DELIMITATORE = ';'

# Output files
FILE_OUTPUT_WIDE = 'gender_gap_dnf_wide.csv'
FILE_OUTPUT_REPORT = 'gender_gap_dnf_filatrato.csv'
FILE_OUTPUT_ANNO = 'anno_export.csv'
FILE_OUTPUT_REGIONE = 'regione_export.csv'
FILE_OUTPUT_ATECO = 'ateco_export.csv'
FILE_OUTPUT_AZIENDE = 'aziende_export.csv'

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

# --- COLORI ANSI ---
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[33m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# --- UTILS ---

def save_csv(df, filename):
    """
    Forza lineterminator='\\n' per evitare problemi di righe vuote extra su alcuni OS.
    """
    try:
        # Usa lineterminator esplicito per evitare problemi misti CR/LF
        df.to_csv(filename, index=False, lineterminator='\n')
        print(f"{Colors.GREEN}✅ File salvato correttamente: {filename} ({len(df)} righe){Colors.ENDC}")
        return True
    except Exception as e:
        print(f"{Colors.FAIL}❌ ERRORE durante il salvataggio di {filename}: {e}{Colors.ENDC}")
        return False

def confirm_action(description):
    """Richiede conferma all'utente prima di procedere."""
    print(f"\n{Colors.CYAN}❓ Richiesta Conferma:{Colors.ENDC} {description}")
    while True:
        response = input(f"   Vuoi procedere? [Y/n]: ").strip().lower()
        if response in ('y', 'yes', ''):
            return True
        elif response in ('n', 'no'):
            print(f"{Colors.WARNING}⏭️  Operazione saltata.{Colors.ENDC}")
            return False

def check_file_exists(filename):
    if not os.path.exists(filename):
        print(f"{Colors.FAIL}❌ ERRORE: File mancante: {filename}{Colors.ENDC}")
        print(f"{Colors.WARNING}   Suggerimento: Verifica di aver eseguito i passaggi precedenti.{Colors.ENDC}")
        return False
    return True

def print_header(title):
    print("\n" + f"{Colors.HEADER}{Colors.BOLD}--- {title} ---{Colors.ENDC}")

# --- LOGICA DI DATA ANALYSIS ---

def analyze_nulls():
    """Analisi dei valori nulli e del dominio"""
    print_header("1. Analisi Valori Nulli e Domini")
    if not check_file_exists(FILE_INPUT_DATI): return

    valori_nulli = ['N.A.', 'n.d.', 'ND', '-', '..', 'n.q.', 'N/A', 'NaN', 'None', '', ' ']
    try:
        df = pd.read_csv(
            FILE_INPUT_DATI,
            sep='[;,]', 
            engine='python',
            on_bad_lines='skip',
            na_values=valori_nulli
        )
    except Exception as e:
        print(f"{Colors.FAIL}Errore lettura file: {e}{Colors.ENDC}")
        return

    # Clean quotes
    df.columns = df.columns.str.replace('"', '')
    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = df[col].str.replace('"', '').str.strip()
    
    df = df.replace(valori_nulli, np.nan)

    # Null analysis
    print(f"\n{Colors.BOLD}[Analisi NULL]{Colors.ENDC}")
    null_value = df.isnull().sum()
    null_value_sorted = null_value[null_value > 0].sort_values(ascending=False)
    if not null_value_sorted.empty:
        print(null_value_sorted)
    else:
        print(f"{Colors.GREEN}Nessun valore NULL rilevante trovato nel dataset.{Colors.ENDC}")

    # Domain analysis
    print(f"\n{Colors.BOLD}[Analisi Dominio e Range]{Colors.ENDC}")
    for col in df.columns:
        val_distinti = df[col].unique()
        unique_count = len(val_distinti)
        print(f"• Attributo: {Colors.BOLD}'{col}'{Colors.ENDC} (Distinti: {unique_count})")
        
        if 1 < unique_count < 10:
            print(f"  ↪ Categorie: {val_distinti}")
        elif pd.api.types.is_numeric_dtype(df[col]):
            print(f"  ↪ Range: [{df[col].min()} - {df[col].max()}]")


def clean_gender_gap_wide():
    """Pulizia e salvataggio formato Wide"""
    print_header("2. Pulizia Dataset (Formato Wide)")
    if not check_file_exists(FILE_INPUT_DATI): return

    try:
        df = pd.read_csv(FILE_INPUT_DATI, delimiter=DELIMITATORE, usecols=COLONNE_GENDER_GAP)
    except Exception as e:
        print(f"{Colors.FAIL}Errore lettura file: {e}{Colors.ENDC}")
        return

    df_pulito = df.copy()
    # Filtri specifici
    df_pulito = df_pulito[df_pulito['Aziende_nel_Database'] != 'KIKO SPA']
    df_pulito = df_pulito[df_pulito['Aziende_nel_Database'] != 'COFIDE ']

    colonne_valori = COLONNE_GENDER_GAP[1:]
    for col in colonne_valori:
        df_pulito[col] = df_pulito[col].replace(['', 'N.R.'], np.nan)
        df_pulito[col] = pd.to_numeric(df_pulito[col], errors='coerce')

    save_csv(df_pulito, FILE_OUTPUT_WIDE)


def generate_dimensions():
    """Generazione tabelle dimensionali: Anno, Regione, Ateco"""
    print_header("3. Generazione Tabelle Dimensionali")
    if not check_file_exists(FILE_INPUT_DATI): return

    try:
        df = pd.read_csv(FILE_INPUT_DATI, delimiter=DELIMITATORE)
    except Exception as e:
        print(f"{Colors.FAIL}Errore lettura file: {e}{Colors.ENDC}")
        return

    # Anno
    ANNO = 2019
    anno_df = pd.DataFrame({'valore': [ANNO]})
    anno_df['id_anno'] = range(1, len(anno_df) + 1)
    anno_df = anno_df[['id_anno', 'valore']]

    # Regioni
    regione_df = df[['Regioni']].drop_duplicates().sort_values(by='Regioni').reset_index(drop=True)
    regione_df.columns = ['nome']
    regione_df['id_regione'] = range(1, len(regione_df) + 1)
    regione_df = regione_df[['id_regione', 'nome']]

    # Ateco
    ateco_df = df[['Settore']].drop_duplicates().sort_values(by='Settore').reset_index(drop=True)
    ateco_df.columns = ['settore']
    ateco_df['id_ateco'] = range(1, len(ateco_df) + 1)
    ateco_df = ateco_df[['id_ateco', 'settore']]

    print(f"Salvataggio dimensioni...")
    save_csv(anno_df, FILE_OUTPUT_ANNO)
    save_csv(regione_df, FILE_OUTPUT_REGIONE)
    save_csv(ateco_df, FILE_OUTPUT_ATECO)


def generate_companies():
    """Generazione tabella Aziende con Foreign Keys"""
    print_header("4. Generazione Tabella Aziende")
    
    needed_files = [FILE_INPUT_DATI, FILE_OUTPUT_REGIONE, FILE_OUTPUT_ATECO]
    for f in needed_files:
        if not check_file_exists(f): return

    try:
        df_raw = pd.read_csv(FILE_INPUT_DATI, delimiter=DELIMITATORE)
        df_raw.rename(columns={'Aziende_nel_Database': 'nome_azienda'}, inplace=True)
        
        regione_df = pd.read_csv(FILE_OUTPUT_REGIONE)
        ateco_df = pd.read_csv(FILE_OUTPUT_ATECO)
    except Exception as e:
        print(f"{Colors.FAIL}Errore lettura file: {e}{Colors.ENDC}")
        return

    # Filter
    aziende_df = df_raw[['nome_azienda', 'Settore', 'Regioni']].drop_duplicates()
    aziende_df = aziende_df[aziende_df['nome_azienda'] != 'KIKO SPA']
    aziende_df = aziende_df[aziende_df['nome_azienda'] != 'COFIDE ']

    # Merge
    aziende_df = aziende_df.merge(regione_df, left_on='Regioni', right_on='nome', how='left')
    aziende_df = aziende_df.merge(ateco_df, left_on='Settore', right_on='settore', how='left')

    # Finalize
    aziende_final_df = aziende_df[['nome_azienda', 'id_ateco', 'id_regione']].copy()
    aziende_final_df.columns = ['nome', 'cod_ateco', 'cod_regione']
    aziende_final_df['id_azienda'] = range(1, len(aziende_final_df) + 1)
    aziende_final_df = aziende_final_df[['id_azienda', 'nome', 'cod_ateco', 'cod_regione']]

    save_csv(aziende_final_df, FILE_OUTPUT_AZIENDE)


def generate_fact_table():
    """Generazione Fact Table/Report unpivoted"""
    print_header("5. Generazione Report/Fact Table")
    
    needed_files = [FILE_INPUT_DATI, FILE_OUTPUT_AZIENDE, FILE_OUTPUT_ANNO]
    for f in needed_files:
        if not check_file_exists(f): return

    try:
        df_raw = pd.read_csv(FILE_INPUT_DATI, delimiter=DELIMITATORE)
        df_raw.rename(columns={'Aziende_nel_Database': 'nome_azienda'}, inplace=True)
        
        colonne_gender_target = COLONNE_GENDER_GAP.copy()
        colonne_gender_target[0] = 'nome_azienda'

        aziende_lookup = pd.read_csv(FILE_OUTPUT_AZIENDE)
        anno_lookup = pd.read_csv(FILE_OUTPUT_ANNO)
    except Exception as e:
        print(f"{Colors.FAIL}Errore lettura file: {e}{Colors.ENDC}")
        return

    # Prepare
    df_gender = df_raw[colonne_gender_target].copy()
    df_gender = df_gender[df_gender['nome_azienda'] != 'KIKO SPA']
    df_gender = df_gender[df_gender['nome_azienda'] != 'COFIDE ']

    colonne_valori = colonne_gender_target[1:]
    for col in colonne_valori:
        df_gender[col] = df_gender[col].replace(['', 'N.R.'], np.nan)
        df_gender[col] = pd.to_numeric(df_gender[col], errors='coerce')

    # Unpivot
    df_unpivoted = pd.melt(
        df_gender,
        id_vars=['nome_azienda'],
        value_vars=colonne_valori,
        var_name='nome_metrica',
        value_name='valore'
    )
    df_unpivoted.dropna(subset=['valore'], inplace=True)

    # Merge FKs
    df_final = df_unpivoted.merge(
        aziende_lookup[['id_azienda', 'nome']],
        left_on='nome_azienda',
        right_on='nome',
        how='left',
        suffixes=('_metrica', '_azienda')
    )

    id_anno_val = anno_lookup['id_anno'].iloc[0]
    df_final['cod_anno'] = id_anno_val

    # Finalize
    report_dnf_final_df = df_final[['nome_metrica', 'id_azienda', 'valore', 'cod_anno']].copy()
    report_dnf_final_df.columns = ['nome', 'cod_azienda', 'valore', 'cod_anno']
    report_dnf_final_df['id_report'] = range(1, len(report_dnf_final_df) + 1)
    report_dnf_final_df = report_dnf_final_df[['id_report', 'nome', 'cod_azienda', 'valore', 'cod_anno']]

    save_csv(report_dnf_final_df, FILE_OUTPUT_REPORT)


# --- MENU INTERATTIVO ---

def main_menu():
    while True:
        os.system('cls' if os.name == 'nt' else 'clear') # Pulisce lo schermo per chiarezza
        print(f"{Colors.HEADER}" + "="*50)
        print("   AnalyzeDNF    |   byNC&AM   ")
        print("="*50 + f"{Colors.ENDC}")
        print(f"{Colors.BLUE}1.{Colors.ENDC} Analizza Nulli e Dominio Data")
        print(f"{Colors.BLUE}2.{Colors.ENDC} Pulisci Dataset (Export Wide Format)")
        print(f"{Colors.BLUE}3.{Colors.ENDC} Genera Dimensioni (Anno, Regione, Ateco)")
        print(f"{Colors.BLUE}4.{Colors.ENDC} Genera Tabella Aziende")
        print(f"{Colors.BLUE}5.{Colors.ENDC} Genera Report (Export Fact Table)")
        print("-" * 50)
        print(f"{Colors.GREEN}9. --> ESEGUI TUTTO (Pipeline Completa){Colors.ENDC}")
        print(f"{Colors.FAIL}0. Esci{Colors.ENDC}")
        
        scelta = input(f"\n{Colors.BOLD}Seleziona un'operazione (0-9):{Colors.ENDC} ")

        if scelta == '1':
            if confirm_action("Analisi statistica (Nulli/Range)"):
                analyze_nulls()
                input(f"\n{Colors.CYAN}Premi INVIO per tornare al menu...{Colors.ENDC}")
        
        elif scelta == '2':
            if confirm_action("Creazione CSV pulito formato Wide"):
                clean_gender_gap_wide()
                input(f"\n{Colors.CYAN}Premi INVIO per tornare al menu...{Colors.ENDC}")
        
        elif scelta == '3':
            if confirm_action("Generazione tabelle dimensionali"):
                generate_dimensions()
                input(f"\n{Colors.CYAN}Premi INVIO per tornare al menu...{Colors.ENDC}")

        elif scelta == '4':
            if confirm_action("Generazione tabella Aziende (FK)"):
                generate_companies()
                input(f"\n{Colors.CYAN}Premi INVIO per tornare al menu...{Colors.ENDC}")

        elif scelta == '5':
            if confirm_action("Generazione Fact Table finale"):
                generate_fact_table()
                input(f"\n{Colors.CYAN}Premi INVIO per tornare al menu...{Colors.ENDC}")
        
        elif scelta == '9':
            if confirm_action("ESECUZIONE COMPLETA PIPELINE"):
                print(f"\n{Colors.GOLD if hasattr(Colors, 'GOLD') else Colors.YELLOW}🚀 Avvio pipeline completa...{Colors.ENDC}")
                try:
                    analyze_nulls()
                    print("-" * 30)
                    clean_gender_gap_wide()
                    print("-" * 30)
                    generate_dimensions()
                    print("-" * 30)
                    generate_companies()
                    print("-" * 30)
                    generate_fact_table()
                    print(f"\n{Colors.GREEN}{Colors.BOLD}✨ PIPELINE COMPLETATA CON SUCCESSO! ✨{Colors.ENDC}")
                except Exception as e:
                    print(f"\n{Colors.FAIL}❌ Errore critico durante la pipeline: {e}{Colors.ENDC}")
                input(f"\n{Colors.CYAN}Premi INVIO per tornare al menu...{Colors.ENDC}")

        elif scelta == '0':
            print(f"{Colors.GREEN}Uscita...{Colors.ENDC}")
            break
        else:
            print(f"{Colors.FAIL}Scelta non valida.{Colors.ENDC}")
            time.sleep(1)

if __name__ == "__main__":
    main_menu()
