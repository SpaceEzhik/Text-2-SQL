from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
from config import settings

static_files: StaticFiles = StaticFiles(directory=str(settings.frontend.static_path))
templates: Jinja2Templates = Jinja2Templates(
    directory=str(settings.frontend.templates_path)
)

# TODO: create a proper frontend and rewrite my kludgy implementation of it
