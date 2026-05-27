from fastapi import APIRouter, HTTPException, status
from sqlmodel import select

from app.api.deps import CurrentUserDep, SessionDep
from app.models.entities import Budget, Category
from app.schemas.budgets import BudgetCreate, BudgetRead, BudgetUpdate
from app.schemas.categories import CategoryRead

router = APIRouter(prefix="/budgets", tags=["budgets"])


def _budget_read(budget: Budget, category: Category) -> BudgetRead:
    return BudgetRead(
        id=budget.id,
        month=budget.month,
        limit_amount=budget.limit_amount,
        category=CategoryRead(id=category.id, name=category.name, kind=category.kind),
    )


@router.get("", response_model=list[BudgetRead])
def list_budgets(current_user: CurrentUserDep, session: SessionDep) -> list[BudgetRead]:
    budgets = session.exec(select(Budget).where(Budget.user_id == current_user.id)).all()
    result: list[BudgetRead] = []
    for budget in budgets:
        category = session.get(Category, budget.category_id)
        if category:
            result.append(_budget_read(budget, category))
    return result


@router.post("", response_model=BudgetRead, status_code=status.HTTP_201_CREATED)
def create_budget(payload: BudgetCreate, current_user: CurrentUserDep, session: SessionDep) -> BudgetRead:
    category = session.get(Category, payload.category_id)
    if not category or category.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid category")

    budget = Budget(
        user_id=current_user.id,
        category_id=payload.category_id,
        month=payload.month,
        limit_amount=payload.limit_amount,
    )
    session.add(budget)
    session.commit()
    session.refresh(budget)
    return _budget_read(budget, category)


@router.get("/{budget_id}", response_model=BudgetRead)
def get_budget(budget_id: int, current_user: CurrentUserDep, session: SessionDep) -> BudgetRead:
    budget = session.get(Budget, budget_id)
    if not budget or budget.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Budget not found")

    category = session.get(Category, budget.category_id)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    return _budget_read(budget, category)


@router.patch("/{budget_id}", response_model=BudgetRead)
def update_budget(
    budget_id: int,
    payload: BudgetUpdate,
    current_user: CurrentUserDep,
    session: SessionDep,
) -> BudgetRead:
    budget = session.get(Budget, budget_id)
    if not budget or budget.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Budget not found")

    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(budget, key, value)

    session.add(budget)
    session.commit()
    session.refresh(budget)

    category = session.get(Category, budget.category_id)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    return _budget_read(budget, category)


@router.delete("/{budget_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_budget(budget_id: int, current_user: CurrentUserDep, session: SessionDep) -> None:
    budget = session.get(Budget, budget_id)
    if not budget or budget.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Budget not found")

    session.delete(budget)
    session.commit()
