from enum import Enum
from typing import Optional

from pydantic import BaseModel


class FinanceKind(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"


class Category(BaseModel):
    id: int
    name: str


class Tag(BaseModel):
    id: int
    name: str


class Transaction(BaseModel):
    id: int
    kind: FinanceKind
    amount: float
    category: Category
    tags: Optional[list[Tag]] = []
