# Bharat BillPay Lite

A small, self-contained demo of a **Bharat BillPay–style bill payment aggregator**, built to
showcase the skills listed in NBBL's *Graduate Engineer Trainee* job description:
backend APIs, relational + NoSQL-style data modelling, basic ML/predictive analytics,
and automated testing.

> This is a portfolio/demo project, not affiliated with NPCI or NBBL.

## What it does

- Registers **billers** across categories (electricity, water, gas, telecom, DTH, education).
- Lets a customer **fetch a pending bill** and **pay it** through a unified REST API
  (mirrors the "unified, interoperable platform" idea behind Bharat BillPay).
- Records every payment attempt in an **append-only event log store**, modelled the way
  you would model it in Apache Cassandra (partition key = customer, clustering key = time),
  to demonstrate NoSQL / distributed-data thinking without requiring a Cassandra cluster to run.
- Scores each payment with a small **ML risk model** (scikit-learn) that predicts the
  probability a transaction will fail, as a stand-in for real-time fraud/risk analytics.
- Ships with **unit + integration tests** (pytest), a **Postman collection**, and an
  optional **Selenium** smoke test against a tiny HTML "bill lookup" page.

## Why this maps to the JD

| JD requirement | Where it shows up here |
|---|---|
| Design, code, test, deploy scalable components | FastAPI app split into routers / services / data layer |
| RESTful APIs, OOP, backend concepts | `app/routers/*`, `app/crud.py`, Pydantic schemas |
| SQL, database design, query optimisation | `app/models.py` (SQLAlchemy), indexed columns, `docs/architecture.md` |
| Apache Cassandra / NoSQL / distributed data | `app/nosql_store.py` — partition/clustering-key design explained in code |
| Basic ML: classification, predictive analytics | `app/ml/train_model.py`, `app/ml/predict.py`, `/analytics/risk-score` endpoint |
| scikit-learn, NumPy, Pandas | used in `app/ml/train_model.py` |
| Testing principles, automation (Selenium/Postman) | `tests/`, `postman_collection.json`, `selenium_test.py` |
| Documentation, SOPs, architecture diagrams | `docs/architecture.md` |

## Project layout

```
bharat-billpay-lite/
├── app/
│   ├── main.py              # FastAPI app entrypoint
│   ├── config.py            # settings
│   ├── database.py          # SQLAlchemy engine/session
│   ├── models.py            # Biller, Customer, Bill, Transaction tables
│   ├── schemas.py           # Pydantic request/response models
│   ├── crud.py               # DB access functions
│   ├── nosql_store.py        # Cassandra-style event log (JSON-backed for local demo)
│   ├── routers/
│   │   ├── billers.py
│   │   ├── bills.py
│   │   ├── payments.py
│   │   └── analytics.py     # risk-score / ML endpoint
│   ├── ml/
│   │   ├── train_model.py   # generates synthetic data + trains classifier
│   │   └── predict.py       # loads model, scores a transaction
│   └── templates/
│       └── lookup.html      # tiny page for the Selenium demo
├── tests/
│   ├── test_billers.py
│   ├── test_payments.py
│   └── test_ml.py
├── selenium_test.py          # optional UI smoke test
├── postman_collection.json
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .github/workflows/ci.yml
└── docs/architecture.md
```

## Running it locally

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

# train the (tiny) ML model once
python -m app.ml.train_model

# start the API
uvicorn app.main:app --reload
```

Then open http://127.0.0.1:8000/docs for interactive Swagger UI.

## Running the tests

```bash
pytest -v
```

## Running with Docker

```bash
docker compose up --build
```

## Pushing this to your own GitHub

```bash
cd bharat-billpay-lite
git init
git add .
git commit -m "Initial commit: Bharat BillPay Lite demo"
git branch -M main
git remote add origin https://github.com/<your-username>/bharat-billpay-lite.git
git push -u origin main
```
