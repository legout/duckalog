"""Security middleware for the dashboard."""

from __future__ import annotations

from starlette.requests import Request
from starlette.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware


class CORSMiddleware(BaseHTTPMiddleware):
    """CORS middleware that only allows localhost access."""

    def __init__(self, app, allow_hosts: list[str] = None):
        super().__init__(app)
        # Default to localhost-only access
        self.allow_hosts = allow_hosts or [
            "127.0.0.1",
            "localhost",
            "::1",
        ]

    async def dispatch(self, request: Request, call_next):
        origin = request.headers.get("origin")
        client_host = request.client.host if request.client else None

        # Check if request is from allowed host
        origin_allowed = False
        if origin:
            # Extract host from origin (handle http/https and ports)
            origin_host = origin.replace("http://", "").replace("https://", "").split(":")[0]
            origin_allowed = origin_host in self.allow_hosts
        elif client_host:
            origin_allowed = client_host in self.allow_hosts

        response = await call_next(request)

        # Set CORS headers for allowed origins
        if origin_allowed:
            response.headers["Access-Control-Allow-Origin"] = origin or "*"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "*"
            response.headers["Access-Control-Allow-Credentials"] = "true"

        # Set security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; connect-src 'self' ws: wss:;"

        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Additional security headers middleware."""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Remove server information
        response.headers["Server"] = "Duckalog Dashboard"

        return response


__all__ = ["CORSMiddleware", "SecurityHeadersMiddleware"]