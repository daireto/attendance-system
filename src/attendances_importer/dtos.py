from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from .enums import DocumentType, Gender


class AttendanceBase(BaseModel):
    full_name: str = Field(min_length=2, max_length=100)
    document: str = Field(min_length=8, max_length=12)
    document_type: DocumentType
    gender: Gender
    birth_date: datetime
    address: str = Field(min_length=2, max_length=100)
    reason: str = Field(min_length=2, max_length=100)
    additional_data: dict[str, object] | None = None
    company_id: UUID


class AttendanceCreate(AttendanceBase):
    pass


class AttendanceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uid: UUID
    full_name: str
    document: str
    document_type: DocumentType
    gender: Gender
    birth_date: datetime
    address: str
    reason: str
    additional_data: dict[str, object] | None = {}
    company_id: UUID
    user_id: UUID
