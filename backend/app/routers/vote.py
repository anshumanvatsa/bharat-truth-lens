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

# ── CM Candidates per state ──────────────────────────────────────────────────
CM_CANDIDATES = {
    "Andhra Pradesh": [
        {"id": "ap_naidu",    "name": "N. Chandrababu Naidu", "party": "TDP",    "color": "#FFD700"},
        {"id": "ap_jagan",    "name": "Y.S. Jagan Reddy",    "party": "YSRCP",  "color": "#00B4D8"},
        {"id": "ap_pawan",    "name": "Pawan Kalyan",         "party": "JanaSena","color": "#FF6B35"},
    ],
    "Arunachal Pradesh": [
        {"id": "ar_pema",     "name": "Pema Khandu",          "party": "BJP",    "color": "#FF6B35"},
        {"id": "ar_nabam",    "name": "Nabam Tuki",           "party": "INC",    "color": "#19A7CE"},
    ],
    "Assam": [
        {"id": "as_himanta",  "name": "Himanta Biswa Sarma",  "party": "BJP",    "color": "#FF6B35"},
        {"id": "as_bharat",   "name": "Bharat Narah",         "party": "INC",    "color": "#19A7CE"},
        {"id": "as_badruddin","name": "Badruddin Ajmal",      "party": "AIUDF",  "color": "#22C55E"},
    ],
    "Bihar": [
        {"id": "br_nitish",   "name": "Nitish Kumar",         "party": "JD(U)",  "color": "#A78BFA"},
        {"id": "br_tejashwi", "name": "Tejashwi Yadav",       "party": "RJD",    "color": "#22C55E"},
        {"id": "br_chirag",   "name": "Chirag Paswan",        "party": "LJP",    "color": "#F59E0B"},
    ],
    "Chhattisgarh": [
        {"id": "cg_vishnu",   "name": "Vishnu Deo Sai",       "party": "BJP",    "color": "#FF6B35"},
        {"id": "cg_baghel",   "name": "Bhupesh Baghel",       "party": "INC",    "color": "#19A7CE"},
        {"id": "cg_tamradhwaj","name":"Tamradhwaj Sahu",      "party": "INC",    "color": "#00B4D8"},
    ],
    "Goa": [
        {"id": "ga_pramod",   "name": "Pramod Sawant",        "party": "BJP",    "color": "#FF6B35"},
        {"id": "ga_digambar", "name": "Digambar Kamat",       "party": "INC",    "color": "#19A7CE"},
        {"id": "ga_khaunte",  "name": "Babush Monserrate",    "party": "IND",    "color": "#A78BFA"},
    ],
    "Gujarat": [
        {"id": "gj_bhupendra","name": "Bhupendra Patel",      "party": "BJP",    "color": "#FF6B35"},
        {"id": "gj_hardik",   "name": "Hardik Patel",         "party": "INC",    "color": "#19A7CE"},
        {"id": "gj_isudan",   "name": "Isudan Gadhvi",        "party": "AAP",    "color": "#00B4D8"},
    ],
    "Haryana": [
        {"id": "hr_nayab",    "name": "Nayab Singh Saini",    "party": "BJP",    "color": "#FF6B35"},
        {"id": "hr_hooda",    "name": "Bhupinder Singh Hooda","party": "INC",    "color": "#19A7CE"},
        {"id": "hr_dushyant", "name": "Dushyant Chautala",    "party": "JJP",    "color": "#F59E0B"},
    ],
    "Himachal Pradesh": [
        {"id": "hp_sukhu",    "name": "Sukhvinder Singh Sukhu","party":"INC",    "color": "#19A7CE"},
        {"id": "hp_jai",      "name": "Jai Ram Thakur",        "party": "BJP",   "color": "#FF6B35"},
        {"id": "hp_mukesh",   "name": "Mukesh Agnihotri",      "party": "INC",   "color": "#00B4D8"},
    ],
    "Jharkhand": [
        {"id": "jh_hemant",   "name": "Hemant Soren",         "party": "JMM",    "color": "#22C55E"},
        {"id": "jh_babulal",  "name": "Babulal Marandi",      "party": "BJP",    "color": "#FF6B35"},
        {"id": "jh_champai",  "name": "Champai Soren",        "party": "BJP",    "color": "#FF8C00"},
    ],
    "Karnataka": [
        {"id": "ka_sidda",    "name": "Siddaramaiah",         "party": "INC",    "color": "#19A7CE"},
        {"id": "ka_dk",       "name": "D.K. Shivakumar",      "party": "INC",    "color": "#00B4D8"},
        {"id": "ka_yediyurappa","name":"B.S. Yediyurappa",    "party": "BJP",    "color": "#FF6B35"},
        {"id": "ka_bommai",   "name": "Basavaraj Bommai",     "party": "BJP",    "color": "#FF8C00"},
    ],
    "Kerala": [
        {"id": "kl_pinarayi", "name": "Pinarayi Vijayan",     "party": "CPI(M)", "color": "#FF0000"},
        {"id": "kl_shashi",   "name": "V.D. Satheesan",       "party": "INC",    "color": "#19A7CE"},
        {"id": "kl_suresh",   "name": "K. Suresh Gopi",       "party": "BJP",    "color": "#FF6B35"},
    ],
    "Madhya Pradesh": [
        {"id": "mp_mohan",    "name": "Mohan Yadav",          "party": "BJP",    "color": "#FF6B35"},
        {"id": "mp_kamal",    "name": "Kamal Nath",           "party": "INC",    "color": "#19A7CE"},
        {"id": "mp_jyotiraditya","name":"Jyotiraditya Scindia","party":"BJP",    "color": "#FF8C00"},
    ],
    "Maharashtra": [
        {"id": "mh_fadnavis", "name": "Devendra Fadnavis",    "party": "BJP",    "color": "#FF6B35"},
        {"id": "mh_shinde",   "name": "Eknath Shinde",        "party": "ShivSena","color":"#F59E0B"},
        {"id": "mh_uddhav",   "name": "Uddhav Thackeray",     "party": "SS(UBT)","color":"#22C55E"},
        {"id": "mh_sharad",   "name": "Sharad Pawar",         "party": "NCP",    "color": "#A78BFA"},
    ],
    "Manipur": [
        {"id": "mn_biren",    "name": "N. Biren Singh",       "party": "BJP",    "color": "#FF6B35"},
        {"id": "mn_okram",    "name": "Okram Ibobi Singh",    "party": "INC",    "color": "#19A7CE"},
    ],
    "Meghalaya": [
        {"id": "ml_sangma",   "name": "Conrad Sangma",        "party": "NPP",    "color": "#A78BFA"},
        {"id": "ml_mukul",    "name": "Mukul Sangma",         "party": "INC",    "color": "#19A7CE"},
    ],
    "Mizoram": [
        {"id": "mz_lalduhoma","name": "Lalduhoma",            "party": "ZPM",    "color": "#00B4D8"},
        {"id": "mz_zoramthanga","name":"Zoramthanga",         "party": "MNF",    "color": "#22C55E"},
    ],
    "Nagaland": [
        {"id": "nl_neiphiu",  "name": "Neiphiu Rio",          "party": "NDPP",   "color": "#F59E0B"},
        {"id": "nl_therie",   "name": "T.R. Zeliang",         "party": "NPF",    "color": "#A78BFA"},
    ],
    "Odisha": [
        {"id": "od_majhi",    "name": "Mohan Majhi",          "party": "BJP",    "color": "#FF6B35"},
        {"id": "od_naveen",   "name": "Naveen Patnaik",       "party": "BJD",    "color": "#19A7CE"},
        {"id": "od_bijayashri","name":"Bijayashri Routray",   "party": "INC",    "color": "#00B4D8"},
    ],
    "Punjab": [
        {"id": "pb_mann",     "name": "Bhagwant Mann",        "party": "AAP",    "color": "#00B4D8"},
        {"id": "pb_channi",   "name": "Charanjit Channi",     "party": "INC",    "color": "#19A7CE"},
        {"id": "pb_sukhbir",  "name": "Sukhbir Singh Badal",  "party": "SAD",    "color": "#F59E0B"},
    ],
    "Rajasthan": [
        {"id": "rj_bhajan",   "name": "Bhajan Lal Sharma",    "party": "BJP",    "color": "#FF6B35"},
        {"id": "rj_gehlot",   "name": "Ashok Gehlot",         "party": "INC",    "color": "#19A7CE"},
        {"id": "rj_pilot",    "name": "Sachin Pilot",         "party": "INC",    "color": "#00B4D8"},
    ],
    "Sikkim": [
        {"id": "sk_pst",      "name": "Prem Singh Tamang",    "party": "SKM",    "color": "#22C55E"},
        {"id": "sk_chamling", "name": "Pawan Kumar Chamling", "party": "SDF",    "color": "#F59E0B"},
    ],
    "Tamil Nadu": [
        {"id": "tn_stalin",   "name": "M.K. Stalin",          "party": "DMK",    "color": "#FF0000"},
        {"id": "tn_eps",      "name": "Edappadi Palaniswami", "party": "AIADMK", "color": "#19A7CE"},
        {"id": "tn_annamalai","name": "K. Annamalai",         "party": "BJP",    "color": "#FF6B35"},
    ],
    "Telangana": [
        {"id": "tg_revanth",  "name": "A. Revanth Reddy",     "party": "INC",    "color": "#19A7CE"},
        {"id": "tg_kcr",      "name": "K. Chandrashekar Rao", "party": "BRS",    "color": "#F59E0B"},
        {"id": "tg_owaisi",   "name": "Asaduddin Owaisi",     "party": "AIMIM",  "color": "#22C55E"},
    ],
    "Tripura": [
        {"id": "tr_manik",    "name": "Manik Saha",           "party": "BJP",    "color": "#FF6B35"},
        {"id": "tr_jishnu",   "name": "Jishnu Dev Varma",     "party": "BJP",    "color": "#FF8C00"},
        {"id": "tr_maniksar", "name": "Manik Sarkar",         "party": "CPI(M)", "color": "#FF0000"},
    ],
    "Uttar Pradesh": [
        {"id": "up_yogi",     "name": "Yogi Adityanath",      "party": "BJP",    "color": "#FF6B35"},
        {"id": "up_akhilesh", "name": "Akhilesh Yadav",       "party": "SP",     "color": "#FF0000"},
        {"id": "up_mayawati", "name": "Mayawati",             "party": "BSP",    "color": "#00B4D8"},
        {"id": "up_rahul",    "name": "Rahul Gandhi",         "party": "INC",    "color": "#19A7CE"},
    ],
    "Uttarakhand": [
        {"id": "uk_dhami",    "name": "Pushkar Singh Dhami",  "party": "BJP",    "color": "#FF6B35"},
        {"id": "uk_harish",   "name": "Harish Rawat",         "party": "INC",    "color": "#19A7CE"},
        {"id": "uk_pritam",   "name": "Pritam Singh",         "party": "INC",    "color": "#00B4D8"},
    ],
    "West Bengal": [
        {"id": "wb_mamata",   "name": "Mamata Banerjee",      "party": "TMC",    "color": "#22C55E"},
        {"id": "wb_suvendu",  "name": "Suvendu Adhikari",     "party": "BJP",    "color": "#FF6B35"},
        {"id": "wb_adhir",    "name": "Adhir Ranjan Chowdhury","party":"INC",    "color": "#19A7CE"},
    ],
    "Delhi": [
        {"id": "dl_kejriwal", "name": "Arvind Kejriwal",      "party": "AAP",    "color": "#00B4D8"},
        {"id": "dl_rekha",    "name": "Rekha Gupta",          "party": "BJP",    "color": "#FF6B35"},
        {"id": "dl_atishi",   "name": "Atishi Marlena",       "party": "AAP",    "color": "#00C4E0"},
    ],
    "Jammu & Kashmir": [
        {"id": "jk_omar",     "name": "Omar Abdullah",        "party": "NC",     "color": "#19A7CE"},
        {"id": "jk_mehbooba", "name": "Mehbooba Mufti",       "party": "PDP",    "color": "#22C55E"},
        {"id": "jk_raina",    "name": "Ravinder Raina",       "party": "BJP",    "color": "#FF6B35"},
    ],
    "Puducherry": [
        {"id": "py_rangasamy","name": "N. Rangasamy",         "party": "AINRC",  "color": "#F59E0B"},
        {"id": "py_namassivayam","name":"A. Namassivayam",    "party": "INC",    "color": "#19A7CE"},
    ],
}

