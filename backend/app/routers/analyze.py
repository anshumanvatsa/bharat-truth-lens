from fastapi import APIRouter
from app.services.analyzer import analyze_claim

router = APIRouter(prefix="/analyze")


@router.post("/")
def analyze(data: dict):

    claim = data["claim"]

    result = analyze_claim(claim)

    return result