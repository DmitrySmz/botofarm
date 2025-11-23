import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr, ConfigDict


class EnvEnum(str, Enum):
    prod = "prod"
    preprod = "preprod"
    stage = "stage"


class DomainEnum(str, Enum):
    canary = "canary"
    regular = "regular"


class UserBase(BaseModel):
    login: EmailStr
    project_id: uuid.UUID
    env: EnvEnum
    domain: DomainEnum


class UserCreate(UserBase):
    password: str


class UserRead(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    locktime: Optional[datetime] = None
    is_locked: bool


class UserListFilters(BaseModel):
    project_id: Optional[uuid.UUID] = None
    env: Optional[EnvEnum] = None
    domain: Optional[DomainEnum] = None
    is_locked: Optional[bool] = None
