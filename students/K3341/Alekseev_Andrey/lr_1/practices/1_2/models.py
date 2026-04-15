from typing import Optional

from sqlmodel import Field, Relationship, SQLModel


class TransactionTagLink(SQLModel, table=True):
    transaction_id: Optional[int] = Field(default=None, foreign_key="transaction.id", primary_key=True)
    tag_id: Optional[int] = Field(default=None, foreign_key="tag.id", primary_key=True)
    importance: int = 1


class Category(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    transactions: list["Transaction"] = Relationship(back_populates="category")


class Tag(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    transactions: list["Transaction"] = Relationship(back_populates="tags", link_model=TransactionTagLink)


class TransactionBase(SQLModel):
    amount: float
    category_id: Optional[int] = Field(default=None, foreign_key="category.id")


class Transaction(TransactionBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    category: Optional[Category] = Relationship(back_populates="transactions")
    tags: list[Tag] = Relationship(back_populates="transactions", link_model=TransactionTagLink)
