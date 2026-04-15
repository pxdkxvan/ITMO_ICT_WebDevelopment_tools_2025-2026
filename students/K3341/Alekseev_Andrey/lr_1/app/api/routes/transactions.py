from fastapi import APIRouter, HTTPException, status
from sqlmodel import select

from app.api.deps import CurrentUserDep, SessionDep
from app.models.entities import Category, Tag, Transaction, TransactionTagLink
from app.schemas.categories import CategoryRead
from app.schemas.transactions import (
    TransactionCreate,
    TransactionRead,
    TransactionTagAttach,
    TransactionTagRead,
    TransactionUpdate,
)

router = APIRouter(prefix="/transactions", tags=["transactions"])


def _build_transaction_read(tx: Transaction, session: SessionDep) -> TransactionRead:
    category = session.get(Category, tx.category_id)
    tag_links = session.exec(
        select(TransactionTagLink).where(TransactionTagLink.transaction_id == tx.id)
    ).all()

    tags: list[TransactionTagRead] = []
    for link in tag_links:
        tag = session.get(Tag, link.tag_id)
        if tag:
            tags.append(
                TransactionTagRead(id=tag.id, name=tag.name, importance=link.importance, note=link.note)
            )

    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    return TransactionRead(
        id=tx.id,
        amount=tx.amount,
        description=tx.description,
        transaction_date=tx.transaction_date,
        kind=tx.kind,
        category=CategoryRead(id=category.id, name=category.name, kind=category.kind),
        tags=tags,
    )


@router.get("", response_model=list[TransactionRead])
def list_transactions(current_user: CurrentUserDep, session: SessionDep) -> list[TransactionRead]:
    items = session.exec(select(Transaction).where(Transaction.user_id == current_user.id)).all()
    return [_build_transaction_read(item, session) for item in items]


@router.post("", response_model=TransactionRead, status_code=status.HTTP_201_CREATED)
def create_transaction(
    payload: TransactionCreate, current_user: CurrentUserDep, session: SessionDep
) -> TransactionRead:
    category = session.get(Category, payload.category_id)
    if not category or category.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid category")

    tx = Transaction(
        amount=payload.amount,
        description=payload.description,
        transaction_date=payload.transaction_date,
        kind=payload.kind,
        category_id=payload.category_id,
        user_id=current_user.id,
    )
    session.add(tx)
    session.commit()
    session.refresh(tx)
    return _build_transaction_read(tx, session)


@router.get("/{transaction_id}", response_model=TransactionRead)
def get_transaction(transaction_id: int, current_user: CurrentUserDep, session: SessionDep) -> TransactionRead:
    tx = session.get(Transaction, transaction_id)
    if not tx or tx.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    return _build_transaction_read(tx, session)


@router.patch("/{transaction_id}", response_model=TransactionRead)
def update_transaction(
    transaction_id: int,
    payload: TransactionUpdate,
    current_user: CurrentUserDep,
    session: SessionDep,
) -> TransactionRead:
    tx = session.get(Transaction, transaction_id)
    if not tx or tx.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")

    update_data = payload.model_dump(exclude_unset=True)
    if "category_id" in update_data:
        category = session.get(Category, update_data["category_id"])
        if not category or category.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid category")

    for key, value in update_data.items():
        setattr(tx, key, value)

    session.add(tx)
    session.commit()
    session.refresh(tx)
    return _build_transaction_read(tx, session)


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(transaction_id: int, current_user: CurrentUserDep, session: SessionDep) -> None:
    tx = session.get(Transaction, transaction_id)
    if not tx or tx.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")

    links = session.exec(
        select(TransactionTagLink).where(TransactionTagLink.transaction_id == transaction_id)
    ).all()
    for link in links:
        session.delete(link)

    session.delete(tx)
    session.commit()


@router.post("/{transaction_id}/tags", response_model=TransactionRead)
def attach_tag(
    transaction_id: int,
    payload: TransactionTagAttach,
    current_user: CurrentUserDep,
    session: SessionDep,
) -> TransactionRead:
    tx = session.get(Transaction, transaction_id)
    if not tx or tx.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")

    tag = session.get(Tag, payload.tag_id)
    if not tag or tag.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")

    link = session.get(TransactionTagLink, (transaction_id, payload.tag_id))
    if link:
        link.importance = payload.importance
        link.note = payload.note
    else:
        link = TransactionTagLink(
            transaction_id=transaction_id,
            tag_id=payload.tag_id,
            importance=payload.importance,
            note=payload.note,
        )

    session.add(link)
    session.commit()
    session.refresh(tx)
    return _build_transaction_read(tx, session)


@router.delete("/{transaction_id}/tags/{tag_id}", response_model=TransactionRead)
def detach_tag(
    transaction_id: int,
    tag_id: int,
    current_user: CurrentUserDep,
    session: SessionDep,
) -> TransactionRead:
    tx = session.get(Transaction, transaction_id)
    if not tx or tx.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")

    link = session.get(TransactionTagLink, (transaction_id, tag_id))
    if not link:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag link not found")

    session.delete(link)
    session.commit()
    session.refresh(tx)
    return _build_transaction_read(tx, session)
