import traceback

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response

from .config import get_settings
from .routers import auth as auth_router
from .routers import analyze as analyze_router
from .routers import vote as vote_router

settings = get_settings()

app = FastAPI(title=settings.app_name)

# ── CORS headers — always injected, even on 500 errors ───────────────────────
CORS_HEADERS = {
    "Access-Control-Allow-Origin":  "*",
    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, PATCH",
    "Access-Control-Allow-Headers": "Content-Type, Authorization, Accept, X-Requested-With",
    "Access-Control-Max-Age":       "3600",
}

@app.middleware("http")
async def cors_middleware(request: Request, call_next):
    # Preflight: respond immediately, never hit routers
    if request.method == "OPTIONS":
        return Response(status_code=200, headers=CORS_HEADERS)

    try:
        response = await call_next(request)
    except Exception as exc:
        # Unhandled exception — return 500 WITH CORS headers so browser
        # can read the error body instead of seeing a CORS block
        tb = traceback.format_exc()
        print(f"[UNHANDLED EXCEPTION] {exc}\n{tb}")
        response = JSONResponse(
            status_code=500,
            content={"detail": f"Internal server error: {str(exc)}"},
            headers=CORS_HEADERS,
        )
        return response

    # Inject CORS into every normal response
    for key, value in CORS_HEADERS.items():
        response.headers[key] = value
    return response


# Routers
app.include_router(auth_router.router)
app.include_router(analyze_router.router)
app.include_router(vote_router.router)


@app.get("/health", tags=["system"])
async def health_check():
    return {"status": "ok"}