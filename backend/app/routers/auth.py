from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from ..database import get_database
from ..schemas.auth import UserCreate, UserOut, Token
from ..utils.auth import hash_password, verify_password, create_access_token, get_current_user
from ..models import now_utc


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def signup(user_in: UserCreate):
    db = get_database()
    existing = await db.users.find_one({"email": user_in.email})
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    user_doc = {
        "_id": user_in.email.lower(),
        "full_name": user_in.full_name,
        "email": user_in.email.lower(),
        "hashed_password": hash_password(user_in.password),
        "age_group": user_in.age_group,
        "state": user_in.state,
        "created_at": now_utc(),
    }
    await db.users.insert_one(user_doc)
    return UserOut(**user_doc)


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    db = get_database()
    user = await db.users.find_one({"email": form_data.username.lower()})
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")

    access_token = create_access_token(subject=str(user["_id"]))
    return Token(access_token=access_token)


@router.get("/me", response_model=UserOut)
async def read_me(current_user=Depends(get_current_user)):
    return UserOut(**current_user)

