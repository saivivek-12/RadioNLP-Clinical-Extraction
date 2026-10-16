# Machine Learning Capstone Phase 3 Project Report
**Course:** 23CSE301 – Machine Learning  
**Student Name:** Chepoori Sai Vivek  
**Roll No:** CH.SC.U4CSE24108  
**Paper ID:** 102  
**Base Paper Title:** *Performance of Natural Language Processing Model in Extracting Information from Free-Text Radiology Reports: A Systematic Review and Meta-Analysis* (*Journal of Imaging Informatics in Medicine*, Springer, 2025)

---

## 1. Problem Identification and Literature Survey (Rubric: 40 Marks)

### 1.1 Context & Clinical Motivation
Radiology reports serve as the definitive communication medium between radiologists and treating physicians. However, over 95% of clinical imaging reports are authored as narrative, unstructured free-text. This format leads to substantial underutilization of retrospective diagnostic data due to lexical ambiguity, lack of standardized terminology, and clinical phrasing variability. 

### 1.2 Base Paper Synthesis
The base paper provides a rigorous systematic review and bivariate random-effects meta-analysis (registered on PROSPERO: CRD420251010537) synthesizing **28 studies**, comprising **51,187 reports** and **421,692 extracted clinical entities**.
- **Pooled Diagnostic Performance:**
  - Pooled Sensitivity: **91%** (95% CI: 87%–93%)
  - Pooled Specificity: **96%** (95% CI: 93%–97%)
  - Summary AUROC: **0.98** (95% CI: 0.96–0.99)
  - Diagnostic Odds Ratio (DOR): **220** (95% CI: 112–435)
  - Positive Likelihood Ratio (PLR): **21.7** | Negative Likelihood Ratio (NLR): **0.10**
- **Heterogeneity & Meta-Regression Insight:**
  - Significant between-study heterogeneity ($I^2 = 100\%$, $p < 0.001$).
  - Multivariable meta-regression identified **anatomical site** as the single statistically significant covariate ($p = 0.027$): extracting information from single anatomical sites achieved superior AUROC (**0.99**) compared to multiple sites (**0.95**).
  - Crucially, model architecture (Traditional NLP vs. LLMs) showed **no statistically significant difference in diagnostic yield** ($p = 0.06$).

### 1.3 Literature Gaps Identified
1. **Severe Lack of External Validation:** Only 8 of 28 studies (28.6%) performed external validation.
2. **Proprietary/Closed Data Reliance:** 26 studies utilized private institutional datasets, making independent auditing impossible.
3. **Reference Standard Bias:** 20 studies had unclear risk of bias due to unrecorded inter-annotator agreement.
4. **Negation & Scope Complexity:** Handling clinical hedges (*"cannot exclude pneumonia"*) in multi-label contexts remains unresolved.

---

## 2. Handling Datasets and Data Preprocessing (Rubric: 40 Marks)

### 2.1 Dataset Source
We benchmarked our models on the **Indiana University OpenI Chest X-ray Collection**, a fully public, de-identified cohort of **3,955 chest reports** paired with frontal/lateral radiographs.

### 2.2 Data Preprocessing & Leakage Prevention
- **Section Isolation:** Extracted exclusively the `FINDINGS` (radiologist observations) and `IMPRESSION` (diagnostic conclusions) sections. 
- **Leakage Prevention:** Deliberately omitted `INDICATION` (referral symptom, which causes target leakage) and `COMPARISON` (historical study references).
- **Cleansing:** Filtered out hospital de-identification masks (`XXXX`), normalized whitespace and punctuation.
- **Cohort Volume:** Exactly **3,927 reports** possessed complete diagnostic text (mean report length: $38.25 \pm 20.43$ words).

### 2.3 Ground Truth Multi-Label Annotation
Derived multi-label ground truth across 8 key chest diagnostic categories using official MeSH and RadLex consensus annotations following the **CheXpert standard**:
1. **Normal (No Finding):** 1,365 cases (34.76%)
2. **Cardiomegaly:** 375 cases (9.55%)
3. **Granulomatous Disease:** 421 cases (10.72%)
4. **Atelectasis:** 332 cases (8.45%)
5. **Emphysema / COPD:** 269 cases (6.85%)
6. **Pleural Effusion:** 166 cases (4.23%)
7. **Pneumonia / Consolidation:** 120 cases (3.06%)
8. **Pulmonary Edema:** 100 cases (2.55%)

