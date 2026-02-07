# Security Quick Fixes - Priority Order

## CRITICAL - Fix Immediately (Before ANY deployment)

### 1. Path Traversal in Receipt Upload (15 min)
**File:** `/Users/anthony/Tax Helper/components/receipt_upload.py`

```python
# Add to generate_receipt_filename() at line 56:
from pathlib import Path

# After line 61, add validation:
if '..' in merchant_clean or os.sep in merchant_clean or '/' in merchant_clean:
    raise ValueError("Invalid merchant name - contains path separators")

# At end of function (line 73), add:
# Validate final path stays in receipts directory
full_path = Path(RECEIPTS_DIR) / filename
full_path = full_path.resolve()
receipts_dir = Path(RECEIPTS_DIR).resolve()

if not str(full_path).startswith(str(receipts_dir)):
    raise ValueError("Security: Path traversal attempt detected")

return filename
```

### 2. Database File Permissions (1 min)
```bash
chmod 600 "/Users/anthony/Tax Helper/tax_helper.db"
```

### 3. Disable Debug Mode (1 min)
**File:** `/Users/anthony/Tax Helper/app.py` line 154

```python
# Change from:
DEBUG = True

# To:
import os
DEBUG = os.getenv('TAX_HELPER_DEBUG', 'false').lower() == 'true'
```

### 4. Add Basic Authentication (30 min)
**File:** `/Users/anthony/Tax Helper/app.py` - Add after imports, before page config:

```python
import hmac
import hashlib

def check_password():
    """Returns True if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if hmac.compare_digest(
            st.session_state["password"],
            os.getenv("TAX_HELPER_PASSWORD", "change_me_now")
        ):
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        st.info("Please enter the application password to continue.")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 Password incorrect")
        return False
    else:
        return True

if not check_password():
    st.stop()

# Then set environment variable:
# export TAX_HELPER_PASSWORD="YourSecurePasswordHere123!"
```

### 5. File Upload Validation (20 min)
**File:** `/Users/anthony/Tax Helper/components/receipt_upload.py`

```python
# Add after imports:
try:
    import magic  # python-magic
    MAGIC_AVAILABLE = True
except ImportError:
    MAGIC_AVAILABLE = False

# In save_receipt() function, after line 106, add:
if MAGIC_AVAILABLE:
    # Validate actual file type
    file_content = uploaded_file.getvalue()
    mime = magic.from_buffer(file_content, mime=True)

    allowed_mimes = {
        'png': 'image/png',
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'pdf': 'application/pdf'
    }

    expected_mime = allowed_mimes.get(file_ext)
    if mime != expected_mime:
        st.error(f"File type mismatch. File appears to be {mime}, not {expected_mime}")
        return None

# Install: pip install python-magic
```

### 6. Sanitize File Deletion (10 min)
**File:** `/Users/anthony/Tax Helper/components/receipt_upload.py`

```python
# In delete_receipt() function, replace lines 450-454 with:
from pathlib import Path

try:
    # Construct and validate path
    base_dir = Path(__file__).parent.parent
    receipts_dir = (base_dir / "receipts").resolve()
    full_path = (base_dir / receipt_path).resolve()

    # Verify path is within receipts directory
    try:
        full_path.relative_to(receipts_dir)
    except ValueError:
        st.error("Security: Cannot delete files outside receipts directory")
        return False

    # Verify file exists
    if full_path.exists():
        full_path.unlink()
    else:
        st.warning("File not found, removing from database anyway")

except Exception as e:
    st.error(f"Error deleting file: {str(e)}")
    return False
```

---

## HIGH PRIORITY - Fix Within 1 Week

### 7. Regex DoS Protection (15 min)
**File:** `/Users/anthony/Tax Helper/utils.py`

```python
# In apply_rules() function, replace lines 132-136 with:
elif rule.match_mode == 'Regex':
    try:
        # Limit regex complexity
        if len(rule.text_to_match) > 200:
            continue  # Skip overly complex patterns

        # Timeout protection (simplified)
        import signal

        def timeout_handler(signum, frame):
            raise TimeoutError()

        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(1)  # 1 second timeout

        match = bool(re.search(rule.text_to_match, description, re.IGNORECASE))

        signal.alarm(0)  # Cancel alarm
    except (re.error, TimeoutError):
        continue
```

### 8. Add Rate Limiting (20 min)
**File:** `/Users/anthony/Tax Helper/components/batch_receipt_upload.py`

