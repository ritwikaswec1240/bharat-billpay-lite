from app.ml.predict import score_transaction, risk_band


def test_score_transaction_returns_probability():
    score = score_transaction(
        amount=500,
        hour_of_day=14,
        biller_category="ELECTRICITY",
        customer_past_failures=0,
    )
    assert 0.0 <= score <= 1.0


def test_repeat_failures_increase_risk():
    low = score_transaction(amount=500, hour_of_day=14, biller_category="ELECTRICITY", customer_past_failures=0)
    high = score_transaction(amount=500, hour_of_day=14, biller_category="ELECTRICITY", customer_past_failures=5)
    assert high >= low


def test_risk_band_thresholds():
    assert risk_band(0.05) == "LOW"
    assert risk_band(0.25) == "MEDIUM"
    assert risk_band(0.8) == "HIGH"
