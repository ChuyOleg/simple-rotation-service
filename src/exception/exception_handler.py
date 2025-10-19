from fastapi.responses import JSONResponse


class InternalException(Exception):
    pass


class RetryableException(Exception):
    pass


class NotFoundTokenException(Exception):
    pass


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
