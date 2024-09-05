from fastapi import Request, Response

from config import settings
from frontend.frontend import templates
from security import auth_prefix


class UnauthorizedException(Exception):
    def __init__(self, details: str):
        self.details = details


class RefreshRequiredException(Exception):
    def __init__(self, details: str):
        self.details = details


def unauthorized_exception_handler(request: Request, exc: UnauthorizedException):
    return templates.TemplateResponse(
        "redirect.html",
        {
            "request": request,
            "request_type": "get",
            "redirect_url": auth_prefix + "/login",
        },
    )


def refresh_required_exception_handler(request: Request, exc: RefreshRequiredException):
    return templates.TemplateResponse(
        "redirect.html",
        {
            "request": request,
            "request_type": "post",
            "redirect_url": auth_prefix + "/refresh",
        },
    )
