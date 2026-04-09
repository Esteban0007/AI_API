# GDPR Account Deletion Implementation Guide

## Quick Start

Users can delete their account at any time by visiting:

```
GET /delete-account
```

This page allows users to:

1. Preview what will be deleted
2. Enter their email and password
3. Confirm deletion
4. Receive confirmation that their account has been deleted

---

## Backend Architecture

### 1. Database Functions (`app/db/users.py`)

#### `delete_user_account(user_email: str) -> dict`

Main function that handles account deletion with GDPR compliance.

```python
def delete_user_account(user_email: str) -> dict:
    """
    Delete user account and associated data (GDPR Article 17 - Right to Erasure).

    Deletes:
    - User account and personal data
    - All API keys and authentication tokens
    - Search logs and usage history
    - Uploaded files and embeddings
    - Confirmation tokens
    - Password reset tokens

    Preserves (Legal Requirement):
    - Consent records (3 years minimum)

    Returns:
        {
            "success": bool,
            "message": str,
            "deleted_at": ISO timestamp,
            "deleted_items": {
                "user_records": count,
                "api_keys": count,
                "search_logs": count,
                "files": count,
                "embeddings": count
            },
            "preserved_items": {
                "consent_records": count,
                "retention_years": 3
            }
        }
    """
```

**Implementation Details:**

- Hard deletes user account (not soft delete)
- Finds all related data through database relationships
- Preserves consent records but disassociates them from user
- Records deletion timestamp for audit trail
- Transaction-safe (all or nothing)

#### `get_user_deletion_summary(user_email: str) -> dict`

Shows users what will be deleted before confirming.

```python
def get_user_deletion_summary(user_email: str) -> dict:
    """
    Get preview of what will be deleted if user requests account deletion.

    Returns:
        {
            "found": bool,
            "email": str,
            "account_created": ISO timestamp,
            "data_to_delete": {
                "user_account": "✅ WILL BE DELETED",
                "personal_email": "✅ WILL BE DELETED",
                ...
            },
            "data_preserved": {
                "consent_records": "N records",
                "reason": "GDPR compliance..."
            }
        }
    """
```

#### `get_users_pending_deletion() -> list`

Utility function to find accounts marked for deletion.

---

### 2. API Endpoints (`app/api/web.py`)

#### `GET /delete-account`

Renders the account deletion page.

**Response:** HTML template with deletion form

```html
<!-- Displays:
  1. Deletion preview (data to delete vs preserve)
  2. Email field (auto-filled if user is logged in)
  3. Password field (for confirmation)
  4. Checkbox to confirm understanding
  5. Submit button
-->
```

#### `GET /api/account-deletion-preview?email=user@example.com`

API endpoint for fetching deletion preview.

**Query Parameters:**

- `email` (required): User email address

**Response:**

```json
{
  "found": true,
  "email": "user@example.com",
  "account_created": "2026-04-01T10:00:00",
  "data_to_delete": { ... },
  "data_preserved": { ... }
}
```

#### `POST /api/delete-account`

API endpoint to execute account deletion.

**Request Body:**

```json
{
  "email": "user@example.com",
  "password": "user_password"
}
```

**Response:**

```json
{
  "success": true,
  "message": "Account deleted successfully",
  "deleted_at": "2026-04-09T10:45:22",
  "summary": { ... }
}
```

**Error Responses:**

```json
// Invalid credentials
{
  "success": false,
  "message": "Invalid email or password"
}

// User not found
{
  "success": false,
  "message": "User not found"
}

// Server error
{
  "success": false,
  "message": "Error: [details]"
}
```

---

### 3. Frontend Implementation (`app/templates/delete_account.html`)

Features:

- **Deletion Preview**: Fetches and displays what will be deleted
- **Email/Password Confirmation**: User must enter credentials to prevent accidents
- **JavaScript Validation**:
  - Loads preview on email change
  - Enables delete button only when checkbox is marked
  - Handles async API calls
  - Shows success/error messages
- **Security**: Requires password to confirm, prevents CSRF with form validation
- **UX**: Clear warnings about irreversibility, staged process (preview → confirm → delete)

**User Flow:**

```
1. User visits /delete-account
2. System loads deletion preview via GET /api/account-deletion-preview
3. User sees what will be deleted and what will be preserved
4. User enters email and password
5. User checks "I understand" checkbox
6. Delete button becomes enabled
7. User clicks delete
8. System calls POST /api/delete-account
9. System executes deletion
10. Page shows success message
11. User is logged out and redirected to home
```

---

## Database Schema

### Relevant Tables

