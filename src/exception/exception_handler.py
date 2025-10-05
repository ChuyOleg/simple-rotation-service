from fastapi.responses import JSONResponse

class InternalException(Exception):
    pass

class RetryableException(Exception):
    pass


async def internal_exception_handler(request, response):
    return JSONResponse(
        status_code=500,
        content={ "error": "Internal Server Error" })


async def retryable_exception_handler(request, response):
    return JSONResponse(
        status_code=500,
        content={ "error": "Something went wrong, RetryableException." })
