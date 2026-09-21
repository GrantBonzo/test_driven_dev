import pytest
from fastapi.testclient import TestClient

import knight_cash_api
from knight_cash_api import app, accounts


@pytest.fixture(autouse=True)
def reset_accounts():
    """Reset the in-memory ledger to a known state before every test."""
    original = {"knight_001": 1000.0, "knight_002": 500.0, "knight_003": 0.0}
    accounts.clear()
    accounts.update(original)
    yield
    accounts.clear()
    accounts.update(original)


@pytest.fixture
def client():
    return TestClient(app)


# ---------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------

def test_get_balance_happy_path(client):
    resp = client.get("/balance/knight_001")
    assert resp.status_code == 200
    assert resp.json() == {"account_id": "knight_001", "balance": 1000.0}


def test_transfer_happy_path(client):
    resp = client.post(
        "/transfer",
        json={"from_account": "knight_001", "to_account": "knight_002", "amount": 100.0},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["from_balance"] == 900.0
    assert body["to_balance"] == 600.0


# ---------------------------------------------------------------------
# Negative / edge cases (these are expected to FAIL against the
# original, unfixed knight_cash_api.py)
# ---------------------------------------------------------------------

def test_transfer_negative_amount_is_rejected(client):
    resp = client.post(
        "/transfer",
        json={"from_account": "knight_001", "to_account": "knight_002", "amount": -100.0},
    )
    assert resp.status_code == 400


def test_transfer_zero_amount_is_rejected(client):
    resp = client.post(
        "/transfer",
        json={"from_account": "knight_001", "to_account": "knight_002", "amount": 0.0},
    )
    assert resp.status_code == 400


def test_transfer_amount_exceeding_balance_is_rejected(client):
    resp = client.post(
        "/transfer",
        json={"from_account": "knight_003", "to_account": "knight_002", "amount": 50.0},
    )
    assert resp.status_code == 400
    # Balances must be untouched after a rejected transfer.
    assert accounts["knight_003"] == 0.0
    assert accounts["knight_002"] == 500.0


def test_transfer_exact_balance_is_allowed(client):
    """Boundary value: transferring exactly the full balance should succeed."""
    resp = client.post(
        "/transfer",
        json={"from_account": "knight_002", "to_account": "knight_001", "amount": 500.0},
    )
    assert resp.status_code == 200
    assert resp.json()["from_balance"] == 0.0


def test_transfer_from_nonexistent_account_returns_404(client):
    resp = client.post(
        "/transfer",
        json={"from_account": "ghost_knight", "to_account": "knight_002", "amount": 10.0},
    )
    assert resp.status_code == 404


def test_transfer_to_nonexistent_account_returns_404(client):
    resp = client.post(
        "/transfer",
        json={"from_account": "knight_001", "to_account": "ghost_knight", "amount": 10.0},
    )
    assert resp.status_code == 404


def test_transfer_to_self_is_rejected(client):
    resp = client.post(
        "/transfer",
        json={"from_account": "knight_001", "to_account": "knight_001", "amount": 50.0},
    )
    assert resp.status_code == 400


def test_get_balance_nonexistent_account_returns_404(client):
    resp = client.get("/balance/ghost_knight")
    assert resp.status_code == 404