```python
# Add at module level:
import time
from collections import defaultdict

upload_times = defaultdict(list)

def check_rate_limit(max_uploads=5, window_seconds=3600):
    """Prevent upload spam"""
    session_id = id(st.session_state)  # Use session object ID
    now = time.time()

    # Clean old uploads
    upload_times[session_id] = [
        t for t in upload_times[session_id]
        if now - t < window_seconds
    ]

    if len(upload_times[session_id]) >= max_uploads:
        raise ValueError(f"Rate limit: Maximum {max_uploads} uploads per hour")

    upload_times[session_id].append(now)

# In render_upload_interface(), add after line 125:
try:
    check_rate_limit()
except ValueError as e:
    st.error(str(e))
    return
```

### 9. CSV Injection Protection (10 min)
**File:** `/Users/anthony/Tax Helper/utils.py`

```python
# Add new function:
def sanitize_csv_value(value):
    """Prevent CSV injection"""
    if not value:
        return value

    value_str = str(value)
    dangerous_chars = ['=', '+', '-', '@', '\t', '\r']

    if value_str and value_str[0] in dangerous_chars:
        return "'" + value_str  # Prefix with single quote

    return value_str

# In parse_csv() or before saving to database:
# Apply to all string columns
for col in df.columns:
    if df[col].dtype == 'object':
        df[col] = df[col].apply(sanitize_csv_value)
```

### 10. Add Security Logging (30 min)
**File:** `/Users/anthony/Tax Helper/security_logger.py` (new file)

```python
import logging
import json
from datetime import datetime
from pathlib import Path

# Configure security logging
log_dir = Path(__file__).parent / "logs"
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / "security.log"),
        logging.StreamHandler()
    ]
)

security_logger = logging.getLogger('security')

def log_security_event(event_type, details, severity='INFO'):
    """
    Log security events
    event_type: AUTH_FAIL, FILE_UPLOAD, FILE_DELETE, ACCESS_DENIED, etc.
    """
    log_entry = {
        'timestamp': datetime.utcnow().isoformat(),
        'event_type': event_type,
        'details': details,
        'severity': severity
    }

    log_method = getattr(security_logger, severity.lower())
    log_method(json.dumps(log_entry))

# Usage in app.py:
from security_logger import log_security_event

# After failed auth:
log_security_event('AUTH_FAIL', {'reason': 'Invalid password'}, 'WARNING')

# After file upload:
log_security_event('FILE_UPLOAD', {'filename': filename, 'size': size}, 'INFO')
```

### 11. Session Timeout (10 min)
**File:** `/Users/anthony/Tax Helper/app.py`

```python
# Add after authentication check:
import time

SESSION_TIMEOUT_MINUTES = 30

if 'last_activity' not in st.session_state:
    st.session_state.last_activity = time.time()

# Check timeout
inactive_time = time.time() - st.session_state.last_activity
if inactive_time > SESSION_TIMEOUT_MINUTES * 60:
    st.session_state.clear()
    st.warning("⏱️ Session expired due to inactivity. Please log in again.")
    st.rerun()

# Update activity time
st.session_state.last_activity = time.time()
```

---

## MEDIUM PRIORITY - Fix Within 2 Weeks

### 12. Update Dependencies (5 min)
```bash
pip install --upgrade streamlit pillow sqlalchemy pandas openpyxl python-dateutil

# Check for vulnerabilities:
pip install pip-audit
pip-audit

# Update requirements.txt:
pip freeze > requirements.txt
```

### 13. Input Length Validation (15 min)
**File:** `/Users/anthony/Tax Helper/app.py`

```python
# Add validation function:
MAX_LENGTHS = {
    'description': 500,
    'supplier': 200,
    'merchant': 200,
    'notes': 2000,
    'category': 100,
}

def validate_length(value, field_name):
    """Enforce maximum lengths"""
    if field_name in MAX_LENGTHS:
        max_len = MAX_LENGTHS[field_name]
        if len(str(value)) > max_len:
            raise ValueError(f"{field_name} exceeds maximum length of {max_len}")
    return value

# Use in forms:
description = st.text_input("Description", max_chars=500)
description = validate_length(description, 'description')
```

### 14. Sensitive Data Redaction in Logs (10 min)
**File:** `/Users/anthony/Tax Helper/security_logger.py`

```python
def sanitize_log_data(data):
    """Remove sensitive fields from logs"""
    sensitive_fields = ['amount', 'balance', 'paid_in', 'paid_out', 'tax_deducted']

    if isinstance(data, dict):
        return {
            k: '***' if k in sensitive_fields else v
            for k, v in data.items()
        }
    return data

# Update log_security_event:
def log_security_event(event_type, details, severity='INFO'):
    details = sanitize_log_data(details)
    # ... rest of function
```

### 15. Add CSRF-like Protection (15 min)
**File:** `/Users/anthony/Tax Helper/app.py`

