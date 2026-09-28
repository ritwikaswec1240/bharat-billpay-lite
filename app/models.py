import enum
from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, Index
from sqlalchemy.orm import relationship

from app.database import Base


class BillerCategory(str, enum.Enum):
    ELECTRICITY = "ELECTRICITY"
    WATER = "WATER"
    GAS = "GAS"
    TELECOM = "TELECOM"
    DTH = "DTH"
    EDUCATION = "EDUCATION"


class BillStatus(str, enum.Enum):
    PENDING = "PENDING"
    PAID = "PAID"


class TransactionStatus(str, enum.Enum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    PENDING = "PENDING"


class Biller(Base):
    __tablename__ = "billers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    code = Column(String(20), unique=True, nullable=False, index=True)
    category = Column(Enum(BillerCategory), nullable=False, index=True)

    bills = relationship("Bill", back_populates="biller")


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    mobile = Column(String(15), unique=True, nullable=False, index=True)

    bills = relationship("Bill", back_populates="customer")


class Bill(Base):
    __tablename__ = "bills"

    id = Column(Integer, primary_key=True, index=True)
    biller_id = Column(Integer, ForeignKey("billers.id"), nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False, index=True)
    bill_number = Column(String(40), nullable=False)
    amount = Column(Float, nullable=False)
    due_date = Column(DateTime, nullable=False)
    status = Column(Enum(BillStatus), default=BillStatus.PENDING, nullable=False, index=True)

    biller = relationship("Biller", back_populates="bills")
    customer = relationship("Customer", back_populates="bills")
    transactions = relationship("Transaction", back_populates="bill")

    # A customer rarely has more than a handful of bills with the same biller,
    # so this composite index keeps "find my pending bills" queries cheap.
    __table_args__ = (
        Index("ix_bills_customer_status", "customer_id", "status"),
    )


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    bill_id = Column(Integer, ForeignKey("bills.id"), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    payment_mode = Column(String(20), nullable=False, default="UPI")
    status = Column(Enum(TransactionStatus), default=TransactionStatus.PENDING, nullable=False)
    risk_score = Column(Float, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    bill = relationship("Bill", back_populates="transactions")
