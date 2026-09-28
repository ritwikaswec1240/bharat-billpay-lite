from fastapi import APIRouter

from app import schemas
from app.ml.predict import score_transaction, risk_band

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.post("/risk-score", response_model=schemas.RiskScoreResponse)
def risk_score(request: schemas.RiskScoreRequest):
    """Score any hypothetical transaction without touching the database --
    handy for demoing the ML model on its own."""
    score = score_transaction(
        amount=request.amount,
        hour_of_day=request.hour_of_day,
        biller_category=request.biller_category.value,
        customer_past_failures=request.customer_past_failures,
    )
    return schemas.RiskScoreResponse(risk_score=score, risk_band=risk_band(score))
