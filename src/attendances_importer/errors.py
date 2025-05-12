from fastapi import HTTPException, status


class AttendanceNotFound(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Attendance was not found',
        )
