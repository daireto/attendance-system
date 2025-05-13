from getpass import getpass

from dotenv import load_dotenv
from sqlactive import DBConnection

from users.config import Settings
from users.enums import UserRole
from users.models import BaseModel, User

load_dotenv()


async def create_admin():
    conn = DBConnection(str(Settings.DATABASE_URL), echo=False)
    BaseModel.set_session(conn.async_scoped_session)

    user = await User.create(
        username=input('Username: '),
        password=getpass('Password: '),
        email='admin@yopmail.com',
        document='1234567890',
        document_type='CC',
        first_name='Admin',
        last_name='Admin',
        role=UserRole.ADMIN,
        phone_number='1234567890',
    )
    await conn.close(BaseModel)
    print(f'Admin created with uid {user.uid}')


if __name__ == '__main__':
    import asyncio

    asyncio.run(create_admin())
