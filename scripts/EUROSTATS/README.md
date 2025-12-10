# AnalyzeESTAT Pipeline

Tool Python interattivo per l'analisi e la normalizzazione dei dati Eurostat (`estat.csv`), progettato per trasformare dati statistici grezzi in un formato strutturato per l'importazione in database.

## 📋 Descrizione
`AnalyzeESTAT.py` gestisce il processo ETL (Extract, Transform, Load) per i dataset Eurostat. Il tool scompone le dimensioni composite, pulisce i dati da flag e caratteri non validi, e normalizza le tabelle dimensionali (Tipo Misura, Metodo di Aggregazione) per produrre una tabella dei fatti pronta per l'analisi.

## 🛠 Prerequisiti
*   **Python 3.x**
*   Librerie richieste:
    *   `pandas`
    *   `numpy`

Puoi installare le dipendenze con:
```bash
pip install pandas numpy
```

## 🚀 Utilizzo
Esegui lo script da terminale:
```bash
python AnalyzeESTAT.py
```
Un menu interattivo ti permetterà di eseguire i singoli step o l'intera pipeline.

### Input
Lo script richiede i seguenti file nella stessa directory:
*   `estat.csv`: File dati grezzo scaricato da Eurostat (Delimitatore: Tab/Comma).
*   `anno_export.csv`: Tabella di lookup per gli anni (necessaria per lo step 4).

### Output
Il processo genera i seguenti file CSV:

1.  **Tabelle Dimensionali:**
    *   `tipo_misura_import_full.csv`: Combinazione normalizzata di `wstatus` e `age`.
    *   `metodo_aggr_import_full.csv`: Combinazione normalizzata di `freq` e `unit`.

2.  **Tabella dei Fatti:**
    *   `observation_import_full.csv`: Tabella finale contenente le osservazioni con chiavi esterne (FK) verso Anno, Misura e Aggregazione.

## ⚙️ Workflow della Pipeline

Lo script è suddiviso in 4 step logici:

1.  **Caricamento e Pulizia Dati (`step_1`)**: 
    *   Lettura del file raw.
    *   Separazione della colonna composita iniziale (`freq,wstatus,age,unit,geo\TIME_PERIOD`).
    *   Pulizia dei dati numerici (rimozione flag 'b', 'u' e gestione valori mancanti ':').
2.  **Preparazione Dimensioni (`step_2`)**:
    *   Identificazione e creazione delle tabelle `tipo_misura` e `metodo_aggr`.
    *   Assegnazione di ID univoci.
3.  **Unpivot (`step_3`)**:
    *   Trasformazione da formato *Wide* (anni sulle colonne) a formato *Long* (un riga per ogni osservazione temporale).
4.  **Generazione Observation (`step_4`)**:
    *   Join con le tabelle dimensionali (inclusa `anno_export.csv`).
    *   Creazione degli ID finali per le osservazioni.

## 📝 Note
*   Il file di input `estat.csv` deve avere la codifica `latin1` o compatibile.
*   Lo script gestisce automaticamente la pulizia di codici speciali Eurostat (es. i periodi temporali nelle intestazioni).

---
**Progetto:** GenderHack  
**Script:** `AnalyzeESTAT.py`  
**Autori:** NC & AM
