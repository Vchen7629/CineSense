# Define all the routes for user related api calls

from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session

from ..db.dbConn import get_db
from ..models.users import User
from ..schemas.users import UserCreate, UserLogin, UserRead
from ..security import hash_password,verify_password
from ..middleware.auth import (
    create_session,
    SESSION_COOKIE_NAME,
    get_current_user,
)

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/signup", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def signup(user_in: UserCreate, db: Session = Depends(get_db)):

    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered",
        )

    hashed = hash_password(user_in.password)
    new_user = User(
        email=user_in.email,
        full_name=user_in.full_name,
        hashed_password=hashed,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login")
def login(
    user_in: UserLogin,
    response:  Response,
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.email == user_in.email).first()
    if not user or not verify_password(user_in.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid email or password",
        )
    
    token = create_session(db, user.id)
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=token,
        httponly=True,
        samesite="lax",
    )
    return {"message": "Login Successful"}

@router.get("/me", response_model=UserRead)
def readme(current_user: User = Depends(get_current_user)):

    return current_user