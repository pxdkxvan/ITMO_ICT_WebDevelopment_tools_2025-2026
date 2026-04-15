from fastapi import APIRouter, HTTPException, status
from sqlmodel import select

from app.api.deps import CurrentUserDep, SessionDep
from app.models.entities import Goal
from app.schemas.goals import GoalCreate, GoalRead, GoalUpdate

router = APIRouter(prefix="/goals", tags=["goals"])


@router.get("", response_model=list[GoalRead])
def list_goals(current_user: CurrentUserDep, session: SessionDep) -> list[Goal]:
    return session.exec(select(Goal).where(Goal.user_id == current_user.id)).all()


@router.post("", response_model=GoalRead, status_code=status.HTTP_201_CREATED)
def create_goal(payload: GoalCreate, current_user: CurrentUserDep, session: SessionDep) -> Goal:
    goal = Goal(
        title=payload.title,
        target_amount=payload.target_amount,
        current_amount=payload.current_amount,
        deadline=payload.deadline,
        user_id=current_user.id,
    )
    session.add(goal)
    session.commit()
    session.refresh(goal)
    return goal


@router.get("/{goal_id}", response_model=GoalRead)
def get_goal(goal_id: int, current_user: CurrentUserDep, session: SessionDep) -> Goal:
    goal = session.get(Goal, goal_id)
    if not goal or goal.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")
    return goal


@router.patch("/{goal_id}", response_model=GoalRead)
def update_goal(goal_id: int, payload: GoalUpdate, current_user: CurrentUserDep, session: SessionDep) -> Goal:
    goal = session.get(Goal, goal_id)
    if not goal or goal.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")

    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(goal, key, value)

    session.add(goal)
    session.commit()
    session.refresh(goal)
    return goal


@router.delete("/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_goal(goal_id: int, current_user: CurrentUserDep, session: SessionDep) -> None:
    goal = session.get(Goal, goal_id)
    if not goal or goal.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")

    session.delete(goal)
    session.commit()