```python
import secrets

def generate_form_token():
    """Generate CSRF-like token for forms"""
    if 'form_token' not in st.session_state:
        st.session_state.form_token = secrets.token_urlsafe(32)
    return st.session_state.form_token

def validate_form_token(token):
    """Validate form token"""
    expected = st.session_state.get('form_token', '')
    return token == expected and token != ''

# In critical forms:
with st.form("delete_expense"):
    form_token = st.text_input("token", value=generate_form_token(), disabled=True, label_visibility="hidden")

    if st.form_submit_button("Delete"):
        if not validate_form_token(form_token):
            st.error("Invalid form token. Please refresh.")
            st.stop()
        # ... process deletion
```

---

## Configuration Files to Create

### 1. .streamlit/config.toml
```toml
[server]
enableCORS = false
enableXsrfProtection = true
maxUploadSize = 10

[browser]
gatherUsageStats = false

[logger]
level = "info"
```

### 2. .env (DO NOT commit to git)
```bash
TAX_HELPER_PASSWORD=YourSecurePasswordHere123!
TAX_HELPER_DEBUG=false
DB_ENCRYPTION_KEY=generate-with-secrets-token-urlsafe-32
```

### 3. .gitignore additions
```
# Security
.env
*.log
logs/
security.log
*.db
receipts/
config/*.key
*.pem
```

### 4. .bandit (security scanner config)
```yaml
exclude_dirs:
  - /tests
  - /migrations

skips:
  - B101  # assert_used (OK in tests)
```

---

## Testing Checklist

After implementing fixes, test:

```bash
# 1. Path traversal test
# Try uploading receipt with merchant name: "../../etc/passwd"
# Expected: Should be sanitized to "etcpasswd"

# 2. File type validation
# Rename .exe file to .jpg and upload
# Expected: Should reject with "File type mismatch"

# 3. Authentication
# Clear browser cache, reload app
# Expected: Should prompt for password

# 4. Rate limiting
# Upload 6 batches of receipts within 1 hour
# Expected: 6th upload should fail with rate limit error

# 5. Database permissions
ls -la tax_helper.db
# Expected: -rw------- (600)

# 6. Session timeout
# Log in, wait 31 minutes without interaction
# Expected: Session expired message

# 7. Dependency vulnerabilities
pip-audit
# Expected: No critical vulnerabilities

# 8. Static analysis
bandit -r . -f screen
# Expected: No high/critical issues
```

---

## Quick Security Scan Commands

```bash
# 1. Check file permissions
find . -type f -name "*.db" -exec ls -la {} \;

# 2. Scan for hardcoded secrets
grep -r "password\|secret\|api_key" --include="*.py" .

# 3. Check for debug mode
grep -n "DEBUG = True" *.py

# 4. Find world-writable files
find . -type f -perm -002

# 5. Scan dependencies
pip-audit --format json

# 6. Static analysis
bandit -r . -ll -i

# 7. Check for sensitive files
ls -la .env config/ receipts/
```

---

## Emergency Incident Response

If you discover active exploitation:

1. **Immediate Actions:**
   ```bash
   # Shut down application
   pkill -f streamlit

   # Backup database
   cp tax_helper.db tax_helper.db.backup.$(date +%Y%m%d_%H%M%S)

   # Check for unauthorized changes
   sqlite3 tax_helper.db "SELECT * FROM audit_log ORDER BY timestamp DESC LIMIT 50;"
   ```

2. **Forensics:**
   ```bash
   # Check access logs
   tail -100 logs/security.log

   # Find recently modified files
   find . -type f -mtime -1 -ls

   # Check for uploaded malicious files
   find receipts/ -type f -exec file {} \; | grep -v "image\|PDF"
   ```

3. **Recovery:**
   - Restore from backup if data compromised
   - Change all passwords
   - Review and fix vulnerability
   - Notify affected users if personal data exposed

---

## Secure Deployment Checklist

Before deploying to production:

- [ ] All Critical fixes applied
- [ ] All High priority fixes applied
- [ ] Authentication enabled with strong password
- [ ] DEBUG = False
- [ ] Database permissions set to 600
- [ ] HTTPS enabled (use reverse proxy)
- [ ] Security headers configured
- [ ] Rate limiting enabled
- [ ] Logging configured
- [ ] Backup strategy in place
- [ ] Incident response plan documented
- [ ] Security testing completed
- [ ] Dependencies updated and scanned
- [ ] .env file secured (not in git)
- [ ] Receipts directory secured

---

## Resources

- **OWASP Cheat Sheets:** https://cheatsheetseries.owasp.org/
- **Python Security Best Practices:** https://python.readthedocs.io/en/latest/library/security_warnings.html
- **Streamlit Security:** https://docs.streamlit.io/library/advanced-features/security

---

**Last Updated:** 2025-10-19
**Next Review:** After implementing all Critical and High priority fixes
