from fastapi import HTTPException
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)
from fastapi import status


class DatabaseHelper:
    def __init__(self, url: str, echo: bool = False):
        self.engine = create_async_engine(
            url=url,
            echo=echo,
        )
        self.session_factory = async_sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=True,
            class_=AsyncSession,
        )

    async def session_dependency(self) -> AsyncSession:
        async with self.session_factory() as session:
            yield session
            await session.close()


class DatabaseErrorHandler:
    def __init__(self, default_error_detail: str):
        self.default_error_detail = default_error_detail

    def handle(self, e: Exception) -> HTTPException:
        error_detail = self.default_error_detail
        if hasattr(e, "orig"):
            mysql_error_code = e.orig.args[0]
            mysql_error_description = e.orig.args[1]
            if mysql_error_code == 1064:
                error_detail = f"Ошибка в синтаксисе SQL запроса.\nПодробности: {mysql_error_description}"
            elif mysql_error_code == 1054:
                error_detail = f"Ошибка в названии столбца.\nПодробности: {mysql_error_description}"
            elif mysql_error_code == 1146:
                error_detail = f"Ошибка в названии таблицы.\nПодробности: {mysql_error_description}"
            elif mysql_error_code == 1142:
                error_detail = f"У Вас нет прав на выполнение данного запроса или указанной таблицы не существует"
            else:
                error_detail = (
                    f"Неизвестная SQL ошибка\nПодробности: {mysql_error_description}"
                )
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=error_detail
        )
