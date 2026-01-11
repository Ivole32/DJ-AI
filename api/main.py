# Import FastAPI
from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
import mimetypes

# Import nessessary configuration
from api.config.config import API_TITLE, API_DESCRIPTION, API_VERSION, API_PREFIX, API_DOCS_ENABLED
from api.config.config import HOST, PORT
from api.config.config import DEBUG

# Import rate limiter
from api.rate_limit.limiter import limiter
from slowapi.middleware import SlowAPIMiddleware

# Import routers
from api.routers.search_router import router as search_router
from api.routers.prediction_router import router as prediction_router
from api.routers.auth_router import router as auth_router
from api.routers.user_router import router as user_router
from api.routers.profile_router import router as profile_router
from api.routers.playlist_router import router as playlist_router
from api.routers.config_router import router as config_router

# Import header middleware
from api.middleware.headers import add_header_middleware

# Import CORS middleware
from api.middleware.cors import setup_cors

# Import logger setup
import logging
from api.logger.logger import logger

# Initialize FastAPI application
app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION,
    swagger_ui_parameters={
        "docExpansion": "list",
        "displayRequestDuration": DEBUG,
        "filter": True,
        "syntaxHighlight.theme": "monokai",
    },
    docs_url="/docs" if API_DOCS_ENABLED else None,
    redoc_url=None,
    openapi_url="/openapi.json" if API_DOCS_ENABLED else None,
    debug=DEBUG,
    on_startup=[lambda: logger.info("Starting up the API...")],
    on_shutdown=[lambda: logger.info("Shutting down the API...")],
)

# Integrate rate limiter middleware
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

# Add WebP MIME type support for Windows
if not mimetypes.guess_type('file.webp')[0]:
    mimetypes.add_type('image/webp', '.webp')

# Mount static files for uploads
app.mount("/uploads", StaticFiles(directory="api/uploads"), name="uploads")

# Include routers
app.include_router(search_router, prefix=API_PREFIX)
app.include_router(prediction_router, prefix=API_PREFIX)
app.include_router(auth_router, prefix=API_PREFIX)
app.include_router(user_router, prefix=API_PREFIX)
app.include_router(profile_router, prefix=API_PREFIX)
app.include_router(playlist_router, prefix=API_PREFIX)
app.include_router(config_router, prefix=API_PREFIX)

# Add custom headers middleware
add_header_middleware(app)

# Setup CORS middleware
setup_cors(app)


@app.get("/", include_in_schema=False)
@limiter.limit("10/second")
async def root(request: Request):
    if DEBUG:
        return {"message": "API is running. See /docs for documentation.", "docs": "/docs"}
    else:
        raise HTTPException(status_code=404)

# Run the application
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=HOST, port=PORT)