import os
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/analyze", tags=["analysis"])

# ── Auto-select analyzer based on available resources ─────────────────────────
# Cloud/Render: no PyTorch → use Groq-based lightweight analyzer (~80MB RAM)
# Local:        fine-tuned DistilBERT available → use full hybrid pipeline

_analyzer_fn = None

def _get_analyzer():
    global _analyzer_fn
    if _analyzer_fn is not None:
        return _analyzer_fn

    # Try full local analyzer first (needs PyTorch + local model)
    try:
        from app.services.analyzer import analyze_claim
        _analyzer_fn = analyze_claim
        print("[Router] Using full hybrid analyzer (DistilBERT + PyTorch)")
    except Exception as e:
        # Fallback: lightweight Groq-based analyzer (no PyTorch needed)
        print(f"[Router] Local analyzer unavailable ({type(e).__name__}). Using cloud analyzer.")
        from app.services.analyzer_cloud import analyze_claim_cloud
        _analyzer_fn = analyze_claim_cloud

    return _analyzer_fn


@router.post("/")
async def analyze(data: dict):
    claim = data.get("claim", "").strip()
    if not claim:
        raise HTTPException(status_code=400, detail="claim field is required")
    if len(claim) > 2000:
        raise HTTPException(status_code=400, detail="claim must be under 2000 characters")

    analyzer = _get_analyzer()
    result   = analyzer(claim)
    return result