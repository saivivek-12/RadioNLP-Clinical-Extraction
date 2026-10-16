"""
Trained Model Pipeline Export & Real-time Inference Engine.
Saves the trained vectorizer and models to disk so they can be served
instantly by interactive prototypes, GUI tools, and verification scripts.
"""

import os
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import GradientBoostingClassifier

DATA_PATH = r"C:\Users\palem\OneDrive\Documents\3rd Year\Machine Learning\data\openi_processed_dataset.csv"
MODEL_DIR = r"C:\Users\palem\OneDrive\Documents\3rd Year\Machine Learning\models"
os.makedirs(MODEL_DIR, exist_ok=True)

TARGET_FINDINGS = [
    "Normal",
    "Cardiomegaly",
    "Edema",
    "Atelectasis",
    "Effusion",
    "Pneumonia",
    "Granuloma",
    "Emphysema"
]

def train_and_export():
    print("Loading OpenI dataset...")
    df = pd.read_csv(DATA_PATH)
    
    train_val_df, test_df = train_test_split(df, test_size=0.20, random_state=42)
    train_df, _ = train_test_split(train_val_df, test_size=0.125, random_state=42)
    
    print(f"Training set: {len(train_df)} reports. Fitting Clinical TF-IDF Vectorizer...")
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 3),
        max_features=10000,
        sublinear_tf=True,
        min_df=2
    )
    X_train = vectorizer.fit_transform(train_df["text"])
    
    # Save vectorizer
    joblib.dump(vectorizer, os.path.join(MODEL_DIR, "tfidf_vectorizer.pkl"))
    print("Saved tfidf_vectorizer.pkl")
    
    trained_models = {}
    for finding in TARGET_FINDINGS:
        print(f"Training classifiers for finding: {finding}...")
        y_train = train_df[finding].values
        
        # Primary: Logistic Regression (L2 Balanced)
        lr = LogisticRegression(C=2.0, class_weight='balanced', max_iter=1000, random_state=42)
        lr.fit(X_train, y_train)
        
        # Linear SVM (Calibrated)
        svm = CalibratedClassifierCV(LinearSVC(C=1.0, class_weight='balanced', max_iter=2000, random_state=42))
        svm.fit(X_train, y_train)
        
        trained_models[finding] = {
            "logistic_regression": lr,
            "svm_calibrated": svm
        }
        
    joblib.dump(trained_models, os.path.join(MODEL_DIR, "clinical_classifiers.pkl"))
    print("Saved clinical_classifiers.pkl successfully!")

if __name__ == "__main__":
    train_and_export()
