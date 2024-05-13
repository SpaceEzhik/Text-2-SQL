from fastapi import HTTPException, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from db.db_helpers import db_error_handler


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
