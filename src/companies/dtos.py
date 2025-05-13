from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from .enums import MedicalCenterType, OwnershipType
from .models import AdditionalAttendanceField


class ResourceDelete(BaseModel):
    uid: UUID
    deleted: bool = True


class CompanyBase(BaseModel):
    nit: str = Field(min_length=8, max_length=12)
    name: str = Field(min_length=2, max_length=100)
    contact_number: str = Field(min_length=10, max_length=15)
    center_type: MedicalCenterType
    ownership_type: OwnershipType
    addresses: list[str] = []
    additional_attendance_fields: list[AdditionalAttendanceField] | None = None


class CompanyCreate(CompanyBase):
    pass


class CompanyUpdate(CompanyBase):
    pass


class CompanyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uid: UUID
    nit: str
    name: str
    contact_number: str
    center_type: MedicalCenterType
    ownership_type: OwnershipType
    addresses: list[str] = []
    additional_attendance_fields: list[AdditionalAttendanceField] | None = None
    created_by: UUID | None = None
    updated_by: UUID | None = None
