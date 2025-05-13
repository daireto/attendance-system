from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel as PydanticBaseModel
from sqlactive import ActiveRecordBaseModel
from sqlalchemy import JSON, Enum
from sqlalchemy.orm import Mapped, mapped_column

from .custom_types import PydanticType
from .enums import MedicalCenterType, OwnershipType


class BaseModel(ActiveRecordBaseModel):
    __abstract__ = True


class AdditionalAttendanceField(PydanticBaseModel):
    name: str
    type_: str


class Company(BaseModel):
    __tablename__ = 'companies'

    uid: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    nit: Mapped[str] = mapped_column(unique=True)
    name: Mapped[str] = mapped_column()
    contact_number: Mapped[str] = mapped_column()
    center_type: Mapped[MedicalCenterType] = mapped_column(
        Enum(MedicalCenterType),
    )
    ownership_type: Mapped[OwnershipType] = mapped_column(
        Enum(OwnershipType),
    )
    addresses: Mapped[list[str]] = mapped_column(
        JSON,
    )
    additional_attendance_fields: Mapped[
        Optional[list[AdditionalAttendanceField]]
    ] = mapped_column(
        PydanticType(list[AdditionalAttendanceField]), nullable=True
    )
    created_by: Mapped[Optional[UUID]] = mapped_column(nullable=True)
    updated_by: Mapped[Optional[UUID]] = mapped_column(nullable=True)

    @classmethod
    async def get_by_nit(cls, nit: str) -> 'Company | None':
        return await cls.find(nit=nit).one_or_none()
