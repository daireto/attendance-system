from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .enums import DocumentType, UserRole


class ResourceDelete(BaseModel):
    uid: UUID
    deleted: bool = True


class UserBase(BaseModel):
    email: str = Field(min_length=5, max_length=70)
    document: str = Field(min_length=8, max_length=12)
    document_type: DocumentType
    first_name: str = Field(min_length=2, max_length=50)
    last_name: str = Field(min_length=2, max_length=50)
    birth_date: datetime
    role: UserRole
    phone_number: str


class UserCreate(UserBase):
    username: str = Field(min_length=5, max_length=20)
    password: str = Field(min_length=8, max_length=100)
    confirm_password: str = Field(min_length=8, max_length=100)

    @field_validator('confirm_password')
    def passwords_match(cls, v, values):
        if v != values.data['password']:
            raise ValueError('Passwords do not match')
        return v


class UserUpdate(UserBase):
    password: str | None = Field(min_length=8, max_length=100)
    confirm_password: str | None = Field(min_length=8, max_length=100)

    @field_validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v


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
