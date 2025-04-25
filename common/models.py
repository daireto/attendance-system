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
    Gender,
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
    full_name: Mapped[str] = mapped_column()
    document: Mapped[str] = mapped_column(unique=True)
    document_type: Mapped[DocumentType] = mapped_column(
        Enum(DocumentType),
    )
    gender: Mapped[Gender] = mapped_column(Enum(Gender))
    birth_date: Mapped[datetime] = mapped_column()
    address: Mapped[str] = mapped_column()
    reason: Mapped[str] = mapped_column()
    additional_data: Mapped[Optional[dict[str, object]]] = mapped_column(
        JSON, nullable=True
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
    nit: Mapped[str] = mapped_column(unique=True)
    name: Mapped[str] = mapped_column(unique=True)
    phone: Mapped[str] = mapped_column(unique=True)
    center_type: Mapped[MedicalCenterType] = mapped_column(
        Enum(MedicalCenterType),
    )
    ownership_type: Mapped[OwnershipType] = mapped_column(
        Enum(OwnershipType),
    )
    addresses: Mapped[list[str]] = mapped_column(
        JSON,
    )
    additional_attendance_fields: Mapped[Optional[list[AdditionalAttendanceField]]] = (
        mapped_column(
            PydanticType(list[AdditionalAttendanceField]), nullable=True
        )
    )
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey('users.uid', ondelete='RESTRICT')
    )

    suscription: Mapped[Optional['Suscription']] = relationship(back_populates='company')
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
    name: Mapped[str] = mapped_column()
    country_code: Mapped[int] = mapped_column()
    number: Mapped[str] = mapped_column()

    company_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey('companies.uid', ondelete='RESTRICT')
    )
    user_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey('users.uid', ondelete='RESTRICT')
    )


class Suscription(BaseModel):
    __tablename__ = 'suscriptions'

    uid: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    company_id: Mapped[UUID] = mapped_column(
        ForeignKey('companies.uid', ondelete='RESTRICT')
    )
    start_date: Mapped[datetime] = mapped_column()
    end_date: Mapped[datetime] = mapped_column()
    active: Mapped[bool] = mapped_column(default=False)

    company: Mapped['Company'] = relationship(back_populates='suscription')


class User(BaseModel):
    __tablename__ = 'users'

    uid: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    username: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str] = mapped_column()
    email: Mapped[str] = mapped_column(unique=True)
    document: Mapped[str] = mapped_column(unique=True)
    document_type: Mapped[DocumentType] = mapped_column(
        Enum(DocumentType),
    )
    first_name: Mapped[str] = mapped_column()
    last_name: Mapped[str] = mapped_column()
    birth_date: Mapped[datetime] = mapped_column()
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole),
    )

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
