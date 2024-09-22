from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from time import time, localtime, asctime
import logging

logging.basicConfig(level=logging.INFO, filename="log.txt")
logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        method = request.method
        url = request.url.path

        start_time = time()
        response = await call_next(request)
        status_code = response.status_code
        process_time = time() - start_time

        logger.info(
            f"{str(asctime(localtime(start_time)))} || Method: {method} || URL: {url} || Status code: {status_code} || Process time: {process_time:.4f} seconds"
        )
        return response
