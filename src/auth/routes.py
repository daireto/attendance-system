from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from .config import Settings
from .dependencies import oauth2_scheme
from .dtos import Token, TokenValidation, UserResponse
from .models import User
from .service import authenticate_user, get_current_user
from .token import TokenPayload, create_access_token

router = APIRouter()


@router.post('/token', response_model=Token, tags=['auth'])
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    expiration = timedelta(minutes=Settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data=TokenPayload(
            sub=user.uid,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            role=user.role,
        ),
        expires_delta=expiration,
    )
    return {'access_token': access_token, 'token_type': 'bearer'}


@router.get('/validate-token', response_model=TokenValidation, tags=['auth'])
async def validate_token(token: str = Depends(oauth2_scheme)):
    user = await get_current_user(token)
    return TokenValidation(
        valid=True,
        user_id=user.uid,
        username=user.username,
        role=user.role,
        company_id=user.company_id,
    )


@router.get('/users/me', response_model=UserResponse, tags=['users'])
async def read_user_me(current_user: User = Depends(get_current_user)):
    return UserResponse.model_validate(current_user)
