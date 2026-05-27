from datetime import date

from fastapi import APIRouter
from sqlmodel import select

from app.api.deps import CurrentUserDep, SessionDep
from app.models.entities import Budget, Category, Transaction, TransactionKind
from app.schemas.reports import BudgetWarningRead, CategorySpendRead, MonthlySummaryRead

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/summary", response_model=MonthlySummaryRead)
def monthly_summary(month: str, current_user: CurrentUserDep, session: SessionDep) -> MonthlySummaryRead:
    txs = session.exec(
        select(Transaction).where(
            Transaction.user_id == current_user.id,
            Transaction.transaction_date >= _month_start(month),
            Transaction.transaction_date < _next_month(month),
        )
    ).all()

    income_total = sum(tx.amount for tx in txs if tx.kind == TransactionKind.INCOME)
    expense_total = sum(tx.amount for tx in txs if tx.kind == TransactionKind.EXPENSE)

    by_category_map: dict[int, float] = {}
    for tx in txs:
        if tx.kind == TransactionKind.EXPENSE:
            by_category_map[tx.category_id] = by_category_map.get(tx.category_id, 0) + tx.amount

    by_category: list[CategorySpendRead] = []
    for category_id, spent in by_category_map.items():
        category = session.get(Category, category_id)
        if category:
            by_category.append(
                CategorySpendRead(category_id=category_id, category_name=category.name, spent=spent)
            )

    return MonthlySummaryRead(
        month=month,
        income_total=income_total,
        expense_total=expense_total,
        balance=income_total - expense_total,
        by_category=by_category,
    )


@router.get("/budget-warnings", response_model=list[BudgetWarningRead])
def budget_warnings(month: str, current_user: CurrentUserDep, session: SessionDep) -> list[BudgetWarningRead]:
    budgets = session.exec(
        select(Budget).where(Budget.user_id == current_user.id, Budget.month == month)
    ).all()

    warnings: list[BudgetWarningRead] = []
    for budget in budgets:
        spent = sum(
            tx.amount
            for tx in session.exec(
                select(Transaction).where(
                    Transaction.user_id == current_user.id,
                    Transaction.category_id == budget.category_id,
                    Transaction.kind == TransactionKind.EXPENSE,
                    Transaction.transaction_date >= _month_start(month),
                    Transaction.transaction_date < _next_month(month),
                )
            ).all()
        )

        if spent > budget.limit_amount:
            category = session.get(Category, budget.category_id)
            category_name = category.name if category else "unknown"
            warnings.append(
                BudgetWarningRead(
                    budget_id=budget.id,
                    category_id=budget.category_id,
                    category_name=category_name,
                    month=month,
                    limit_amount=budget.limit_amount,
                    spent=spent,
                    exceeded_by=spent - budget.limit_amount,
                )
            )

    return warnings


def _month_start(month: str) -> date:
    year, month_num = month.split("-")
    return date(int(year), int(month_num), 1)


def _next_month(month: str) -> date:
    year, month_num = month.split("-")
    y = int(year)
    m = int(month_num)
    if m == 12:
        return date(y + 1, 1, 1)
    return date(y, m + 1, 1)