# Fallback candidates for states without specific data
DEFAULT_CM_CANDIDATES = [
    {"id": "default_bjp", "name": "BJP Candidate",  "party": "BJP", "color": "#FF6B35"},
    {"id": "default_inc", "name": "INC Candidate",  "party": "INC", "color": "#19A7CE"},
    {"id": "default_oth", "name": "Regional Party", "party": "Regional", "color": "#A78BFA"},
]


def get_cm_candidates_for_state(state: str):
    return CM_CANDIDATES.get(state, DEFAULT_CM_CANDIDATES)


# ── POST /vote/pm ─────────────────────────────────────────────────────────────
@router.post("/pm")
async def cast_pm_vote(body: dict, current_user=Depends(get_current_user)):
    """Cast one vote for PM candidate. One user = one vote."""
    db           = get_database()
    user_id      = str(current_user["_id"])
    candidate_id = body.get("candidate_id", "")

    valid_ids = [c["id"] for c in PM_CANDIDATES]
    if candidate_id not in valid_ids:
        raise HTTPException(status_code=400, detail=f"Invalid candidate. Choose from: {valid_ids}")

    existing = await db.pm_votes.find_one({"user_id": user_id})
    if existing:
        raise HTTPException(status_code=409, detail="You have already cast your PM vote. One person, one vote.")

    await db.pm_votes.insert_one({
        "user_id":      user_id,
        "candidate_id": candidate_id,
        "age_group":    current_user.get("age_group", "unknown"),
        "state":        current_user.get("state", "unknown"),
        "voted_at":     now_utc(),
    })
    return {"success": True, "message": "Your PM vote has been recorded!", "candidate_id": candidate_id}


