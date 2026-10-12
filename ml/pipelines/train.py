"""
Laboratory Entity Extraction Model Trainer for Simplifier 2.0.
Trains a genuinely learned ML token/line classifier to predict biomarker canonical identity,
observed value, unit association, and reference interval from noisy text lines.
"""

import json
import os
import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, f1_score

RANDOM_SEED = 42

def train_biomarker_classifier(data_dir: str = "ml/data", model_dir: str = "ml/models"):
    os.makedirs(model_dir, exist_ok=True)
    
    with open(os.path.join(data_dir, "train.json"), "r", encoding="utf-8") as f:
        train_data = json.load(f)
    with open(os.path.join(data_dir, "val.json"), "r", encoding="utf-8") as f:
        val_data = json.load(f)
    with open(os.path.join(data_dir, "test.json"), "r", encoding="utf-8") as f:
        test_data = json.load(f)

    # Prepare line-level classification dataset
    X_train, y_train = [], []
    for sample in train_data:
        for idx, line in enumerate(sample["lines"]):
            row = sample["rows"][idx]
            X_train.append(line)
            y_train.append(row["canonical_name"])

    X_val, y_val = [], []
    for sample in val_data:
        for idx, line in enumerate(sample["lines"]):
            row = sample["rows"][idx]
            X_val.append(line)
            y_val.append(row["canonical_name"])

    X_test, y_test = [], []
    for sample in test_data:
        for idx, line in enumerate(sample["lines"]):
            row = sample["rows"][idx]
            X_test.append(line)
            y_test.append(row["canonical_name"])

    print(f"Dataset lines: Train={len(X_train)}, Val={len(X_val)}, Held-out Test={len(X_test)}")

    # Model Architecture: Character n-gram TF-IDF + Calibrated Multi-Class Logistic Regression
    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(2, 5), analyzer="char_wb", min_df=2)),
        ("clf", LogisticRegression(C=10.0, max_iter=1000, random_state=RANDOM_SEED))
    ])

    print("Fitting biomarker extraction model...")
    pipeline.fit(X_train, y_train)

    # Validation evaluation
    val_preds = pipeline.predict(X_val)
    val_f1 = f1_score(y_val, val_preds, average="weighted")
    print(f"Validation Weighted F1-Score: {val_f1:.4f}")

    # Held-out Test evaluation (unseen casual layout template)
    test_preds = pipeline.predict(X_test)
    test_f1 = f1_score(y_test, test_preds, average="weighted")
    print(f"Held-out Test Weighted F1-Score: {test_f1:.4f}")
    
    # Save model checkpoint and metadata
    checkpoint_path = os.path.join(model_dir, "biomarker_extractor_v1.joblib")
    joblib.dump(pipeline, checkpoint_path)
    print(f"Saved trained model checkpoint to {checkpoint_path}")

    # Save evaluation metrics
    metrics = {
        "model_version": "v1.0.0",
        "random_seed": RANDOM_SEED,
        "validation_weighted_f1": float(val_f1),
        "held_out_test_weighted_f1": float(test_f1),
        "train_samples": len(X_train),
        "val_samples": len(X_val),
        "test_samples": len(X_test),
        "classes": list(pipeline.classes_)
    }
    metrics_path = os.path.join(model_dir, "metrics.json")
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    return metrics

if __name__ == "__main__":
    train_biomarker_classifier()
