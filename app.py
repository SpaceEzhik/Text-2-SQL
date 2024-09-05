import uvicorn
from fastapi import FastAPI

from config import settings
from frontend.frontend import static_files
from security.auth import router as auth_router
from security.exceptions import (
    UnauthorizedException,
    RefreshRequiredException,
    unauthorized_exception_handler,
    refresh_required_exception_handler,
)
from api import router as api_router

app = FastAPI()
app.include_router(auth_router)
app.include_router(api_router)

app.mount(settings.frontend.static_path_relative, static_files, name="static")

app.add_exception_handler(UnauthorizedException, unauthorized_exception_handler)
app.add_exception_handler(RefreshRequiredException, refresh_required_exception_handler)

if __name__ == "__main__":
    uvicorn.run("app:app", host=settings.run.host, port=settings.run.port, reload=False)
