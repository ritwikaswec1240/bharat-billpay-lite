from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models import BillerCategory, BillStatus, TransactionStatus


class BillerCreate(BaseModel):
    name: str
    code: str
    category: BillerCategory


class BillerOut(BillerCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int


class CustomerCreate(BaseModel):
    name: str
    mobile: str


class CustomerOut(CustomerCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int


class BillCreate(BaseModel):
    biller_id: int
    customer_id: int
    bill_number: str
    amount: float
    due_date: datetime


class BillOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    biller_id: int
    customer_id: int
    bill_number: str
    amount: float
    due_date: datetime
    status: BillStatus


class PaymentRequest(BaseModel):
    bill_id: int
    payment_mode: str = "UPI"


class PaymentResult(BaseModel):
    transaction_id: int
    bill_id: int
    amount: float
    status: TransactionStatus
    risk_score: float
    created_at: datetime


class RiskScoreRequest(BaseModel):
    amount: float
    hour_of_day: int
    biller_category: BillerCategory
    customer_past_failures: int = 0


class RiskScoreResponse(BaseModel):
    risk_score: float
    risk_band: str
