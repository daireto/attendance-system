from uuid import UUID

from fastapi import APIRouter
from starlette.authentication import requires
from starlette.requests import Request
from starlette.responses import JSONResponse

from .dtos import (
    AttendanceCreate,
    AttendanceCreateMultiple,
    AttendanceResponse,
)
from .enums import UserRole
from .errors import AttendanceNotFound, NoCompanyId
from .service import (
    create_multiple_attendances,
    create_new_attendance,
    fetch_attendances,
    read_attendance,
)

router = APIRouter()


def check_company_id(request: Request):
    if request.user.role == UserRole.ADMIN:
        return
    if not request.user.company_id:
        raise NoCompanyId()


@router.post(
    '/attendances/', response_model=AttendanceResponse, tags=['attendances']
)
@requires(UserRole.ATTENDANCE_OFFICER)
async def create_attendance(request: Request, data: AttendanceCreate):
    check_company_id(request)
    attendance = await create_new_attendance(request.user, data)
    return AttendanceResponse.model_validate(attendance)


@router.get(
    '/attendances/',
    response_model=list[AttendanceResponse],
    tags=['attendances'],
)
@requires(UserRole.ATTENDANCE_OFFICER)
async def get_attendances(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    search: str | None = None,
):
    check_company_id(request)
    attendances = await fetch_attendances(
        request.user.company_id, skip, limit, search
    )
    return [
        AttendanceResponse.model_validate(attendance)
        for attendance in attendances
    ]


@router.get(
    '/attendances/{uid:uuid}',
    response_model=AttendanceResponse,
    tags=['attendances'],
)
@requires(UserRole.ATTENDANCE_OFFICER)
async def get_attendance(request: Request, uid: UUID):
    check_company_id(request)
    attendance = await read_attendance(request.user, uid)
    if not attendance:
        raise AttendanceNotFound()

    return AttendanceResponse.model_validate(attendance)


@router.post(
    '/attendances/multiple',
    response_model=AttendanceResponse,
    tags=['attendances'],
)
@requires(UserRole.ATTENDANCE_OFFICER)
async def create_multiple(request: Request, data: AttendanceCreateMultiple):
    check_company_id(request)
    await create_multiple_attendances(request.user, data)
    return JSONResponse({'message': 'Asistencias importadas correctamente'})
