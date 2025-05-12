from enum import Enum


class StrEnum(str, Enum):
    pass


class MedicalCenterType(StrEnum):
    HOSPITAL = 'hospital'
    CLINIC = 'clinic'
    DENTAL_CLINIC = 'dental_clinic'
    PHARMACY = 'pharmacy'
    URGENT_CARE = 'urgent_care'
    LABORATORY = 'laboratory'
    REHABILITATION_CENTER = 'rehabilitation_center'
    NURSING_HOME = 'nursing_home'
    MATERNITY_CENTER = 'maternity_center'
    SPECIALIZED_CENTER = 'specialized_center'


class OwnershipType(StrEnum):
    PRIVATE = 'private'
    PUBLIC = 'public'


class UserRole(StrEnum):
    ADMIN = 'admin'
    COMPANY_MANAGER = 'company_manager'
    ATTENDANCE_OFFICER = 'attendance_officer'
