# AnalyzeDNF Pipeline

Tool Python interattivo per l'analisi, la pulizia e la normalizzazione dei dati DNF (Dichiarazione Non Finanziaria), con focus sulle metriche di Gender Gap.

## 📋 Descrizione
`AnalyzeDNF.py` è uno script progettato per gestire il processo ETL (Extract, Transform, Load) a partire da dati grezzi in formato CSV. Il tool analizza la qualità dei dati, normalizza le dimensioni (Aziende, Regioni, Settori) e genera tabelle relazionali pronte per l'importazione in un database SQL o per l'analisi con strumenti di BI.

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
python AnalyzeDNF.py
```
Apparirà un menu interattivo che ti guiderà attraverso le fasi della pipeline.

### Input
Lo script richiede la presenza del file sorgente nella stessa directory:
*   `DNF.csv` (Delimitatore: `;`)

### Output
Il processo genera diversi file CSV nella cartella di lavoro:

1.  **Tabelle Dimensionali (Lookup):**
    *   `anno_export.csv`: Tabella Anno (fissato al 2019 per questo dataset).
    *   `regione_export.csv`: Elenco univoco e normalizzato delle regioni.
    *   `ateco_export.csv`: Elenco dei settori industriali (Codici ATECO).
    *   `aziende_export.csv`: Anagrafica aziende con chiavi esterne verso Regione e Settore.

2.  **Tabelle dei Fatti & Dati Puliti:**
    *   `gender_gap_dnf_filatrato.csv`: Fact table finale in formato "unpivoted" (Metriche su righe), ottimizzata per query analitiche.
    *   `gender_gap_dnf_wide.csv`: Dataset pulito mantenendo il formato originale (una riga per azienda).

## ⚙️ Funzionalità della Pipeline

1.  **Analisi Nulli e Dominio**: 
    *   Identifica valori nulli mascherati (es. "N.A.", "n.d.", "-").
    *   Analizza la distribuzione e il range dei valori numerici e categorici.
2.  **Pulizia Dataset**:
    *   Standardizzazione dei tipi di dato.
    *   Rimozione di record non validi o duplicati specifici.
3.  **Normalizzazione**:
    *   Creazione di ID univoci per le entità (Aziende, Regioni, Settori).
    *   Gestione delle relazioni tramite Foreign Keys.
4.  **Generazione Report**:
    *   Trasformazione dei dati da formato *Wide* a *Long* (Unpivoting) per facilitare aggregazioni su diverse metriche di Gender Gap.

## 📝 Note
*   I file CSV sono salvati con encoding standard e terminatori di riga compatibili per evitare problemi di importazione.
*   Lo script include controlli di esistenza dei file propedeutici prima di eseguire ogni step.

---
**Progetto:** GenderHack  
**Script:** `AnalyzeDNF.py`  
**Autori:** NC & AM
