from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import Engine, select
from sqlalchemy.orm import Session

from ._auth import authenticate_user, create_access_token, hash_password
from ._deps import get_engine
from ..model import Entity, Person, User
from ..schema import LoginRequest, RegisterRequest, TokenResponse


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
def register_user(payload: RegisterRequest, engine: Engine = Depends(get_engine)) -> TokenResponse:
    with Session(engine) as session:
        existing = session.scalars(select(User).where(User.user_name == payload.user_name)).first()
        if existing is not None:
            raise HTTPException(status_code=409, detail="Username already exists")

        if payload.first_name:
            entity = Person(name=payload.name, first_name=payload.first_name)
        else:
            entity = Entity(name=payload.name)

        user = User(
            user_name=payload.user_name,
            password_hash=hash_password(payload.password),
            entity=entity,
        )
        session.add(entity)
        session.add(user)
        session.commit()

    token = create_access_token(subject=payload.user_name)
    return TokenResponse(access_token=token)


@router.post(
    "/token",
    response_model=TokenResponse,
    summary="Log in and receive JWT token",
)
def login(payload: LoginRequest, engine: Engine = Depends(get_engine)) -> TokenResponse:
    user = authenticate_user(engine=engine, user_name=payload.user_name, password=payload.password)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    token = create_access_token(subject=user.user_name)
    return TokenResponse(access_token=token)
