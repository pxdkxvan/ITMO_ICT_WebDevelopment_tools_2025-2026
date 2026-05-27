from pydantic import BaseModel, Field

from app.models.entities import TransactionKind


class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    kind: TransactionKind


class CategoryUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    kind: TransactionKind | None = None


class CategoryRead(BaseModel):
    id: int
    name: str
    kind: TransactionKind
