# Import FastAPI
from fastapi import FastAPI, Request, HTTPException

# Import nessessary configuration
from api.config.config import API_TITLE, API_DESCRIPTION, API_VERSION, API_PREFIX
from api.config.config import HOST, PORT
from api.config.config import DEBUG

# Import rate limiter
from api.rate_limit.limiter import limiter
from slowapi.middleware import SlowAPIMiddleware

# Import routers
from api.routers.search_router import router as search_router
from api.routers.prediction_router import router as prediction_router

# Import header middleware
from api.middleware.headers import add_header_middleware

# Import CORS middleware
from api.middleware.cors import setup_cors

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
    docs_url="/docs",
    redoc_url=None,
    debug=DEBUG,
)

# Integrate rate limiter middleware
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

# Include routers
app.include_router(search_router, prefix=API_PREFIX)
app.include_router(prediction_router, prefix=API_PREFIX)

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