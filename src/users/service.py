from uuid import UUID

from argon2 import PasswordHasher
from fastapi import HTTPException

from .dtos import UserCreate, UserUpdate
from .enums import UserRole
from .models import User
from .token import AuthenticatedUser


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

    if (
        read_by.role != UserRole.ADMIN
        and user.company_id != read_by.company_id
    ):
        return None

    return user


async def create_new_user(created_by: AuthenticatedUser, data: UserCreate):
    user = await User.get_by_username(username=data.username)
    if user:
        raise HTTPException(
            status_code=400, detail='Username already registered'
        )

    ph = PasswordHasher()
    data.password = ph.hash(data.password)

    create_data = data.model_dump()
    create_data.pop('confirm_password', None)

    return await User.create(
        **create_data,
        company_id=created_by.company_id,
        created_by=created_by.uid,
    )


async def update_user(
    updated_by: AuthenticatedUser, uid: UUID, data: UserUpdate
):
    user = await read_user(updated_by, uid)
    if not user:
        return None

    if data.password:
        user.set_password(data.password)

    update_data = data.model_dump()
    update_data.pop('password', None)
    update_data.pop('confirm_password', None)

    return await user.update(**update_data, updated_by=updated_by.uid)
