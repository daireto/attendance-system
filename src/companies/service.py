from uuid import UUID

from fastapi import HTTPException

from .dtos import CompanyCreate, CompanyUpdate
from .enums import UserRole
from .models import Company
from .token import AuthenticatedUser


async def fetch_companies(
    skip: int = 0, limit: int = 100, search: str | None = None
):
    query = Company.get_async_query()
    query.skip(skip).limit(limit if limit > 0 else 100).sort('-created_at')

    if search:
        query.search(search)

    return await query.all()


async def read_company(read_by: AuthenticatedUser, uid_or_nit: str | UUID):
    if isinstance(uid_or_nit, UUID):
        company = await Company.get(uid_or_nit)
    else:
        company = await Company.get_by_nit(uid_or_nit)

    if not company:
        return None

    if read_by.role != UserRole.ADMIN and company.uid != read_by.company_id:
        return None

    return company


async def create_new_company(
    created_by: AuthenticatedUser, data: CompanyCreate
):
    company = await Company.get_by_nit(nit=data.nit)
    if company:
        raise HTTPException(
            status_code=400, detail='Company already registered'
        )

    return await Company.create(**data.model_dump(), created_by=created_by.uid)


async def update_company(
    updated_by: AuthenticatedUser, nit: str, data: CompanyUpdate
):
    company = await read_company(updated_by, nit)
    if not company:
        return None

    return await company.update(**data.model_dump(), updated_by=updated_by.uid)
