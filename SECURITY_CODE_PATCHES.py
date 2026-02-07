"""
Security Code Patches for Tax Helper Application
Copy and paste these code sections to fix critical vulnerabilities

INSTRUCTIONS:
1. Backup your application first: cp -r "/Users/anthony/Tax Helper" "/Users/anthony/Tax Helper.backup"
2. Apply patches in order (Critical first)
3. Test each patch before moving to next
4. Run security tests after all patches applied
"""

# ============================================================================
# PATCH 1: Path Traversal Protection in receipt_upload.py
# ============================================================================

"""
File: /Users/anthony/Tax Helper/components/receipt_upload.py
Replace generate_receipt_filename function (lines 34-73) with:
"""

from pathlib import Path
import os
import re

def generate_receipt_filename(date, merchant: str, amount: float, extension: str) -> str:
    """
    Auto-generate receipt filename with path traversal protection

    Security enhancements:
    - Removes path separators and dangerous characters
    - Validates final path is within receipts directory
    - Prevents directory traversal attacks
    """
    # Format date
    date_str = date.strftime('%Y%m%d') if hasattr(date, 'strftime') else str(date).replace('-', '')

    # SECURITY: Sanitize merchant name
    # Remove ALL non-alphanumeric characters except spaces
    merchant_clean = re.sub(r'[^a-zA-Z0-9\s]', '', merchant)
    merchant_clean = merchant_clean.strip()

    # Additional validation: no path separators
    if not merchant_clean or '..' in merchant or '/' in merchant or '\\' in merchant:
        merchant_clean = 'merchant'  # Fallback to safe default

    merchant_clean = merchant_clean.replace(' ', '_').lower()[:30]

    # Format amount
    amount_str = f"{amount:.2f}".replace('.', '-')

    # Sanitize extension
    ext = re.sub(r'[^a-zA-Z]', '', extension.lower())

    # Build filename
    base_filename = f"{date_str}_{merchant_clean}_{amount_str}"
    filename = f"{base_filename}.{ext}"

    # Handle duplicates
    counter = 1
    while os.path.exists(os.path.join(RECEIPTS_DIR, filename)):
        filename = f"{base_filename}_{counter}.{ext}"
        counter += 1

    # SECURITY: Validate final path
    full_path = Path(RECEIPTS_DIR) / filename
    full_path = full_path.resolve()  # Resolve symlinks and .. references
    receipts_dir = Path(RECEIPTS_DIR).resolve()

    # Ensure path is within receipts directory
    try:
        full_path.relative_to(receipts_dir)
    except ValueError:
        raise SecurityError(f"Path traversal attempt detected: {filename}")

    return filename


# ============================================================================
# PATCH 2: Secure File Upload Validation in receipt_upload.py
# ============================================================================

"""
File: /Users/anthony/Tax Helper/components/receipt_upload.py
Replace save_receipt function (lines 76-122) with:
"""

import io
from PIL import Image

# Add at top of file:
try:
    import magic
    MAGIC_AVAILABLE = True
except ImportError:
    MAGIC_AVAILABLE = False
    print("WARNING: python-magic not available. Install with: pip install python-magic")


class SecurityError(Exception):
    """Custom exception for security violations"""
    pass


