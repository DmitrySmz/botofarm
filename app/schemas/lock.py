import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class LockResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: uuid.UUID
    locked: bool
    locktime: Optional[datetime]
