from fastapi import APIRouter, HTTPException, status
from sqlmodel import select

from app.api.deps import CurrentUserDep, SessionDep
from app.models.entities import Tag
from app.schemas.tags import TagCreate, TagRead, TagUpdate

router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("", response_model=list[TagRead])
def list_tags(current_user: CurrentUserDep, session: SessionDep) -> list[Tag]:
    return session.exec(select(Tag).where(Tag.user_id == current_user.id)).all()


@router.post("", response_model=TagRead, status_code=status.HTTP_201_CREATED)
def create_tag(payload: TagCreate, current_user: CurrentUserDep, session: SessionDep) -> Tag:
    tag = Tag(name=payload.name, user_id=current_user.id)
    session.add(tag)
    session.commit()
    session.refresh(tag)
    return tag


@router.patch("/{tag_id}", response_model=TagRead)
def update_tag(tag_id: int, payload: TagUpdate, current_user: CurrentUserDep, session: SessionDep) -> Tag:
    tag = session.get(Tag, tag_id)
    if not tag or tag.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")

    tag.name = payload.name
    session.add(tag)
    session.commit()
    session.refresh(tag)
    return tag


@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tag(tag_id: int, current_user: CurrentUserDep, session: SessionDep) -> None:
    tag = session.get(Tag, tag_id)
    if not tag or tag.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")

    session.delete(tag)
    session.commit()
