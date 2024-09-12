import httpx
from config import settings

HEADERS = {
    "Content-Type": "application/json",
}


async def generate_sql(question: str) -> str:
    prompt = settings.core_llm.prompt.format(question)
    async with httpx.AsyncClient() as client:
        response = await client.post(
            url=settings.core_llm.url,
            json={"prompt": prompt, **settings.core_llm.config},
            headers=HEADERS,
            timeout=100,
        )
        query = response.json()["response"].strip(" `\n")
        # TODO: add proper parsing/processing for the model output
    return query
