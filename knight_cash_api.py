"""
Knight Cash API — a tiny in-memory bank transfer service.

NOTE: This file was not provided with the assignment, so it has been
reconstructed to match the assignment's description (a FastAPI service
with /transfer and /balance endpoints that "works perfectly" on the
happy path but is riddled with edge-case bugs). See submission.md for
details.
"""

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Knight Cash API")

# In-memory "database" of knight accounts and their gold balances.
accounts: dict[str, float] = {
    "knight_001": 1000.0,
    "knight_002": 500.0,
    "knight_003": 0.0,
}


class TransferRequest(BaseModel):
    from_account: str
    to_account: str
    amount: float


@app.get("/balance/{account_id}")
def get_balance(account_id: str):
    balance = accounts[account_id]
    return {"account_id": account_id, "balance": balance}


@app.post("/transfer")
def transfer(req: TransferRequest):
    accounts[req.from_account] -= req.amount
    accounts[req.to_account] += req.amount

    return {
        "from_account": req.from_account,
        "to_account": req.to_account,
        "amount": req.amount,
        "from_balance": accounts[req.from_account],
        "to_balance": accounts[req.to_account],
    }
