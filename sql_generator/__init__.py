from fastapi import HTTPException
from pydantic_ai import Agent, UnexpectedModelBehavior
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from config import settings
from sql_generator.sql_generator import sql_agent, logger


async def generate_sql(
    question: str, db_context: str, db_session: AsyncSession, agent: Agent = sql_agent
) -> str:
    prompt = settings.core_llm.prompt.format(question, db_context)
    try:
        response = await agent.run(user_prompt=prompt, deps=db_session)
        response = response.output
    except UnexpectedModelBehavior as e:
        logger.error(f"Validation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Генерация не удалась, попробуйте ещё раз",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Сервис недоступен, попробуйте позже",
        )
    return response
