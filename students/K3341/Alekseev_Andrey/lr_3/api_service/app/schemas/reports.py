from pydantic import BaseModel


class CategorySpendRead(BaseModel):
    category_id: int
    category_name: str
    spent: float


class MonthlySummaryRead(BaseModel):
    month: str
    income_total: float
    expense_total: float
    balance: float
    by_category: list[CategorySpendRead]


class BudgetWarningRead(BaseModel):
    budget_id: int
    category_id: int
    category_name: str
    month: str
    limit_amount: float
    spent: float
    exceeded_by: float
