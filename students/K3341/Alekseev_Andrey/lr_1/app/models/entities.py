from datetime import date, datetime
from enum import Enum
from typing import Optional

from sqlalchemy import Column, DateTime, UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel


class TransactionKind(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"


class GoalStatus(str, Enum):
    ACTIVE = "active"
    DONE = "done"
    CANCELED = "canceled"


class UserBase(SQLModel):
    email: str = Field(index=True, unique=True)
    full_name: str
    is_active: bool = True


class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    hashed_password: str
    created_at: datetime = Field(
        default_factory=datetime.utcnow, sa_column=Column(DateTime(timezone=False), nullable=False)
    )

    categories: list["Category"] = Relationship(back_populates="user")
    transactions: list["Transaction"] = Relationship(back_populates="user")
    budgets: list["Budget"] = Relationship(back_populates="user")
    goals: list["Goal"] = Relationship(back_populates="user")
    tags: list["Tag"] = Relationship(back_populates="user")


class CategoryBase(SQLModel):
    name: str
    kind: str


class Category(CategoryBase, table=True):
    __table_args__ = (UniqueConstraint("user_id", "name", "kind", name="uq_user_category"),)

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)

    user: User = Relationship(back_populates="categories")
    transactions: list["Transaction"] = Relationship(back_populates="category")
    budgets: list["Budget"] = Relationship(back_populates="category")


class TransactionBase(SQLModel):
    amount: float = Field(gt=0)
    description: str = ""
    transaction_date: date = Field(default_factory=date.today)


class TransactionTagLink(SQLModel, table=True):
    transaction_id: int | None = Field(default=None, foreign_key="transaction.id", primary_key=True)
    tag_id: int | None = Field(default=None, foreign_key="tag.id", primary_key=True)
    importance: int = Field(default=1, ge=1, le=10)
    note: str = ""


class Transaction(TransactionBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    kind: str
    user_id: int = Field(foreign_key="user.id", index=True)
    category_id: int = Field(foreign_key="category.id", index=True)

    user: User = Relationship(back_populates="transactions")
    category: Category = Relationship(back_populates="transactions")
    tags: list["Tag"] = Relationship(back_populates="transactions", link_model=TransactionTagLink)


class TagBase(SQLModel):
    name: str


class Tag(TagBase, table=True):
    __table_args__ = (UniqueConstraint("user_id", "name", name="uq_user_tag"),)

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)

    user: User = Relationship(back_populates="tags")
    transactions: list[Transaction] = Relationship(back_populates="tags", link_model=TransactionTagLink)


class BudgetBase(SQLModel):
    month: str = Field(description="Format: YYYY-MM")
    limit_amount: float = Field(gt=0)


class Budget(BudgetBase, table=True):
    __table_args__ = (UniqueConstraint("user_id", "category_id", "month", name="uq_budget_month"),)

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    category_id: int = Field(foreign_key="category.id", index=True)

    user: User = Relationship(back_populates="budgets")
    category: Category = Relationship(back_populates="budgets")


class GoalBase(SQLModel):
    title: str
    target_amount: float = Field(gt=0)
    current_amount: float = Field(default=0, ge=0)
    deadline: date | None = None


class Goal(GoalBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    status: str = Field(default=GoalStatus.ACTIVE.value)
    user_id: int = Field(foreign_key="user.id", index=True)

    user: User = Relationship(back_populates="goals")
