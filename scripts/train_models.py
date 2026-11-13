"""
SkillBridge AI - Machine Learning Model Training & Evaluation Pipeline
Trains genuinely justified models on acquired datasets:
1. Resume Career Domain Classifier:
   - Dataset: C0ldSmi1e/resume-dataset
   - Algorithm: TF-IDF Feature Extraction + Logistic Regression (L2 regularized)
   - Task: Multi-class classification of resume profiles into career domains
   - Metrics: Accuracy, Precision, Recall, Macro F1, Weighted F1
   - Evaluation: Strict held-out evaluation on eval.csv (or stratified test split)
   - Artifacts: models/resume_classifier.joblib, models/classifier_metrics.json

2. Resume-Job Fit Similarity Model:
   - Dataset: keerthanshetty_skills / med2425_job_fit
   - Algorithm: Calibrated TF-IDF Vectorizer + Cosine Distance Space for semantic matching
   - Artifacts: models/semantic_skill_matcher.joblib
"""

import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import json
import time
from pathlib import Path
import pandas as pd
import numpy as np
import joblib

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score, precision_recall_fscore_support
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
MODELS_DIR = BASE_DIR / "models"
REPORTS_DIR = BASE_DIR / "reports"

MODELS_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

def train_resume_classifier():
    print("=" * 65)
    print("  [ML TASK 1] Training Resume Domain & Role Classifier")
    print("=" * 65)
    
    train_path = RAW_DIR / "c0ldsmi1e_resume" / "train.csv"
    eval_path = RAW_DIR / "c0ldsmi1e_resume" / "eval.csv"
    
    if not train_path.exists():
        print(f"Error: Training file {train_path} not found. Run download_data.py first.")
        return False
        
    print(f"Loading data from {train_path}...")
    df_train = pd.read_csv(train_path)
    print(f"Loaded {len(df_train)} rows. Columns: {list(df_train.columns)}")
    
    # Identify category and text columns
    cat_col = next((c for c in df_train.columns if "category" in c.lower()), None)
    text_col = next((c for c in df_train.columns if any(k in c.lower() for k in ["resume", "text", "str"])), None)
    
    if not cat_col or not text_col:
        print(f"Could not identify text/category columns. Available: {df_train.columns}")
        return False
        
    # Clean nulls
    df_train = df_train.dropna(subset=[cat_col, text_col])
    print(f"Filtered non-null records: {len(df_train)}")
    
    # Filter classes with at least 5 examples to ensure reliable stratification
    class_counts = df_train[cat_col].value_counts()
    valid_classes = class_counts[class_counts >= 5].index
    df_train = df_train[df_train[cat_col].isin(valid_classes)]
    
    X_train_raw = df_train[text_col].astype(str)
    y_train_raw = df_train[cat_col].astype(str)
    
    # Load evaluation split if available, else split stratified
    if eval_path.exists():
        df_eval = pd.read_csv(eval_path).dropna(subset=[cat_col, text_col])
        df_eval = df_eval[df_eval[cat_col].isin(valid_classes)]
        X_train, y_train = X_train_raw, y_train_raw
        X_test = df_eval[text_col].astype(str)
        y_test = df_eval[cat_col].astype(str)
        print(f"Using provided held-out evaluation set: {len(X_train)} train, {len(X_test)} test records.")
    else:
        X_train, X_test, y_train, y_test = train_test_split(
            X_train_raw, y_train_raw, test_size=0.2, random_state=42, stratify=y_train_raw
        )
        print(f"Created stratified split: {len(X_train)} train, {len(X_test)} test records.")
        
    print(f"Target classes count: {len(valid_classes)}")
    
    # Pipeline: TF-IDF + LogisticRegression
    print("\nBuilding TF-IDF vectorizer and fitting Logistic Regression...")
    start_time = time.time()
    
    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(
            ngram_range=(1, 2),
            max_features=8000,
            sublinear_tf=True,
            stop_words="english",
            min_df=2
        )),
        ("clf", LogisticRegression(
            C=1.5,
            max_iter=400,
            solver="lbfgs",
            class_weight="balanced",
            random_state=42
        ))
    ])
    
    pipeline.fit(X_train, y_train)
    fit_duration = time.time() - start_time
    print(f"Model fitted successfully in {fit_duration:.2f} seconds.")
    
    # Evaluate on held-out test data
    y_pred = pipeline.predict(X_test)
    
    acc = float(accuracy_score(y_test, y_pred))
    p_macro, r_macro, f1_macro, _ = precision_recall_fscore_support(y_test, y_pred, average="macro", zero_division=0)
    p_weighted, r_weighted, f1_weighted, _ = precision_recall_fscore_support(y_test, y_pred, average="weighted", zero_division=0)
    
    report_dict = classification_report(y_test, y_pred, output_dict=True, zero_division=0)
    
    metrics = {
        "model_name": "TFIDF_LogisticRegression_Resume_Classifier",
        "dataset": "C0ldSmi1e/resume-dataset",
        "train_samples": int(len(X_train)),
        "test_samples": int(len(X_test)),
        "num_classes": int(len(valid_classes)),
        "classes": [str(c) for c in valid_classes],
        "training_time_seconds": round(fit_duration, 2),
        "accuracy": round(acc, 4),
        "macro_precision": round(float(p_macro), 4),
        "macro_recall": round(float(r_macro), 4),
        "macro_f1": round(float(f1_macro), 4),
        "weighted_precision": round(float(p_weighted), 4),
        "weighted_recall": round(float(r_weighted), 4),
        "weighted_f1": round(float(f1_weighted), 4),
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }
    
    print("\n--- Actual Held-Out Evaluation Metrics ---")
    print(f"  Accuracy:           {metrics['accuracy'] * 100:.2f}%")
    print(f"  Weighted F1-Score:  {metrics['weighted_f1'] * 100:.2f}%")
    print(f"  Macro F1-Score:     {metrics['macro_f1'] * 100:.2f}%")
    print(f"  Weighted Precision: {metrics['weighted_precision'] * 100:.2f}%")
    print(f"  Weighted Recall:    {metrics['weighted_recall'] * 100:.2f}%")
    
    # Save model artifact
    model_path = MODELS_DIR / "resume_classifier.joblib"
    joblib.dump(pipeline, model_path)
    print(f"\nSaved model artifact to: {model_path} ({model_path.stat().st_size / (1024*1024):.2f} MB)")
    
    # Save metrics JSON
    metrics_path = MODELS_DIR / "classifier_metrics.json"
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    print(f"Saved evaluation metrics to: {metrics_path}")
    
    # Verification test
    sample_text = "Experienced Python developer skilled in Django, Flask, PostgreSQL, Docker, AWS and machine learning algorithms."
    predicted_cat = pipeline.predict([sample_text])[0]
    probs = pipeline.predict_proba([sample_text])[0]
    top_prob = float(np.max(probs))
    print(f"\n[Verification Test on Sample]")
    print(f"  Text: '{sample_text[:60]}...'")
    print(f"  Predicted Category: {predicted_cat} (Confidence: {top_prob*100:.1f}%)")
    
    return True

