from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi_auth_middleware import AuthMiddleware
from sqlactive import DBConnection

from .config import Settings
from .models import BaseModel
from .routes import router
from .token import verify_authorization_header

conn = DBConnection(str(Settings.DATABASE_URL), echo=False)


@asynccontextmanager
async def lifespan(_: FastAPI):
    await conn.init_db(BaseModel)
    yield
    await conn.close(BaseModel)


app = FastAPI(title='Attendances Service', lifespan=lifespan)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=['*'])
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*'],
)
app.add_middleware(AuthMiddleware, verify_header=verify_authorization_header)  # type: ignore
app.include_router(router)

if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host='0.0.0.0', port=8003)
