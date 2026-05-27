from pydantic import BaseModel, Field

from app.schemas.categories import CategoryRead


class BudgetCreate(BaseModel):
    category_id: int
    month: str = Field(pattern=r"^\d{4}-\d{2}$")
    limit_amount: float = Field(gt=0)


class BudgetUpdate(BaseModel):
    month: str | None = Field(default=None, pattern=r"^\d{4}-\d{2}$")
    limit_amount: float | None = Field(default=None, gt=0)


class BudgetRead(BaseModel):
    id: int
    month: str
    limit_amount: float
    category: CategoryRead
