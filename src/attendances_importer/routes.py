from uuid import UUID

from fastapi import APIRouter
from starlette.authentication import requires
from starlette.requests import Request

from .dtos import AttendanceCreate, AttendanceResponse
from .enums import UserRole
from .errors import AttendanceNotFound
from .models import Attendance
from .service import create_new_attendance, fetch_attendances

router = APIRouter()


@router.post(
    '/attendances/', response_model=AttendanceResponse, tags=['attendances']
)
@requires(UserRole.ADMIN)
async def create_attendance(request: Request, data: AttendanceCreate):
    attendance = await create_new_attendance(request.user.uid, data)
    return AttendanceResponse.model_validate(attendance)


@router.get(
    '/attendances/',
    response_model=list[AttendanceResponse],
    tags=['attendances'],
)
@requires(UserRole.ADMIN)
async def get_attendances(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    search: str | None = None,
):
    attendances = await fetch_attendances(skip, limit, search)
    return [
        AttendanceResponse.model_validate(attendance)
        for attendance in attendances
    ]


@router.get(
    '/attendances/{uid:uuid}',
    response_model=AttendanceResponse,
    tags=['attendances'],
)
@requires(UserRole.ADMIN)
async def get_attendance(request: Request, uid: UUID):
    attendance = await Attendance.get(uid)
    if not attendance:
        raise AttendanceNotFound()
    return AttendanceResponse.model_validate(attendance)
