import json
from uuid import UUID

import httpx
from fastapi import HTTPException

from .config import Settings
from .dtos import AttendanceCreate, AttendanceCreateMultiple
from .enums import UserRole
from .errors import NoCompanyId
from .models import Attendance
from .token import AuthenticatedUser


async def fetch_user_company(access_token: str):
    async with httpx.AsyncClient() as client:
        return await client.get(
            f'{Settings.COMPANIES_URL}/companies/me',
            headers={'Authorization': 'Bearer ' + access_token},
        )


async def check_company_exists(access_token: str):
    company_response = await fetch_user_company(access_token)
    if company_response.is_error:
        try:
            detail = company_response.json()['detail']
        except (json.decoder.JSONDecodeError, KeyError):
            detail = company_response.text

        raise HTTPException(
            status_code=company_response.status_code,
            detail=detail,
        )


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

    if read_by.role != UserRole.ADMIN and attendance.company_id != read_by.company_id:
        return None

    return attendance


async def create_new_attendance(created_by: AuthenticatedUser, data: AttendanceCreate):
    if not created_by.company_id:
        raise NoCompanyId

    await check_company_exists(created_by.access_token)

    return await Attendance.create(
        **data.model_dump(),
        company_id=created_by.company_id,
        created_by=created_by.uid,
    )


async def create_multiple_attendances(
    created_by: AuthenticatedUser, data: AttendanceCreateMultiple
):
    if not created_by.company_id:
        raise NoCompanyId

    await check_company_exists(created_by.access_token)

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
