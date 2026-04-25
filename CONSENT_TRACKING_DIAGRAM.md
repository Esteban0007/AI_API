```
╔══════════════════════════════════════════════════════════════════════════════════════╗
║                          GDPR CONSENT TRACKING FLOW                                 ║
╚══════════════════════════════════════════════════════════════════════════════════════╝

┌─────────────────────────────────────────────────────────────────────────────────────┐
│ 1️⃣  FRONTEND: USER REGISTRATION PAGE                                               │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│   Form Fields:                                                                      │
│   ┌──────────────────────────────────────┐                                         │
│   │ Email: user@example.com              │                                         │
│   │ Password: ••••••••                   │                                         │
│   │ Confirm: ••••••••                   │                                         │
│   │                                      │                                         │
│   │ ☐ I have read and agree to the      │ ← Checkbox (disabled by default)      │
│   │   Terms of Service and Privacy      │                                         │
│   │   Policy. I consent to...           │                                         │
│   │                                      │                                         │
│   │ [Sign Up] ← Button (disabled until  │                                         │
│   │           checkbox is checked)       │                                         │
│   └──────────────────────────────────────┘                                         │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘

                                    │
                                    │ User clicks checkbox ✓
                                    ▼

┌─────────────────────────────────────────────────────────────────────────────────────┐
│ 2️⃣  FRONTEND: JAVASCRIPT VALIDATION                                                │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│   - Checkbox enabled                                                                │
│   - Button enabled (opacity: 100%)                                                  │
│   - Button cursor: pointer                                                          │
│                                                                                     │
│   User clicks "Sign Up" button                                                      │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘

                                    │
                                    │ Form submit event
                                    ▼

┌─────────────────────────────────────────────────────────────────────────────────────┐
│ 3️⃣  FRONTEND: CONSENT DATA CAPTURE & API CALL                                      │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│   JavaScript captures:                                                              │
│   {                                                                                  │
│     email: "user@example.com",           ← From form input                        │
│     privacy_version: "v1.0",             ← Hardcoded in script                   │
│     consent_method: "Web Form"           ← Hardcoded in script                   │
│   }                                                                                  │
│                                                                                     │
│   POST /api/consent (async)                                                         │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘

                                    │
                                    │ HTTP Request
                                    ▼

┌─────────────────────────────────────────────────────────────────────────────────────┐
│ 4️⃣  BACKEND: FASTAPI ENDPOINT (/api/consent)                                       │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│   Receives JSON:                                                                    │
│   {                                                                                  │
│     email: "user@example.com",                                                     │
│     privacy_version: "v1.0",                                                       │
│     consent_method: "Web Form"                                                     │
│   }                                                                                  │
│                                                                                     │
│   Extracts from Request object:                                                     │
│   - consent_ip = request.client.host    ← "85.54.XX.XXX" (automatic)            │
│   - user_agent = header "user-agent"    ← "Mozilla/5.0..." (automatic)          │
│                                                                                     │
│   Calls: save_consent_record(                                                       │
│     user_email="user@example.com",                                                 │
│     consent_status=True,                                                            │
│     consent_type="privacy_policy",                                                  │
│     privacy_version="v1.0",                                                         │
│     consent_method="Web Form",                                                      │
│     consent_ip="85.54.XX.XXX",                                                      │
│     user_agent="Mozilla/5.0...",                                                    │
│     user_id=None                        ← NULL for pre-registration users         │
│   )                                                                                  │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘

                                    │
                                    │ save_consent_record()
                                    ▼

┌─────────────────────────────────────────────────────────────────────────────────────┐
│ 5️⃣  DATABASE: INSERT INTO consent_records                                          │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│   SQL INSERT:                                                                       │
│   ┌─────────────────────────────────────────────────────────────────────┐          │
│   │ INSERT INTO consent_records (                                       │          │
│   │   id,                 → AUTOINCREMENT                              │          │
│   │   user_id,            → NULL (user not yet created)               │          │
│   │   user_email,         → "user@example.com"                        │          │
│   │   consent_status,     → 1 (TRUE = accepted)                       │          │
│   │   consent_type,       → "privacy_policy"                          │          │
│   │   privacy_version,    → "v1.0"                                    │          │
│   │   consent_method,     → "Web Form"                                │          │
│   │   consent_ip,         → "85.54.XX.XXX"                            │          │
│   │   user_agent,         → "Mozilla/5.0..."                          │          │
│   │   consent_timestamp   → "2026-04-09T10:45:22" (UTC)              │          │
│   │ )                                                                  │          │
│   └─────────────────────────────────────────────────────────────────────┘          │
│                                                                                     │
│   ✅ Record saved to: data/users.db → consent_records table                        │
│                                                                                     │
│   File System:                                                                      │
│   data/users.db                                                                     │
│   └── TABLE: consent_records                                                        │
│       └── ID: 1                                                                     │
│           ├── user_email: "user@example.com"                                       │
│           ├── consent_status: 1                                                     │
│           ├── consent_timestamp: "2026-04-09 10:45:22"                             │
│           ├── consent_ip: "85.54.XX.XXX"                                           │
│           ├── privacy_version: "v1.0"                                              │
│           ├── consent_method: "Web Form"                                           │
│           └── user_agent: "Mozilla/5.0..."                                         │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘

                                    │
                                    │ Response to frontend
                                    ▼

┌─────────────────────────────────────────────────────────────────────────────────────┐
│ 6️⃣  API RESPONSE                                                                   │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│   JSON Response:                                                                    │
│   {                                                                                  │
│     "success": true,                                                                │
│     "message": "Consent recorded successfully",                                     │
│     "timestamp": "2026-04-09T10:45:22.123456"                                       │
│   }                                                                                  │
│                                                                                     │
│   Status: 200 OK                                                                    │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘

                                    │
                                    │ Frontend continues with
                                    │ standard registration
                                    ▼

┌─────────────────────────────────────────────────────────────────────────────────────┐
│ 7️⃣  STANDARD REGISTRATION FLOW                                                     │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│   POST /register                                                                    │
│   {                                                                                  │
│     email: "user@example.com",                                                     │
│     password: "hashed...",                                                          │
│     terms_agreement: true                                                           │
│   }                                                                                  │
│                                                                                     │
│   ✅ User account created                                                          │
│   ✅ API key generated                                                              │
│   ✅ Confirmation email sent                                                        │
│                                                                                     │
│   User links:                                                                       │
│   - consent_records (pre-creation): user_id = NULL                                 │
│   - users (after creation): links via email                                        │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘

╔══════════════════════════════════════════════════════════════════════════════════════╗
║                              GDPR AUDIT TRAIL RESULT                                ║
╚══════════════════════════════════════════════════════════════════════════════════════╝

Database Record (GDPR Evidence):
┌──────────────────────────────────────────────────────────────────────────────────────┐
│ ID: 1                                                                                │
│ user_email: "user@example.com"        ← WHO: Email of person giving consent       │
│ consent_status: 1                     ← STATUS: Accepted (1=yes, 0=withdrawn)      │
│ consent_timestamp: "2026-04-09 10:45:22 UTC"  ← WHEN: Exact date & time (GDPR)    │
│ consent_ip: "85.54.XX.XXX"            ← WHERE: IP address (proof of consent)      │
│ privacy_version: "v1.0"               ← WHAT: Which policy version accepted       │
│ consent_method: "Web Form"            ← HOW: Registration form                     │
│ user_agent: "Mozilla/5.0..."          ← DEVICE: Browser/device info               │
│ consent_type: "privacy_policy"        ← TYPE: What kind of consent                │
│ user_id: 42 (after email confirmation) ← Links to user account                    │
│ created_at: "2026-04-09 10:45:22"     ← RECORD CREATED: Timestamp                 │
└──────────────────────────────────────────────────────────────────────────────────────┘

GDPR Requirements Met:
┌──────────────────────────────────────────────────────────────────────────────────────┐
│ ✅ Proof of consent       → consent_status = 1, consent_timestamp recorded        │
│ ✅ Lawful basis           → Explicit consent checkbox + database proof            │
│ ✅ When given             → consent_timestamp (UTC, precise to second)            │
│ ✅ Policy version         → privacy_version (v1.0)                                │
│ ✅ Technical proof        → consent_ip (origin of consent)                        │
│ ✅ Audit trail            → Complete record with user_agent, method               │
│ ✅ Right to access        → view_consent_records.py script                        │
│ ✅ Data minimization      → Only essential fields stored                          │
└──────────────────────────────────────────────────────────────────────────────────────┘

Query to Retrieve Audit Trail:
┌──────────────────────────────────────────────────────────────────────────────────────┐
│ SELECT consent_timestamp, consent_ip, privacy_version, consent_status              │
│ FROM consent_records                                                                 │
│ WHERE user_email = "user@example.com"                                               │
│ ORDER BY consent_timestamp DESC;                                                    │
│                                                                                      │
│ Result:                                                                              │
│ 2026-04-09 10:45:22 | 85.54.XX.XXX | v1.0 | 1 (ACCEPTED)                          │
│ 2026-04-15 14:30:01 | 85.54.XX.YYY | v1.1 | 0 (WITHDRAWN - for v1.1)             │
│ 2026-04-15 14:30:15 | 85.54.XX.YYY | v1.1 | 1 (ACCEPTED)                          │
│                                                                                      │
│ This proves the user:                                                                │
│ - Accepted v1.0 on April 9 from IP XX.XXX                                          │
│ - Withdrew consent for v1.1 on April 15                                             │
│ - Re-accepted v1.1 immediately after from same IP                                  │
└──────────────────────────────────────────────────────────────────────────────────────┘
```