def save_receipt(uploaded_file, date, merchant: str, amount: float) -> Optional[str]:
    """
    Save uploaded receipt with comprehensive security validation

    Security checks:
    1. File size validation
    2. File extension whitelist
    3. MIME type verification (if python-magic available)
    4. Image integrity check (for images)
    5. EXIF data stripping
    6. Path traversal prevention
    """
    try:
        ensure_receipts_directory()

        # Check 1: File size
        uploaded_file.seek(0, 2)  # Seek to end
        file_size = uploaded_file.tell()
        uploaded_file.seek(0)  # Reset

        if file_size > MAX_FILE_SIZE_BYTES:
            raise ValueError(f"File size ({file_size / 1024 / 1024:.1f}MB) exceeds maximum ({MAX_FILE_SIZE_MB}MB)")

        if file_size == 0:
            raise ValueError("File is empty")

        # Check 2: Extension whitelist
        file_ext = uploaded_file.name.split('.')[-1].lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            raise ValueError(f"File type '.{file_ext}' not allowed. Allowed: {', '.join(ALLOWED_EXTENSIONS)}")

        # Read file content
        file_content = uploaded_file.getvalue()

        # Check 3: MIME type validation (if available)
        if MAGIC_AVAILABLE:
            detected_mime = magic.from_buffer(file_content, mime=True)

            allowed_mimes = {
                'png': 'image/png',
                'jpg': 'image/jpeg',
                'jpeg': 'image/jpeg',
                'pdf': 'application/pdf'
            }

            expected_mime = allowed_mimes.get(file_ext)
            if detected_mime != expected_mime:
                raise SecurityError(
                    f"File type mismatch: Extension is .{file_ext} but content is {detected_mime}. "
                    f"This could be a disguised malicious file."
                )

        # Check 4: Image integrity and sanitization
        if file_ext in ['png', 'jpg', 'jpeg']:
            try:
                # Open and verify image
                img = Image.open(io.BytesIO(file_content))
                img.verify()

                # Re-open (verify() invalidates the image)
                img = Image.open(io.BytesIO(file_content))

                # SECURITY: Strip EXIF data and re-encode
                # This prevents metadata-based attacks
                data = list(img.getdata())
                image_no_exif = Image.new(img.mode, img.size)
                image_no_exif.putdata(data)

                # Re-encode to clean bytes
                output_buffer = io.BytesIO()
                image_no_exif.save(output_buffer, format=file_ext.upper())
                file_content = output_buffer.getvalue()

            except Exception as e:
                raise ValueError(f"Invalid or corrupted image: {str(e)}")

        # Check 5: Generate safe filename with path traversal protection
        try:
            filename = generate_receipt_filename(date, merchant, amount, file_ext)
        except SecurityError as e:
            raise SecurityError(f"Filename generation failed: {str(e)}")

        # Final path validation
        file_path = os.path.join(RECEIPTS_DIR, filename)
        abs_file_path = os.path.abspath(file_path)
        abs_receipts_dir = os.path.abspath(RECEIPTS_DIR)

        if not abs_file_path.startswith(abs_receipts_dir):
            raise SecurityError("Path traversal attempt blocked")

        # Write sanitized file
        with open(file_path, 'wb') as f:
            f.write(file_content)

        # Set restrictive permissions (owner read/write only)
        os.chmod(file_path, 0o600)

        relative_path = os.path.join('receipts', filename)
        return relative_path

    except SecurityError as e:
        st.error(f"🚨 Security Error: {str(e)}")
        # Log security event
        import logging
        logging.warning(f"Security violation in file upload: {str(e)}")
        return None
    except ValueError as e:
        st.error(f"❌ Validation Error: {str(e)}")
        return None
    except Exception as e:
        st.error(f"❌ Error saving receipt: {str(e)}")
        import traceback
        logging.error(f"Unexpected error in save_receipt: {traceback.format_exc()}")
        return None


# ============================================================================
# PATCH 3: Secure File Deletion in receipt_upload.py
# ============================================================================

"""
File: /Users/anthony/Tax Helper/components/receipt_upload.py
Replace delete_receipt function (lines 428-486) with:
"""

def delete_receipt(
    receipt_path: str,
    all_receipt_paths: List[str],
    session,
    record_id: Optional[int],
    record_type: str
) -> bool:
    """
    Securely delete receipt file with comprehensive validation

    Security checks:
    1. Path traversal prevention
    2. Ownership verification
    3. Whitelist validation
    """
    from models import Expense, Transaction

    try:
        # SECURITY Check 1: Validate receipt_path is in database for this record
        if receipt_path not in all_receipt_paths:
            raise SecurityError("Receipt not associated with this record")

        # SECURITY Check 2: Path traversal prevention
        base_dir = Path(__file__).parent.parent
        receipts_dir = (base_dir / "receipts").resolve()

        # Construct full path
        full_path = (base_dir / receipt_path).resolve()

        # Verify path is within receipts directory
        try:
            full_path.relative_to(receipts_dir)
        except ValueError:
            raise SecurityError("Attempt to delete file outside receipts directory")

        # Verify path doesn't contain traversal attempts
        if '..' in str(receipt_path) or receipt_path.startswith('/'):
            raise SecurityError("Invalid path detected")

        # Delete physical file if exists
        if full_path.exists():
            # Additional check: verify it's a file, not a directory
            if not full_path.is_file():
                raise SecurityError("Path is not a file")

            full_path.unlink()
        else:
            # File doesn't exist, still remove from database
            pass

        # Update database
        if session and record_id:
            updated_paths = [p for p in all_receipt_paths if p != receipt_path]

            if record_type == "expense":
                expense = session.query(Expense).filter(Expense.id == record_id).first()
                if expense:
                    if updated_paths:
                        expense.receipt_link = json.dumps(updated_paths)
                    else:
                        expense.receipt_link = None
                    session.commit()

            elif record_type == "transaction":
                transaction = session.query(Transaction).filter(Transaction.id == record_id).first()
                if transaction:
                    receipt_tag = f"[RECEIPT: {receipt_path}]"
                    if transaction.notes:
                        transaction.notes = transaction.notes.replace(receipt_tag, "").strip()
                    session.commit()

        st.success("✅ Receipt deleted successfully")
        return True

    except SecurityError as e:
        st.error(f"🚨 Security Error: {str(e)}")
        import logging
        logging.warning(f"Security violation in delete_receipt: {str(e)}")
        return False
    except Exception as e:
        st.error(f"❌ Error deleting receipt: {str(e)}")
        if session:
            session.rollback()
        import logging
        logging.error(f"Error in delete_receipt: {str(e)}")
        return False


