import pytest

from sql_generator import generate_sql


@pytest.mark.asyncio
@pytest.mark.slow
async def test_generator_availability():
    model_output = await generate_sql("return People table")
    assert model_output is not None
    assert isinstance(model_output, str)
    assert len(model_output) > 0
