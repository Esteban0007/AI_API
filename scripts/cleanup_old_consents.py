#!/usr/bin/env python3
"""
Script to cleanup old consent records after 3 years.
This is required for GDPR compliance - we preserve consent records for 3 years
as legal proof, then delete them after the retention period expires.

Usage:
    python scripts/cleanup_old_consents.py [--dry-run] [--older-than-days 1095]

    Options:
        --dry-run              Show what would be deleted without actually deleting
        --older-than-days N    Cleanup records older than N days (default: 1095 = 3 years)
"""

import sys
import sqlite3
from datetime import datetime, timedelta
import argparse
from pathlib import Path


def get_db_path():
    """Get database path."""
    base_dir = Path(__file__).parent.parent
    return base_dir / "data" / "users.db"


def cleanup_old_consents(dry_run=False, days=1095):
    """
    Delete consent records older than specified days.

    Args:
        dry_run: If True, show what would be deleted without deleting
        days: Number of days to retain (default 1095 = 3 years)
    """
    db_path = get_db_path()

    if not db_path.exists():
        print(f"❌ Database not found: {db_path}")
        return False

    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()

        # Calculate cutoff date
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        cutoff_timestamp = cutoff_date.isoformat()

        print(f"🔍 Searching for consent records older than {days} days")
        print(f"   Cutoff date: {cutoff_timestamp}\n")

        # Find records to delete
        c.execute(
            """
            SELECT id, user_email, consent_timestamp, user_id
            FROM consent_records
            WHERE consent_timestamp < ?
            ORDER BY consent_timestamp ASC
        """,
            (cutoff_timestamp,),
        )

        old_records = c.fetchall()

        if not old_records:
            print("✅ No consent records found older than 3 years.")
            conn.close()
            return True

        print(f"📋 Found {len(old_records)} old consent records:\n")

        for record in old_records:
            user_status = (
                f"User: {record['user_email']}"
                if record["user_id"]
                else "User: DELETED (preserved record)"
            )
            print(f"   • {record['consent_timestamp']} - {user_status}")

        print(
            f"\n{'[DRY RUN] Would delete' if dry_run else 'Deleting'} {len(old_records)} record(s)...\n"
        )

        if not dry_run:
            c.execute(
                """
                DELETE FROM consent_records
                WHERE consent_timestamp < ?
            """,
                (cutoff_timestamp,),
            )

            deleted_count = c.rowcount
            conn.commit()

            print(f"✅ Successfully deleted {deleted_count} old consent record(s)")
            print(f"   Execution time: {datetime.utcnow().isoformat()}")
        else:
            print("✅ [DRY RUN] No changes made to database")

        conn.close()
        return True

    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def get_consent_retention_stats():
    """Show statistics about consent record retention."""
    db_path = get_db_path()

    if not db_path.exists():
        print(f"❌ Database not found: {db_path}")
        return False

    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()

        # Get total records
        c.execute("SELECT COUNT(*) as count FROM consent_records")
        total = c.fetchone()["count"]

        # Get records with associated users
        c.execute(
            "SELECT COUNT(*) as count FROM consent_records WHERE user_id IS NOT NULL"
        )
        with_users = c.fetchone()["count"]

        # Get orphaned records (users deleted)
        c.execute("SELECT COUNT(*) as count FROM consent_records WHERE user_id IS NULL")
        orphaned = c.fetchone()["count"]

        # Get oldest and newest records
        c.execute(
            "SELECT MIN(consent_timestamp) as oldest, MAX(consent_timestamp) as newest FROM consent_records"
        )
        dates = c.fetchone()

        # Calculate how many would be deleted in 3 years
        cutoff_date = (datetime.utcnow() - timedelta(days=1095)).isoformat()
        c.execute(
            """
            SELECT COUNT(*) as count FROM consent_records
            WHERE consent_timestamp < ?
        """,
            (cutoff_date,),
        )
        to_delete_soon = c.fetchone()["count"]

        print("\n📊 CONSENT RECORDS RETENTION STATISTICS")
        print("=" * 50)
        print(f"Total consent records:        {total}")
        print(f"With active users:            {with_users}")
        print(f"Orphaned (users deleted):     {orphaned}")
        print(f"Oldest record:                {dates['oldest']}")
        print(f"Newest record:                {dates['newest']}")
        print(f"Ready for cleanup (3+ years): {to_delete_soon}")
        print("=" * 50)

        conn.close()
        return True

    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Cleanup old GDPR consent records (older than 3 years)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Show statistics
  python scripts/cleanup_old_consents.py --stats
  
  # Dry run (show what would be deleted)
  python scripts/cleanup_old_consents.py --dry-run
  
  # Actually delete records older than 3 years
  python scripts/cleanup_old_consents.py
  
  # Delete records older than 2 years (custom retention)
  python scripts/cleanup_old_consents.py --older-than-days 730
        """,
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be deleted without actually deleting",
    )

    parser.add_argument(
        "--older-than-days",
        type=int,
        default=1095,
        help="Delete records older than N days (default: 1095 = 3 years)",
    )

    parser.add_argument(
        "--stats", action="store_true", help="Show consent records retention statistics"
    )

    args = parser.parse_args()

    if args.stats:
        print("\n🔍 Retrieving consent retention statistics...\n")
        success = get_consent_retention_stats()
    else:
        success = cleanup_old_consents(dry_run=args.dry_run, days=args.older_than_days)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
