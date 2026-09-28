from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db

router = APIRouter(prefix="/billers", tags=["billers"])


@router.post("/", response_model=schemas.BillerOut)
def create_biller(biller: schemas.BillerCreate, db: Session = Depends(get_db)):
    return crud.create_biller(db, biller)


@router.get("/", response_model=list[schemas.BillerOut])
def list_billers(category: Optional[str] = None, db: Session = Depends(get_db)):
    return crud.list_billers(db, category)
