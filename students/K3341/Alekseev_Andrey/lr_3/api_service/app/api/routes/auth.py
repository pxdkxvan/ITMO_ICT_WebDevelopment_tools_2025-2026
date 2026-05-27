from fastapi import APIRouter, HTTPException, status
from sqlmodel import select

from app.api.deps import CurrentUserDep, SessionDep
from app.core.security import create_access_token, hash_password, verify_password
from app.models.entities import User
from app.schemas.auth import ChangePasswordRequest, LoginRequest, RegisterRequest, TokenResponse
from app.schemas.users import UserRead

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, session: SessionDep) -> User:
    existing_user = session.exec(select(User).where(User.email == payload.email)).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already exists")

    user = User(
        email=payload.email,
        full_name=payload.full_name,
        hashed_password=hash_password(payload.password),
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, session: SessionDep) -> TokenResponse:
    user = session.exec(select(User).where(User.email == payload.email)).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access_token = create_access_token(str(user.id))
    return TokenResponse(access_token=access_token)


@router.get("/me", response_model=UserRead)
def me(current_user: CurrentUserDep) -> User:
    return current_user


@router.patch("/me/password", status_code=status.HTTP_204_NO_CONTENT)
def change_password(payload: ChangePasswordRequest, current_user: CurrentUserDep, session: SessionDep) -> None:
    if not verify_password(payload.old_password, current_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Old password is incorrect")

    current_user.hashed_password = hash_password(payload.new_password)
    session.add(current_user)
    session.commit()
