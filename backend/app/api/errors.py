"""The one place domain errors become HTTP (docs/conventions.md, Error handling).

Bodies are always {"error": {"code", "message"}} and never echo what the client sent.
"""

from collections.abc import Awaitable, Callable

from fastapi import FastAPI, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.domain.errors import (
    DataStoreUnavailable,
    DomainError,
    InvalidCredentials,
    InvalidInput,
    SessionExpired,
    Unauthenticated,
)

_MAPPING: dict[type[DomainError], tuple[int, str, str]] = {
    InvalidInput: (422, "INVALID_INPUT", "Geçersiz giriş."),
    InvalidCredentials: (401, "INVALID_CREDENTIALS", "Kullanıcı adı veya parola hatalı."),
    Unauthenticated: (401, "UNAUTHENTICATED", "Oturum gerekli."),
    SessionExpired: (401, "SESSION_EXPIRED", "Oturumunuz sona erdi."),
    DataStoreUnavailable: (503, "DATA_STORE_UNAVAILABLE", "Hizmet şu anda kullanılamıyor."),
}


def error_response(status: int, code: str, message: str) -> JSONResponse:
    return JSONResponse(status_code=status, content={"error": {"code": code, "message": message}})


async def _domain_error(_: Request, error: Exception) -> JSONResponse:
    mapped = _MAPPING.get(type(error)) if isinstance(error, DomainError) else None
    status, code, message = mapped or (500, "INTERNAL_ERROR", "Beklenmeyen bir hata oluştu.")
    return error_response(status, code, message)


async def _validation_error(_: Request, __: Exception) -> JSONResponse:
    # FastAPI's default body echoes the submitted values — passwords included.
    return error_response(422, "INVALID_INPUT", "Geçersiz giriş.")


async def _json_only(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    # CSRF: state-changing API calls accept application/json only (docs/security.md).
    content_type = request.headers.get("content-type", "")
    if (
        request.method == "POST"
        and request.url.path.startswith("/api/")
        and not content_type.startswith("application/json")
    ):
        return error_response(415, "UNSUPPORTED_MEDIA_TYPE", "İstek JSON olmalı.")
    return await call_next(request)


def install_error_handling(app: FastAPI) -> None:
    app.add_exception_handler(DomainError, _domain_error)
    app.add_exception_handler(RequestValidationError, _validation_error)
    app.middleware("http")(_json_only)
