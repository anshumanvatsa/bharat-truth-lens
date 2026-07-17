from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .routers import auth as auth_router
from .routers import analyze as analyze_router
from .routers import vote as vote_router

settings = get_settings()

app = FastAPI(title=settings.app_name)

# CORS — open to all origins
# We use JWT Bearer tokens (not cookies) so allow_credentials=False is correct.
# allow_origins=["*"] works with allow_credentials=False and handles all Vercel
# preview URLs, localhost variants, and any future domain without code changes.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth_router.router)
app.include_router(analyze_router.router)
app.include_router(vote_router.router)

# Health check
@app.get("/health", tags=["system"])
async def health_check():
    return {"status": "ok"}