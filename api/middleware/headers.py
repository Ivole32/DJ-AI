"""
Middleware to add custom headers to API responses.
"""

from fastapi import Request
from fastapi.responses import Response

from api.config.config import API_VERSION

def add_header_middleware(app):
    @app.middleware("http")
    async def header_middleware(request: Request, call_next):
        response: Response = await call_next(request)

        response.headers["X-API-Version"] = API_VERSION
        response.headers["X-Content-Type-Options"] = "nosniff" # Security header to prevent MIME type sniffing
        response.headers["Cache-Control"] = "no-store"


        return response
    
    return app