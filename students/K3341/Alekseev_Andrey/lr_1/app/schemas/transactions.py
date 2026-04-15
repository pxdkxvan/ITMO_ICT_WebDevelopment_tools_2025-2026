from datetime import date

from pydantic import BaseModel, Field

from app.models.entities import TransactionKind
from app.schemas.categories import CategoryRead


class TransactionCreate(BaseModel):
    amount: float = Field(gt=0)
    description: str = ""
    transaction_date: date = Field(default_factory=date.today)
    kind: TransactionKind
    category_id: int


class TransactionUpdate(BaseModel):
    amount: float | None = Field(default=None, gt=0)
    description: str | None = None
    transaction_date: date | None = None
    kind: TransactionKind | None = None
    category_id: int | None = None


class TransactionTagAttach(BaseModel):
    tag_id: int
    importance: int = Field(default=1, ge=1, le=10)
    note: str = ""


class TransactionTagRead(BaseModel):
    id: int
    name: str
    importance: int
    note: str


class TransactionRead(BaseModel):
    id: int
    amount: float
    description: str
    transaction_date: date
    kind: TransactionKind
    category: CategoryRead
    tags: list[TransactionTagRead]
