from config import settings
from .db_helpers import DatabaseHelper, DatabaseErrorHandler

db_helper_api = DatabaseHelper(
    url=settings.db.url_api,
    echo=settings.db.echo,
)
db_helper_admin = DatabaseHelper(
    url=settings.db.url_admin,
    echo=settings.db.echo,
)
db_error_handler = DatabaseErrorHandler(default_error_detail="¯\\_(ツ)_/¯")
