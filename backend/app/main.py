from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .routers import auth as auth_router
from .routers import analyze as analyze_router
from .routers import vote as vote_router

settings = get_settings()

app = FastAPI(title=settings.app_name)

# Allow frontend origins
origins = [
    "http://localhost:8080",
    "http://127.0.0.1:8080",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    # Production Vercel deployment
    "https://bharat-truth-lens.vercel.app",
    "https://bharat-truth-lens-gdj4b8ad6-atulvatsamishra-gmailcoms-projects.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
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