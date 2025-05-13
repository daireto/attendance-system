import json
from uuid import UUID

import httpx
from argon2 import PasswordHasher
from fastapi import HTTPException

from .config import Settings
from .dtos import UserCreate, UserUpdate
from .enums import UserRole
from .errors import CompanyRequired, UserAlreadyExists
from .models import User
from .token import AuthenticatedUser


async def fetch_company_by_id(company_id: UUID, access_token: str):
    async with httpx.AsyncClient() as client:
        return await client.get(
            f'{Settings.COMPANIES_URL}/companies/{company_id}',
            headers={'Authorization': 'Bearer ' + access_token},
        )


async def check_company_exists(company_id: UUID, access_token: str):
    company_response = await fetch_company_by_id(company_id, access_token)
    if company_response.is_error:
        try:
            detail = company_response.json()['detail']
        except (json.decoder.JSONDecodeError, KeyError):
            detail = company_response.text

        raise HTTPException(
            status_code=company_response.status_code,
            detail=detail,
        )


async def fetch_users(
    company_id: UUID | None = None,
    skip: int = 0,
    limit: int = 100,
    search: str | None = None,
):
    query = User.get_async_query()
    query.skip(skip).limit(limit if limit > 0 else 100).sort('-created_at')

    if search:
        query.search(search)

    if company_id:
        query.find(User.company_id == company_id)

    return await query.all()


async def read_user(read_by: AuthenticatedUser, uid_or_username: str | UUID):
    if isinstance(uid_or_username, UUID):
        user = await User.get(uid_or_username)
    else:
        user = await User.get_by_username(uid_or_username)

    if not user:
        return None

    if read_by.role != UserRole.ADMIN and user.company_id != read_by.company_id:
        return None

    return user


async def create_new_user(created_by: AuthenticatedUser, data: UserCreate):
    user = await User.get_by_username(username=data.username)
    if user:
        raise UserAlreadyExists

    ph = PasswordHasher()
    data.password = ph.hash(data.password)

    create_data = data.model_dump()
    create_data.pop('confirm_password', None)

    if created_by.role != UserRole.ADMIN:
        create_data['company_id'] = created_by.company_id

    if data.role != UserRole.ADMIN:
        company_id = create_data.get('company_id')
        if not company_id:
            raise CompanyRequired

        await check_company_exists(company_id, created_by.access_token)

    return await User.create(
        **create_data,
        created_by=created_by.uid,
    )


async def update_user(updated_by: AuthenticatedUser, uid: UUID, data: UserUpdate):
    user = await read_user(updated_by, uid)
    if not user:
        return None

    if data.password:
        user.set_password(data.password)

    update_data = data.model_dump()
    update_data.pop('password', None)
    update_data.pop('confirm_password', None)

    if updated_by.role != UserRole.ADMIN:
        update_data['company_id'] = updated_by.company_id

    if data.role != UserRole.ADMIN:
        company_id = update_data.get('company_id')
        if not company_id:
            raise CompanyRequired

        await check_company_exists(company_id, updated_by.access_token)

    return await user.update(**update_data, updated_by=updated_by.uid)
