import uvicorn
from fastapi import FastAPI, HTTPException, Request, status, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from db.crud import execute_sql
from db.db_helpers import db_helper_api
from frontend.frontend import static_files, templates
from guardian.guardian import anti_fraud
from schemas import ModelRequest, DBRequest
from security.auth import router as auth_router
from sql_generator import sql_generator

app = FastAPI()
app.include_router(auth_router)
app.mount(settings.frontend.static_path_relative, static_files, name="static")


@app.get("/")
def root(request: Request):
    return templates.TemplateResponse(
        "index.html", {"request": request, "action_url": "/generate_sql"}
    )


@app.get("/generate_sql", response_class=HTMLResponse)
def prompt_form(request: Request):
    return templates.TemplateResponse(
        "submit_prompt.html",
        {
            "request": request,
            "generate_url": "/submit_prompt",
            "execute_url": "/execute_sql",
        },
    )


@app.post("/submit_prompt")
async def prompt_handler(model_request: ModelRequest) -> dict[str, str]:
    if not anti_fraud.predict(model_request.prompt):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Запрос не относится к выбранной базе данных",
        )
    sql_query = await sql_generator.generate_sql(model_request.prompt)
    return {"sql_query": sql_query}


@app.post("/execute_sql", response_class=HTMLResponse)
async def execute_generated_sql(
    request: Request,
    db_request: DBRequest,
    db_session: AsyncSession = Depends(db_helper_api.session_dependency),
):
    result = await execute_sql(db_session, db_request.sql_query)
    return templates.TemplateResponse(
        "table.html", {"request": request, "data": result}
    )


if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=1337, reload=False)
