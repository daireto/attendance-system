from datetime import datetime

from pydantic import BaseModel, Field

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


class AttendanceCreate(AttendanceBase):
    pass


class AttendanceCreateMultiple(BaseModel):
    attendances: list[AttendanceCreate]


class AttendanceImportResponse(BaseModel):
    attendances: list[AttendanceCreate]
    insertion_response: dict[str, object]
    file_extension: str
