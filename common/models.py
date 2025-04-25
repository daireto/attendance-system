from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from argon2 import PasswordHasher
from pydantic import BaseModel as PydanticBaseModel
from sqlactive import ActiveRecordBaseModel
from sqlalchemy import JSON, Enum, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .custom_types import PydanticType
from .enums import (
    DocumentType,
    MedicalCenterType,
    OwnershipType,
    UserRole,
)


class BaseModel(ActiveRecordBaseModel):
    __abstract__ = True


class AdditionalAttendanceField(PydanticBaseModel):
    name: str
    type_: str


class Attendance(BaseModel):
    __tablename__ = 'attendances'

    uid: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    full_name: Mapped[str] = mapped_column(nullable=False)
    document: Mapped[str] = mapped_column(nullable=False, unique=True)
    document_type: Mapped[DocumentType] = mapped_column(
        Enum(DocumentType), nullable=False
    )
    birth_date: Mapped[datetime] = mapped_column(nullable=False)
    address: Mapped[str] = mapped_column(nullable=False)
    reason: Mapped[str] = mapped_column(nullable=False)
    admission_date: Mapped[datetime] = mapped_column(nullable=False)
    additional_data: Mapped[dict[str, object]] = mapped_column(
        JSON, nullable=False
    )
    company_id: Mapped[UUID] = mapped_column(
        ForeignKey('companies.uid', ondelete='RESTRICT')
    )
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey('users.uid', ondelete='RESTRICT')
    )

    company: Mapped['Company'] = relationship(
        back_populates='attendances', lazy='noload'
    )
    user: Mapped['User'] = relationship(
        back_populates='attendances', lazy='noload'
    )


class Company(BaseModel):
    __tablename__ = 'companies'

    uid: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    nit: Mapped[str] = mapped_column(nullable=False, unique=True)
    name: Mapped[str] = mapped_column(nullable=False, unique=True)
    phone: Mapped[str] = mapped_column(nullable=False, unique=True)
    center_type: Mapped[MedicalCenterType] = mapped_column(
        Enum(MedicalCenterType), nullable=False
    )
    ownership_type: Mapped[OwnershipType] = mapped_column(
        Enum(OwnershipType), nullable=False
    )
    addresses: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    additional_attendance_fields: Mapped[list[AdditionalAttendanceField]] = (
        mapped_column(
            PydanticType(list[AdditionalAttendanceField]), nullable=False
        )
    )
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey('users.uid', ondelete='RESTRICT')
    )

    user: Mapped['User'] = relationship(
        back_populates='companies', lazy='noload'
    )
    contact_numbers: Mapped[list['ContactNumber']] = relationship()
    attendances: Mapped[list['Attendance']] = relationship(
        back_populates='company', lazy='noload'
    )

    @classmethod
    async def get_by_nit(cls, nit: str):
        return await cls.find(nit=nit).one_or_none()


class ContactNumber(BaseModel):
    __tablename__ = 'contact_numbers'
    __table_args__ = (
        UniqueConstraint(
            'country_code', 'number', name='_country_code_number_uc'
        ),
    )

    uid: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(nullable=False)
    country_code: Mapped[int] = mapped_column(nullable=False)
    number: Mapped[str] = mapped_column(nullable=False)

    company_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey('companies.uid', ondelete='RESTRICT')
    )
    user_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey('users.uid', ondelete='RESTRICT')
    )


class User(BaseModel):
    __tablename__ = 'users'

    uid: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    username: Mapped[str] = mapped_column(nullable=False, unique=True)
    password: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(nullable=False, unique=True)
    document: Mapped[str] = mapped_column(nullable=False, unique=True)
    document_type: Mapped[DocumentType] = mapped_column(
        Enum(DocumentType), nullable=False
    )
    first_name: Mapped[str] = mapped_column(nullable=False)
    last_name: Mapped[str] = mapped_column(nullable=False)
    birth_date: Mapped[datetime] = mapped_column(nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), nullable=False)

    contact_numbers: Mapped[list['ContactNumber']] = relationship()
    attendances: Mapped[list['Attendance']] = relationship(
        back_populates='user', lazy='noload'
    )
    companies: Mapped[list['Company']] = relationship(
        back_populates='user', lazy='noload'
    )

    def set_password(self, password: str) -> None:
        ph = PasswordHasher()
        self.password = ph.hash(password)

    def verify_password(self, password: str) -> bool:
        ph = PasswordHasher()
        return ph.verify(self.password, password)

    @classmethod
    async def get_by_username(cls, username: str):
        return await cls.find(username=username).one_or_none()
