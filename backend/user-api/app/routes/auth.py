# Define all the routes for user related api calls

from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db.config.conn import get_session
from models.users import User
from schemas.users import SignUpRequest, UserLoginRequest, SignUpResponse
from middleware.security import hash_password, verify_password
import uuid
from db.utils.user_sql_queries import get_user_by_email, get_user_by_session_token
from db.utils.auth_sql_queries import check_valid_session_token, create_session

SESSION_COOKIE_NAME = "session_token"


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=SignUpResponse, status_code=status.HTTP_201_CREATED)
async def signup(request: SignUpRequest, db: AsyncSession = Depends(get_session)):
    existing = await get_user_by_email(db, request.email)

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered",
        )

    hashed_password = hash_password(request.password)
    uuid_user_id = str(uuid.uuid4())

    new_user = User(
        user_id=uuid_user_id,
        username=request.username,
        email=request.email,
        password=hashed_password,
    )

    db.add(new_user)
    await db.flush()
    stmt = select(User).where(User.user_id == uuid_user_id)
    result = await db.execute(stmt)
    db_user = result.scalar_one_or_none()

    print(f"Verified in DB: {db_user.user_id}, {db_user.username}, {db_user.email}")

    return new_user

@router.post("/login")
async def login(
    request: UserLoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_session),
):
    user = await get_user_by_email(db, request.email)
    if not user or not verify_password(request.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid email or password",
        )
    
    session_token = await create_session(user.user_id, db)

    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=session_token,
        httponly=True,
        samesite="lax",
        max_age=3600 # 1 hour
    )

    return {"message": "Login Successful"}

@router.get("/authenticate", response_model=SignUpResponse)
async def fetch_user_data(request: Request, db: AsyncSession = Depends(get_session)):
    token = request.cookies.get(SESSION_COOKIE_NAME)

    if not token:
        raise  HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized",
        )
    
    valid_session = await check_valid_session_token(db, token)

    if not valid_session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid session",
        )

    user = await get_user_by_session_token(db, token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session"
        )

    return user