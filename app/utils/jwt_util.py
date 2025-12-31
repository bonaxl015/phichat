import time
import jwt
from app.core.config import settings


def create_access_token(subject: str) -> str:
    payload = {
        "sub": subject,
        "exp": int(time.time()) + (settings.access_token_expire_minutes * 60),
        "iat": int(time.time()),
    }

    return jwt.encode(payload, settings.secret_key, algorithm="HS256")


def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
