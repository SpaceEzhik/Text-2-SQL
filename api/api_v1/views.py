from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.requests import Request
from starlette.responses import HTMLResponse

from db.crud import execute_sql
from db.db_helpers import db_helper_api

from frontend.frontend import templates
from guardian.guardian import anti_fraud
from schemas import ModelRequest, DBRequest
from security import auth_prefix
from security.validation import check_auth_user
from sql_generator import sql_generator

router = APIRouter(
    dependencies=[Depends(check_auth_user)],
)


@router.get("/")
def root(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "action_url": request.url_for("prompt_form")},
    )


@router.get("/generate_sql", response_class=HTMLResponse)
def prompt_form(request: Request):
    return templates.TemplateResponse(
        "submit_prompt.html",
        {
            "request": request,
            "generate_url": request.url_for("prompt_handler"),
            "execute_url": request.url_for("execute_generated_sql"),
            "logout_url": str(request.base_url)[:-1] + auth_prefix + "/logout",
            "redirect_url": request.url_for("root"),
        },
    )


@router.post("/submit_prompt")
async def prompt_handler(model_request: ModelRequest) -> dict[str, str]:
    if not anti_fraud.predict(model_request.prompt):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Запрос не относится к выбранной базе данных",
        )
    sql_query = await sql_generator.generate_sql(model_request.prompt)
    return {"sql_query": sql_query}


@router.post("/execute_sql", response_class=HTMLResponse)
async def execute_generated_sql(
    request: Request,
    db_request: DBRequest,
    db_session: AsyncSession = Depends(db_helper_api.session_dependency),
):
    result = await execute_sql(db_session, db_request.sql_query)
    return templates.TemplateResponse(
        "table.html", {"request": request, "data": result}
    )
