import asyncio
import random
from collections.abc import Sequence
from datetime import datetime
from logging import getLogger
from typing import Literal

from dummy_text_generator import (
    generate_email_from_username,
    generate_username_from_fullname,
)
from faker import Faker
from sqlactive import DBConnection

from common.config import Settings
from common.models import BaseModel, DocumentType, User, UserRole
from common.utils import random_datetime, strip_accents

FAKER_LANG = 'es_CO'
USERS_NUMBER = 100


logger = getLogger(__name__)
conn = DBConnection(str(Settings.DATABASE_URL), echo=False)
faker = Faker(FAKER_LANG)


async def connect():
    logger.info('Connecting to database and initializing models...')
    await conn.init_db(BaseModel)
    logger.info('Database connected and models initialized')


async def disconnect():
    logger.info('Disconnecting from database...')
    await conn.close(BaseModel)
    logger.info('Database disconnected')


async def create_admin():
    username = 'admin'
    admin = await User.find(username=username).first()
    if admin:
        logger.info('Admin already exists')
        return admin

    logger.info('Creating admin...')
    admin = User(
        username=username,
        email='admin@yopmail.com',
        document='1234567890',
        document_type=DocumentType.CC,
        first_name='Admin',
        last_name='User',
        birth_date=datetime(2002, 12, 4),
        role=UserRole.ADMIN,
    )
    admin.set_password(username)
    await admin.save()
    logger.info('Admin created')
    return admin


async def seed_users() -> Sequence[User]:
    users = await User.limit(USERS_NUMBER).all()
    if users:
        logger.info('Users already seeded')
        return users

    def get_users(gender: Literal['male', 'female']):
        users = []
        usernames = []
        initial_document = random.randint(1000000000, 9999999999)
        for _ in range(int(USERS_NUMBER / 2)):
            while True:
                if gender == 'male':
                    first_name = faker.first_name_male()
                    last_name = faker.last_name_male()
                else:
                    first_name = faker.first_name_female()
                    last_name = faker.last_name_female()

                username = generate_username_from_fullname(
                    f'{first_name} {last_name}'
                )
                username = strip_accents(username)
                if username not in usernames:
                    usernames.append(username)
                    break

            user = User(
                username=username,
                email=generate_email_from_username(username),
                document=str(initial_document),
                document_type=random.choice(list(DocumentType)),
                first_name=first_name,
                last_name=last_name,
                birth_date=random_datetime(min_year=1980, max_year=2004),
                role=UserRole.ATTENDANCE_OFFICER,
            )
            user.set_password(username)
            users.append(user)
            initial_document += 1

        return users

    logger.debug('Seeding users...')
    users = get_users('male') + get_users('female')
    await User.insert_all(users)
    logger.info('Users seeded')
    return users


async def seed():
    logger.debug('Seeding database...')
    await create_admin()
    users = await seed_users()
    logger.info('Database seeded')


async def main():
    try:
        await connect()
        await seed()
        await disconnect()
    except Exception as e:
        logger.critical(e)


if __name__ == '__main__':
    asyncio.run(main())
