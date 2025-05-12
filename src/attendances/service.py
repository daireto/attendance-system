from uuid import UUID

from .dtos import AttendanceCreate, AttendanceCreateMultiple
from .enums import UserRole
from .models import Attendance
from .token import AuthenticatedUser


async def fetch_attendances(
    company_id: UUID | None = None,
    skip: int = 0,
    limit: int = 100,
    search: str | None = None,
):
    query = Attendance.get_async_query()
    query.skip(skip).limit(limit if limit > 0 else 100).sort('-created_at')

    if search:
        query.search(search)

    if company_id:
        query.find(Attendance.company_id == company_id)

    return await query.all()


async def read_attendance(read_by: AuthenticatedUser, uid: UUID):
    attendance = await Attendance.get(uid)
    if not attendance:
        return None

    if (
        read_by.role != UserRole.ADMIN
        and attendance.company_id != read_by.company_id
    ):
        return None

    return attendance


async def create_new_attendance(
    created_by: AuthenticatedUser, data: AttendanceCreate
):
    return await Attendance.create(
        **data.model_dump(),
        company_id=created_by.company_id,
        created_by=created_by.uid,
    )


async def create_multiple_attendances(
    created_by: AuthenticatedUser, data: AttendanceCreateMultiple
):
    await Attendance.insert_all(
        [
            Attendance(
                **attendance.model_dump(),
                company_id=created_by.company_id,
                created_by=created_by.uid,
            )
            for attendance in data.attendances
        ]
    )
