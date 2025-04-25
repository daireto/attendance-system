from fastapi import APIRouter
from starlette.authentication import requires
from starlette.requests import Request

from common.dtos import (
    CompanyCreate,
    CompanyResponse,
    CompanyUpdate,
    ResourceDelete,
)
from common.enums import UserRole
from common.errors import CompanyNotFound
from common.models import Company

from .service import create_new_company, fetch_companies, update_company

router = APIRouter()


@router.post('/companies/', response_model=CompanyResponse, tags=['companies'])
@requires(UserRole.ADMIN)
async def create_company(request: Request, data: CompanyCreate):
    company = await create_new_company(data)
    return CompanyResponse.model_validate(company)


@router.get(
    '/companies/', response_model=list[CompanyResponse], tags=['companies']
)
@requires(UserRole.ADMIN)
async def get_companies(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    search: str | None = None,
):
    companies = await fetch_companies(skip, limit, search)
    return [CompanyResponse.model_validate(company) for company in companies]


@router.get(
    '/companies/{nit}', response_model=CompanyResponse, tags=['companies']
)
@requires(UserRole.ADMIN)
async def get_company(request: Request, nit: str):
    company = await Company.get_by_nit(nit)
    if not company:
        raise CompanyNotFound()

    return CompanyResponse.model_validate(company)


@router.put(
    '/companies/{nit}', response_model=CompanyResponse, tags=['companies']
)
@requires(UserRole.ADMIN)
async def modify_company(request: Request, nit: str, data: CompanyUpdate):
    company = await update_company(nit, data)
    if not company:
        raise CompanyNotFound()

    return CompanyResponse.model_validate(company)


@router.delete(
    '/companies/{nit}', response_model=ResourceDelete, tags=['companies']
)
@requires(UserRole.ADMIN)
async def delete_company(request: Request, nit: str):
    company = await Company.get_by_nit(nit)
    if not company:
        raise CompanyNotFound()

    uid = company.uid
    await company.delete()
    return ResourceDelete(uid=uid)