# ── GET /vote/pm/results ──────────────────────────────────────────────────────
@router.get("/pm/results")
async def get_pm_results():
    db = get_database()
    total_votes = await db.pm_votes.count_documents({})

    overall = {}
    for c in PM_CANDIDATES:
        count = await db.pm_votes.count_documents({"candidate_id": c["id"]})
        overall[c["id"]] = {
            "name":       c["name"], "party": c["party"], "color": c["color"],
            "votes":      count,
            "percentage": round((count / total_votes * 100), 1) if total_votes > 0 else 0,
        }

    by_age = {}
    for age in AGE_GROUPS:
        age_total = await db.pm_votes.count_documents({"age_group": age})
        by_age[age] = {}
        for c in PM_CANDIDATES:
            count = await db.pm_votes.count_documents({"candidate_id": c["id"], "age_group": age})
            by_age[age][c["id"]] = {
                "votes": count,
                "percentage": round((count / age_total * 100), 1) if age_total > 0 else 0,
            }

    by_state = {}
    for state in INDIAN_STATES:
        state_total = await db.pm_votes.count_documents({"state": state})
        if state_total == 0:
            by_state[state] = {"total": 0, "leading": None}
            continue
        leading_id, leading_count = None, 0
        for c in PM_CANDIDATES:
            count = await db.pm_votes.count_documents({"candidate_id": c["id"], "state": state})
            if count > leading_count:
                leading_count = count
                leading_id = c["id"]
        by_state[state] = {
            "total": state_total, "leading": leading_id,
            "leading_name": next((c["name"] for c in PM_CANDIDATES if c["id"] == leading_id), None),
        }

    return {"total_votes": total_votes, "candidates": PM_CANDIDATES, "overall": overall, "by_age": by_age, "by_state": by_state}


