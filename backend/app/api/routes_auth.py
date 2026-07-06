from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import hash_password, verify_password, create_access_token
from app.models.core import User
from app.schemas.auth import LoginRequest, TokenResponse, RegisterRequest

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.username == payload.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    user = User(username=payload.username, hashed_password=hash_password(payload.password))
    db.add(user)
    db.commit()
    token = create_access_token(subject=user.username)
    return TokenResponse(access_token=token)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == payload.username).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
    token = create_access_token(subject=user.username)
    return TokenResponse(access_token=token)


@router.post("/logout")
def logout():
    # Stateless JWT: logout is a client-side token discard. Present for API completeness.
    return {"detail": "Logged out. Discard the client-side token."}
