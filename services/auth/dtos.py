from uuid import UUID
from pydantic import BaseModel

from common.enums import UserRole


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenValidation(BaseModel):
    valid: bool
    user_id: UUID
    username: str
    role: UserRole
