import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_session
from app.schemas.lock import LockResponse
from app.schemas.user import UserCreate, UserListFilters, UserRead
from app.services import user_service
from app.services.exceptions import (
    UserAlreadyExists,
    UserAlreadyLocked,
    UserNotFound,
)

router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    "",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Создать нового пользователя",
)
async def create_user_endpoint(
    user_in: UserCreate,
    session: AsyncSession = Depends(get_session),
) -> UserRead:
    try:
        user = await user_service.create_user(session, user_in)
    except UserAlreadyExists as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )
    return UserRead.model_validate(user)


@router.get(
    "",
    response_model=list[UserRead],
    summary="Получить список пользователей",
)
async def list_users_endpoint(
    filters: UserListFilters = Depends(),
    session: AsyncSession = Depends(get_session),
) -> list[UserRead]:
    users = await user_service.list_users(session, filters)
    return [UserRead.model_validate(u) for u in users]


@router.post(
    "/{user_id}/lock",
    response_model=LockResponse,
    summary="Поставить блокировку на пользователя",
)
async def acquire_lock_endpoint(
    user_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
) -> LockResponse:
    try:
        user = await user_service.acquire_lock(session, user_id)
    except UserNotFound as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )
    except UserAlreadyLocked as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )

    return LockResponse(user_id=user.id, locked=True, locktime=user.locktime)


@router.post(
    "/{user_id}/unlock",
    response_model=LockResponse,
    summary="Снять блокировку с пользователя",
)
async def release_lock_endpoint(
    user_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
) -> LockResponse:
    try:
        user = await user_service.release_lock(session, user_id)
    except UserNotFound as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )

    return LockResponse(user_id=user.id, locked=False, locktime=user.locktime)
