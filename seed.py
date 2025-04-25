import asyncio
import logging
import random
from collections.abc import Sequence
from datetime import datetime
from logging import getLogger

from dummy_text_generator import (
    generate_email_from_username,
    generate_username_from_fullname,
)
from faker import Faker
from sqlactive import DBConnection

from common.config import Settings
from common.enums import Gender
from common.models import (
    Attendance,
    BaseModel,
    Company,
    DocumentType,
    MedicalCenterType,
    OwnershipType,
    User,
    UserRole,
)
from common.utils import random_datetime, strip_accents

FAKER_LANG = 'es_CO'
USERS_NUMBER = 100
COMPANIES_NUMBER = 20
ATTENDANCES_NUMBER = 200


logger = getLogger(__name__)
logger.setLevel('DEBUG')
logger.addHandler(logging.StreamHandler())

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
    if len(users) >= USERS_NUMBER:
        logger.info('Users already seeded')
        return users

    def get_users(gender: Gender):
        users = []
        usernames = []
        initial_document = random.randint(1000000000, 9999999999)
        for _ in range(int(USERS_NUMBER / 2)):
            while True:
                if gender == Gender.MALE:
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
    users = get_users(Gender.MALE) + get_users(Gender.FEMALE)
    await User.insert_all(users)
    logger.info('Users seeded')
    return users


async def seed_companies(users: Sequence[User]) -> Sequence[Company]:
    companies = await Company.limit(COMPANIES_NUMBER).all()
    if companies:
        logger.info('Companies already seeded')
        return companies

    logger.debug('Seeding companies...')
    companies = []
    initial_nit = random.randint(800000000, 900000000)

    for _ in range(COMPANIES_NUMBER):
        company_name = faker.company()
        phone = f'3{random.randint(10, 99)}{random.randint(1000000, 9999999)}'
        center_type = random.choice(list(MedicalCenterType))
        ownership_type = random.choice(list(OwnershipType))

        num_addresses = random.randint(1, 3)
        addresses = [
            faker.address().replace('\n', ', ') for _ in range(num_addresses)
        ]

        user = random.choice(users)

        company = Company(
            nit=str(initial_nit),
            name=company_name,
            phone=phone,
            center_type=center_type,
            ownership_type=ownership_type,
            addresses=addresses,
            user_id=user.uid,
        )

        companies.append(company)
        initial_nit += 1

    await Company.insert_all(companies)
    logger.info('Companies seeded')
    return companies


async def seed_attendances(
    companies: Sequence[Company], users: Sequence[User]
) -> Sequence[Attendance]:
    attendances = await Attendance.limit(ATTENDANCES_NUMBER).all()
    if attendances:
        logger.info('Attendances already seeded')
        return attendances

    logger.debug('Seeding attendances...')
    attendances = []
    initial_document = random.randint(1000000000, 9999999999)

    for _ in range(ATTENDANCES_NUMBER):
        company = random.choice(companies)
        user = random.choice(users)

        gender = random.choice([Gender.MALE, Gender.FEMALE])
        if gender == Gender.MALE:
            first_name = faker.first_name_male()
            last_name = faker.last_name_male()
        else:
            first_name = faker.first_name_female()
            last_name = faker.last_name_female()

        full_name = f'{first_name} {last_name}'
        document = str(initial_document)
        document_type = random.choice(list(DocumentType))
        birth_date = random_datetime(min_year=1950, max_year=2010)

        address = random.choice(company.addresses)

        reasons = [
            'Control regular',
            'Fiebre',
            'Dolor de cabeza',
            'Dolor de estómago',
            'Reacción alérgica',
            'Lesión',
            'Vacunación',
            'Análisis de sangre',
            'Consulta',
            'Seguimiento',
            'Emergencia',
            'Renovación de receta',
        ]
        reason = random.choice(reasons)

        attendance = Attendance(
            full_name=full_name,
            document=document,
            document_type=document_type,
            gender=gender,
            birth_date=birth_date,
            address=address,
            reason=reason,
            company_id=company.uid,
            user_id=user.uid,
        )

        attendances.append(attendance)
        initial_document += 1

    await Attendance.insert_all(attendances)
    logger.info('Attendances seeded')
    return attendances


async def seed():
    logger.debug('Seeding database...')
    await create_admin()
    users = await seed_users()
    companies = await seed_companies(users)
    await seed_attendances(companies, users)
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
