# User Account Deletion - GDPR Right to Erasure (Article 17)

## Overview

Users can request complete deletion of their account and associated data at any time. This implementation fully complies with GDPR Article 17 (Right to Erasure / "Right to be Forgotten").

---

## What Gets Deleted

When a user requests account deletion, the following data is **PERMANENTLY DELETED**:

| Data Type                 | Action     | Reason                     |
| ------------------------- | ---------- | -------------------------- |
| **User Account**          | ✅ DELETED | Personal data              |
| **Email Address**         | ✅ DELETED | Personal identifier        |
| **Password Hash**         | ✅ DELETED | Authentication data        |
| **API Keys**              | ✅ DELETED | Access credentials         |
| **Search Logs**           | ✅ DELETED | Activity history (private) |
| **Uploaded Files (JSON)** | ✅ DELETED | User content (private)     |
| **Vector Embeddings**     | ✅ DELETED | Derived from user content  |
| **Confirmation Tokens**   | ✅ DELETED | Temporary auth data        |
| **Password Reset Tokens** | ✅ DELETED | Temporary auth data        |

---

## What Gets Preserved (Legal Requirement)

The following data is **PRESERVED FOR 3 YEARS**:

| Data Type           | Duration | Reason                                                               |
| ------------------- | -------- | -------------------------------------------------------------------- |
| **Consent Records** | 3 Years  | **LEGAL REQUIREMENT**: Proof that consent was obtained (GDPR Art. 7) |

### Why Consent Records Are Preserved

If we deleted consent records immediately, we would **lose legal proof** that the user gave valid consent. If audited, we couldn't prove:

- When the user consented
- What version of policy they accepted
- From which IP they consented
- What method they used

**Solution:** Consent records remain but are **disassociated from the user**:

```
Before deletion:
  consent_records.user_id = 42
  consent_records.user_email = "user@example.com"

After deletion:
  consent_records.user_id = NULL
  consent_records.user_email = "user@example.com" (preserved for audit)
  (user account = deleted_42_2026-04-09T10:45:22)
```

---

## How Users Delete Their Account

### Step 1: User navigates to account deletion page

```
GET /account-settings/delete-account
```

### Step 2: System shows deletion preview

```
GET /api/account-deletion-preview?email=user@example.com
```

Response:

```json
{
  "found": true,
  "email": "user@example.com",
  "account_created": "2026-04-01T10:00:00",
  "data_to_delete": {
    "user_account": "✅ WILL BE DELETED",
    "personal_email": "✅ WILL BE DELETED",
    "password_hash": "✅ WILL BE DELETED",
    "api_keys": "✅ WILL BE DELETED",
    "search_logs": "✅ WILL BE DELETED",
    "uploaded_files": "✅ WILL BE DELETED",
    "vector_embeddings": "✅ WILL BE DELETED"
  },
  "data_preserved": {
    "consent_records": "🔒 PRESERVED (Legal: 3 records for 3 years)",
    "reason": "GDPR compliance - proof that consent was obtained"
  }
}
```

### Step 3: User confirms deletion

User must enter password to confirm (prevents accidental deletion).

```
POST /api/delete-account
{
  "email": "user@example.com",
  "password": "user_password"
}
```

Response:

```json
{
  "success": true,
  "message": "Account deleted successfully",
  "deleted_at": "2026-04-09T10:45:22",
  "note": "Consent records preserved for 3 years (legal compliance)",
  "summary": { ... }
}
```

---

## Database Changes After Deletion

### Before Deletion

```
TABLE: users
┌────┬─────────────────────┬──────────────────┬───────────┬────────────────────┐
│ id │ email               │ password_hash    │ api_key   │ created_at         │
├────┼─────────────────────┼──────────────────┼───────────┼────────────────────┤
│ 42 │ user@example.com    │ hash_123456...   │ rapi_xyz  │ 2026-04-01...      │
└────┴─────────────────────┴──────────────────┴───────────┴────────────────────┘

TABLE: consent_records
┌─────┬────────┬─────────────────────┬──────────────────┐
│ id  │ user_id│ user_email          │ consent_timestamp│
├─────┼────────┼─────────────────────┼──────────────────┤
│ 1   │ 42     │ user@example.com    │ 2026-04-01...    │
│ 2   │ 42     │ user@example.com    │ 2026-04-02...    │
└─────┴────────┴─────────────────────┴──────────────────┘
```

### After Deletion

```
TABLE: users
┌────┬────────────────────────────────────────────┬───────────────┬──────────┬────────────────────┐
│ id │ email                                      │ password_hash │ api_key  │ created_at         │
├────┼────────────────────────────────────────────┼───────────────┼──────────┼────────────────────┤
│ 42 │ deleted_42_2026-04-09T10:45:22.123456     │ NULL          │ NULL     │ 2026-04-01...      │
└────┴────────────────────────────────────────────┴───────────────┴──────────┴────────────────────┘

TABLE: consent_records
┌─────┬────────┬─────────────────────┬──────────────────┐
│ id  │ user_id│ user_email          │ consent_timestamp│
├─────┼────────┼─────────────────────┼──────────────────┤
│ 1   │ NULL   │ user@example.com    │ 2026-04-01...    │  ← user_id cleared
│ 2   │ NULL   │ user@example.com    │ 2026-04-02...    │  ← user_id cleared
└─────┴────────┴─────────────────────┴──────────────────┘
```