#### `users` table

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    api_key TEXT UNIQUE,
    confirmed BOOLEAN DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    ...
);
```

When user deletes account:

- Email: Set to `deleted_{id}_{timestamp}`
- Password hash: Set to NULL
- API key: Set to NULL
- Other fields: Cleared

#### `consent_records` table

```sql
CREATE TABLE consent_records (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    user_email TEXT,
    consent_status TEXT,
    consent_timestamp DATETIME,
    consent_ip TEXT,
    privacy_version TEXT,
    consent_method TEXT,
    user_agent TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

When user deletes account:

- `user_id`: Set to NULL (disassociate from user)
- Other fields: Preserved as-is (legal proof)

---

## GDPR Compliance

### Article 17 - Right to Erasure

✅ **Implemented:**

- Users can request deletion on demand
- System deletes personal data
- System preserves data only where legally required
- Clear communication about what is deleted/preserved
- Deletion is irreversible (no recovery window)

✅ **Article 17(3) Exception:**

- Consent records preserved for 3 years (legal obligation)
- Separated from user data (user is anonymized)
- Can be identified only through audit logs

✅ **Article 5(1)(e) - Storage Limitation:**

- Consent records automatically deleted after 3 years
- Script: `scripts/cleanup_old_consents.py`
- Can be run via cron job or manual execution

### Documentation

- **Privacy Policy**: `/privacy-policy` (visible, linked in footer)
- **Deletion Guide**: `/delete-account` (visible, linked in footer)
- **GDPR Compliance**: `GDPR_COMPLIANCE.md` (internal documentation)

---

## Testing

### Manual Testing

```bash
# 1. Create test user
curl -X POST http://localhost:8000/register \
  -d "email=test@example.com&password=TestPass123&password2=TestPass123"

# 2. Get deletion preview
curl "http://localhost:8000/api/account-deletion-preview?email=test@example.com"

# 3. Delete account
curl -X POST http://localhost:8000/api/delete-account \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"TestPass123"}'

# 4. Verify deletion
sqlite3 data/users.db "SELECT email FROM users WHERE email LIKE '%test%';"
# Should return: deleted_XX_2026-04-09T...

# 5. Verify consent records preserved
sqlite3 data/users.db "SELECT * FROM consent_records WHERE user_email = 'test@example.com';"
# Should show consent records with user_id = NULL
```

### Automated Testing

```python
# tests/test_gdpr_deletion.py
def test_delete_account():
    # Create user
    # Call POST /api/delete-account
    # Assert: user deleted from users table
    # Assert: consent records preserved with user_id = NULL
```

---

## Maintenance

### 3-Year Consent Record Cleanup

Run periodically to delete old consent records:

```bash
# Dry run (see what would be deleted)
python scripts/cleanup_old_consents.py --dry-run

# Actually delete
python scripts/cleanup_old_consents.py

# Show statistics
python scripts/cleanup_old_consents.py --stats
```

**Recommended Schedule:**

- Add to cron job (run monthly or quarterly)
- Or add to deployment pipeline (run after each deployment)

```bash
# Cron example: Run on first day of month at midnight
0 0 1 * * cd /var/www/readyapi && python scripts/cleanup_old_consents.py
```

---

## Error Handling

### Common Errors

| Error                       | Cause                     | Solution                   |
| --------------------------- | ------------------------- | -------------------------- |
| "User not found"            | Email doesn't exist in DB | Check email spelling       |
| "Invalid email or password" | Wrong password            | Verify password is correct |
| "Error: ..."                | Server error              | Check logs, try again      |

### Debugging

Check application logs:

```bash
# On VPS
tail -f /var/log/readyapi.log

# Locally
python app/main.py  # debug output in console
```

---

## Security Considerations

1. **Password Confirmation**: Prevents accidental/unauthorized deletion
2. **No Recovery**: Deletion is permanent (teach users about backups first)
3. **IP Logging**: System logs which IP deleted the account (for security audits)
4. **Email Notification**: Send confirmation email after deletion (optional enhancement)
5. **Audit Trail**: Deletion timestamp recorded in database

---

## Future Enhancements

1. **Email Confirmation**: Send email before actual deletion (24-hour window)
2. **Data Export**: Allow users to download their data before deletion
3. **Bulk Deletion**: Automated cleanup of orphaned/unused accounts
4. **Deletion Status**: Allow users to check status of deletion request
5. **Partial Deletion**: Let users choose which data to delete

---

## Related Files

| File                                | Purpose                       |
| ----------------------------------- | ----------------------------- |
| `app/db/users.py`                   | Database deletion functions   |
| `app/api/web.py`                    | API endpoints                 |
| `app/templates/delete_account.html` | Frontend form                 |
| `scripts/cleanup_old_consents.py`   | 3-year consent cleanup        |
| `GDPR_RIGHT_TO_ERASURE.md`          | User-facing documentation     |
| `GDPR_COMPLIANCE.md`                | Internal GDPR compliance docs |

---

## Legal Notice

This implementation complies with:

- **EU GDPR Article 17** - Right to erasure
- **EDPB Guidelines 05/2020** - Right to erasure interpretation
- **CCPA** - California Consumer Privacy Act (similar requirements)
- **LGPD** - Brazil General Data Protection Law

For questions about legal compliance, consult your Data Protection Officer (DPO) or legal counsel.
