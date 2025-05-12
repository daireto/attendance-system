from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from .enums import DocumentType, UserRole


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenValidation(BaseModel):
    valid: bool
    user_id: UUID
    username: str
    role: UserRole
    company_id: UUID | None = None


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uid: UUID
    username: str
    email: str
    document: str
    document_type: DocumentType
    first_name: str
    last_name: str
    birth_date: datetime
    role: UserRole
    phone_number: str
    company_id: UUID | None = None
    created_by: UUID | None = None
    updated_by: UUID | None = None
