from argon2 import PasswordHasher
from fastapi import HTTPException

from common.dtos import UserCreate, UserUpdate
from common.models import User


async def fetch_users(
    skip: int = 0, limit: int = 100, search: str | None = None
):
    query = User.get_async_query()
    query.skip(skip).limit(limit)

    if search:
        query.search(search)

    return await query.all()


async def create_new_user(data: UserCreate):
    user = await User.get_by_username(username=data.username)
    if user:
        raise HTTPException(
            status_code=400, detail='Username already registered'
        )

    ph = PasswordHasher()
    hashed_password = ph.hash(data.password)
    return await User.create(
        username=data.username,
        password=hashed_password,
        email=data.email,
        document=data.document,
        document_type=data.document_type,
        first_name=data.first_name,
        last_name=data.last_name,
        birth_date=data.birth_date,
        role=data.role,
    )


async def update_user(username: str, data: UserUpdate):
    user = await User.get_by_username(username)
    if not user:
        return None

    if data.password:
        user.set_password(data.password)

    update_data = data.model_dump()
    update_data.pop('password', None)
    update_data.pop('confirm_password', None)

    return await user.update(**update_data)
