from uuid import UUID

from fastapi import APIRouter
from starlette.authentication import requires
from starlette.requests import Request

from .dtos import (
    CompanyCreate,
    CompanyResponse,
    CompanyUpdate,
    ResourceDelete,
)
from .enums import UserRole
from .errors import CompanyNotFound
from .service import (
    create_new_company,
    fetch_companies,
    read_company,
    update_company,
)

router = APIRouter()


@router.post('/companies/', response_model=CompanyResponse, tags=['companies'])
@requires(UserRole.ADMIN)
async def create_company(request: Request, data: CompanyCreate):
    company = await create_new_company(request.user, data)
    return CompanyResponse.model_validate(company)


@router.get('/companies/', response_model=list[CompanyResponse], tags=['companies'])
@requires(UserRole.ADMIN)
async def get_companies(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    search: str | None = None,
):
    companies = await fetch_companies(skip, limit, search)
    return [CompanyResponse.model_validate(company) for company in companies]


@router.get('/companies/me', response_model=CompanyResponse, tags=['companies'])
@requires(UserRole.ATTENDANCE_OFFICER)
async def get_user_company(request: Request):
    if not request.user.company_id:
        raise CompanyNotFound

    company = await read_company(request.user, request.user.company_id)
    if not company:
        raise CompanyNotFound

    return CompanyResponse.model_validate(company)


@router.get('/companies/{uid:uuid}', response_model=CompanyResponse, tags=['companies'])
@requires(UserRole.COMPANY_MANAGER)
async def get_company(request: Request, uid: UUID):
    company = await read_company(request.user, uid)
    if not company:
        raise CompanyNotFound

    return CompanyResponse.model_validate(company)


@router.get(
    '/companies/by_nit/{nit}',
    response_model=CompanyResponse,
    tags=['companies'],
)
@requires(UserRole.COMPANY_MANAGER)
async def get_company_by_nit(request: Request, nit: str):
    company = await read_company(request.user, nit)
    if not company:
        raise CompanyNotFound

    return CompanyResponse.model_validate(company)


@router.put('/companies/{nit}', response_model=CompanyResponse, tags=['companies'])
@requires(UserRole.COMPANY_MANAGER)
async def modify_company(request: Request, nit: str, data: CompanyUpdate):
    company = await update_company(request.user, nit, data)
    if not company:
        raise CompanyNotFound

    return CompanyResponse.model_validate(company)


@router.delete('/companies/{nit}', response_model=ResourceDelete, tags=['companies'])
@requires(UserRole.ADMIN)
async def delete_company(request: Request, nit: str):
    company = await read_company(request.user, nit)
    if not company:
        raise CompanyNotFound

    uid = company.uid
    await company.delete()
    return ResourceDelete(uid=uid)
