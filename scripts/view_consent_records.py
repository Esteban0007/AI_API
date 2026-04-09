#!/usr/bin/env python
"""
Script to view consent records (GDPR audit trail).
Usage: python scripts/view_consent_records.py [email]
"""

import sqlite3
import sys
from datetime import datetime
from pathlib import Path

DB_PATH = "./data/users.db"


def view_all_consents():
    """Display all consent records."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute(
        """
        SELECT 
            id,
            user_id,
            user_email,
            consent_status,
            consent_type,
            privacy_version,
            consent_method,
            consent_ip,
            user_agent,
            consent_timestamp
        FROM consent_records
        ORDER BY consent_timestamp DESC
    """
    )

    records = c.fetchall()
    conn.close()

    if not records:
        print("📋 No consent records found.")
        return

    print("\n" + "=" * 150)
    print("📋 ALL CONSENT RECORDS (GDPR Audit Trail)")
    print("=" * 150)

    for record in records:
        print(f"\n📌 Record ID: {record['id']}")
        print(f"   User: {record['user_email']} (ID: {record['user_id']})")
        print(
            f"   Status: {'✅ ACCEPTED' if record['consent_status'] else '❌ WITHDRAWN'}"
        )
        print(f"   Type: {record['consent_type']}")
        print(f"   Policy Version: {record['privacy_version']}")
        print(f"   Method: {record['consent_method']}")
        print(f"   IP: {record['consent_ip']}")
        print(f"   Timestamp: {record['consent_timestamp']} (UTC)")
        print(
            f"   User-Agent: {record['user_agent'][:80]}..."
            if len(record["user_agent"] or "") > 80
            else f"   User-Agent: {record['user_agent']}"
        )

    print("\n" + "=" * 150 + "\n")


def view_user_consents(email: str):
    """Display consent records for specific user."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute(
        """
        SELECT 
            id,
            user_id,
            user_email,
            consent_status,
            consent_type,
            privacy_version,
            consent_method,
            consent_ip,
            user_agent,
            consent_timestamp
        FROM consent_records
        WHERE user_email = ?
        ORDER BY consent_timestamp DESC
    """,
        (email,),
    )

    records = c.fetchall()
    conn.close()

    if not records:
        print(f"📋 No consent records found for {email}")
        return

    print("\n" + "=" * 150)
    print(f"📋 CONSENT RECORDS FOR: {email}")
    print("=" * 150)

    for record in records:
        print(f"\n📌 Record ID: {record['id']}")
        print(
            f"   Status: {'✅ ACCEPTED' if record['consent_status'] else '❌ WITHDRAWN'}"
        )
        print(f"   Type: {record['consent_type']}")
        print(f"   Policy Version: {record['privacy_version']}")
        print(f"   Method: {record['consent_method']}")
        print(f"   IP: {record['consent_ip']}")
        print(f"   Timestamp: {record['consent_timestamp']} (UTC)")
        print(
            f"   User-Agent: {record['user_agent'][:80]}..."
            if len(record["user_agent"] or "") > 80
            else f"   User-Agent: {record['user_agent']}"
        )

    print("\n" + "=" * 150 + "\n")


def get_latest_consent(email: str) -> dict:
    """Get the most recent consent for a user."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute(
        """
        SELECT 
            privacy_version,
            consent_timestamp,
            consent_status
        FROM consent_records
        WHERE user_email = ? AND consent_status = 1
        ORDER BY consent_timestamp DESC
        LIMIT 1
    """,
        (email,),
    )

    record = c.fetchone()
    conn.close()

    return dict(record) if record else None


def stats():
    """Display consent statistics."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Total consents
    c.execute("SELECT COUNT(*) FROM consent_records")
    total = c.fetchone()[0]

    # Active consents
    c.execute("SELECT COUNT(*) FROM consent_records WHERE consent_status = 1")
    active = c.fetchone()[0]

    # Withdrawn consents
    c.execute("SELECT COUNT(*) FROM consent_records WHERE consent_status = 0")
    withdrawn = c.fetchone()[0]

    # Unique users
    c.execute("SELECT COUNT(DISTINCT user_email) FROM consent_records")
    unique_users = c.fetchone()[0]

    # Policy versions
    c.execute(
        "SELECT DISTINCT privacy_version FROM consent_records ORDER BY privacy_version"
    )
    versions = [v[0] for v in c.fetchall()]

    conn.close()

    print("\n" + "=" * 60)
    print("📊 CONSENT STATISTICS")
    print("=" * 60)
    print(f"Total Records: {total}")
    print(f"Active Consents: {active} ✅")
    print(f"Withdrawn: {withdrawn} ❌")
    print(f"Unique Users: {unique_users}")
    print(f"Policy Versions: {', '.join(versions)}")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    if not Path(DB_PATH).exists():
        print(f"❌ Database not found at {DB_PATH}")
        sys.exit(1)

    if len(sys.argv) > 1:
        email = sys.argv[1]
        view_user_consents(email)
        latest = get_latest_consent(email)
        if latest:
            print(
                f"✅ Latest consent: {latest['privacy_version']} on {latest['consent_timestamp']}"
            )
    else:
        stats()
        view_all_consents()
