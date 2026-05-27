from fastapi import APIRouter, HTTPException, status
from sqlmodel import select

from app.api.deps import CurrentUserDep, SessionDep
from app.models.entities import Category
from app.schemas.categories import CategoryCreate, CategoryRead, CategoryUpdate

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=list[CategoryRead])
def list_categories(current_user: CurrentUserDep, session: SessionDep) -> list[Category]:
    return session.exec(select(Category).where(Category.user_id == current_user.id)).all()


@router.post("", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
def create_category(payload: CategoryCreate, current_user: CurrentUserDep, session: SessionDep) -> Category:
    category = Category(name=payload.name, kind=payload.kind, user_id=current_user.id)
    session.add(category)
    session.commit()
    session.refresh(category)
    return category


@router.get("/{category_id}", response_model=CategoryRead)
def get_category(category_id: int, current_user: CurrentUserDep, session: SessionDep) -> Category:
    category = session.get(Category, category_id)
    if not category or category.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return category


@router.patch("/{category_id}", response_model=CategoryRead)
def update_category(
    category_id: int, payload: CategoryUpdate, current_user: CurrentUserDep, session: SessionDep
) -> Category:
    category = session.get(Category, category_id)
    if not category or category.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(category, key, value)

    session.add(category)
    session.commit()
    session.refresh(category)
    return category


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: int, current_user: CurrentUserDep, session: SessionDep) -> None:
    category = session.get(Category, category_id)
    if not category or category.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    session.delete(category)
    session.commit()
