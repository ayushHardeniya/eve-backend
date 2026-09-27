def test_signup_and_login(client):
    response = client.post(
        "/auth/signup",
        json={
            "email": "user@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 200
    assert "access_token" in response.json()

    response = client.post(
        "/auth/login",
        json={
            "email": "user@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 200
    assert "access_token" in response.json()


def test_duplicate_signup(client):
    payload = {
        "email": "user@example.com",
        "password": "password123",
    }

    assert client.post("/auth/signup", json=payload).status_code == 200
    assert client.post("/auth/signup", json=payload).status_code == 400


def test_protected_endpoint_requires_auth(client):
    response = client.get("/auth/me")
    assert response.status_code == 401


def test_create_booking(client, auth_headers):
    centre = client.post(
        "/centres/",
        json={"name": "City Diagnostics", "location": "Delhi"},
    ).json()

    test = client.post(
        "/tests/",
        json={"name": "CBC"},
    ).json()

    client.post(
        f"/centres/{centre['id']}/tests/",
        json={"test_id": test["id"], "price": 500},
    )

    response = client.post(
        "/bookings/",
        headers=auth_headers,
        json={
            "test_id": test["id"],
            "centre_id": centre["id"],
            "appointment_at": "2026-10-01T10:00:00",
        },
    )

    assert response.status_code == 200
    assert response.json()["amount"] == "500.00"
    assert response.json()["status"] == "PENDING"


def test_payment_success_confirms_booking(client, auth_headers):
    centre = client.post(
        "/centres/",
        json={"name": "City Diagnostics", "location": "Delhi"},
    ).json()

    test = client.post(
        "/tests/",
        json={"name": "CBC"},
    ).json()

    client.post(
        f"/centres/{centre['id']}/tests/",
        json={"test_id": test["id"], "price": 500},
    )

    booking = client.post(
        "/bookings/",
        headers=auth_headers,
        json={
            "test_id": test["id"],
            "centre_id": centre["id"],
            "appointment_at": "2026-10-01T10:00:00",
        },
    ).json()

    response = client.post(
        "/payments/",
        headers=auth_headers,
        json={
            "booking_id": booking["id"],
            "status": "SUCCESS",
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "SUCCESS"

    booking = client.get(
        f"/bookings/{booking['id']}",
        headers=auth_headers,
    ).json()

    assert booking["status"] == "CONFIRMED"


def test_webhook_is_idempotent(client, auth_headers):
    centre = client.post(
        "/centres/",
        json={"name": "City Diagnostics", "location": "Delhi"},
    ).json()

    test = client.post(
        "/tests/",
        json={"name": "CBC"},
    ).json()

    client.post(
        f"/centres/{centre['id']}/tests/",
        json={"test_id": test["id"], "price": 500},
    )

    booking = client.post(
        "/bookings/",
        headers=auth_headers,
        json={
            "test_id": test["id"],
            "centre_id": centre["id"],
            "appointment_at": "2026-10-01T10:00:00",
        },
    ).json()

    payload = {
        "event_id": "evt_123",
        "booking_id": booking["id"],
        "status": "SUCCESS",
    }

    first = client.post("/payments/webhook/", json=payload)
    second = client.post("/payments/webhook/", json=payload)

    assert first.status_code == 200
    assert second.status_code == 200
    assert second.json()["message"] == "Event already processed"
