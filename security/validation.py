from fastapi import Depends, HTTPException, Form, status

# from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from db.crud import get_user_by_email
from db.db_helpers import db_helper_admin
from .exceptions import UnauthorizedException, RefreshRequiredException
from .helpers import (
    TOKEN_TYPE_FIELD,
    access_token_getter,
    refresh_token_getter,
    get_current_access_token_payload,
    get_current_refresh_token_payload,
)
import security.utils as auth_utils
from schemas import UserSchema

# oauth2_scheme = OAuth2PasswordBearer(
#     tokenUrl="/auth/login/",
# )


def validate_token_type(
    payload: dict,
    token_type: str,
) -> bool:
    current_token_type = payload.get(TOKEN_TYPE_FIELD)
    if current_token_type == token_type:
        return True
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=f"Неправильный тип токена {current_token_type!r}, ожидается {token_type!r}",
    )


async def validate_auth_user(
    username: str = Form(),  # actually its email in my app, but if I replace "username" with "email" - OAuth2 wouldn't work ¯\_(ツ)_/¯
    password: str = Form(),
    db_session: AsyncSession = Depends(db_helper_admin.session_dependency),
) -> UserSchema:
    unauthed_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Неправильная почта или пароль",
    )

    user = await get_user_by_email(db_session, username)
    if not user:
        raise unauthed_exc

    if not auth_utils.validate_password(
        password=password,
        hashed_password=user.password,
    ):
        raise unauthed_exc

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Пользователь деактивирован",
        )

    return UserSchema.model_validate(user)


def check_auth_user(
    access_token: str = Depends(access_token_getter),
    refresh_token: str = Depends(refresh_token_getter),
):
    try:
        refresh_token = get_current_refresh_token_payload(refresh_token)
    except Exception as e:
        raise UnauthorizedException("login required")

    try:
        access_token = get_current_access_token_payload(access_token)
    except Exception as e:
        raise RefreshRequiredException("refresh required")
