from fastapi import APIRouter, UploadFile
from starlette.authentication import requires
from starlette.requests import Request

from .enums import UserRole
from .errors import InvalidExtension, NoFilename
from .service import from_csv, from_excel

router = APIRouter()


@router.post('/attendances/import', tags=['attendances'])
@requires(UserRole.ATTENDANCE_OFFICER)
async def read_file(request: Request, file: UploadFile):
    if not file.filename:
        raise NoFilename

    if file.filename.endswith('.csv'):
        return await from_csv(request.user.access_token, file)

    if file.filename.endswith('.xlsx'):
        return await from_excel(request.user.access_token, file)

    raise InvalidExtension
