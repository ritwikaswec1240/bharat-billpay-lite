"""Central place for settings so nothing is hard-coded in business logic."""
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Relational store: SQLite by default so the demo runs with zero setup.
# Point DATABASE_URL at Postgres/MySQL in a real deployment.
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR}/billpay.db")

# "NoSQL" event log store. In production this would be an Apache Cassandra
# table; for the demo we persist to a JSON file so it runs anywhere.
NOSQL_LOG_PATH = os.getenv("NOSQL_LOG_PATH", os.path.join(BASE_DIR, "data", "transaction_log.json"))

ML_MODEL_PATH = os.getenv("ML_MODEL_PATH", os.path.join(BASE_DIR, "app", "ml", "risk_model.pkl"))
