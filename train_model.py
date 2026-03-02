"""
Phase 3 — Train a logistic regression model on password strength features.

Steps:
  1. Load the train/val/test CSVs from Phase 2
  2. Scale features with StandardScaler (so all features contribute equally)
  3. Train logistic regression with balanced class weights (upweights weak & strong)
  4. Evaluate on validation set — focus on weak recall
  5. Save the model + scaler for later use
"""

import csv
import numpy as np
import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
)

FEATURE_COLS = [
    "length", "num_lower", "num_upper", "num_digits", "num_symbols",
    "num_unique_chars", "unique_ratio", "max_run_length",
    "has_sequence", "has_dictionary_word", "ends_with_year",
]

LABEL_NAMES = {0: "weak", 1: "ok", 2: "strong"}


def load_csv(path):
    """Load a dataset CSV into numpy arrays (X features, y labels)."""
    X_rows = []
    y_rows = []

    with open(path, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            features = [float(row[col]) for col in FEATURE_COLS]
            X_rows.append(features)
            y_rows.append(int(row["label"]))

    return np.array(X_rows), np.array(y_rows)


def print_evaluation(name, y_true, y_pred):
    """Print accuracy, per-class metrics, and confusion matrix."""
    print(f"\n{'='*50}")
    print(f"  {name} Evaluation")
    print(f"{'='*50}")

    print(f"\nAccuracy: {accuracy_score(y_true, y_pred):.4f}")

    # per-class precision, recall, f1
    # recall for class 0 (weak) is the one we care about most
    print("\nPer-class metrics:")
    print(classification_report(
        y_true, y_pred,
        target_names=["weak (0)", "ok (1)", "strong (2)"],
    ))

    # confusion matrix: rows = actual, columns = predicted
    # helps us see if weak passwords are being mislabeled as ok/strong
    cm = confusion_matrix(y_true, y_pred)
    print("Confusion matrix (rows=actual, cols=predicted):")
    print(f"            predicted_0  predicted_1  predicted_2")
    for i, row in enumerate(cm):
        print(f"  actual_{i}:  {row[0]:>10}  {row[1]:>10}  {row[2]:>10}")


def main():
    # --- 1. Load data ---
    print("Loading datasets...")
    X_train, y_train = load_csv("dataset_train.csv")
    X_val, y_val = load_csv("dataset_val.csv")
    X_test, y_test = load_csv("dataset_test.csv")

    print(f"  train: {X_train.shape[0]} rows, val: {X_val.shape[0]} rows, test: {X_test.shape[0]} rows")

    # --- 2. Scale features ---
    # StandardScaler: transforms each feature to mean=0, std=1
    # this matters for logistic regression because it uses gradient descent —
    # features on different scales (length ~1-30 vs has_sequence 0/1) would
    # cause some features to dominate the learning process unfairly
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)  # fit on train only
    X_val_scaled = scaler.transform(X_val)           # apply same transform to val
    X_test_scaled = scaler.transform(X_test)

    # --- 3. Train logistic regression ---
    # class_weight='balanced': automatically gives higher weight to minority classes
    # (weak and strong are ~13% each vs ok at 74%)
    # this means the model is penalized more for getting a weak password wrong
    # than for getting an ok password wrong — exactly what we want for weak recall
    #
    # max_iter=1000: give the solver enough iterations to converge
    print("\nTraining logistic regression (balanced class weights)...")
    model = LogisticRegression(
        class_weight="balanced",
        max_iter=1000,
        random_state=42,
    )
    model.fit(X_train_scaled, y_train)

    # --- 4. Evaluate ---
    y_val_pred = model.predict(X_val_scaled)
    print_evaluation("Validation", y_val, y_val_pred)

    # also show test set (final held-out evaluation)
    y_test_pred = model.predict(X_test_scaled)
    print_evaluation("Test", y_test, y_test_pred)

    # --- 5. Save model + scaler ---
    joblib.dump(model, "model_logreg.pkl")
    joblib.dump(scaler, "scaler.pkl")
    print("\nSaved: model_logreg.pkl, scaler.pkl")


if __name__ == "__main__":
    main()
