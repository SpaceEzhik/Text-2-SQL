from fastapi import HTTPException, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.exc import SQLAlchemyError, ProgrammingError

DATABASE_URL = "[ДАННЫЕ УДАЛЕНЫ]"
engine = create_async_engine(DATABASE_URL)

async_session = async_sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)


async def get_db_session() -> AsyncSession:
    async with async_session() as session:
        yield session


async def execute_sql(db_session: AsyncSession, sql_query: str) -> tuple[dict, ...] | None:
    query_type = sql_query.strip().lower().split()[0]
    if query_type == 'select':
        try:
            result = await db_session.execute(text(sql_query))
            keys = tuple(result.keys())
            named_rows = tuple(dict(zip(keys, row)) for row in result.fetchall())
            return named_rows if len(named_rows) else tuple([{"По вашему запросу ничего не найдено": None}])
        except Exception as e:
            raise db_error_handler(e)
    elif query_type in ('insert', 'update', 'delete'):
        try:
            await db_session.execute(text(sql_query))
            result = await db_session.execute(text("SELECT ROW_COUNT()"))
            rows_affected = result.fetchall()[0][0]
            await db_session.commit()
            return tuple([{"rows_affected": rows_affected}])
        except Exception as e:
            await db_session.rollback()
            raise db_error_handler(e)
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Данный тип запросов недоступен")


def db_error_handler(e: Exception) -> HTTPException:
    error_detail = "¯\\_(ツ)_/¯"
    if hasattr(e, "orig"):
        mysql_error_code = e.orig.args[0]
        mysql_error_description = e.orig.args[1]
        if mysql_error_code == 1064:
            error_detail = f"Ошибка в синтаксисе SQL запроса.\nПодробности: {mysql_error_description}"
        elif mysql_error_code == 1054:
            error_detail = f"Ошибка в названии столбца.\nПодробности: {mysql_error_description}"
        elif mysql_error_code == 1146:
            error_detail = f"Ошибка в названии таблицы.\nПодробности: {mysql_error_description}"
        else:
            error_detail = f"Неизвестная SQL ошибка\nПодробности: {mysql_error_description}"
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_detail)
