"""
Database models for user management and API keys.
Designed to be payment-gateway ready (Stripe, etc.).
"""

from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    Boolean,
    DateTime,
    ForeignKey,
    JSON,
    Enum,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()


class PlanType(str, enum.Enum):
    """Subscription plan types."""

    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class Plan(Base):
    """Subscription plans with limits and pricing."""

    __tablename__ = "plans"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)  # "free", "pro", "enterprise"
    display_name = Column(String, nullable=False)  # "Free Plan", "Pro Plan"
    price_monthly = Column(Float, default=0.0)  # Monthly price in USD
    price_yearly = Column(Float, default=0.0)  # Yearly price in USD

    # Limits
    searches_per_day = Column(Integer, default=100)
    searches_per_month = Column(Integer, default=1000)
    max_documents = Column(Integer, default=10000)
    max_api_keys = Column(Integer, default=1)

    # Features
    features = Column(JSON, default=list)  # ["feature1", "feature2"]

    # Stripe integration (for future)
    stripe_price_id_monthly = Column(String, nullable=True)
    stripe_price_id_yearly = Column(String, nullable=True)

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    users = relationship("User", back_populates="plan")


class User(Base):
    """User/Organization account."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    company = Column(String, nullable=True)

    # Authentication (for future web dashboard)
    hashed_password = Column(String, nullable=True)  # Optional for now

    # Plan & Billing
    plan_id = Column(Integer, ForeignKey("plans.id"), default=1)  # Default: Free
    plan = relationship("Plan", back_populates="users")

    # Stripe integration
    stripe_customer_id = Column(String, nullable=True, index=True)
    stripe_subscription_id = Column(String, nullable=True)
    subscription_status = Column(String, default="active")  # active, canceled, past_due
    subscription_expires_at = Column(DateTime, nullable=True)

    # Account status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    # Relationships
    api_keys = relationship(
        "APIKey", back_populates="user", cascade="all, delete-orphan"
    )
    usage_records = relationship(
        "Usage", back_populates="user", cascade="all, delete-orphan"
    )


class APIKey(Base):
    """API Keys for authentication."""

    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True, nullable=False)  # The actual API key
    key_prefix = Column(String, index=True)  # First 8 chars for display: "rapi_xk8..."
    name = Column(String, nullable=False)  # User-friendly name: "Production App"

    # Ownership
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="api_keys")

    # Status
    is_active = Column(Boolean, default=True)

    # Usage tracking
    last_used_at = Column(DateTime, nullable=True)
    total_requests = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)  # Optional expiration

    # IP restrictions (optional security)
    allowed_ips = Column(JSON, default=list)  # ["192.168.1.1", "10.0.0.0/24"]


class Usage(Base):
    """Daily usage tracking for rate limiting and billing."""

    __tablename__ = "usage"

    id = Column(Integer, primary_key=True, index=True)

    # User reference
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="usage_records")

    # Date tracking
    date = Column(DateTime, index=True, nullable=False)  # Daily granularity

    # Counters
    searches_count = Column(Integer, default=0)
    documents_indexed = Column(Integer, default=0)

    # For billing calculation
    billable_searches = Column(Integer, default=0)  # Searches beyond free tier

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class PaymentHistory(Base):
    """Payment transaction history (for Stripe webhook integration)."""

    __tablename__ = "payment_history"

    id = Column(Integer, primary_key=True, index=True)

    # User reference
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Stripe data
    stripe_payment_intent_id = Column(String, unique=True, index=True)
    stripe_invoice_id = Column(String, nullable=True)

    # Payment details
    amount = Column(Float, nullable=False)  # Amount in USD
    currency = Column(String, default="usd")
    status = Column(String)  # succeeded, failed, pending

    # Metadata
    description = Column(String, nullable=True)
    receipt_url = Column(String, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    paid_at = Column(DateTime, nullable=True)
