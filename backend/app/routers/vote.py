from fastapi import APIRouter, Depends, HTTPException, status
from ..database import get_database
from ..utils.auth import get_current_user
from ..models import now_utc

router = APIRouter(prefix="/vote", tags=["voting"])

# ── All Indian States + UTs ──────────────────────────────────────────────────
INDIAN_STATES = [
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
    "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka",
    "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya",
    "Mizoram", "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim",
    "Tamil Nadu", "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand",
    "West Bengal",
    # Union Territories
    "Delhi", "Jammu & Kashmir", "Ladakh", "Puducherry",
    "Chandigarh", "Dadra & Nagar Haveli", "Daman & Diu", "Lakshadweep",
    "Andaman & Nicobar Islands",
]

# ── PM Candidates ────────────────────────────────────────────────────────────
PM_CANDIDATES = [
    {"id": "candidate_a", "name": "Narendra Modi",   "party": "BJP",     "color": "#FF6B35"},
    {"id": "candidate_b", "name": "Rahul Gandhi",    "party": "INC",     "color": "#19A7CE"},
    {"id": "candidate_c", "name": "Arvind Kejriwal", "party": "AAP",     "color": "#00B4D8"},
    {"id": "candidate_d", "name": "Mamata Banerjee", "party": "TMC",     "color": "#22C55E"},
    {"id": "candidate_e", "name": "Nitish Kumar",    "party": "JDU",     "color": "#A78BFA"},
    {"id": "candidate_f", "name": "M.K. Stalin",     "party": "DMK",     "color": "#F59E0B"},
]

AGE_GROUPS = ["18-25", "26-40", "41-60", "60+"]


# ── POST /vote/pm ─────────────────────────────────────────────────────────────
@router.post("/pm")
async def cast_pm_vote(body: dict, current_user=Depends(get_current_user)):
    """
    Cast one vote for PM candidate. One user = one vote, enforced by DB.
    Stores: user_id, candidate_id, age_group (from user profile), state (from user profile).
    """
    db          = get_database()
    user_id     = str(current_user["_id"])
    candidate_id = body.get("candidate_id", "")

    # Validate candidate
    valid_ids = [c["id"] for c in PM_CANDIDATES]
    if candidate_id not in valid_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid candidate. Choose from: {valid_ids}"
        )

    # One vote per user — check if already voted
    existing = await db.pm_votes.find_one({"user_id": user_id})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You have already cast your vote. One person, one vote."
        )

    # Record vote
    vote_doc = {
        "user_id":      user_id,
        "candidate_id": candidate_id,
        "age_group":    current_user.get("age_group", "unknown"),
        "state":        current_user.get("state", "unknown"),
        "voted_at":     now_utc(),
    }
    await db.pm_votes.insert_one(vote_doc)

    return {
        "success": True,
        "message": "Your vote has been recorded. Thank you for participating!",
        "candidate_id": candidate_id,
    }


# ── GET /vote/pm/results ──────────────────────────────────────────────────────
@router.get("/pm/results")
async def get_pm_results():
    """
    Get PM election results broken down by:
    - Overall vote count per candidate
    - By age group
    - By state
    Public endpoint — no auth required.
    """
    db = get_database()
    total_votes = await db.pm_votes.count_documents({})

    # ── Overall counts ─────────────────────────────────────────────────────
    overall = {}
    for c in PM_CANDIDATES:
        count = await db.pm_votes.count_documents({"candidate_id": c["id"]})
        overall[c["id"]] = {
            "name":         c["name"],
            "party":        c["party"],
            "color":        c["color"],
            "votes":        count,
            "percentage":   round((count / total_votes * 100), 1) if total_votes > 0 else 0,
        }

    # ── By age group ───────────────────────────────────────────────────────
    by_age = {}
    for age in AGE_GROUPS:
        age_total = await db.pm_votes.count_documents({"age_group": age})
        by_age[age] = {}
        for c in PM_CANDIDATES:
            count = await db.pm_votes.count_documents(
                {"candidate_id": c["id"], "age_group": age}
            )
            by_age[age][c["id"]] = {
                "votes":      count,
                "percentage": round((count / age_total * 100), 1) if age_total > 0 else 0,
            }

    # ── By state ───────────────────────────────────────────────────────────
    by_state = {}
    for state in INDIAN_STATES:
        state_total = await db.pm_votes.count_documents({"state": state})
        if state_total == 0:
            by_state[state] = {"total": 0, "leading": None}
            continue
        leading_id, leading_count = None, 0
        for c in PM_CANDIDATES:
            count = await db.pm_votes.count_documents(
                {"candidate_id": c["id"], "state": state}
            )
            if count > leading_count:
                leading_count = count
                leading_id    = c["id"]
        by_state[state] = {
            "total":   state_total,
            "leading": leading_id,
            "leading_name": next(
                (c["name"] for c in PM_CANDIDATES if c["id"] == leading_id), None
            ),
        }

    return {
        "total_votes": total_votes,
        "candidates":  PM_CANDIDATES,
        "overall":     overall,
        "by_age":      by_age,
        "by_state":    by_state,
    }


# ── GET /vote/pm/my-vote ──────────────────────────────────────────────────────
@router.get("/pm/my-vote")
async def get_my_vote(current_user=Depends(get_current_user)):
    """Check if the current user has already voted."""
    db      = get_database()
    user_id = str(current_user["_id"])
    vote    = await db.pm_votes.find_one({"user_id": user_id})
    if vote:
        return {"has_voted": True, "candidate_id": vote["candidate_id"]}
    return {"has_voted": False, "candidate_id": None}


# ── GET /vote/pm/candidates ───────────────────────────────────────────────────
@router.get("/pm/candidates")
async def get_candidates():
    """Return the list of PM candidates. Public."""
    return {"candidates": PM_CANDIDATES}


# ── GET /vote/states ─────────────────────────────────────────────────────────
@router.get("/states")
async def get_states():
    """Return all Indian states and UTs."""
    return {"states": INDIAN_STATES}
