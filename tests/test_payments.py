def _setup_biller_customer_bill(client, amount=250.0):
    biller = client.post("/billers/", json={
        "name": "MSEB", "code": "MSEB01", "category": "ELECTRICITY",
    }).json()

    customer = client.post("/customers/", json={
        "name": "Test User", "mobile": "9999999999",
    }).json()

    bill = client.post("/bills/", json={
        "biller_id": biller["id"],
        "customer_id": customer["id"],
        "bill_number": "BILL-001",
        "amount": amount,
        "due_date": "2026-12-01T00:00:00",
    }).json()

    return biller, customer["id"], bill


def test_pay_bill_records_transaction_and_event(client):
    biller, customer_id, bill = _setup_biller_customer_bill(client)

    resp = client.post("/payments/", json={"bill_id": bill["id"], "payment_mode": "UPI"})
    assert resp.status_code == 200
    result = resp.json()
    assert result["status"] in ("SUCCESS", "FAILED")
    assert 0.0 <= result["risk_score"] <= 1.0

    history = client.get(f"/payments/customer/{customer_id}/history").json()
    assert len(history) == 1
    assert history[0]["bill_id"] == bill["id"]


def test_paying_twice_is_rejected(client):
    biller, customer_id, bill = _setup_biller_customer_bill(client)

    first = client.post("/payments/", json={"bill_id": bill["id"]}).json()
    if first["status"] == "SUCCESS":
        second = client.post("/payments/", json={"bill_id": bill["id"]})
        assert second.status_code == 400