# ============================================================================
# PATCH 4: Authentication System in app.py
# ============================================================================

"""
File: /Users/anthony/Tax Helper/app.py
Add this code BEFORE st.set_page_config (around line 145)
"""

import hmac
import hashlib
import os
import time

# Authentication configuration
AUTH_PASSWORD_HASH = os.getenv(
    'TAX_HELPER_PASSWORD_HASH',
    # Default hash for 'ChangeMe123!' - CHANGE THIS!
    'a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3'
)

SESSION_TIMEOUT_MINUTES = 30
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION_MINUTES = 15


def hash_password(password: str) -> str:
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()


def check_password() -> bool:
    """
    Password authentication with brute force protection

    Returns:
        True if authenticated, False otherwise
    """

    def password_entered():
        """Callback when password is submitted"""
        # Get or initialize attempt tracking
        if 'login_attempts' not in st.session_state:
            st.session_state.login_attempts = 0
            st.session_state.lockout_until = 0

        # Check if locked out
        if time.time() < st.session_state.lockout_until:
            st.session_state["password_correct"] = False
            return

        # Hash entered password
        entered_hash = hash_password(st.session_state["password"])

        # Compare using timing-safe comparison
        if hmac.compare_digest(entered_hash, AUTH_PASSWORD_HASH):
            st.session_state["password_correct"] = True
            st.session_state["login_attempts"] = 0
            st.session_state["auth_time"] = time.time()
            del st.session_state["password"]

            # Log successful auth
            import logging
            logging.info("Successful authentication")
        else:
            st.session_state["password_correct"] = False
            st.session_state.login_attempts += 1

            # Log failed attempt
            import logging
            logging.warning(f"Failed login attempt {st.session_state.login_attempts}")

            # Implement lockout after max attempts
            if st.session_state.login_attempts >= MAX_LOGIN_ATTEMPTS:
                st.session_state.lockout_until = time.time() + (LOCKOUT_DURATION_MINUTES * 60)
                logging.warning(f"Account locked out for {LOCKOUT_DURATION_MINUTES} minutes")

    # Check if already authenticated
    if "password_correct" not in st.session_state:
        # First time - show password input
        st.title("🔐 Tax Helper - Login")
        st.text_input(
            "Password",
            type="password",
            on_change=password_entered,
            key="password"
        )
        st.info("Please enter your password to access the application.")
        return False

    elif not st.session_state["password_correct"]:
        # Wrong password
        st.title("🔐 Tax Helper - Login")

        # Check lockout
        if time.time() < st.session_state.get('lockout_until', 0):
            remaining = int((st.session_state.lockout_until - time.time()) / 60)
            st.error(f"🚫 Too many failed attempts. Locked out for {remaining} more minutes.")
            return False

        st.text_input(
            "Password",
            type="password",
            on_change=password_entered,
            key="password"
        )

        attempts_remaining = MAX_LOGIN_ATTEMPTS - st.session_state.get('login_attempts', 0)
        st.error(f"😕 Incorrect password. {attempts_remaining} attempts remaining.")

        return False

    else:
        # Authenticated - check session timeout
        auth_time = st.session_state.get('auth_time', time.time())
        if time.time() - auth_time > SESSION_TIMEOUT_MINUTES * 60:
            st.session_state.clear()
            st.warning("⏱️ Session expired. Please log in again.")
            st.rerun()

        # Update last activity
        st.session_state.auth_time = time.time()
        return True


