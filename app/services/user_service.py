import uuid
from datetime import datetime, timedelta, timezone
from typing import Iterable, List, Optional

from sqlalchemy import Select, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import settings
from app.db.models.user import User
from app.schemas.user import UserCreate, UserListFilters
from app.services.exceptions import (
    UserAlreadyExists,
    UserAlreadyLocked,
    UserNotFound,
)
from app.utils.security import hash_password


async def create_user(
    session: AsyncSession,
    user_in: UserCreate,
) -> User:
    # Проверяем уникальность логина
    stmt: Select = select(User).where(User.login == user_in.login)
    result = await session.execute(stmt)
    existing = result.scalar_one_or_none()
    if existing is not None:
        raise UserAlreadyExists("User with this login already exists")

    user = User(
        login=user_in.login,
        password_hash=hash_password(user_in.password),
        project_id=user_in.project_id,
        env=user_in.env.value,
        domain=user_in.domain.value,
    )

    session.add(user)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        # На случай гонки по уникальному индексу
        raise UserAlreadyExists("User with this login already exists")

    await session.refresh(user)
    return user


async def list_users(
    session: AsyncSession,
    filters: UserListFilters,
) -> List[User]:
    stmt: Select = select(User)

    if filters.project_id is not None:
        stmt = stmt.where(User.project_id == filters.project_id)

    if filters.env is not None:
        stmt = stmt.where(User.env == filters.env.value)

    if filters.domain is not None:
        stmt = stmt.where(User.domain == filters.domain.value)

    if filters.is_locked is not None:
        if filters.is_locked:
            stmt = stmt.where(User.locktime.is_not(None))
        else:
            stmt = stmt.where(User.locktime.is_(None))

    result = await session.execute(stmt)
    users: Iterable[User] = result.scalars().all()
    return list(users)


async def acquire_lock(
    session: AsyncSession,
    user_id: uuid.UUID,
    now: Optional[datetime] = None,
) -> User:
    if now is None:
        now = datetime.now(timezone.utc)

    stmt: Select = select(User).where(User.id == user_id)
    result = await session.execute(stmt)
    user: Optional[User] = result.scalar_one_or_none()

    if user is None:
        raise UserNotFound("User not found")

    # Если уже есть locktime — проверяем TTL, если он включен
    if user.locktime is not None:
        ttl = settings.lock_ttl_seconds
        if ttl is None:
            raise UserAlreadyLocked("User is already locked")

        if now - user.locktime <= timedelta(seconds=ttl):
            # Блокировка ещё активна
            raise UserAlreadyLocked("User is already locked")

    user.locktime = now
    await session.commit()
    await session.refresh(user)
    return user


async def release_lock(
    session: AsyncSession,
    user_id: uuid.UUID,
) -> User:
    stmt: Select = select(User).where(User.id == user_id)
    result = await session.execute(stmt)
    user: Optional[User] = result.scalar_one_or_none()

    if user is None:
        raise UserNotFound("User not found")

    user.locktime = None
    await session.commit()
    await session.refresh(user)
    return user
