import os

import joblib
import pandas as pd

from app.config import ML_MODEL_PATH
from app.ml.train_model import CATEGORIES, train

_cache = {}


def _load():
    if "bundle" not in _cache:
        if not os.path.exists(ML_MODEL_PATH):
            # First run convenience: train on the fly rather than crashing.
            train()
        _cache["bundle"] = joblib.load(ML_MODEL_PATH)
    return _cache["bundle"]


def score_transaction(amount: float, hour_of_day: int, biller_category: str, customer_past_failures: int) -> float:
    bundle = _load()
    model = bundle["model"]
    feature_columns = bundle["feature_columns"]

    row = {"amount": amount, "hour_of_day": hour_of_day, "past_failures": customer_past_failures}
    for cat in CATEGORIES:
        row[f"cat_{cat}"] = 1 if cat == biller_category else 0

    X = pd.DataFrame([row])[feature_columns]
    return float(model.predict_proba(X)[0, 1])


def risk_band(score: float) -> str:
    if score < 0.15:
        return "LOW"
    if score < 0.4:
        return "MEDIUM"
    return "HIGH"
