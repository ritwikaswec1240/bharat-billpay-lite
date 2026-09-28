import random
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, schemas, models, nosql_store
from app.database import get_db
from app.ml.predict import score_transaction, risk_band

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("/", response_model=schemas.PaymentResult)
def pay_bill(payment: schemas.PaymentRequest, db: Session = Depends(get_db)):
    bill = crud.get_bill(db, payment.bill_id)
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")
    if bill.status == models.BillStatus.PAID:
        raise HTTPException(status_code=400, detail="Bill already paid")

    past_failures = crud.count_past_failures(db, bill.customer_id)
    risk = score_transaction(
        amount=bill.amount,
        hour_of_day=datetime.now(timezone.utc).hour,
        biller_category=bill.biller.category.value,
        customer_past_failures=past_failures,
    )

    # Simulate the actual payment gateway call. Higher risk -> more likely to fail,
    # mirroring how a real risk score would feed into step-up authentication / declines.
    failed = random.random() < min(risk, 0.9)
    status = models.TransactionStatus.FAILED if failed else models.TransactionStatus.SUCCESS

    txn = crud.create_transaction(
        db,
        bill_id=bill.id,
        amount=bill.amount,
        payment_mode=payment.payment_mode,
        status=status,
        risk_score=risk,
    )

    nosql_store.append_event(
        customer_id=bill.customer_id,
        transaction_id=txn.id,
        bill_id=bill.id,
        event_type=status.value,
        details=f"payment_mode={payment.payment_mode}, risk_score={risk:.3f}",
    )

    if status == models.TransactionStatus.SUCCESS:
        crud.mark_bill_paid(db, bill)

    return schemas.PaymentResult(
        transaction_id=txn.id,
        bill_id=bill.id,
        amount=txn.amount,
        status=txn.status,
        risk_score=txn.risk_score,
        created_at=txn.created_at,
    )


@router.get("/customer/{customer_id}/history")
def payment_history(customer_id: int):
    """Reads from the Cassandra-style event log, not the relational DB."""
    return nosql_store.get_events_for_customer(customer_id)
