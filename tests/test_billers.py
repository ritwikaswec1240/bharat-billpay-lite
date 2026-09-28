def test_create_and_list_biller(client):
    resp = client.post("/billers/", json={
        "name": "Tata Power",
        "code": "TATAPWR",
        "category": "ELECTRICITY",
    })
    assert resp.status_code == 200
    body = resp.json()
    assert body["code"] == "TATAPWR"

    resp = client.get("/billers/", params={"category": "ELECTRICITY"})
    assert resp.status_code == 200
    assert any(b["code"] == "TATAPWR" for b in resp.json())


def test_pending_bills_for_unknown_customer_404s(client):
    resp = client.get("/bills/customer/999/pending")
    assert resp.status_code == 404
