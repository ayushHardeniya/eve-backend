from datetime import datetime, timedelta, timezone

from argon2 import PasswordHasher
from jose import JWTError, jwt

SECRET_KEY = "change-this-secret"
ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = 60

password_hasher = PasswordHasher()


def hash_password(password: str) -> str:
    return password_hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    try:
        password_hasher.verify(password_hash, password)
        return True
    except Exception:
        return False


def create_token(user_id: int) -> str:
    expires = datetime.now(timezone.utc) + timedelta(
        minutes=TOKEN_EXPIRE_MINUTES
    )
    data = {"sub": str(user_id), "exp": expires}

    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)


def get_user_id(token: str) -> int:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")

        if user_id is None:
            raise ValueError

        return int(user_id)
    except (JWTError, ValueError):
        raise ValueError("Invalid token")
        