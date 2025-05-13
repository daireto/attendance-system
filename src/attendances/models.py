from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlactive import ActiveRecordBaseModel
from sqlalchemy import JSON, Enum
from sqlalchemy.orm import Mapped, mapped_column

from .enums import DocumentType, Gender


class BaseModel(ActiveRecordBaseModel):
    __abstract__ = True


class Attendance(BaseModel):
    __tablename__ = 'attendances'

    uid: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    full_name: Mapped[str] = mapped_column()
    document: Mapped[str] = mapped_column()
    document_type: Mapped[DocumentType] = mapped_column(
        Enum(DocumentType, name='document_type'),
    )
    gender: Mapped[Gender] = mapped_column(Enum(Gender, name='gender'))
    birth_date: Mapped[datetime] = mapped_column()
    address: Mapped[str] = mapped_column()
    reason: Mapped[str] = mapped_column()
    additional_data: Mapped[Optional[dict[str, object]]] = mapped_column(
        JSON, nullable=True
    )
    company_id: Mapped[UUID] = mapped_column()
    created_by: Mapped[UUID] = mapped_column()
