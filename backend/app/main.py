from fastapi import FastAPI, Request
from fastapi.responses import Response

from .config import get_settings
from .routers import auth as auth_router
from .routers import analyze as analyze_router
from .routers import vote as vote_router

settings = get_settings()

app = FastAPI(title=settings.app_name)

# ── Explicit CORS — bypasses CORSMiddleware entirely ─────────────────────────
# CORSMiddleware was failing to add headers (Starlette version / middleware
# ordering issue on Render). This custom middleware always adds the headers.
#
# We use JWT Bearer tokens (not cookies) so allow_credentials is not needed.

CORS_HEADERS = {
    "Access-Control-Allow-Origin":  "*",
    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, PATCH",
    "Access-Control-Allow-Headers": "Content-Type, Authorization, Accept, X-Requested-With",
    "Access-Control-Max-Age":       "3600",
}

@app.middleware("http")
async def cors_middleware(request: Request, call_next):
    # Handle preflight immediately — never pass OPTIONS to routers
    if request.method == "OPTIONS":
        return Response(status_code=200, headers=CORS_HEADERS)

    response = await call_next(request)

    # Inject CORS headers into every response
    for key, value in CORS_HEADERS.items():
        response.headers[key] = value

    return response


# Routers
app.include_router(auth_router.router)
app.include_router(analyze_router.router)
app.include_router(vote_router.router)


# Health check
@app.get("/health", tags=["system"])
async def health_check():
    return {"status": "ok"}