"""
Global exception handlers — register with the FastAPI app.
"""

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import ORJSONResponse
from pydantic import ValidationError


def register_exception_handlers(app: FastAPI) -> None:

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        details = []
        for error in exc.errors():
            field = ".".join(str(loc) for loc in error["loc"] if loc != "body")
            details.append({"field": field or None, "message": error["msg"]})
        return ORJSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"error": "Validation failed.", "details": details},
        )

    @app.exception_handler(ValidationError)
    async def pydantic_validation_handler(request: Request, exc: ValidationError):
        return ORJSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"error": "Validation failed.", "details": exc.errors()},
        )

    @app.exception_handler(404)
    async def not_found_handler(request: Request, exc):
        return ORJSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": "The requested resource was not found."},
        )

    @app.exception_handler(500)
    async def internal_error_handler(request: Request, exc):
        return ORJSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "An unexpected internal server error occurred."},
        )
