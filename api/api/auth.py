from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from api.db.database import get_db
from api.schemas.user import UserCreate, UserResponse, Token, OAuthUserSync
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


@router.post("/sync-user", response_model=UserResponse)
def sync_oauth_user(
    user_data: OAuthUserSync,
    db: Session = Depends(get_db)
):
    """
    Sync user from NextAuth OAuth callback.
    Creates user if doesn't exist, updates if exists.
    Idempotent operation - safe to call multiple times.
    """
    # Check if user exists
    db_user = db.query(User).filter(User.email == user_data.email).first()

    if db_user:
        # Update existing user (preserve subscription/credits)
        if user_data.name and db_user.name != user_data.name:
            db_user.name = user_data.name
        # Always update on OAuth sync
        db_user.is_active = True
        db.commit()
        db.refresh(db_user)
        return db_user
    else:
        # Create new user
        import uuid
        new_user = User(
            id=str(uuid.uuid4()),
            email=user_data.email,
            name=user_data.name or user_data.email.split("@")[0],
            subscription_tier="free",  # Default to free tier
            credits_remaining=5,  # Free tier gets 5 credits
            is_active=True,
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
