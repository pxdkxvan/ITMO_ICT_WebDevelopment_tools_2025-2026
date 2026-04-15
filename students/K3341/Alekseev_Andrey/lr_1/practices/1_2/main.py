from fastapi import Depends, FastAPI, HTTPException
from sqlmodel import select

from connection import get_session, init_db
from models import Transaction, TransactionBase

app = FastAPI(title="Practice 1.2")


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.post("/transactions")
def create_transaction(payload: TransactionBase, session=Depends(get_session)) -> Transaction:
    item = Transaction.model_validate(payload)
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


@app.get("/transactions")
def list_transactions(session=Depends(get_session)) -> list[Transaction]:
    return session.exec(select(Transaction)).all()


@app.get("/transactions/{transaction_id}")
def get_transaction(transaction_id: int, session=Depends(get_session)) -> Transaction:
    item = session.get(Transaction, transaction_id)
    if not item:
        raise HTTPException(status_code=404, detail="Not found")
    return item
