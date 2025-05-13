from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi_auth_middleware import AuthMiddleware

from .routes import router
from .token import verify_authorization_header

app = FastAPI(title='Attendances Importer Service')
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

    uvicorn.run(app, host='0.0.0.0', port=8004)