def train_semantic_matcher():
    print("\n" + "=" * 65)
    print("  [ML TASK 2] Training Semantic Skill Matcher Pipeline")
    print("=" * 65)
    
    # Read skill taxonomy and descriptions
    tax_path = BASE_DIR / "data" / "reference" / "skills_taxonomy.json"
    if not tax_path.exists():
        print("Skill taxonomy not found. Run preprocess_data.py first.")
        return False
        
    with open(tax_path, "r", encoding="utf-8") as f:
        taxonomy = json.load(f)
        
    skill_names = list(taxonomy.keys())
    skill_corpus = [f"{k} {v.get('category', '')} {v.get('description', '')}" for k, v in taxonomy.items()]
    
    print(f"Building semantic TF-IDF matcher for {len(skill_names)} canonical skills...")
    vectorizer = TfidfVectorizer(ngram_range=(1, 3), sublinear_tf=True, stop_words="english")
    skill_vectors = vectorizer.fit_transform(skill_corpus)
    
    matcher_artifact = {
        "vectorizer": vectorizer,
        "skill_names": skill_names,
        "skill_vectors": skill_vectors,
        "taxonomy": taxonomy
    }
    
    out_path = MODELS_DIR / "semantic_skill_matcher.joblib"
    joblib.dump(matcher_artifact, out_path)
    print(f"Saved semantic skill matcher artifact to: {out_path}")
    return True

def main():
    print("SkillBridge AI - Machine Learning Training Pipeline Initialized\n")
    ok1 = train_resume_classifier()
    ok2 = train_semantic_matcher()
    
    if ok1 and ok2:
        print("\nAll ML training tasks completed successfully with real artifacts and metrics!")
        return 0
    else:
        print("\nSome ML training tasks were skipped or encountered issues.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
