"""
Trains a small classifier that predicts the probability a bill payment will
FAIL, given: amount, hour of day, biller category, and the customer's past
failure count. This stands in for the "predictive analytics" bullet in the
JD -- in production you'd swap the synthetic data for real transaction
history and probably retrain with a scheduled job.

Run with:  python -m app.ml.train_model
"""
import os

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, roc_auc_score

from app.config import ML_MODEL_PATH

CATEGORIES = ["ELECTRICITY", "WATER", "GAS", "TELECOM", "DTH", "EDUCATION"]


def generate_synthetic_dataset(n_rows: int = 4000, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    amount = rng.gamma(shape=2.0, scale=400, size=n_rows)          # skewed, mostly small bills
    hour_of_day = rng.integers(0, 24, size=n_rows)
    category = rng.choice(CATEGORIES, size=n_rows)
    past_failures = rng.poisson(0.3, size=n_rows)

    # Hand-crafted "ground truth" so the model learns a plausible pattern:
    # bigger amounts, odd hours, and repeat-failure customers fail more.
    category_risk = {
        "ELECTRICITY": 0.02, "WATER": 0.01, "GAS": 0.02,
        "TELECOM": 0.04, "DTH": 0.03, "EDUCATION": 0.05,
    }
    base_risk = np.array([category_risk[c] for c in category])
    late_night_penalty = np.where((hour_of_day < 5) | (hour_of_day > 23), 0.10, 0.0)
    amount_penalty = np.clip(amount / 10000, 0, 0.25)
    repeat_offender_penalty = np.clip(past_failures * 0.15, 0, 0.5)

    fail_prob = np.clip(base_risk + late_night_penalty + amount_penalty + repeat_offender_penalty, 0, 0.95)
    is_failed = rng.binomial(1, fail_prob)

    return pd.DataFrame({
        "amount": amount,
        "hour_of_day": hour_of_day,
        "category": category,
        "past_failures": past_failures,
        "is_failed": is_failed,
    })


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    encoded = pd.get_dummies(df["category"], prefix="cat")
    for cat in CATEGORIES:
        col = f"cat_{cat}"
        if col not in encoded:
            encoded[col] = 0
    return pd.concat([df[["amount", "hour_of_day", "past_failures"]], encoded[[f"cat_{c}" for c in CATEGORIES]]], axis=1)


def train():
    df = generate_synthetic_dataset()
    X = build_features(df)
    y = df["is_failed"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    model = RandomForestClassifier(n_estimators=150, max_depth=6, random_state=42, class_weight="balanced")
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    proba = model.predict_proba(X_test)[:, 1]
    print(f"Accuracy: {accuracy_score(y_test, preds):.3f}")
    print(f"ROC AUC:  {roc_auc_score(y_test, proba):.3f}")

    os.makedirs(os.path.dirname(ML_MODEL_PATH), exist_ok=True)
    joblib.dump({"model": model, "feature_columns": list(X.columns)}, ML_MODEL_PATH)
    print(f"Saved model to {ML_MODEL_PATH}")


if __name__ == "__main__":
    train()
