import logging
from typing import Annotated
from annotated_types import MinLen
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic_ai import Agent, RunContext, ModelRetry
from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.google_gla import GoogleGLAProvider
from pydantic_ai.providers.openai import OpenAIProvider
from openai import AsyncOpenAI

from db.crud import execute_sql
from config import settings


logging.basicConfig(
    encoding="utf-8",
    level=logging.DEBUG,
    handlers=[logging.FileHandler("log.txt")],
)
logger = logging.getLogger(__name__)


if settings.core_llm.provider == "ollama":
    openai_client = AsyncOpenAI(base_url=settings.core_llm.url, api_key="ollama")
    core_llm = OpenAIModel(
        model_name=settings.core_llm.model_name,
        provider=OpenAIProvider(
            # base_url=settings.local_llm.url,
            openai_client=openai_client,
        ),
    )
elif settings.core_llm.provider == "gemini":
    core_llm = GeminiModel(
        model_name=settings.core_llm.model_name,
        provider=GoogleGLAProvider(api_key=settings.core_llm.api_key),
    )


class ValidSQL(BaseModel):
    """Valid SQL query."""

    sql_query: Annotated[str, MinLen(1)]


sql_agent = Agent(
    model=core_llm,
    system_prompt=settings.core_llm.prompt,
    output_type=ValidSQL,
    deps_type=AsyncSession,
    retries=settings.core_llm.retry_count,
)


@sql_agent.output_validator
async def validate_sql(ctx: RunContext[AsyncSession], output: ValidSQL) -> str:
    # print(output)
    logger.info(f"Validation attempt for SQL: {output.sql_query}")
    try:
        await execute_sql(
            db_session=ctx.deps,
            sql_query=f"explain {output.sql_query}",
        )
        logger.info(f"SQL validation successful")
    except Exception as e:
        error_msg = str(e)
        logger.error(f"SQL validation failed: {error_msg} || Let's try again...")
        raise ModelRetry(str(e))
    return output.sql_query
