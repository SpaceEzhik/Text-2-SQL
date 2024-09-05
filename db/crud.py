from fastapi import HTTPException, status
from sqlalchemy import text, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from db.db_helpers import db_error_handler
from db.models import User
from schemas import CreateUser
from security.utils import hash_password


async def execute_sql(
    db_session: AsyncSession, sql_query: str
) -> tuple[dict, ...] | None:
    query_type = sql_query.strip().lower().split()[0]
    if query_type == "select":
        try:
            result = await db_session.execute(text(sql_query))
            keys = tuple(result.keys())
            named_rows = tuple(dict(zip(keys, row)) for row in result.fetchall())
            return (
                named_rows
                if len(named_rows)
                else tuple([{"По вашему запросу ничего не найдено": None}])
            )
        except Exception as e:
            raise db_error_handler.handle(e)
    elif query_type in ("insert", "update", "delete"):
        try:
            await db_session.execute(text(sql_query))
            result = await db_session.execute(text("SELECT ROW_COUNT()"))
            rows_affected = result.fetchall()[0][0]
            await db_session.commit()
            return tuple([{"rows_affected": rows_affected}])
        except Exception as e:
            await db_session.rollback()
            raise db_error_handler.handle(e)
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Данный тип запросов недоступен",
        )


async def create_user(db_session: AsyncSession, user_in: CreateUser) -> User | None:
    user = User(**user_in.model_dump())
    user.password = hash_password(user.password)
    db_session.add(user)
    try:
        await db_session.commit()
    except Exception as e:
        await db_session.rollback()
        raise db_error_handler.handle(e)
    return user


async def get_user_by_email(db_session: AsyncSession, email: str) -> User | None:
    query = select(User).where(User.email == email)
    result = await db_session.execute(query)
    user = result.scalars().first()
    return user


async def update_user_refresh_token(
    db_session: AsyncSession, token: str | None, email: str
) -> None:
    query = (
        update(User)
        .where(User.email == email)
        .values(refresh_token=token)
        .execution_options(synchronize_session="fetch")
    )
    try:
        result = await db_session.execute(query)
        await db_session.commit()
    except Exception as e:
        await db_session.rollback()
        raise db_error_handler.handle(e)
