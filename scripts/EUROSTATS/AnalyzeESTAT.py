import pandas as pd
import numpy as np
import os
import time
import sys

# --- Configurazione File ---
FILE_ESTAT = 'estat.csv'
FILE_ANNO_LOOKUP = 'anno_export.csv'
DELIMITATORE_INIZIALE = '\t'

class Colors:
    """Codici ANSI per output colorato nel terminale."""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class EuroStatsETL:
    def __init__(self):
        self.df_all = None
        self.tipo_misura_df = None
        self.metodo_aggr_df = None
        self.df_long = None
        self.observation_df = None
        self.colonne_anno = []

    def step_1_load_and_clean(self):
        print(f"{Colors.HEADER}--- 1. Caricamento Dati e Pulizia ---{Colors.ENDC}")
        try:
            if not os.path.exists(FILE_ESTAT):
                 print(f"{Colors.FAIL}❌ ERRORE: Il file {FILE_ESTAT} non esiste.{Colors.ENDC}")
                 return False

            print(f"Leggendo {FILE_ESTAT}...")
            df = pd.read_csv(FILE_ESTAT, delimiter=DELIMITATORE_INIZIALE, encoding='latin1')
            
            # Gestione colonne composite
            composite_col = df.columns[0]
            df.rename(columns={composite_col: 'DIM_COMPOSITA'}, inplace=True)
            
            print("Separazione colonne composite...")
            df[['freq', 'wstatus', 'age', 'unit', 'geo']] = df['DIM_COMPOSITA'].str.split(',', expand=True)
            self.df_all = df.drop(columns=['DIM_COMPOSITA']).copy()
            self.df_all['geo'] = self.df_all['geo'].str.replace(r'\\TIME_PERIOD', '', regex=True)
            
            # Pulizia Header
            self.df_all.columns = self.df_all.columns.str.strip()
            
            # Identificazione colonne anno
            self.colonne_anno = [str(col) for col in self.df_all.columns if str(col).isdigit() and len(str(col)) == 4]
            print(f"✅ Trovate {len(self.colonne_anno)} colonne anno.")
            
            # Pulizia dati
            print("Pulizia dati numerici e rimozione flag...")
            for col in self.colonne_anno:
                # Rimuovi codici errore 'b', 'u'
                self.df_all[col] = self.df_all[col].astype(str).str.replace(r'\s+[bu]', '', regex=True)
                # Sostituisci ':' con NaN
                self.df_all[col] = self.df_all[col].replace(':', np.nan)
                # Conversione a numerico
                self.df_all[col] = pd.to_numeric(self.df_all[col], errors='coerce')
                
            print(f"{Colors.GREEN}✅ Step 1 Completato con successo.{Colors.ENDC}")
            return True
            
        except Exception as e:
            print(f"{Colors.FAIL}❌ ERRORE durante il caricamento: {e}{Colors.ENDC}")
            return False

    def step_2_prepare_dimensions(self):
        if self.df_all is None:
             print(f"{Colors.WARNING}⚠️ Esegui prima lo Step 1.{Colors.ENDC}")
             return False
             
        print(f"\n{Colors.HEADER}--- 2. Preparazione Tabelle Dimensionali ---{Colors.ENDC}")
        
        try:
            # Tipo Misura
            self.df_all['tipo_misura_valore'] = self.df_all['wstatus'].fillna('NA').astype(str) + '_' + self.df_all['age'].fillna('NA').astype(str)
            self.tipo_misura_df = self.df_all[['tipo_misura_valore']].drop_duplicates().reset_index(drop=True)
            self.tipo_misura_df.columns = ['valore']
            self.tipo_misura_df['id_misura'] = range(1, len(self.tipo_misura_df) + 1)
            self.tipo_misura_df.to_csv('tipo_misura_import_full.csv', index=False)
            print(f"✅ Salvato 'tipo_misura_import_full.csv'")

            # Metodo Aggr
            self.df_all['metodo_aggr_nome'] = self.df_all['freq'].fillna('NA').astype(str) + '_' + self.df_all['unit'].fillna('NA').astype(str)
            self.metodo_aggr_df = self.df_all[['metodo_aggr_nome']].drop_duplicates().reset_index(drop=True)
            self.metodo_aggr_df.columns = ['nome']
            self.metodo_aggr_df['id_aggr'] = range(1, len(self.metodo_aggr_df) + 1)
            self.metodo_aggr_df.to_csv('metodo_aggr_import_full.csv', index=False)
            print(f"✅ Salvato 'metodo_aggr_import_full.csv'")
            
            print(f"{Colors.GREEN}✅ Step 2 Completato.{Colors.ENDC}")
            return True
        except Exception as e:
            print(f"{Colors.FAIL}❌ ERRORE durante la preparazione dimensioni: {e}{Colors.ENDC}")
            return False

    def step_3_unpivot(self):
        if self.df_all is None:
             print(f"{Colors.WARNING}⚠️ Esegui prima gli step precedenti.{Colors.ENDC}")
             return False

        print(f"\n{Colors.HEADER}--- 3. Esecuzione Unpivot (Wide -> Long) ---{Colors.ENDC}")
        colonne_id = ['geo', 'tipo_misura_valore', 'metodo_aggr_nome']
        
        try:
            print("Esecuzione melt...")
            self.df_long = pd.melt(
                self.df_all,
                id_vars=colonne_id,
                value_vars=self.colonne_anno,
                var_name='ANNO_valore',
                value_name='valore_misurato'
            )
            self.df_long.dropna(subset=['tipo_misura_valore', 'metodo_aggr_nome'], inplace=True)
            print(f"{Colors.GREEN}✅ Step 3 Completato. Righe ottenute: {len(self.df_long)}{Colors.ENDC}")
            return True
        except Exception as e:
            print(f"{Colors.FAIL}❌ ERRORE durante l'unpivot: {e}{Colors.ENDC}")
            return False

    def step_4_generate_observation(self):
        if self.df_long is None:
             print(f"{Colors.WARNING}⚠️ Esegui prima lo Step 3.{Colors.ENDC}")
             return False
        if self.tipo_misura_df is None or self.metodo_aggr_df is None:
             print(f"{Colors.WARNING}⚠️ Esegui prima lo Step 2.{Colors.ENDC}")
             return False

        print(f"\n{Colors.HEADER}--- 4. Generazione Tabella OBSERVATION ---{Colors.ENDC}")
        
        try:
            if not os.path.exists(FILE_ANNO_LOOKUP):
                 print(f"{Colors.FAIL}❌ ERRORE: Il file {FILE_ANNO_LOOKUP} non esiste.{Colors.ENDC}")
                 return False

            anno_lookup = pd.read_csv(FILE_ANNO_LOOKUP)
            anno_lookup['valore'] = anno_lookup['valore'].astype(str)
        except Exception as e:
            print(f"{Colors.FAIL}❌ ERRORE GRAVE nel caricamento lookup: {e}{Colors.ENDC}")
            return False

        try:
            print("Merging con tabelle di lookup...")
            df_final = self.df_long.merge(anno_lookup[['id_anno', 'valore']], left_on='ANNO_valore', right_on='valore', how='left')
            df_final = df_final.merge(self.tipo_misura_df, left_on='tipo_misura_valore', right_on='valore', how='left')
            df_final = df_final.merge(self.metodo_aggr_df, left_on='metodo_aggr_nome', right_on='nome', how='left')

            df_final['observation_name'] = df_final['geo'].fillna('NA') + '_' + df_final['tipo_misura_valore'] + '_' + df_final['metodo_aggr_nome']

            self.observation_df = df_final[['observation_name', 'id_misura', 'id_aggr', 'id_anno', 'valore_misurato']].copy()
            self.observation_df.columns = ['nome', 'cod_misura', 'cod_aggr', 'cod_anno', 'valore']
            
            self.observation_df['id_observation'] = range(1, len(self.observation_df) + 1)
            self.observation_df = self.observation_df[['id_observation', 'nome', 'cod_misura', 'cod_anno', 'cod_aggr', 'valore']]
            
            self.observation_df.to_csv('observation_import_full.csv', index=False)
            print(f"✅ Salvato 'observation_import_full.csv'")
            print(f"{Colors.GREEN}✅ Step 4 Completato. Righe Totali: {len(self.observation_df)}{Colors.ENDC}")
            return True
        except Exception as e:
            print(f"{Colors.FAIL}❌ ERRORE durante la generazione observation: {e}{Colors.ENDC}")
            return False

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def main_menu():
    etl = EuroStatsETL()
    while True:
        clear_screen()
        print(f"{Colors.HEADER}{Colors.BOLD}===   AnalyzeESTAT    |   byNC&AM   ==={Colors.ENDC}")
        print(f"{Colors.BLUE}1.{Colors.ENDC} Caricamento e Pulizia Dati")
        print(f"{Colors.BLUE}2.{Colors.ENDC} Preparazione Dimensioni")
        print(f"{Colors.BLUE}3.{Colors.ENDC} Unpivot Dati")
        print(f"{Colors.BLUE}4.{Colors.ENDC} Generazione Tabella Observation")
        print("-----------------------------------")
        print(f"{Colors.CYAN}9.{Colors.ENDC} {Colors.BOLD}Esegui Pipeline Completa (1-4){Colors.ENDC}")
        print(f"{Colors.FAIL}0. Esci{Colors.ENDC}")
        
        choice = input(f"\n{Colors.WARNING}Seleziona un'opzione: {Colors.ENDC}")
        
        if choice == '1':
            clear_screen()
            etl.step_1_load_and_clean()
            input("\nPremere Invio per continuare...")
        elif choice == '2':
            clear_screen()
            etl.step_2_prepare_dimensions()
            input("\nPremere Invio per continuare...")
        elif choice == '3':
            clear_screen()
            etl.step_3_unpivot()
            input("\nPremere Invio per continuare...")
        elif choice == '4':
            clear_screen()
            etl.step_4_generate_observation()
            input("\nPremere Invio per continuare...")
        elif choice == '9':
            clear_screen()
            print(f"{Colors.BOLD}Avvio pipeline completa...{Colors.ENDC}\n")
            if etl.step_1_load_and_clean():
                if etl.step_2_prepare_dimensions():
                    if etl.step_3_unpivot():
                        etl.step_4_generate_observation()
            input("\nPremere Invio per continuare...")
        elif choice == '0':
            print(f"\n{Colors.GREEN}Uscita... A presto! 👋{Colors.ENDC}")
            break
        else:
             print(f"\n{Colors.FAIL}❌ Scelta non valida.{Colors.ENDC}")
             time.sleep(1)

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.WARNING}Interruzione forzata dall'utente.{Colors.ENDC}")