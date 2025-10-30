from typing import Any

from fastapi.responses import JSONResponse


class InternalException(Exception):
    pass


class RetryableException(Exception):
    pass


class NotFoundTokenException(Exception):
    pass


class AiHttpCallException(Exception):
    def __init__(self, data: Any, inner: Exception | None = None):
        super().__init__()
        self.data = data
        self.inner = inner

    def __str__(self):
        if self.inner:
            return f"{self.data} (caused by {repr(self.inner)})"
        return self.data


async def internal_exception_handler(request, response):
    return JSONResponse(
        status_code=500,
        content={"error": "Internal Server Error"})


async def retryable_exception_handler(request, response):
    return JSONResponse(
        status_code=500,
        content={"error": "Something went wrong, RetryableException."})


async def not_found_token_exception_handler(request, response):
    return JSONResponse(
        status_code=500,
        content={"error": "Either API token is absent or all of them are locked."})
