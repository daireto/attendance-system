from fastapi import APIRouter
from starlette.authentication import requires
from starlette.requests import Request

from common.dtos import ResourceDelete, UserCreate, UserResponse, UserUpdate
from common.enums import UserRole
from common.errors import UserNotFound
from common.models import User

from .service import create_new_user, fetch_users, update_user

router = APIRouter()


@router.post('/users/', response_model=UserResponse, tags=['users'])
@requires(UserRole.ADMIN)
async def create_user(request: Request, data: UserCreate):
    user = await create_new_user(data)
    return UserResponse.model_validate(user)


@router.get('/users/', response_model=list[UserResponse], tags=['users'])
@requires(UserRole.ADMIN)
async def get_users(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    search: str | None = None,
):
    users = await fetch_users(skip, limit, search)
    return [UserResponse.model_validate(user) for user in users]


@router.get('/users/{username}', response_model=UserResponse, tags=['users'])
@requires(UserRole.ADMIN)
async def get_user(request: Request, username: str):
    user = await User.get_by_username(username)
    if not user:
        raise UserNotFound()

    return UserResponse.model_validate(user)


@router.put('/users/{username}', response_model=UserResponse, tags=['users'])
@requires(UserRole.ADMIN)
async def modify_user(request: Request, username: str, data: UserUpdate):
    user = await update_user(username, data)
    if not user:
        raise UserNotFound()

    return UserResponse.model_validate(user)


@router.delete(
    '/users/{username}', response_model=ResourceDelete, tags=['users']
)
@requires(UserRole.ADMIN)
async def delete_user(request: Request, username: str):
    user = await User.get_by_username(username)
    if not user:
        raise UserNotFound()

    uid = user.uid
    await user.delete()
    return ResourceDelete(uid=uid)