# ── GET /vote/pm/my-vote ──────────────────────────────────────────────────────
@router.get("/pm/my-vote")
async def get_my_pm_vote(current_user=Depends(get_current_user)):
    db = get_database()
    vote = await db.pm_votes.find_one({"user_id": str(current_user["_id"])})
    if vote:
        return {"has_voted": True, "candidate_id": vote["candidate_id"]}
    return {"has_voted": False, "candidate_id": None}


# ── GET /vote/pm/candidates ───────────────────────────────────────────────────
@router.get("/pm/candidates")
async def get_pm_candidates():
    return {"candidates": PM_CANDIDATES}


# ── GET /vote/states ─────────────────────────────────────────────────────────
@router.get("/states")
async def get_states():
    return {"states": INDIAN_STATES}


# ══════════════════════════════════════════════════════════════════════════════
# CM VOTING — State-wise Chief Minister Poll
# ══════════════════════════════════════════════════════════════════════════════

# ── GET /vote/cm/candidates ───────────────────────────────────────────────────
@router.get("/cm/candidates")
async def get_cm_candidates(current_user=Depends(get_current_user)):
    """Return CM candidates for the user's registered state."""
    state = current_user.get("state", "")
    candidates = get_cm_candidates_for_state(state)
    return {"state": state, "candidates": candidates}


