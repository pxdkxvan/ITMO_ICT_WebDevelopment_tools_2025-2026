from fastapi import APIRouter
from sqlmodel import select

from app.api.deps import CurrentUserDep, SessionDep
from app.models.entities import User
from app.schemas.users import UserPublicRead

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=list[UserPublicRead])
def users_list(_: CurrentUserDep, session: SessionDep) -> list[User]:
    return session.exec(select(User)).all()
