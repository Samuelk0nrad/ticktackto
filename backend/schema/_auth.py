from pydantic import BaseModel, Field


class RegisterRequest(BaseModel):
    user_name: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=6, max_length=128)
    name: str = Field(min_length=1, max_length=255)
    first_name: str | None = Field(default=None, max_length=255)


class LoginRequest(BaseModel):
    user_name: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