# ── GET /vote/cm/my-vote ─────────────────────────────────────────────────────
@router.get("/cm/my-vote")
async def get_my_cm_vote(current_user=Depends(get_current_user)):
    db = get_database()
    vote = await db.cm_votes.find_one({"user_id": str(current_user["_id"])})
    if vote:
        return {"has_voted": True, "candidate_id": vote["candidate_id"], "state": vote.get("state")}
    return {"has_voted": False, "candidate_id": None}


# ── POST /vote/cm ─────────────────────────────────────────────────────────────
@router.post("/cm")
async def cast_cm_vote(body: dict, current_user=Depends(get_current_user)):
    """Cast one CM vote for the user's registered state. One vote per person."""
    db           = get_database()
    user_id      = str(current_user["_id"])
    candidate_id = body.get("candidate_id", "")
    state        = current_user.get("state", "")

    candidates = get_cm_candidates_for_state(state)
    valid_ids  = [c["id"] for c in candidates]

    if candidate_id not in valid_ids:
        raise HTTPException(status_code=400, detail=f"Invalid CM candidate for {state}")

    existing = await db.cm_votes.find_one({"user_id": user_id})
    if existing:
        raise HTTPException(status_code=409, detail="You have already cast your CM vote. One person, one vote.")

    await db.cm_votes.insert_one({
        "user_id":      user_id,
        "candidate_id": candidate_id,
        "state":        state,
        "age_group":    current_user.get("age_group", "unknown"),
        "voted_at":     now_utc(),
    })
    return {"success": True, "message": f"Your CM vote for {state} has been recorded!", "candidate_id": candidate_id}


# ── GET /vote/cm/results ──────────────────────────────────────────────────────
@router.get("/cm/results")
async def get_cm_results(state: str):
    """Get CM results for a specific state. Public endpoint."""
    db = get_database()
    candidates = get_cm_candidates_for_state(state)
    total_votes = await db.cm_votes.count_documents({"state": state})

    overall = {}
    for c in candidates:
        count = await db.cm_votes.count_documents({"candidate_id": c["id"], "state": state})
        overall[c["id"]] = {
            "name":       c["name"], "party": c["party"], "color": c["color"],
            "votes":      count,
            "percentage": round((count / total_votes * 100), 1) if total_votes > 0 else 0,
        }

    by_age = {}
    for age in AGE_GROUPS:
        age_total = await db.cm_votes.count_documents({"state": state, "age_group": age})
        by_age[age] = {}
        for c in candidates:
            count = await db.cm_votes.count_documents({"candidate_id": c["id"], "state": state, "age_group": age})
            by_age[age][c["id"]] = {
                "votes": count,
                "percentage": round((count / age_total * 100), 1) if age_total > 0 else 0,
            }

    return {
        "state": state,
        "total_votes": total_votes,
        "candidates":  candidates,
        "overall":     overall,
        "by_age":      by_age,
    }
