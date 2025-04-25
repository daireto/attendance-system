from uuid import UUID

from common.dtos import AttendanceCreate
from common.models import Attendance


async def fetch_attendances(
    skip: int = 0, limit: int = 100, search: str | None = None
):
    query = Attendance.get_async_query()
    query.skip(skip).limit(limit if limit > 0 else 100).sort('-created_at')

    if search:
        query.search(search)

    return await query.all()


async def create_new_attendance(registered_by: UUID, data: AttendanceCreate):
    return await Attendance.create(
        full_name=data.full_name,
        document=data.document,
        document_type=data.document_type,
        gender=data.gender,
        birth_date=data.birth_date,
        address=data.address,
        reason=data.reason,
        additional_data=data.additional_data,
        company_id=data.company_id,
        user_id=registered_by,
    )