### 2.4 Class Imbalance Strategy
To handle severe real-world clinical rarity (e.g. Edema at 2.55%, Pneumonia at 3.06%), all models used balanced class weighting (inverse class frequency penalties).

---

## 3. Algorithmic Design, Implementation & Results (Rubric: 40 Marks)

### 3.1 Feature Representation
Constructed high-dimensional sublinear TF-IDF features ($N = 10,000$, n-gram range $1\text{--}3$) specifically configured to capture clinical negation and modification phrases (*"no pleural effusion"*, *"without focal airspace consolidation"*).

### 3.2 Evaluated Model Architectures
1. **Logistic Regression (L2 Balanced):** Convex linear classifier offering direct probability calibration and interpretable feature coefficients.
2. **Calibrated Linear Support Vector Classifier (LinearSVC):** Maximum-margin separation with isotonic calibration.
3. **Random Forest Classifier (150 trees):** Non-linear ensemble bagging model.
4. **Gradient Boosting Classifier (120 trees):** Sequential gradient boosting capturing complex clinical term interactions.

### 3.3 Quantitative Results vs. Base Paper Benchmarks

| Model / Benchmark | Sensitivity (%) | Specificity (%) | AUROC | DOR | PLR | NLR |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Base Paper Pooled Benchmark** | **91.0%** [87–93%] | **96.0%** [93–97%] | **0.980** [0.96–0.99] | **220.0** | **21.7** | **0.10** |
| **Our Logistic Regression (L2)** | **90.2%** | **97.7%** | **0.984** | **393.1** | **39.78** | **0.10** |
| **Our Linear SVM (Calibrated)** | **86.2%** | **99.1%** | **0.988** | **661.2** | **93.54** | **0.14** |
| **Our Gradient Boosting** | **90.1%** | **98.9%** | **0.982** | **791.1** | **80.68** | **0.10** |
| **Our Random Forest** | **77.5%** | **98.7%** | **0.981** | **256.7** | **59.10** | **0.23** |

### 3.4 Key Empirical Findings
- **Target Attainment:** Our Logistic Regression model achieved **90.2% Sensitivity** (Target: $\ge 90\%$) and **0.984 AUROC** (Target: $\ge 0.95$), perfectly aligning with the base paper's 95% confidence intervals.
- **Superior Discrimination:** Our micro-pooled DOR reached **393.1** for Logistic Regression and **791.1** for Gradient Boosting, markedly surpassing the base paper's pooled benchmark of 220.
- **Precision in Specificity:** Specificities across all models exceeded **97%**, preventing false positive fatigue in hospital alarm workflows.

---

## 4. Error Analysis & Clinical Decision Support (Rubric: 30 Marks)

1. **Negation Resolution:** Trigram features successfully resolved long-range negations (e.g. *"clear without pleural effusion"*), yielding 97.6% specificity on Pleural Effusion.
2. **Diagnostic Hedging:** Pneumonia achieved lower sensitivity (66.7%) due to frequent radiologist hedging (*"opacity may represent atelectasis vs developing pneumonia"*), where human MeSH indexing conservatively labeled only one pathology.
3. **Clinical Feasibility:** The high-speed CPU inferencing ($<5\text{ ms}$ per report) guarantees seamless on-premise PACS integration without sending protected health information (PHI) to third-party cloud APIs.

---

## 5. Artifacts and Generated Files
- **Final Phase 3 PPTX:** `C:\Users\palem\OneDrive\Documents\3rd Year\Machine Learning\24108_102.pptx`
- **Backup Phase 2 PPTX:** `C:\Users\palem\OneDrive\Documents\3rd Year\Machine Learning\24108_102_backup_phase2.pptx`
- **Data Preprocessing Code:** `C:\Users\palem\OneDrive\Documents\3rd Year\Machine Learning\src\preprocess.py`
- **Model Training & Evaluation Code:** `C:\Users\palem\OneDrive\Documents\3rd Year\Machine Learning\src\train_models.py`
- **Figure Generation Script:** `C:\Users\palem\OneDrive\Documents\3rd Year\Machine Learning\src\generate_figures.py`
- **Generated Figures:**
  - `figures\benchmark_comparison.png`
  - `figures\roc_curves_multilabel.png`
  - `figures\dor_comparison.png`
  - `figures\finding_performance_heatmap.png`
- **Full Results JSON:** `results\model_comparison_results.json`
