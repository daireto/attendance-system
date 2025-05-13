from uuid import UUID

from fastapi import APIRouter
from starlette.authentication import requires
from starlette.requests import Request

from .dtos import ResourceDelete, UserCreate, UserResponse, UserUpdate
from .enums import UserRole
from .errors import Forbidden, NoCompanyId, UserNotFound
from .service import create_new_user, fetch_users, read_user, update_user

router = APIRouter()


def check_company_id(request: Request):
    if request.user.role == UserRole.ADMIN:
        return
    if not request.user.company_id:
        raise NoCompanyId


@router.post('/users/', response_model=UserResponse, tags=['users'])
@requires(UserRole.COMPANY_MANAGER)
async def create_user(request: Request, data: UserCreate):
    check_company_id(request)
    if request.user.role != UserRole.ADMIN and data.role in (
        UserRole.ADMIN,
        UserRole.COMPANY_MANAGER,
    ):
        raise Forbidden

    user = await create_new_user(request.user, data)
    return UserResponse.model_validate(user)


@router.get('/users/', response_model=list[UserResponse], tags=['users'])
@requires(UserRole.COMPANY_MANAGER)
async def get_users(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    search: str | None = None,
):
    check_company_id(request)
    users = await fetch_users(request.user.company_id, skip, limit, search)
    return [UserResponse.model_validate(user) for user in users]


@router.get('/users/{uid:uuid}', response_model=UserResponse, tags=['users'])
@requires(UserRole.COMPANY_MANAGER)
async def get_user(request: Request, uid: UUID):
    check_company_id(request)
    user = await read_user(request.user, uid)
    if not user:
        raise UserNotFound

    return UserResponse.model_validate(user)


@router.get(
    '/users/by_username/{username}',
    response_model=UserResponse,
    tags=['users'],
)
@requires(UserRole.COMPANY_MANAGER)
async def get_user_by_username(request: Request, username: str):
    check_company_id(request)
    user = await read_user(request.user, username)
    if not user:
        raise UserNotFound

    return UserResponse.model_validate(user)


@router.put('/users/{uid:uuid}', response_model=UserResponse, tags=['users'])
@requires(UserRole.COMPANY_MANAGER)
async def modify_user(request: Request, uid: UUID, data: UserUpdate):
    check_company_id(request)
    user = await update_user(request.user, uid, data)
    if not user:
        raise UserNotFound

    return UserResponse.model_validate(user)


@router.delete(
    '/users/{uid:uuid}', response_model=ResourceDelete, tags=['users']
)
@requires(UserRole.COMPANY_MANAGER)
async def delete_user(request: Request, uid: UUID):
    check_company_id(request)
    user = await read_user(request.user, uid)
    if not user:
        raise UserNotFound

    uid = user.uid
    await user.delete()
    return ResourceDelete(uid=uid)
