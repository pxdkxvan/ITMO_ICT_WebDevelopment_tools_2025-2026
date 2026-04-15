from fastapi import FastAPI, HTTPException

from models import Category, Tag, Transaction

app = FastAPI(title="Practice 1.1")

temp_db: list[dict] = [
    {
        "id": 1,
        "kind": "income",
        "amount": 70000,
        "category": {"id": 1, "name": "Salary"},
        "tags": [{"id": 1, "name": "job"}],
    },
    {
        "id": 2,
        "kind": "expense",
        "amount": 2500,
        "category": {"id": 2, "name": "Food"},
        "tags": [{"id": 2, "name": "groceries"}],
    },
]


@app.get("/transactions", response_model=list[Transaction])
def list_transactions() -> list[dict]:
    return temp_db


@app.get("/transactions/{transaction_id}", response_model=Transaction)
def get_transaction(transaction_id: int) -> dict:
    tx = next((item for item in temp_db if item["id"] == transaction_id), None)
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return tx


@app.post("/transactions", response_model=Transaction)
def create_transaction(payload: Transaction) -> dict:
    temp_db.append(payload.model_dump())
    return payload.model_dump()


@app.put("/transactions/{transaction_id}", response_model=Transaction)
def update_transaction(transaction_id: int, payload: Transaction) -> dict:
    for index, item in enumerate(temp_db):
        if item["id"] == transaction_id:
            temp_db[index] = payload.model_dump()
            return temp_db[index]
    raise HTTPException(status_code=404, detail="Transaction not found")


@app.delete("/transactions/{transaction_id}")
def delete_transaction(transaction_id: int) -> dict[str, bool]:
    for index, item in enumerate(temp_db):
        if item["id"] == transaction_id:
            temp_db.pop(index)
            return {"ok": True}
    raise HTTPException(status_code=404, detail="Transaction not found")
