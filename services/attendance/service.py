from common.dtos import AttendanceCreate
from common.models import Attendance


async def fetch_attendances(
    skip: int = 0, limit: int = 100, search: str | None = None
):
    query = Attendance.get_async_query()
    query.skip(skip).limit(limit)

    if search:
        query.search(search)

    return await query.all()


async def create_new_attendance(data: AttendanceCreate):
    return await Attendance.create(
        full_name=data.full_name,
        document=data.document,
        document_type=data.document_type,
        birth_date=data.birth_date,
        address=data.address,
        reason=data.reason,
        admission_date=data.admission_date,
        additional_data=data.additional_data,
        company_id=data.company_id,
        user_id=data.user_id,
    )
