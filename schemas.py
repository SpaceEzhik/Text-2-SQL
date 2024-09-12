from typing import Annotated
from annotated_types import MinLen, MaxLen
from pydantic import BaseModel, EmailStr, ConfigDict, field_validator
from config import settings


class ModelRequest(BaseModel):
    prompt: str


class DBRequest(BaseModel):
    sql_query: str


class UserSchema(BaseModel):
    model_config = ConfigDict(strict=True, from_attributes=True)

    email: EmailStr
    password: str
    user_group: str
    is_active: bool
    refresh_token: str | None


class CreateUser(BaseModel):
    email: EmailStr
    password: Annotated[str, MinLen(3), MaxLen(20)]
    user_group: str

    @field_validator("user_group")
    @classmethod
    def check_user_group(cls, group: str) -> str:
        allowed_user_groups = set(settings.security.user_group_rights.keys())
        if group not in allowed_user_groups:
            raise ValueError(
                f"Invalid user {group=}. Must be one of: {allowed_user_groups}"
            )
        return group


class TokenInfo(BaseModel):
    access_token: str
    refresh_token: str | None = None
    # token_type: str = "Bearer"
