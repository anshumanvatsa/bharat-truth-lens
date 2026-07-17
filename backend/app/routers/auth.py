from datetime import datetime
import traceback

from fastapi import APIRouter, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Depends

from ..database import get_database
from ..schemas.auth import UserCreate, UserOut, Token
from ..utils.auth import hash_password, verify_password, create_access_token, get_current_user
from ..models import now_utc


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def signup(user_in: UserCreate):
    try:
        db = get_database()

        # Check for existing user
        try:
            existing = await db.users.find_one({"email": user_in.email.lower()})
        except Exception as db_err:
            print(f"[signup] MongoDB find_one error: {db_err}\n{traceback.format_exc()}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Database connection failed: {str(db_err)}"
            )

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        user_doc = {
            "_id":             user_in.email.lower(),
            "full_name":       user_in.full_name,
            "email":           user_in.email.lower(),
            "hashed_password": hash_password(user_in.password),
            "age_group":       user_in.age_group,
            "state":           user_in.state,
            "created_at":      now_utc(),
        }

        try:
            await db.users.insert_one(user_doc)
        except Exception as insert_err:
            print(f"[signup] MongoDB insert_one error: {insert_err}\n{traceback.format_exc()}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Database write failed: {str(insert_err)}"
            )

        # Build response — exclude hashed_password
        out_doc = {k: v for k, v in user_doc.items() if k != "hashed_password"}
        return UserOut.model_validate(out_doc)

    except HTTPException:
        raise  # re-raise FastAPI HTTP exceptions unchanged
    except Exception as e:
        print(f"[signup] Unexpected error: {e}\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Signup failed: {str(e)}"
        )


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        db = get_database()
        user = await db.users.find_one({"email": form_data.username.lower()})
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection failed: {str(e)}"
        )

    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    access_token = create_access_token(subject=str(user["_id"]))
    return Token(access_token=access_token)


@router.get("/me", response_model=UserOut)
async def read_me(current_user=Depends(get_current_user)):
    return UserOut.model_validate(current_user)
