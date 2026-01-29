#!/usr/bin/env python
"""
Admin script to create a new user and generate their first API key.
Usage: python scripts/create_user.py --email user@example.com --name "John Doe" --plan free
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import argparse
from app.db.session import SessionLocal, init_db
from app.models.user import User, APIKey, Plan
from app.core.security import create_api_key
from datetime import datetime


def create_user_with_api_key(
    email: str, name: str, plan_name: str = "free", company: str = None
):
    """Create a new user and generate their first API key."""

    # Initialize database
    init_db()

    db = SessionLocal()
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            print(f"❌ User with email {email} already exists!")
            print(f"   User ID: {existing_user.id}")
            print(f"   Plan: {existing_user.plan.name}")
            return

        # Get plan
        plan = db.query(Plan).filter(Plan.name == plan_name).first()
        if not plan:
            print(f"❌ Plan '{plan_name}' not found!")
            print("   Available plans: free, pro, enterprise")
            return

        # Create user
        user = User(
            email=email,
            name=name,
            company=company,
            plan_id=plan.id,
            is_active=True,
            is_verified=True,
            subscription_status="active",
        )

        db.add(user)
        db.flush()  # Get user.id

        # Generate API key
        api_key_value = create_api_key()
        key_prefix = api_key_value[:12] + "..."

        api_key = APIKey(
            key=api_key_value,
            key_prefix=key_prefix,
            name="Default API Key",
            user_id=user.id,
            is_active=True,
        )

        db.add(api_key)
        db.commit()

        # Display success message
        print("\n" + "=" * 60)
        print("✅ USER CREATED SUCCESSFULLY")
        print("=" * 60)
        print(f"\n📧 Email: {user.email}")
        print(f"👤 Name: {user.name}")
        if company:
            print(f"🏢 Company: {company}")
        print(f"📦 Plan: {plan.display_name}")
        print(f"🆔 User ID: {user.id}")
        print(f"\n🔑 API KEY (save this - won't be shown again):")
        print(f"\n   {api_key_value}")
        print(f"\n📊 Plan Limits:")
        print(f"   - Searches per day: {plan.searches_per_day}")
        print(f"   - Searches per month: {plan.searches_per_month}")
        print(f"   - Max documents: {plan.max_documents}")
        print(f"   - Max API keys: {plan.max_api_keys}")
        print("\n" + "=" * 60)
        print("\n💡 Test the API:")
        print(f'\ncurl -X POST "http://localhost:8000/api/v1/search/query" \\')
        print(f'  -H "Content-Type: application/json" \\')
        print(f'  -H "X-API-Key: {api_key_value}" \\')
        print(f'  -d \'{{"query": "test", "top_k": 5}}\'')
        print("\n")

    except Exception as e:
        db.rollback()
        print(f"❌ Error creating user: {str(e)}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a new user with API key")
    parser.add_argument("--email", required=True, help="User email address")
    parser.add_argument("--name", required=True, help="User full name")
    parser.add_argument("--company", help="Company name (optional)")
    parser.add_argument(
        "--plan",
        default="free",
        choices=["free", "pro", "enterprise"],
        help="Subscription plan (default: free)",
    )

    args = parser.parse_args()

    create_user_with_api_key(
        email=args.email, name=args.name, plan_name=args.plan, company=args.company
    )
