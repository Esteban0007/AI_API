#!/usr/bin/env python
"""
Admin script to list all users, their plans, and API keys.
Usage: python scripts/list_users.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.session import SessionLocal, init_db
from app.models.user import User, APIKey
from datetime import datetime


def list_all_users():
    """List all users with their details."""

    # Initialize database
    init_db()

    db = SessionLocal()
    try:
        users = db.query(User).all()

        if not users:
            print("\n📭 No users found in database.")
            print("\n💡 Create a user with:")
            print(
                "   python scripts/create_user.py --email user@example.com --name 'John Doe'\n"
            )
            return

        print("\n" + "=" * 80)
        print(f"👥 USERS ({len(users)} total)")
        print("=" * 80 + "\n")

        for user in users:
            # Get API keys for this user
            api_keys = db.query(APIKey).filter(APIKey.user_id == user.id).all()
            active_keys = [k for k in api_keys if k.is_active]

            print(f"📧 {user.email}")
            print(f"   👤 Name: {user.name}")
            if user.company:
                print(f"   🏢 Company: {user.company}")
            print(
                f"   📦 Plan: {user.plan.display_name} (${user.plan.price_monthly}/month)"
            )
            print(f"   🆔 User ID: {user.id}")
            print(f"   ✅ Status: {'Active' if user.is_active else 'Inactive'}")
            print(f"   💳 Subscription: {user.subscription_status}")
            print(f"   📅 Created: {user.created_at.strftime('%Y-%m-%d %H:%M')}")

            if active_keys:
                print(f"   🔑 API Keys ({len(active_keys)}/{user.plan.max_api_keys}):")
                for key in active_keys:
                    last_used = (
                        key.last_used_at.strftime("%Y-%m-%d %H:%M")
                        if key.last_used_at
                        else "Never"
                    )
                    print(
                        f"      - {key.name}: {key.key_prefix} (used {key.total_requests} times, last: {last_used})"
                    )
            else:
                print(f"   🔑 No active API keys")

            print()

        print("=" * 80 + "\n")

    except Exception as e:
        print(f"❌ Error listing users: {str(e)}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    list_all_users()
