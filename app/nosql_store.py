"""
Transaction event log — modelled the way you would model it in Apache Cassandra,
implemented here as a lightweight JSON-backed store so the demo needs no
external database server.

Design (maps directly onto a CQL table):

    CREATE TABLE transaction_events (
        customer_id   int,
        event_time    timestamp,
        transaction_id int,
        bill_id       int,
        event_type    text,   -- INITIATED / SUCCESS / FAILED
        details       text,
        PRIMARY KEY (customer_id, event_time)
    ) WITH CLUSTERING ORDER BY (event_time DESC);

- Partition key: customer_id -> all of one customer's events live together,
  which is exactly how you'd want to page through "my recent payments".
- Clustering key: event_time -> events come back time-ordered for free.

This is a write-heavy, append-only, denormalised log — a good fit for a
wide-column store like Cassandra rather than a normalised relational table,
which is why it's kept separate from the SQL models in models.py.
"""
import json
import os
import threading
from datetime import datetime, timezone
from typing import Optional

from app.config import NOSQL_LOG_PATH

_lock = threading.Lock()


def _ensure_store():
    os.makedirs(os.path.dirname(NOSQL_LOG_PATH), exist_ok=True)
    if not os.path.exists(NOSQL_LOG_PATH):
        with open(NOSQL_LOG_PATH, "w") as f:
            json.dump([], f)


def append_event(
    customer_id: int,
    transaction_id: int,
    bill_id: int,
    event_type: str,
    details: Optional[str] = None,
) -> dict:
    """Append one event. Analogous to an INSERT into the Cassandra table above."""
    _ensure_store()
    event = {
        "customer_id": customer_id,
        "event_time": datetime.now(timezone.utc).isoformat(),
        "transaction_id": transaction_id,
        "bill_id": bill_id,
        "event_type": event_type,
        "details": details,
    }
    with _lock:
        with open(NOSQL_LOG_PATH, "r") as f:
            events = json.load(f)
        events.append(event)
        with open(NOSQL_LOG_PATH, "w") as f:
            json.dump(events, f, indent=2)
    return event


def get_events_for_customer(customer_id: int) -> list[dict]:
    """Analogous to SELECT * FROM transaction_events WHERE customer_id = ?
    ORDER BY event_time DESC -- cheap because it's the partition key."""
    _ensure_store()
    with open(NOSQL_LOG_PATH, "r") as f:
        events = json.load(f)
    matching = [e for e in events if e["customer_id"] == customer_id]
    return sorted(matching, key=lambda e: e["event_time"], reverse=True)
