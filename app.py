import uvicorn
from fastapi import FastAPI, HTTPException, Request, Form, Body
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from db import db
from guardian.guardian import anti_fraud
from sql_generator import sql_generator

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


class ModelRequest(BaseModel):
    prompt: str


@app.get("/")
def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "action_url": "/generate_sql"})


@app.get("/generate_sql", response_class=HTMLResponse)
def prompt_form(request: Request):
    return templates.TemplateResponse("submit_prompt.html", {"request": request, "action_url": "/submit_prompt"})


@app.post("/submit_prompt")
async def prompt_handler(model_request: ModelRequest) -> dict[str, str]:
    if not anti_fraud.is_approved(model_request.prompt):
        raise HTTPException(status_code=422, detail="Запрос не относится к выбранной базе данных")
    sql_query = await sql_generator.generate_sql(model_request.prompt)
    return {"sql_query": sql_query}


if __name__ == '__main__':
    uvicorn.run('app:app', host='127.0.0.1', port=1337, reload=True)
