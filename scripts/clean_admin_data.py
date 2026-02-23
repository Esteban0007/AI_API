#!/usr/bin/env python3
"""
Clean ADMIN user data - removes all documents and vectors for ADMIN user
while keeping the user and API key intact.

Usage: python scripts/clean_admin_data.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import shutil
import os
from app.db.session import SessionLocal, init_db
from app.models.user import User


def clean_admin_data():
    """Remove all data for ADMIN user."""

    # Initialize database
    init_db()

    db = SessionLocal()
    try:
        # Find ADMIN user
        admin_user = db.query(User).filter(User.email == "admin@example.com").first()

        if not admin_user:
            print("❌ ADMIN user not found!")
            print("   Looking for users in database...")
            users = db.query(User).all()
            for user in users:
                print(f"   - {user.email} (ID: {user.id})")
            return

        print(f"✅ Found ADMIN user: {admin_user.email} (ID: {admin_user.id})")
        print(f"   Plan: {admin_user.plan.name}")

        # Clean Chroma database (vector store)
        print("\n🧹 Cleaning Chroma database...")
        chroma_path = Path("./data/chroma_db")
        if chroma_path.exists():
            # Backup first
            backup_path = Path("./data/chroma_db.backup")
            if backup_path.exists():
                shutil.rmtree(backup_path)
            shutil.copytree(chroma_path, backup_path)
            print(f"   ✅ Backed up to: {backup_path}")

            # Remove collections
            shutil.rmtree(chroma_path)
            print(f"   ✅ Removed: {chroma_path}")

        print("\n✨ ADMIN data cleaned successfully!")
        print(f"   User ID: {admin_user.id}")
        print(f"   Email: {admin_user.email}")
        print(f"   Status: Ready for new documents")
        print(f"\n💡 Next step: Upload new documents with your API key")

    except Exception as e:
        print(f"❌ Error cleaning ADMIN data: {str(e)}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    clean_admin_data()
