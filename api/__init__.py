from fastapi import APIRouter

from config import settings
from .api_v1.views import router as router_v1

router = APIRouter(
    prefix=settings.api.prefix,
)
router.include_router(router_v1, prefix=settings.api.v1.prefix)
