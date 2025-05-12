from enum import Enum


class StrEnum(str, Enum):
    pass


class Gender(StrEnum):
    MALE = 'male'
    FEMALE = 'female'


class DocumentType(StrEnum):
    CC = 'CC'
    CE = 'CE'
    TI = 'TI'
    PP = 'PP'


class UserRole(StrEnum):
    ADMIN = 'admin'
    COMPANY_MANAGER = 'company_manager'
    ATTENDANCE_OFFICER = 'attendance_officer'