## Data

```
USER MARKS CHECKBOX
        │
        ▼
FORM SUBMIT
        │
        ├─► Validate checkbox (JavaScript)
        │
        ├─► POST /api/consent
        │   └─► Capture IP, User-Agent
        │
        └─► INSERT consent_records
            └─► Email, timestamp, IP, version, etc.
                │
                ▼
        ✅ GDPR COMPLIANCE RECORDED
                │
                ▼
        Continue to POST /register
        (Standard registration flow)
```

## Auditory

```
AUDITOR REQUESTS: "Prove this user consented to your Privacy Policy"

RESPONSE:
┌────────────────────────────────────────────────────────────────┐
│ EVIDENCE OF GDPR COMPLIANCE                                     │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│ 1. Consent Record ID: 42                                       │
│ 2. Email: user@example.com                                     │
│ 3. Accepted: Yes (consent_status = 1)                         │
│ 4. When: 2026-04-09 10:45:22 UTC (timestamp)                  │
│ 5. IP Address: 85.54.XX.XXX (proof of origin)                │
│ 6. Policy Version: v1.0 (which policy they accepted)          │
│ 7. Method: Web Form Registration                              │
│ 8. Device: Mozilla/5.0... (browser fingerprint)               │
│ 9. Database: SQLite, encrypted backup                         │
│                                                                 │
│ COMPLIANCE: ✅ GDPR Article 7 - Proof of Lawful Basis         │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```
