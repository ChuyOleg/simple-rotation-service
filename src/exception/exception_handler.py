from typing import Any

from fastapi.responses import JSONResponse


class InternalException(Exception):
    pass


class NotFoundTokenException(Exception):
    pass


class RotatableException(Exception):
    def __init__(self, http_response_json: Any, inner: Exception | None = None):
        super().__init__()
        self.http_response_json = http_response_json
        self.inner = inner

    def __str__(self):
        if self.inner:
            return f"{self.http_response_json} (caused by {repr(self.inner)})"
        return self.http_response_json


class AiHttpCallRetryableException(RotatableException):
    def __init__(self, data: Any, inner: Exception | None = None):
        super().__init__(data, inner)


async def internal_exception_handler(request, response):
    return JSONResponse(
        status_code=500,
        content={"error": "Internal Server Error"})


async def internal_retryable_exception_handler(request, response):
    return JSONResponse(
        status_code=500,
        content={"error": "Something went wrong, HttpCallRetryableException."})


async def rotation_retryable_exception_handler(request, response):
    return JSONResponse(
        status_code=500,
        content={"error": "Something went wrong, RotationRetryableException."})


async def not_found_token_exception_handler(request, response):
    return JSONResponse(
        status_code=500,
        content={"error": "Either API token is absent or all of them are locked."})
