from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app import models, schemas


# ---- Billers -------------------------------------------------------------

def create_biller(db: Session, biller: schemas.BillerCreate) -> models.Biller:
    db_biller = models.Biller(**biller.model_dump())
    db.add(db_biller)
    db.commit()
    db.refresh(db_biller)
    return db_biller


def list_billers(db: Session, category: str | None = None):
    query = db.query(models.Biller)
    if category:
        query = query.filter(models.Biller.category == category)
    return query.all()


# ---- Customers -------------------------------------------------------------

def create_customer(db: Session, customer: schemas.CustomerCreate) -> models.Customer:
    db_customer = models.Customer(**customer.model_dump())
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer


def get_customer(db: Session, customer_id: int):
    return db.query(models.Customer).filter(models.Customer.id == customer_id).first()


# ---- Bills -------------------------------------------------------------

def create_bill(db: Session, bill: schemas.BillCreate) -> models.Bill:
    db_bill = models.Bill(**bill.model_dump())
    db.add(db_bill)
    db.commit()
    db.refresh(db_bill)
    return db_bill


def get_bill(db: Session, bill_id: int):
    return db.query(models.Bill).filter(models.Bill.id == bill_id).first()


def list_pending_bills(db: Session, customer_id: int):
    return (
        db.query(models.Bill)
        .filter(models.Bill.customer_id == customer_id, models.Bill.status == models.BillStatus.PENDING)
        .all()
    )


def count_past_failures(db: Session, customer_id: int) -> int:
    """Used as a feature for the ML risk model."""
    return (
        db.query(models.Transaction)
        .join(models.Bill)
        .filter(
            models.Bill.customer_id == customer_id,
            models.Transaction.status == models.TransactionStatus.FAILED,
        )
        .count()
    )


# ---- Transactions -------------------------------------------------------------

def create_transaction(
    db: Session,
    bill_id: int,
    amount: float,
    payment_mode: str,
    status: models.TransactionStatus,
    risk_score: float,
) -> models.Transaction:
    txn = models.Transaction(
        bill_id=bill_id,
        amount=amount,
        payment_mode=payment_mode,
        status=status,
        risk_score=risk_score,
        created_at=datetime.now(timezone.utc),
    )
    db.add(txn)
    db.commit()
    db.refresh(txn)
    return txn


def mark_bill_paid(db: Session, bill: models.Bill):
    bill.status = models.BillStatus.PAID
    db.commit()
    db.refresh(bill)
    return bill