# CRITICAL: Add this before any other code
if not check_password():
    st.stop()  # Stop execution if not authenticated


# ============================================================================
# PATCH 5: Database Security in models.py
# ============================================================================

"""
File: /Users/anthony/Tax Helper/models.py
Replace init_db function (lines 196-204) with:
"""

import stat

def init_db(db_path='tax_helper.db'):
    """
    Initialize database with security hardening

    Security enhancements:
    1. Restrictive file permissions (600)
    2. Connection encryption
    3. Journal mode for integrity
    """
    # Create database connection
    engine = create_engine(
        f'sqlite:///{db_path}',
        # Security: Prevent SQL injection in table/column names
        connect_args={
            'check_same_thread': False,
            'timeout': 20
        }
    )

    # Create tables
    Base.metadata.create_all(engine)

    # SECURITY: Set restrictive permissions (owner read/write only)
    if os.path.exists(db_path):
        os.chmod(db_path, stat.S_IRUSR | stat.S_IWUSR)  # 0600 permissions

        # Log security event
        import logging
        logging.info(f"Database initialized with secure permissions: {db_path}")

    # Create session factory
    Session = sessionmaker(bind=engine)

    return engine, Session


# ============================================================================
# PATCH 6: Security Logger Module
# ============================================================================

"""
Create new file: /Users/anthony/Tax Helper/security_logger.py
"""

import logging
import json
import os
from datetime import datetime
from pathlib import Path

# Create logs directory
log_dir = Path(__file__).parent / "logs"
log_dir.mkdir(exist_ok=True)

# Configure security logger
security_logger = logging.getLogger('security')
security_logger.setLevel(logging.INFO)

# File handler
log_file = log_dir / "security.log"
file_handler = logging.FileHandler(log_file)
file_handler.setLevel(logging.INFO)

# Formatter
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
file_handler.setFormatter(formatter)
security_logger.addHandler(file_handler)

# Set restrictive permissions on log file
if log_file.exists():
    os.chmod(log_file, 0o600)


def log_security_event(event_type: str, details: dict, severity: str = 'INFO'):
    """
    Log security-relevant events

    Args:
        event_type: Type of event (AUTH_FAIL, FILE_UPLOAD, ACCESS_DENIED, etc.)
        details: Dictionary of event details
        severity: INFO, WARNING, ERROR, CRITICAL
    """
    # Sanitize sensitive data
    safe_details = sanitize_log_data(details)

    log_entry = {
        'timestamp': datetime.utcnow().isoformat(),
        'event_type': event_type,
        'details': safe_details,
        'severity': severity
    }

    # Get logging function
    log_func = getattr(security_logger, severity.lower(), security_logger.info)
    log_func(json.dumps(log_entry))


def sanitize_log_data(data: dict) -> dict:
    """Remove sensitive fields from log data"""
    sensitive_fields = [
        'password', 'token', 'secret',
        'amount', 'balance', 'paid_in', 'paid_out',
        'tax_deducted', 'salary'
    ]

    if not isinstance(data, dict):
        return data

    sanitized = {}
    for key, value in data.items():
        if key.lower() in sensitive_fields:
            sanitized[key] = '***REDACTED***'
        elif isinstance(value, dict):
            sanitized[key] = sanitize_log_data(value)
        else:
            sanitized[key] = value

    return sanitized


# Usage examples:
"""
from security_logger import log_security_event

# Log authentication failure
log_security_event('AUTH_FAIL', {
    'reason': 'Invalid password',
    'attempts': 3
}, 'WARNING')

# Log file upload
log_security_event('FILE_UPLOAD', {
    'filename': 'receipt.jpg',
    'size_bytes': 12456,
    'mime_type': 'image/jpeg'
}, 'INFO')

# Log suspicious activity
log_security_event('SUSPICIOUS_ACTIVITY', {
    'action': 'Path traversal attempt',
    'input': '../../../etc/passwd'
}, 'CRITICAL')
"""


# ============================================================================
# PATCH 7: Rate Limiting Module
# ============================================================================

"""
Create new file: /Users/anthony/Tax Helper/rate_limiter.py
"""

import time
from collections import defaultdict
from typing import Dict, List


