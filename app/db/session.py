"""
Database connection and session management.
Supports SQLite (default) and PostgreSQL (production).
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from pathlib import Path
import os

from ..core.config import get_settings
from ..models.user import Base

settings = get_settings()

# Database URL
# For SQLite: sqlite:///./data/app.db
# For PostgreSQL: postgresql://user:password@host:port/dbname
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/app.db")

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    echo=settings.DEBUG,  # Log SQL queries in debug mode
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initialize database tables."""
    # Create data directory if using SQLite
    if "sqlite" in DATABASE_URL:
        db_path = Path(DATABASE_URL.replace("sqlite:///", ""))
        db_path.parent.mkdir(parents=True, exist_ok=True)

    # Create all tables
    Base.metadata.create_all(bind=engine)

    # Initialize default plans
    _create_default_plans()


def _create_default_plans():
    """Create default subscription plans."""
    from ..models.user import Plan

    db = SessionLocal()
    try:
        # Check if plans already exist
        if db.query(Plan).first():
            return

        # Free Plan
        free_plan = Plan(
            name="free",
            display_name="Free Plan",
            price_monthly=0.0,
            price_yearly=0.0,
            searches_per_day=100,
            searches_per_month=1000,
            max_documents=10000,
            max_api_keys=1,
            features=["Basic semantic search", "1 API key", "Community support"],
        )

        # Pro Plan
        pro_plan = Plan(
            name="pro",
            display_name="Pro Plan",
            price_monthly=29.0,
            price_yearly=290.0,  # 2 months free
            searches_per_day=10000,
            searches_per_month=200000,
            max_documents=1000000,
            max_api_keys=10,
            features=[
                "Advanced semantic search",
                "10 API keys",
                "Priority support",
                "Custom embeddings",
                "Analytics dashboard",
            ],
        )

        # Enterprise Plan
        enterprise_plan = Plan(
            name="enterprise",
            display_name="Enterprise Plan",
            price_monthly=299.0,
            price_yearly=2990.0,
            searches_per_day=100000,
            searches_per_month=-1,  # Unlimited
            max_documents=-1,  # Unlimited
            max_api_keys=-1,  # Unlimited
            features=[
                "Unlimited searches",
                "Unlimited documents",
                "Unlimited API keys",
                "Dedicated support",
                "Custom deployment",
                "SLA guarantee",
                "Advanced analytics",
            ],
        )

        db.add_all([free_plan, pro_plan, enterprise_plan])
        db.commit()

    finally:
        db.close()


@contextmanager
def get_db() -> Session:
    """
    Database session context manager.

    Usage:
        with get_db() as db:
            user = db.query(User).first()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db_session():
    """
    Get database session for FastAPI dependency injection.

    Usage:
        @app.get("/")
        def endpoint(db: Session = Depends(get_db_session)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
