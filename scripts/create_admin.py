#!/usr/bin/env python
"""
Create an admin user with unlimited access (no rate limits).
Usage: python scripts/create_admin.py --email admin@readyapi.net --name "Administrator"
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import argparse
from app.db.session import SessionLocal, init_db
from app.models.user import User, APIKey, Plan
from app.core.security import create_api_key
from datetime import datetime


def create_admin_user(email: str, name: str, company: str = None):
    """Create a new admin user with unlimited access."""
    
    # Initialize database
    init_db()
    
    db = SessionLocal()
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            print(f"❌ User with email {email} already exists!")
            print(f"   User ID: {existing_user.id}")
            print(f"   Is Admin: {existing_user.is_admin}")
            return
        
        # Get enterprise plan (unlimited features)
        enterprise_plan = db.query(Plan).filter(Plan.name == "enterprise").first()
        if not enterprise_plan:
            print("❌ Enterprise plan not found!")
            return
        
        # Create admin user
        user = User(
            email=email,
            name=name,
            company=company,
            plan_id=enterprise_plan.id,
            is_active=True,
            is_verified=True,
            is_admin=True,  # ← Key field: Admin user
            subscription_status="active"
        )
        
        db.add(user)
        db.flush()  # Get user.id
        
        # Generate API key
        api_key_value = create_api_key()
        key_prefix = api_key_value[:12] + "..."
        
        api_key = APIKey(
            key=api_key_value,
            key_prefix=key_prefix,
            name="Admin API Key (Unlimited)",
            user_id=user.id,
            is_active=True
        )
        
        db.add(api_key)
        db.commit()
        
        # Display success message
        print("\n" + "="*60)
        print("✅ ADMIN USER CREATED SUCCESSFULLY")
        print("="*60)
        print(f"\n📧 Email: {user.email}")
        print(f"👤 Name: {user.name}")
        if company:
            print(f"🏢 Company: {company}")
        print(f"📦 Plan: Enterprise (UNLIMITED)")
        print(f"⭐ Status: ADMIN USER (no rate limits)")
        print(f"🆔 User ID: {user.id}")
        print(f"\n🔑 API KEY (save this - won't be shown again):")
        print(f"\n   {api_key_value}")
        print(f"\n🚀 Capabilities:")
        print(f"   ✅ Unlimited searches per day")
        print(f"   ✅ Unlimited searches per month")
        print(f"   ✅ Unlimited documents")
        print(f"   ✅ Unlimited API keys")
        print(f"   ✅ No rate limiting")
        print(f"   ✅ Full access to all features")
        print("\n" + "="*60)
        print("\n💡 Test with admin user:")
        print(f'\ncurl -X POST "http://localhost:8000/api/v1/search/query" \\')
        print(f'  -H "Content-Type: application/json" \\')
        print(f'  -H "X-API-Key: {api_key_value}" \\')
        print(f'  -d \'{{"query": "test", "top_k": 5}}\'')
        print("\n")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating admin user: {str(e)}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create an admin user with unlimited access")
    parser.add_argument("--email", required=True, help="Admin email address")
    parser.add_argument("--name", required=True, help="Admin full name")
    parser.add_argument("--company", help="Company name (optional)")
    
    args = parser.parse_args()
    
    create_admin_user(
        email=args.email,
        name=args.name,
        company=args.company
    )
