from fastapi import HTTPException, status


class InvalidExtension(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Invalid file extension',
        )


class NoFilename(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='No filename provided',
        )


class NoActiveSheet(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='No active sheet',
        )


class RowValidationError(HTTPException):
    def __init__(self, row: int, detail: str) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Row validation error: {row} - {detail}',
        )
