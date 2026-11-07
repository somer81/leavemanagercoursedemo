"""Login, identity and logout (spec 0002). Only login is public (docs/security.md)."""

from collections.abc import Callable
from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, Response
from pydantic import BaseModel

from app.domain.auth import Identity
from app.domain.errors import Unauthenticated
from app.services.auth_service import SESSION_LIFETIME, AuthService

SESSION_COOKIE = "session"

SessionDependency = Callable[..., Identity]


class LoginRequest(BaseModel):
    # Types only: format rules live in the service, so there is one source of truth.
    username: str
    password: str


class IdentityResponse(BaseModel):
    display_name: str
    role: str


def _identity_response(identity: Identity) -> IdentityResponse:
    return IdentityResponse(display_name=identity.display_name, role=identity.role.value)


def session_dependency(get_service: Callable[[], AuthService]) -> SessionDependency:
    """The dependency every protected route carries: a valid session or 401."""

    def require_session(session: Annotated[str | None, Cookie()] = None) -> Identity:
        if not session:
            raise Unauthenticated()
        return get_service().authenticate(session)

    return require_session


def auth_router(
    get_service: Callable[[], AuthService],
    require_session: SessionDependency,
    cookie_secure: bool,
) -> APIRouter:
    router = APIRouter()

    @router.post("/api/auth/login")
    def login(body: LoginRequest, response: Response) -> IdentityResponse:
        result = get_service().login(body.username, body.password)
        response.set_cookie(
            SESSION_COOKIE,
            result.token,
            max_age=int(SESSION_LIFETIME.total_seconds()),
            path="/",
            httponly=True,
            samesite="strict",
            secure=cookie_secure,
        )
        return _identity_response(result.identity)

    @router.get("/api/auth/me")
    def me(identity: Annotated[Identity, Depends(require_session)]) -> IdentityResponse:
        return _identity_response(identity)

    @router.post("/api/auth/logout", status_code=204, dependencies=[Depends(require_session)])
    def logout(response: Response, session: Annotated[str, Cookie()]) -> Response:
        get_service().logout(session)
        response.status_code = 204
        response.delete_cookie(
            SESSION_COOKIE, path="/", httponly=True, samesite="strict", secure=cookie_secure
        )
        return response

    return router
