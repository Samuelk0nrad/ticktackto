from datetime import UTC, datetime, timedelta
import os

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import Engine, select
from sqlalchemy.orm import Session

from ..model import User


SECRET_KEY = os.getenv("TICTACTOE_SECRET_KEY", "test_key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(subject: str, expires_delta: timedelta | None = None) -> str:
    expire = datetime.now(UTC) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def authenticate_user(engine: Engine, user_name: str, password: str) -> User | None:
    with Session(engine) as session:
        stmt = select(User).where(User.user_name == user_name)
        user = session.scalars(stmt).first()
        if user is None or user.password_hash is None:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user


def get_current_user(token: str = Depends(oauth2_scheme), engine: Engine | None = None) -> User:
    if engine is None:
        raise RuntimeError("Database engine is required")

    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError as exc:
        raise unauthorized from exc

    user_name = payload.get("sub")
    if not isinstance(user_name, str):
        raise unauthorized

    with Session(engine) as session:
        stmt = select(User).where(User.user_name == user_name)
        user = session.scalars(stmt).first()
        if user is None:
            raise unauthorized
        return user
