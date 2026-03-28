from sqlalchemy import Column, String, Integer, Boolean, DateTime, Enum
from sqlalchemy.sql import func
from api.db.database import Base
import enum


class SubscriptionTier(str, enum.Enum):
    """Subscription tiers"""
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class User(Base):
    """User model"""
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String)
    linkedin_url = Column(String)
    company_url = Column(String)
    hashed_password = Column(String)
    subscription_tier = Column(Enum(SubscriptionTier), default=SubscriptionTier.FREE)
    credits_remaining = Column(Integer, default=5)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<User {self.email}>"
