import jwt
import pydantic
from fastapi import Depends

from .config import Settings
from .dependencies import oauth2_scheme
from .errors import Unauthorized, UserNotFound
from .models import User
from .token import TokenPayload


async def authenticate_user(username: str, password: str):
    user = await User.get_by_username(username)
    if not user or not user.verify_password(password):
        return None

    return user


async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(
            token, str(Settings.SECRET_KEY), algorithms=[Settings.ALGORITHM]
        )
        token_payload = TokenPayload(**payload)
    except (jwt.PyJWTError, pydantic.ValidationError):
        raise Unauthorized()

    user = await User.get_by_username(token_payload.username)
    if user is None:
        raise UserNotFound()

    return user
