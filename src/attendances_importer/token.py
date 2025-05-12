import json
from datetime import datetime, timedelta, timezone
from uuid import UUID

import jwt
from fastapi.security.utils import get_authorization_scheme_param
from pydantic import BaseModel
from starlette.authentication import BaseUser, SimpleUser, UnauthenticatedUser
from starlette.datastructures import Headers

from .config import Settings
from .enums import UserRole


class TokenPayload(BaseModel):
    sub: UUID
    username: str
    first_name: str
    last_name: str
    role: UserRole
    company_id: UUID | None = None


class AuthenticatedUser(SimpleUser):
    def __init__(self, token_payload: TokenPayload) -> None:
        self.uid = token_payload.sub
        self.username = token_payload.username
        self.first_name = token_payload.first_name
        self.last_name = token_payload.last_name
        self.role = token_payload.role
        self.company_id = token_payload.company_id

    @property
    def display_name(self) -> str:
        return f'{self.first_name.strip()} {self.last_name.strip()}'.strip()


class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            return str(obj)
        return super().default(obj)


def create_access_token(
    data: TokenPayload, expires_delta: timedelta | None = None
):
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=15)
    )
    payload = {**data.model_dump(), 'exp': expire}
    return jwt.encode(
        payload, str(Settings.SECRET_KEY), algorithm=Settings.ALGORITHM, json_encoder=JSONEncoder
    )


def decode_access_token(token: str) -> TokenPayload:
    payload = jwt.decode(
        token, str(Settings.SECRET_KEY), algorithms=[Settings.ALGORITHM]
    )
    return TokenPayload.model_validate(payload)


def verify_authorization_header(
    headers: Headers,
) -> tuple[list[UserRole], BaseUser]:
    authorization = headers.get('Authorization')
    scheme, param = get_authorization_scheme_param(authorization)
    if not scheme or not param:
        return [], UnauthenticatedUser()

    payload = decode_access_token(param)
    scopes = [payload.role]
    return scopes, AuthenticatedUser(payload)
