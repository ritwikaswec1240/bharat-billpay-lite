from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db

router = APIRouter(prefix="/bills", tags=["bills"])


@router.post("/", response_model=schemas.BillOut)
def create_bill(bill: schemas.BillCreate, db: Session = Depends(get_db)):
    return crud.create_bill(db, bill)


@router.get("/customer/{customer_id}/pending", response_model=list[schemas.BillOut])
def pending_bills(customer_id: int, db: Session = Depends(get_db)):
    if not crud.get_customer(db, customer_id):
        raise HTTPException(status_code=404, detail="Customer not found")
    return crud.list_pending_bills(db, customer_id)


@router.get("/{bill_id}", response_model=schemas.BillOut)
def get_bill(bill_id: int, db: Session = Depends(get_db)):
    bill = crud.get_bill(db, bill_id)
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")
    return bill
