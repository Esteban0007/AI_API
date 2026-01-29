#!/usr/bin/env python
"""
Initialize the database with tables and default plans.
Run this once before starting the application.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.session import init_db


if __name__ == "__main__":
    print("🔧 Initializing database...")
    print("=" * 50)

    try:
        init_db()

        print("\n✅ Database initialized successfully!")
        print("\n📋 Default plans created:")
        print("   1. Free Plan - $0/month")
        print("   2. Pro Plan - $29/month")
        print("   3. Enterprise Plan - $299/month")
        print("\n💡 Next steps:")
        print("   1. Create a user:")
        print(
            "      python scripts/create_user.py --email user@example.com --name 'John Doe'"
        )
        print("\n   2. Start the server:")
        print("      python scripts/run_server.py")
        print("\n   3. List all users:")
        print("      python scripts/list_users.py")
        print()

    except Exception as e:
        print(f"\n❌ Error initializing database: {str(e)}")
        raise
