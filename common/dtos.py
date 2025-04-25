from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from common.models import AdditionalAttendanceField

from .enums import DocumentType, MedicalCenterType, OwnershipType, UserRole


class ResourceDelete(BaseModel):
    uid: UUID
    deleted: bool = True


class AttendanceBase(BaseModel):
    full_name: str = Field(min_length=2, max_length=100)
    document: str = Field(min_length=8, max_length=12)
    document_type: DocumentType
    birth_date: datetime
    address: str = Field(min_length=2, max_length=100)
    reason: str = Field(min_length=2, max_length=100)
    admission_date: datetime
    additional_data: dict[str, object] = {}
    company_id: UUID
    user_id: UUID


class AttendanceCreate(AttendanceBase):
    pass


class AttendanceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uid: UUID
    full_name: str
    document: str
    document_type: DocumentType
    birth_date: datetime
    address: str
    reason: str
    admission_date: datetime
    additional_data: dict[str, object] = {}
    company_id: UUID
    user_id: UUID


class CompanyBase(BaseModel):
    nit: str = Field(min_length=8, max_length=12)
    name: str = Field(min_length=2, max_length=100)
    phone: str = Field(min_length=10, max_length=10)
    center_type: MedicalCenterType
    ownership_type: OwnershipType
    addresses: list[str] = []
    additional_attendance_fields: list[AdditionalAttendanceField] = []
    user_id: UUID


class CompanyCreate(CompanyBase):
    pass


class CompanyUpdate(CompanyBase):
    pass


class CompanyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uid: UUID
    nit: str
    name: str
    phone: str
    center_type: MedicalCenterType
    ownership_type: OwnershipType
    additional_attendance_fields: list[AdditionalAttendanceField] = []
    user_id: UUID


class UserBase(BaseModel):
    email: str = Field(min_length=5, max_length=70)
    document: str = Field(min_length=8, max_length=12)
    document_type: DocumentType
    first_name: str = Field(min_length=2, max_length=50)
    last_name: str = Field(min_length=2, max_length=50)
    birth_date: datetime
    role: UserRole


class UserCreate(UserBase):
    username: str = Field(min_length=5, max_length=20)
    password: str = Field(min_length=8, max_length=100)
    confirm_password: str = Field(min_length=8, max_length=100)

    @field_validator('confirm_password')
    def passwords_match(cls, v, values):
        if v != values['password']:
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
