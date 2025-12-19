# AnalyzeMIUR Pipeline

Tool Python interattivo per l'elaborazione dei dati sulle iscrizioni universitarie del MUR (Ministero dell'Università e della Ricerca).

## 📋 Descrizione
`AnalyzeMUR.py` è uno script progettato per normalizzare e strutturare i dati storici degli iscritti universitari. Partendo dai dati grezzi, lo script estrae le dimensioni temporali e didattiche (Anni, Facoltà) e calcola la distribuzione di genere degli studenti, generando un set di tabelle relazionali pronte per l'analisi.

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
python AnalyzeMIUR.py
```
Utilizza il menu interattivo per selezionare la fase di elaborazione desiderata o per lanciare l'intera pipeline.

### Input
Lo script richiede il seguente file nella directory di esecuzione:
*   `bdg_serie_iscritti.csv`: Dataset storico degli iscritti (Delimitatore: `;`, Encoding: `latin-1`).

### Output
Il tool produce tre file CSV ottimizzati per l'importazione in database relazionali:

1.  **Tabelle Dimensionali:**
    *   `anno_export.csv`: Tabella dimensionale degli anni accademici (incrementale rispetto a una base 2019).
    *   `facolta_export.csv`: Anagrafica univoca delle facoltà/aree didattiche.

2.  **Tabella dei Fatti:**
    *   `analisi_export.csv`: Tabella contenente il numero di iscritti divisi per genere (M/F), con riferimenti (Foreign Keys) alle tabelle Anno e Facoltà.

## ⚙️ Funzionalità della Pipeline

1.  **Generazione Anni (`step_1`)**:
    *   Estrae gli anni accademici dal dataset grezzo.
    *   Gestisce l'aggiornamento incrementale della dimensione temporale.
2.  **Generazione Facoltà (`step_2`)**:
    *   Estrae e normalizza i nomi delle facoltà (es. da colonna `DESC_FoET2013`).
    *   Assegna identificativi univoci per le relazioni.
3.  **Generazione Analisi (`step_3`)**:
    *   Filtra i dati per il totale degli atenei.
    *   Esegue un **Pivot** dei dati per trasformare la colonna del sesso in due metriche distinte (`num_iscritti_m`, `num_iscritti_f`).
    *   Effettua il merge con le tabelle dimensionali per associare gli ID corretti.
    *   Gestisce eventuali valori mancanti o incongruenti.

## 📝 Note
*   Lo script è configurato per leggere file con codifica `latin-1`.
*   Include controlli robusti per verificare l'esistenza dei file e la coerenza delle colonne chiave (es. Sesso, Anno).

---
**Progetto:** GenderHack  
**Script:** `AnalyzeMUR.py`  
**Autori:** NC & AM
