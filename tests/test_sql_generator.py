import pytest

from config import settings
from sql_generator import generate_sql
from db import db_helper_api


@pytest.mark.anyio
@pytest.mark.slow
async def test_generator_availability():
    async for db_session in db_helper_api.session_dependency():
        model_output = await generate_sql(
            "return People table", settings.core_llm.db_context, db_session=db_session
        )
        assert model_output is not None
        assert isinstance(model_output, str)
        assert len(model_output) > 0
