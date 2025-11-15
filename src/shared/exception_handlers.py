from typing import Any, Dict, Optional, Type, Callable, Coroutine
from fastapi import FastAPI, Request, status, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel
from sqlalchemy.exc import SQLAlchemyError
from src.core.logger import log_exception, log_with_context


# -------------------------
# Standard Error Response
# -------------------------
class ErrorResponse(BaseModel):
    success: bool = False
    message: str
    error_code: str
    details: Optional[Dict[str, Any]] = None
    resolution: Optional[str] = None


# -------------------------
# Domain Exceptions
# -------------------------
class BookApiException(Exception):
    """Base class for domain exceptions"""

    def __init__(self, message: str, error_code: str, details: Optional[Dict[str, Any]] = None,
                 resolution: Optional[str] = None, status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.resolution = resolution
        self.status_code = status_code


# Example domain exceptions
class InvalidToken(BookApiException):
    def __init__(self, details=None):
        super().__init__(
            message="Token is invalid or expired",
            error_code="invalid_token",
            details=details,
            resolution="Please get a new token",
            status_code=status.HTTP_401_UNAUTHORIZED
        )


class RevokedToken(BookApiException):
    def __init__(self, details=None):
        super().__init__(
            message="Token has been revoked",
            error_code="token_revoked",
            details=details,
            resolution="Please get a new token",
            status_code=status.HTTP_401_UNAUTHORIZED
        )


class AccessTokenRequired(BookApiException):
    def __init__(self, details=None):
        super().__init__(
            message="Access token required",
            error_code="access_token_required",
            details=details,
            resolution="Provide a valid access token",
            status_code=status.HTTP_401_UNAUTHORIZED
        )


class RefreshTokenRequired(BookApiException):
    def __init__(self, details=None):
        super().__init__(
            message="Refresh token required",
            error_code="refresh_token_required",
            details=details,
            resolution="Provide a valid refresh token",
            status_code=status.HTTP_403_FORBIDDEN
        )


class UserAlreadyExists(BookApiException):
    def __init__(self, details=None):
        super().__init__(
            message="User with email already exists",
            error_code="user_exists",
            details=details,
            status_code=status.HTTP_403_FORBIDDEN
        )


class UserNotFound(BookApiException):
    def __init__(self, details=None):
        super().__init__(
            message="User not found",
            error_code="user_not_found",
            details=details,
            status_code=status.HTTP_404_NOT_FOUND
        )


class BookNotFound(BookApiException):
    def __init__(self, details=None):
        super().__init__(
            message="Book not found",
            error_code="book_not_found",
            details=details,
            status_code=status.HTTP_404_NOT_FOUND
        )


class TagNotFound(BookApiException):
    def __init__(self, details=None):
        super().__init__(
            message="Tag not found",
            error_code="tag_not_found",
            details=details,
            resolution="Create a new Tag.",
            status_code=status.HTTP_404_NOT_FOUND
        )


class TagAlreadyExists(BookApiException):
    def __init__(self, details=None):
        super().__init__(
            message="Tag already exists",
            error_code="tag_exists",
            details=details,
            status_code=status.HTTP_403_FORBIDDEN
        )


class AccountNotVerified(BookApiException):
    def __init__(self, details=None):
        super().__init__(
            message="Account not verified",
            error_code="account_not_verified",
            details=details,
            resolution="Check your email for verification details",
            status_code=status.HTTP_403_FORBIDDEN
        )


class InvalidCredentials(BookApiException):
    def __init__(self, details=None):
        super().__init__(
            message="Invalid email or password",
            error_code="invalid_email_or_password",
            details=details,
            status_code=status.HTTP_400_BAD_REQUEST
        )


class InsufficientPermission(BookApiException):
    def __init__(self, details=None):
        super().__init__(
            message="Insufficient permissions",
            error_code="insufficient_permissions",
            details=details,
            status_code=status.HTTP_401_UNAUTHORIZED
        )


class PasswordNotMatch(BookApiException):
    def __init__(self, details=None):
        super().__init__(
            message="Password do not match",
            error_code="password_do_not_match",
            details=details,
            status_code=status.HTTP_400_BAD_REQUEST
        )


# -------------------------
# Exception Handlers
# -------------------------
def register_exception_handlers(app: FastAPI):
    """Register all exception handlers"""

    # 1️⃣ Domain Exceptions (BookApiException subclasses)
    domain_exceptions: list[Type[BookApiException]] = [
        BookNotFound, UserNotFound, UserAlreadyExists, InvalidCredentials,
        InvalidToken, RevokedToken, AccessTokenRequired, RefreshTokenRequired,
        InsufficientPermission, TagNotFound, TagAlreadyExists, AccountNotVerified
    ]

    for exc_class in domain_exceptions:
        # Use default argument trick to avoid late binding in loops
        def _make_handler(exc_type: Type[BookApiException]) -> Callable[
            [Request, Exception], Coroutine[Any, Any, JSONResponse]]:
            async def handler(request: Request, exc: BookApiException) -> JSONResponse:
                log_with_context(
                    "warning",
                    f"Handled BookApiException: {exc.error_code}",
                    details=exc.details,
                    path=str(request.url),
                    method=request.method
                )
                log_exception(exc, context=f"{exc_type.__name__}", **exc.details)
                return JSONResponse(
                    status_code=exc.status_code,
                    content=ErrorResponse(
                        message=exc.message,
                        error_code=exc.error_code,
                        details=exc.details,
                        resolution=exc.resolution
                    ).model_dump()
                )

            return handler  # Type: ignore

        app.add_exception_handler(exc_class, _make_handler(exc_class))

    # 2️⃣ Database errors
    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
        log_exception(exc, context="SQLAlchemyError", path=str(request.url), method=request.method,
                      query=getattr(exc, "statement", None))
        log_with_context("error", "Database error", path=str(request.url), method=request.method)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(
                message="Database error",
                error_code="database_error",
                details={"message": str(exc)}
            ).model_dump()
        )

    # 3️⃣ Pydantic / Request Validation errors
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        errors = exc.errors()
        log_exception(exc, context="RequestValidationError", path=str(request.url), method=request.method)
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content=ErrorResponse(
                message="Validation error",
                error_code="validation_error",
                details={"errors": errors},
                resolution="Please check the request payload"
            ).model_dump()
        )

    # 4️⃣ FastAPI HTTPException (optional short-circuit)
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        details = {"detail": exc.detail} if exc.detail else None
        log_with_context("info", "HTTPException raised", path=str(request.url), method=request.method,
                         status_code=exc.status_code, **(details or {}))
        return JSONResponse(
            status_code=exc.status_code or status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(
                message=str(exc.detail) if isinstance(exc.detail, str) else "HTTP error",
                error_code="http_error",
                details=details
            ).model_dump()
        )

    # 5️⃣ Catch-all fallback
    @app.exception_handler(Exception)
    async def fallback_exception_handler(request: Request, exc: Exception):
        log_exception(exc, context="UnhandledException", path=str(request.url), method=request.method)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(
                message="Internal server error",
                error_code="internal_server_error",
                details=None
            ).model_dump()
        )
