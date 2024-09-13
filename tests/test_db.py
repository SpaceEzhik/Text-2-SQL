import pytest

from db import db_helper_api, db_helper_admin
from db.crud import execute_sql, create_user, get_user_by_email, delete_user_by_email
from schemas import CreateUser


@pytest.mark.asyncio
async def test_db_availability():
    async for db_session in db_helper_api.session_dependency():
        result = await execute_sql(db_session, "select 1")
        assert result
        assert len(result) == 1


@pytest.mark.asyncio
async def test_user_db_cycle():
    async for db_session in db_helper_admin.session_dependency():
        test_user = CreateUser(
            email="test@test.com", password="test", user_group="developer"
        )
        created_user = await create_user(db_session, test_user)
        found_user = await get_user_by_email(db_session, test_user.email)
        assert created_user == found_user

        await delete_user_by_email(db_session, test_user.email)
        found_user = await get_user_by_email(db_session, test_user.email)
        assert found_user is None
