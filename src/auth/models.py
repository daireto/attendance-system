from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from argon2 import PasswordHasher
from sqlactive import ActiveRecordBaseModel
from sqlalchemy import Enum
from sqlalchemy.orm import Mapped, mapped_column

from .enums import DocumentType, UserRole


class BaseModel(ActiveRecordBaseModel):
    __abstract__ = True


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
    phone_number: Mapped[str] = mapped_column()
    company_id: Mapped[Optional[UUID]] = mapped_column(nullable=True)
    created_by: Mapped[Optional[UUID]] = mapped_column(nullable=True)
    updated_by: Mapped[Optional[UUID]] = mapped_column(nullable=True)

    def set_password(self, password: str) -> None:
        ph = PasswordHasher()
        self.password = ph.hash(password)

    def verify_password(self, password: str) -> bool:
        ph = PasswordHasher()
        return ph.verify(self.password, password)

    @classmethod
    async def get_by_username(cls, username: str) -> 'User | None':
        return await cls.find(username=username).one_or_none()
