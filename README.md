# RadioNLP: Clinical Decision Support & Information Extraction System
### Multi-Label Thoracic Finding Extraction from Unstructured Radiology Narratives
**Course:** 23CSE301 (Machine Learning Capstone Phase 3)  
**Paper ID:** 102  
**Base Paper:** Yang et al., *"Performance of Natural Language Processing Model in Extracting Information from Free-Text Radiology Reports: A Systematic Review and Meta-Analysis"*, *Journal of Imaging Informatics in Medicine*, Springer (2025).

---

## 📌 Project Overview
Over 85% of hospital clinical findings are recorded in unstructured free-text narratives. This project presents an operational, end-to-end clinical NLP extraction and triage system trained on the **Indiana University OpenI Chest X-Ray Collection (3,927 reports)**.

The system addresses three critical gaps identified in the base paper meta-analysis:
1. **Eliminating Literature Heterogeneity ($p = 0.027$):** Restricting domain framing strictly to thoracic chest radiography, removing cross-anatomical vocabulary drift.
2. **Solving Scanned Document Blindness:** Incorporating neural vision OCR (`EasyOCR` + `pypdfium2`) to extract text from scanned/faxed hospital PDF reports automatically.
3. **Word-Level Explainability:** Pinpointing token-level positive and negative evidence cues behind each diagnostic prediction.

---

## 📊 Verification vs. Base Paper Meta-Analysis Benchmark

Benchmarked directly against the pooled meta-analysis across 28 global studies (Yang et al., 2025):

| Evaluation Metric | Base Paper Benchmark (Yang et al., 2025) | Our Trained Model (Phase 3) | Performance Status |
| :--- | :--- | :--- | :--- |
| **Pooled Sensitivity** | 91.0% (95% CI: 87.0% – 93.0%) | **90.2%** | **Within 95% Confidence Interval** |
| **Pooled Specificity** | 96.0% (95% CI: 93.0% – 97.0%) | **97.7%** | **Exceeds Base Paper (+1.7%)** |
| **Summary AUROC** | 0.980 (95% CI: 0.960 – 0.990) | **0.984** | **Exceeds Benchmark (0.984 vs 0.980)** |
| **Diagnostic Odds Ratio (DOR)** | 220.0 (95% CI: 112 – 435) | **393.1** | **+78.7% Higher Discriminative Power** |
| **Negative Likelihood Ratio (NLR)** | 0.10 (95% CI: 0.07 – 0.14) | **0.10** | **Exact Match (Optimal Rule-Out)** |
| **Positive Likelihood Ratio (PLR)** | 21.7 (95% CI: 13.1 – 35.8) | **39.78** | **Substantially Stronger Rule-In Capacity** |

### Granular CheXpert Pathology Performance:
* **Cardiomegaly:** AUROC = **0.991** | Sensitivity = 95.2% | Specificity = 98.3%
* **Pleural Effusion:** AUROC = **0.995** | Sensitivity = 92.0% | Specificity = 97.6%
* **Pulmonary Edema:** AUROC = **0.973** | Sensitivity = 84.2% | Specificity = 99.2%
* **Atelectasis:** AUROC = **0.988** | Sensitivity = 92.4% | Specificity = 96.8%
* **Complex Negation / Normal:** AUROC = **0.983** | Specificity = 92.0% (Zero false alarms on negated scans)

---

## 🏗️ System Architecture

```
[ Free-Text Clinical Input (.pdf / .xml / .txt / .csv) ]
                         │
                         ▼
        ┌──────────────────────────────────┐
        │  Tier 1: Document Ingestion Layer │
        │  - PDF Digital Stream Extraction │
        │  - EasyOCR Vision (Scanned PDFs) │
        │  - XML DOM Section Parser        │
        └──────────────────────────────────┘
                         │
                         ▼
        ┌──────────────────────────────────┐
        │ Tier 2: Multi-Label NLP Engine   │
        │ - Sublinear TF-IDF N-Grams (1,2) │
        │ - Calibrated L2 Linear Heads     │
        │ - Token Salience / Cue Extractor │
        └──────────────────────────────────┘
                         │
                         ▼
        ┌──────────────────────────────────┐
        │  Tier 3: Clinical Triage Router  │
        │  - Automated Probability Gates   │
        │  - Emergency Triage Routing      │
        │  - Exportable Structured JSON    │
        └──────────────────────────────────┘
```

---

## 🚀 Getting Started

### 1. Installation
Clone the repository and install the dependencies:
```bash
git clone https://github.com/saivivek-12/RadioNLP-Clinical-Extraction.git
cd RadioNLP-Clinical-Extraction
pip install -r requirements.txt
```

### 2. Run the Clinical Dashboard
Launch the web interface locally on `http://localhost:8501`:
```bash
python src/app_server.py
```
*(Or simply double-click `START_DEMO.bat` on Windows)*

### 3. Command-Line Inference
Run standalone prediction in the terminal without opening a browser:
```bash
python predict.py
```

### 4. Verify Benchmark Metrics
Run the automated verification script:
```bash
python src/verify_results.py
```

---

## 📁 Repository Directory Structure

```
├── data/                       # Indiana University OpenI radiology dataset
├── figures/                    # High-resolution ROC and loss curves
├── models/                     # Trained scikit-learn classifiers and vectorizer
├── results/                    # Multi-epoch validation metrics and test outputs
├── src/
│   ├── app_server.py           # Production dashboard server
│   ├── index.html              # Clean hospital decision support UI
│   ├── inference_engine.py     # Real-time multi-label extraction & explainability
│   ├── preprocess.py           # Negation preservation & section parser
│   ├── train_clinicalbert.py   # PyTorch ClinicalBERT fine-tuning script
│   ├── train_models.py         # Multi-classifier training & benchmark pipeline
│   └── verify_results.py       # Base paper meta-analysis verification audit
├── 24108_102.pptx              # Capstone presentation deck (15 slides)
├── Sample-pdf.pdf              # Sample scanned report for live demo
├── START_DEMO.bat              # 1-click Windows launcher
└── requirements.txt            # Python dependencies
```

---

## 📄 Citation & Attribution
If using this work, please cite:
* **Base Paper:** Yang, R., et al. (2025). *Performance of Natural Language Processing Model in Extracting Information from Free-Text Radiology Reports: A Systematic Review and Meta-Analysis*. Journal of Imaging Informatics in Medicine, Springer.
* **Dataset:** Demner-Fushman, D., et al. (2016). *Preparing a collection of radiology examinations for distribution and retrieval*. Journal of the American Medical Informatics Association (OpenI / NLM).
