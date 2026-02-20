from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from api.db.database import get_db
from api.schemas.user import UserCreate, UserResponse, Token
from api.models.user import User

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")


@router.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if user already exists
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create new user
    # Note: For OAuth, you'll need to implement the OAuth flow
    import uuid
    new_user = User(
        id=str(uuid.uuid4()),
        email=user.email,
        name=user.name,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.post("/login", response_model=Token)
def login(email: str, password: str, db: Session = Depends(get_db)):
    """Login user - Placeholder for OAuth"""
    # Note: For OAuth (Google, Magic Link), you'll need to implement
    # the OAuth flow with NextAuth.js on the frontend
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="OAuth login is handled by NextAuth.js on the frontend"
    )


@router.get("/me", response_model=UserResponse)
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """Get current user profile"""
    # Note: You'll need to verify the JWT token here
    # For now, this is a placeholder
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Authentication is handled by NextAuth.js"
    )
