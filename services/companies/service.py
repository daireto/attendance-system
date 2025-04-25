from fastapi import HTTPException

from common.dtos import CompanyCreate, CompanyUpdate
from common.models import Company


async def fetch_companies(
    skip: int = 0, limit: int = 100, search: str | None = None
):
    query = Company.get_async_query()
    query.skip(skip).limit(limit if limit > 0 else 100).sort('-created_at')

    if search:
        query.search(search)

    return await query.all()


async def create_new_company(data: CompanyCreate):
    company = await Company.get_by_nit(nit=data.nit)
    if company:
        raise HTTPException(
            status_code=400, detail='Company already registered'
        )

    return await Company.create(
        nit=data.nit,
        name=data.name,
        phone=data.phone,
        center_type=data.center_type,
        ownership_type=data.ownership_type,
        addresses=data.addresses,
        additional_attendance_fields=data.additional_attendance_fields,
        user_id=data.user_id,
    )


async def update_company(nit: str, data: CompanyUpdate):
    company = await Company.get_by_nit(nit)
    if not company:
        return None
    return await company.update(**data.model_dump())