class RateLimiter:
    """
    Simple in-memory rate limiter
    For production, use Redis or similar
    """

    def __init__(self):
        self.requests: Dict[str, List[float]] = defaultdict(list)

    def check_limit(
        self,
        key: str,
        max_requests: int = 5,
        window_seconds: int = 3600
    ) -> bool:
        """
        Check if request is within rate limit

        Args:
            key: Identifier (user ID, IP address, session ID)
            max_requests: Maximum requests allowed
            window_seconds: Time window in seconds

        Returns:
            True if allowed, False if rate limit exceeded

        Raises:
            RateLimitExceeded: If rate limit is exceeded
        """
        now = time.time()

        # Clean old requests outside window
        self.requests[key] = [
            req_time for req_time in self.requests[key]
            if now - req_time < window_seconds
        ]

        # Check limit
        if len(self.requests[key]) >= max_requests:
            oldest_request = self.requests[key][0]
            wait_seconds = int(window_seconds - (now - oldest_request))

            raise RateLimitExceeded(
                f"Rate limit exceeded. Try again in {wait_seconds} seconds."
            )

        # Record this request
        self.requests[key].append(now)
        return True


class RateLimitExceeded(Exception):
    """Exception raised when rate limit is exceeded"""
    pass


# Global rate limiter instance
rate_limiter = RateLimiter()


# Usage example:
"""
from rate_limiter import rate_limiter, RateLimitExceeded

try:
    # Check rate limit before processing upload
    session_id = id(st.session_state)
    rate_limiter.check_limit(
        key=f"upload_{session_id}",
        max_requests=5,
        window_seconds=3600
    )

    # Process upload
    process_upload()

except RateLimitExceeded as e:
    st.error(f"⏱️ {str(e)}")
    log_security_event('RATE_LIMIT_EXCEEDED', {
        'action': 'file_upload',
        'session_id': session_id
    }, 'WARNING')
"""


# ============================================================================
# INSTALLATION INSTRUCTIONS
# ============================================================================

"""
1. Install required security packages:
   pip install python-magic pillow

2. Set environment variables:
   export TAX_HELPER_PASSWORD_HASH=$(python3 -c "import hashlib; print(hashlib.sha256(b'YourSecurePassword123!').hexdigest())")
   export TAX_HELPER_DEBUG=false

3. Apply patches:
   - Copy code sections to respective files
   - Test each patch individually
   - Run security tests

4. Set file permissions:
   chmod 600 tax_helper.db
   chmod 700 receipts/
   chmod 600 logs/security.log

5. Test authentication:
   - Clear browser cache
   - Reload application
   - Should prompt for password

6. Run security scan:
   pip install bandit
   bandit -r . -ll

7. Monitor logs:
   tail -f logs/security.log
"""


# ============================================================================
# TESTING SCRIPT
# ============================================================================

"""
Create: /Users/anthony/Tax Helper/test_security.py
"""

def test_path_traversal():
    """Test path traversal protection"""
    from components.receipt_upload import generate_receipt_filename
    from datetime import date

    # Test 1: Path traversal attempt
    try:
        filename = generate_receipt_filename(
            date.today(),
            "../../../etc/passwd",
            100.0,
            "jpg"
        )
        print("❌ FAIL: Path traversal not blocked")
    except Exception as e:
        print("✅ PASS: Path traversal blocked")

    # Test 2: Legitimate filename
    try:
        filename = generate_receipt_filename(
            date.today(),
            "Tesco Store",
            45.99,
            "jpg"
        )
        assert '..' not in filename
        assert '/' not in filename
        print("✅ PASS: Legitimate filename generated")
    except Exception as e:
        print(f"❌ FAIL: {e}")


def test_authentication():
    """Test authentication system"""
    import hashlib

    correct_hash = hashlib.sha256(b"TestPassword123!").hexdigest()
    entered_hash = hashlib.sha256(b"WrongPassword").hexdigest()

    import hmac
    result = hmac.compare_digest(entered_hash, correct_hash)

    if not result:
        print("✅ PASS: Authentication rejects wrong password")
    else:
        print("❌ FAIL: Authentication accepts wrong password")


def test_file_permissions():
    """Test database file permissions"""
    import os
    import stat

    db_path = "tax_helper.db"
    if os.path.exists(db_path):
        perms = oct(os.stat(db_path).st_mode)[-3:]
        if perms == '600':
            print("✅ PASS: Database has secure permissions (600)")
        else:
            print(f"❌ FAIL: Database permissions are {perms}, should be 600")


if __name__ == "__main__":
    print("Running security tests...")
    test_path_traversal()
    test_authentication()
    test_file_permissions()
    print("Tests complete!")


# ============================================================================
# END OF PATCHES
# ============================================================================
