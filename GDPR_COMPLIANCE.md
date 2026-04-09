# GDPR Compliance & Consent Management

## Overview

This system implements GDPR-compliant consent tracking for the Privacy Policy and Terms of Service. All user consents are recorded in the database with complete audit trails.

## Consent Record Structure

When a user accepts the Privacy Policy during registration, the system automatically saves:

| Field               | Example                   | Purpose                                                                   |
| ------------------- | ------------------------- | ------------------------------------------------------------------------- |
| `consent_status`    | `true`                    | Proof that consent action occurred                                        |
| `consent_timestamp` | `2026-04-09 10:45:22 UTC` | Exact date/time of consent (GDPR requirement)                             |
| `consent_ip`        | `85.54.XX.XXX`            | Technical proof of consent origin                                         |
| `privacy_version`   | `v1.0`                    | Critical: Version of policy accepted (needed if policy changes in future) |
| `consent_method`    | `Web Form`                | Channel through which consent was given                                   |
| `user_email`        | `user@example.com`        | Email at time of consent                                                  |
| `user_agent`        | `Mozilla/5.0...`          | Browser/device information                                                |
| `user_id`           | `42`                      | Links to user account (nullable for pre-registration)                     |

## Database Schema

### Consent Records Table

```sql
CREATE TABLE consent_records (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,                    -- NULL for pre-registration consents
    user_email TEXT NOT NULL,           -- Email at time of consent
    consent_status BOOLEAN DEFAULT 1,   -- True = accepted, False = withdrawn
    consent_type TEXT,                  -- privacy_policy, terms_of_service, etc.
    privacy_version TEXT,               -- Version of policy (e.g., v1.0, v1.1)
    consent_method TEXT,                -- Web Form, API, Mobile App, etc.
    consent_ip TEXT,                    -- IP address of consent
    user_agent TEXT,                    -- Browser/User-Agent info
    consent_timestamp TIMESTAMP,        -- When consent was given (primary audit field)
    created_at TIMESTAMP,               -- Record creation time
    updated_at TIMESTAMP                -- Last update time
)
```

## How It Works

### During Registration

1. **Frontend**: User checks the privacy policy checkbox (initially disabled)
2. **Form Validation**: JavaScript validates checkbox is checked before allowing form submission
3. **Consent Capture**:
   - Email is extracted from the form
   - IP address is captured from request headers
   - User-Agent is captured from browser
   - Privacy version defaults to `v1.0`
   - Consent method is set to `Web Form`
4. **API Call**: `POST /api/consent` is called with consent data
5. **Database Storage**: Consent record is saved to `consent_records` table
6. **User Registration**: Standard registration form is submitted to `/register`
7. **Audit Trail**: Both consent record and user account are now linked

### Accessing Consent Records

**Python (Backend)**:

```python
from app.db.users import get_consent_records

# Get all consent records for a user
records = get_consent_records("user@example.com")

# Each record contains:
# {
#   'id': 1,
#   'user_id': 42,
#   'user_email': 'user@example.com',
#   'consent_status': True,
#   'consent_type': 'privacy_policy',
#   'privacy_version': 'v1.0',
#   'consent_method': 'Web Form',
#   'consent_ip': '85.54.XX.XXX',
#   'user_agent': 'Mozilla/5.0...',
#   'consent_timestamp': '2026-04-09T10:45:22'
# }
```

**Direct SQLite Query**:

```bash
sqlite3 data/users.db
```

```sql
-- Get all consents for a user
SELECT * FROM consent_records
WHERE user_email = 'user@example.com'
ORDER BY consent_timestamp DESC;

-- Get latest consent version accepted by user
SELECT privacy_version, consent_timestamp
FROM consent_records
WHERE user_email = 'user@example.com' AND consent_status = 1
ORDER BY consent_timestamp DESC
LIMIT 1;

-- Audit trail: All consent events for compliance review
SELECT consent_timestamp, consent_ip, consent_status, privacy_version
FROM consent_records
WHERE user_email = 'user@example.com'
ORDER BY consent_timestamp DESC;

-- Export all consents for GDPR Subject Access Request
SELECT * FROM consent_records ORDER BY consent_timestamp DESC;
```

## GDPR Compliance Features

### ✅ Lawful Basis for Processing

- **Consent**: Users must explicitly check the privacy policy checkbox
- **Proof**: Each consent is timestamped and IP-logged
- **Withdrawal**: Users can request consent withdrawal (sets `consent_status = false`)

### ✅ Right to Access (Data Subject Access Request)

- Users can request all their consent records via `/api/consent-records` endpoint (to be implemented)
- Complete audit trail showing all consent events

### ✅ Right to Erasure ("Right to be Forgotten")

- When user account is deleted, consent records are preserved for legal compliance
- Records show user accepted specific policy version at specific time

### ✅ Data Minimization

- Only essential fields: email, timestamp, IP, consent status, policy version
- No unnecessary personal data stored

### ✅ Accountability & Documentation

- Every consent action is timestamped with UTC precision
- IP address proves origin of consent
- Policy version ensures we know which terms were accepted
- Database serves as evidence for regulatory audits

## API Endpoints (Backend)

### Save Consent Record

```
POST /api/consent

Request Body:
{
  "email": "user@example.com",
  "privacy_version": "v1.0",
  "consent_method": "Web Form"
}

Response:
{
  "success": true,
  "message": "Consent recorded successfully",
  "timestamp": "2026-04-09T10:45:22.123456"
}
```

**Note**: IP and User-Agent are automatically captured from request headers.

## Versioning Your Privacy Policy

When you update your Privacy Policy:

1. **Update the template**: Modify `/app/templates/privacy_policy.html`
2. **Increment version**: Change privacy version (e.g., `v1.0` → `v1.1`)
3. **Database is ready**: Existing consents remain with their original version
4. **Compliance**: You can prove users accepted specific version at specific time

Example:

```
April 2026: User accepts v1.0
July 2026: You update policy to v1.1
Future consents: Tracked as v1.1
Audit trail: Shows user accepted v1.0 on April 9
```

## Regulatory References

This implementation covers:

- **GDPR (EU)**: Articles 4, 6, 7 (Lawfulness, Consent)
- **GDPR Article 17**: Right to Erasure (data preserved for legal reasons)
- **GDPR Article 15**: Right to Access (audit trail available)
- **ePrivacy Directive**: Cookie/consent tracking
- **CCPA (California)**: Consumer right to know

## Audit Commands

```bash
# Check total consents recorded
sqlite3 data/users.db "SELECT COUNT(*) FROM consent_records;"

# Get consents from last 30 days
sqlite3 data/users.db "
SELECT user_email, consent_timestamp, consent_ip, privacy_version
FROM consent_records
WHERE consent_timestamp > datetime('now', '-30 days')
ORDER BY consent_timestamp DESC;"

# Get withdrawal requests
sqlite3 data/users.db "
SELECT * FROM consent_records
WHERE consent_status = 0
ORDER BY consent_timestamp DESC;"
```

## Future Enhancements

- [ ] Endpoint to retrieve user consent records (Data Subject Access Request)
- [ ] Endpoint to withdraw consent (GDPR Right to Withdrawal)
- [ ] Email notification when privacy policy changes
- [ ] Periodic re-consent for inactive users (if required by regulation)
- [ ] Integration with email service for proof of delivery
- [ ] Dashboard to manage consent records and view audit trail
