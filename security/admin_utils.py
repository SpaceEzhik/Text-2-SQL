import asyncio

from db.crud import create_user
from schemas import CreateUser
from db import db_helper_admin


async def main():
    new_user = CreateUser(
        email=input("Введите почту пользователя:\n"),
        password=input("Введите пароль пользователя:\n"),
        user_group=input("Введите группу пользователя:\n"),
    )
    async for session in db_helper_admin.session_dependency():
        try:
            created_user = await create_user(session, new_user)
            print(created_user)
        except Exception as e:
            print(f"An error occurred: {e}")


if __name__ == "__main__":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())

# 123@mail.ru
# 123
# developer
