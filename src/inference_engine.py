"""
Real-time NLP Inference Engine with Explainable Attention/Salience & Rule Verification.
Provides programmatic predictions, word-level importance weights, and structured FHIR-like outputs.
"""

import os
import joblib
import numpy as np
import re

MODEL_DIR = r"C:\Users\palem\OneDrive\Documents\3rd Year\Machine Learning\models"
VEC_PATH = os.path.join(MODEL_DIR, "tfidf_vectorizer.pkl")
CLF_PATH = os.path.join(MODEL_DIR, "clinical_classifiers.pkl")

# Lazy-loaded globals
_VECTORIZER = None
_MODELS = None

def get_engine():
    global _VECTORIZER, _MODELS
    if _VECTORIZER is None or _MODELS is None:
        if not os.path.exists(VEC_PATH) or not os.path.exists(CLF_PATH):
            raise FileNotFoundError("Model artifacts not found. Run export_models.py first.")
        _VECTORIZER = joblib.load(VEC_PATH)
        _MODELS = joblib.load(CLF_PATH)
    return _VECTORIZER, _MODELS

def analyze_report(report_text: str, model_type="logistic_regression"):
    """
    Analyzes an unstructured radiology report text.
    Returns:
    - Detected findings with probability and binary presence
    - Top salient positive and negative n-grams influencing each finding
    - Clinical triage alert level
    """
    vectorizer, models = get_engine()
    
    # Preprocess text
    cleaned_text = re.sub(r'X+', ' ', report_text)
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
    
    X = vectorizer.transform([cleaned_text])
    feature_names = np.array(vectorizer.get_feature_names_out())
    nonzero_indices = X.nonzero()[1]
    
    predictions = {}
    detected_abnormalities = []
    
    for finding, clfs in models.items():
        clf = clfs.get(model_type, clfs["logistic_regression"])
        prob = clf.predict_proba(X)[0, 1]
        decision = bool(prob >= 0.50)
        
        # Explainability: Extract top contributing tokens for this finding
        feature_weights = clf.coef_[0]
        active_weights = [(feature_names[i], float(feature_weights[i] * X[0, i])) for i in nonzero_indices]
        # Sort by contribution
        top_positive_cues = sorted([w for w in active_weights if w[1] > 0], key=lambda x: x[1], reverse=True)[:3]
        top_negative_cues = sorted([w for w in active_weights if w[1] < 0], key=lambda x: x[1])[:3]
        
        predictions[finding] = {
            "present": decision,
            "confidence_percent": round(float(prob * 100), 1),
            "probability": round(float(prob), 4),
            "positive_evidence": [cue[0] for cue in top_positive_cues],
            "negative_evidence": [cue[0] for cue in top_negative_cues]
        }
        
        if decision and finding != "Normal":
            detected_abnormalities.append(finding)
            
    # Triage logic
    if any(k in detected_abnormalities for k in ["Pneumonia", "Effusion", "Edema"]):
        triage_urgency = "HIGH (Actionable Acute Pathology)"
    elif len(detected_abnormalities) > 0:
        triage_urgency = "MEDIUM (Routine Cardiopulmonary Abnormality)"
    else:
        triage_urgency = "LOW (Normal / Clear Thorax)"
        
    return {
        "input_text": report_text,
        "triage_urgency": triage_urgency,
        "abnormalities_found": detected_abnormalities,
        "findings_detail": predictions
    }

if __name__ == "__main__":
    test_sample = "Cardiomegaly is present. Mild vascular congestion. No pneumothorax or large pleural effusion. Normal lungs."
    res = analyze_report(test_sample)
    print("Test Report Analysis:")
    print("Triage Urgency:", res["triage_urgency"])
    print("Detected Findings:", res["abnormalities_found"])
    for f, d in res["findings_detail"].items():
        print(f"  {f:<15}: {'PRESENT' if d['present'] else 'ABSENT':<7} ({d['confidence_percent']}%) | Evidence: {d['positive_evidence']}")
