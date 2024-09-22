import httpx
from fastapi import HTTPException, status

from config import settings

HEADERS = {
    "Content-Type": "application/json",
}


async def generate_sql(question: str, db_context: str) -> str:
    prompt = settings.core_llm.prompt.format(question, db_context)
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url=settings.core_llm.url,
                json={"prompt": prompt, **settings.core_llm.config},
                headers=HEADERS,
                timeout=100,
            )
            query = response.json()["response"].strip(" `\n")
            # TODO: add proper parsing/processing for the model output
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Сервис недоступен, попробуйте позже",
        )
    return query
