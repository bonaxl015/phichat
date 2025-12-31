import uuid
from app.core.exceptions import AppException


async def to_uuid(value):
    """
    Convert incoming values to uuid.UUID
    Value can be:
    - uuid.UUID
    - string
    - any object with __str__ returning valid UUID
    """

    if isinstance(value, uuid.UUID):
        return value
    try:
        return uuid.UUID(str(value))
    except Exception:
        raise AppException(f"Invalid UUID: {value}")
