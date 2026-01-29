#!/usr/bin/env python
"""
Generate a secure admin API key and show how to use it.
Usage: python scripts/generate_admin_key.py
"""
import secrets
import sys


def generate_admin_key():
    """Generate a secure admin API key."""
    # Generate 40 random characters (more than enough entropy)
    admin_key = "rapi_" + secrets.token_urlsafe(40)

    print("\n" + "=" * 70)
    print("🔐 ADMIN API KEY GENERATOR")
    print("=" * 70)
    print("\n🔑 Your secure admin API key:")
    print(f"\n   {admin_key}")
    print("\n📝 Add this to your .env file:")
    print(f"\n   ADMIN_API_KEY={admin_key}")
    print("\n🛡️  Security Tips:")
    print("   ✓ Keep this key SECRET (only you should have it)")
    print("   ✓ Don't commit it to version control")
    print("   ✓ Don't share it with anyone")
    print("   ✓ Store it in .env (which is in .gitignore)")
    print("\n🚀 Use it with:")
    print(f'\n   curl -H "X-API-Key: {admin_key}" https://readyapi.net/api/v1/...')
    print("\n⚡ Benefits:")
    print("   • Unlimited searches (no rate limits)")
    print("   • No daily/monthly limits")
    print("   • Instant access to everything")
    print("   • No billing involved")
    print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    generate_admin_key()