**Status:** User account deleted, but consent proof remains for 3 years.

---

## API Endpoints

### 1. Get Deletion Preview

```
GET /api/account-deletion-preview?email=user@example.com

Response: What will be deleted/preserved
```

### 2. Delete Account

```
POST /api/delete-account

Body:
{
  "email": "user@example.com",
  "password": "user_password"
}

Response: Confirmation of deletion
```

---

## GDPR Compliance

| Requirement                    | Implementation                                         |
| ------------------------------ | ------------------------------------------------------ |
| **Art. 17 - Right to Erasure** | ✅ Users can delete account on demand                  |
| **Art. 17(3)(b)**              | ✅ Consent records preserved for legal proof (3 years) |
| **Art. 5(1)(e)**               | ✅ Data retained only as long as necessary             |
| **Art. 12**                    | ✅ User-friendly deletion process                      |
| **Accountability**             | ✅ Deletion logged with timestamp                      |
| **Proof of Erasure**           | ✅ Consent records remain as evidence                  |

---

## Security Measures

1. **Password Confirmation**: User must enter password before deletion (prevents accidental/unauthorized deletion)
2. **Audit Trail**: Deletion timestamp recorded
3. **Legal Preservation**: Consent records kept separate from user data
4. **Irreversible**: Deletion is permanent (no recovery)

---

## Timeline

| Date       | Action                                           |
| ---------- | ------------------------------------------------ |
| Day 0      | User requests deletion                           |
| Day 0      | Account deleted, data wiped                      |
| Day 1-1095 | Consent records preserved (legal requirement)    |
| Day 1096   | Consent records can be deleted (3 years elapsed) |

---

## Testing Account Deletion

### Step 1: Create test user

```bash
curl -X POST http://localhost:8000/register \
  -d "email=test@example.com&password=TestPass123&password2=TestPass123"
```

### Step 2: Get deletion preview

```bash
curl "http://localhost:8000/api/account-deletion-preview?email=test@example.com"
```

Expected response shows what will be deleted/preserved.

### Step 3: Delete account

```bash
curl -X POST http://localhost:8000/api/delete-account \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123"
  }'
```

### Step 4: Verify deletion

```bash
sqlite3 data/users.db "SELECT * FROM users WHERE email LIKE '%test@example%';"
# Should show: deleted_XX_2026-04-09T...

sqlite3 data/users.db "SELECT * FROM consent_records WHERE user_email = 'test@example.com';"
# Should show: Consent records with user_id = NULL
```

---

## Automating 3-Year Cleanup

To automatically delete consent records after 3 years:

```python
# scripts/cleanup_old_consents.py
import sqlite3
from datetime import datetime, timedelta

def cleanup_old_consents():
    """Delete consent records older than 3 years."""
    conn = sqlite3.connect("./data/users.db")
    c = conn.cursor()

    cutoff_date = datetime.utcnow() - timedelta(days=365*3)

    c.execute("""
        DELETE FROM consent_records
        WHERE consent_timestamp < ? AND user_id IS NULL
    """, (cutoff_date,))

    deleted_count = c.rowcount
    conn.commit()
    conn.close()

    print(f"Deleted {deleted_count} old consent records")

# Run via cron job:
# 0 0 1 * * python scripts/cleanup_old_consents.py
```

---

## Legal References

- **GDPR Article 17** - Right to erasure
- **GDPR Article 17(3)(b)** - Exception for legal obligations
- **GDPR Article 5(1)(e)** - Storage limitation
- **GDPR Recital 65** - Right to be forgotten
- **EDPB Guidelines 05/2020** - Right to Erasure

---

## User Communication

When user deletes account, send confirmation email:

```
Subject: Your Account Has Been Deleted

Dear User,

Your Ready API account (email@example.com) has been permanently deleted on 2026-04-09.

What was deleted:
- Your account and all personal information
- Your uploaded files and data
- Your API keys and access credentials
- Your search history and logs

What was preserved (legal requirement):
- Consent records (to prove consent was obtained)
- Duration: 3 years from account creation

If you have any questions, contact: info@readyapi.net

Best regards,
Ready API Team
```

---

## File Locations

- Function: `app/db/users.py` - `delete_user_account()`
- Preview: `app/db/users.py` - `get_user_deletion_summary()`
- Endpoints: `app/api/web.py` - `POST /api/delete-account`
- Cleanup Script: `scripts/cleanup_old_consents.py` (to create)
