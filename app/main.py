import os

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.database import Base, engine
from app.routers import billers, bills, payments, analytics, customers

# Create tables on startup. For a real deployment you'd use Alembic migrations instead.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Bharat BillPay Lite",
    description="Demo bill-payment aggregator: REST APIs + SQL + Cassandra-style event log + ML risk scoring.",
    version="0.1.0",
)

templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))

app.include_router(customers.router)
app.include_router(billers.router)
app.include_router(bills.router)
app.include_router(payments.router)
app.include_router(analytics.router)


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("lookup.html", {"request": request})


@app.get("/health")
def health():
    return {"status": "ok"}
