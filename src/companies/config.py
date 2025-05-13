from starlette.config import Config
from starlette.datastructures import Secret

config = Config()


class Settings:
    DATABASE_URL = config(
        'COMPANIES_DATABASE_URL',
        cast=Secret,
        default='sqlite+aiosqlite:///./db/companies.sqlite3',
    )
    SECRET_KEY = config('SECRET_KEY', cast=Secret, default='your-secret-key')
    ALGORITHM = config('ALGORITHM', default='HS256')
    ACCESS_TOKEN_EXPIRE_MINUTES = config(
        'ACCESS_TOKEN_EXPIRE_MINUTES', cast=int, default=30
    )
    USERS_URL = config('USERS_URL', default='http://localhost:8001')
