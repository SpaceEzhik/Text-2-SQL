from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.requests import Request
from starlette.responses import HTMLResponse

from config import settings
from db.crud import execute_sql
from db import db_helper_api
from frontend import templates
from guardian import anti_fraud
from schemas import ModelRequest, DBRequest
from security import auth_prefix
from security.helpers import get_user_group_from_token
from security.validation import check_auth_user, validate_query_type
from sql_generator import generate_sql

router = (
    APIRouter(
        dependencies=[Depends(check_auth_user)],
    )
    if settings.security.enabled
    else APIRouter()
)


@router.get("/")
def root(request: Request):
    return templates.TemplateResponse(
        request,
        "index.html",
        {"action_url": request.url_for("prompt_form")},
    )


@router.get("/generate_sql", response_class=HTMLResponse)
def prompt_form(request: Request):
    return templates.TemplateResponse(
        request,
        "submit_prompt.html",
        {
            "generate_url": request.url_for("prompt_handler"),
            "execute_url": request.url_for("execute_generated_sql"),
            "logout_url": str(request.base_url)[:-1] + auth_prefix + "/logout",
            "redirect_url": request.url_for("root"),
        },
    )


@router.post("/submit_prompt")
async def prompt_handler(
    model_request: ModelRequest,
    db_session: AsyncSession = Depends(db_helper_api.session_dependency),
) -> dict[str, str]:
    if not anti_fraud.predict(model_request.prompt):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Запрос не относится к выбранной базе данных",
        )
    sql_query = await generate_sql(
        model_request.prompt, settings.core_llm.db_context, db_session
    )
    return {"sql_query": sql_query}


@router.post("/execute_sql", response_class=HTMLResponse)
async def execute_generated_sql(
    request: Request,
    db_request: DBRequest,
    db_session: AsyncSession = Depends(db_helper_api.session_dependency),
    user_group: str = (
        Depends(get_user_group_from_token)
        if settings.security.enabled
        else settings.security.user_group_default
    ),
):
    validate_query_type(db_request.sql_query, user_group)
    result = await execute_sql(db_session, db_request.sql_query)
    return templates.TemplateResponse(request, "table.html", {"data": result})
