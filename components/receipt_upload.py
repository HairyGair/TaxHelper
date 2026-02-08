"""
Receipt Upload Component for Tax Helper
Handles drag & drop upload, image gallery, receipt linking, and storage
"""

import streamlit as st
import os
from datetime import datetime
from PIL import Image
import io
import base64
from pathlib import Path
from typing import Optional, List, Dict, Any
import json
import re
import unicodedata

# Try to import werkzeug's secure_filename, fallback to our own implementation
try:
    from werkzeug.utils import secure_filename
except ImportError:
    # Fallback implementation if werkzeug is not available
    def secure_filename(filename: str) -> str:
        """
        Secure filename implementation (fallback when werkzeug not available)
        Based on werkzeug's implementation
        """
        if not filename:
            return 'unnamed'

        # Normalize unicode characters
        filename = unicodedata.normalize('NFKD', filename)
        filename = filename.encode('ascii', 'ignore').decode('ascii')

        # Remove path separators and special chars
        filename = re.sub(r'[^\w\s.-]', '', filename)
        filename = re.sub(r'[-\s]+', '-', filename)
        filename = filename.strip('.-')

        if not filename:
            return 'unnamed'

        return filename


# Configuration
RECEIPTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'receipts')
MAX_FILE_SIZE_MB = 10
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
ALLOWED_EXTENSIONS = ['png', 'jpg', 'jpeg', 'pdf']
THUMBNAIL_SIZE = (200, 200)


def ensure_receipts_directory():
    """
    Create receipts directory if it doesn't exist
    Returns the absolute path to the receipts directory
    Security: Creates directory with restrictive permissions (0o700)
    """
    os.makedirs(RECEIPTS_DIR, mode=0o700, exist_ok=True)
    return RECEIPTS_DIR


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent path traversal attacks

    Security measures:
    - Remove directory traversal sequences (../, ..\)
    - Remove absolute path indicators
    - Keep only alphanumeric, dash, underscore, and dot
    - Limit filename length

    Args:
        filename: Original filename

    Returns:
        Sanitized safe filename
    """
    if not filename:
        return "unknown_file.jpg"

    # Use werkzeug's secure_filename as first pass
    safe_name = secure_filename(filename)

    # Additional sanitization: remove any remaining path separators
    safe_name = safe_name.replace('/', '_').replace('\\', '_')

    # Remove any dots at the start (hidden files) or multiple consecutive dots
    safe_name = re.sub(r'^\.+', '', safe_name)
    safe_name = re.sub(r'\.{2,}', '.', safe_name)

    # Limit filename length (keep extension)
    name_parts = safe_name.rsplit('.', 1)
    if len(name_parts) == 2:
        name, ext = name_parts
        name = name[:100]  # Limit base name to 100 chars
        safe_name = f"{name}.{ext}"
    else:
        safe_name = safe_name[:100]

    # Ensure we have something left after sanitization
    if not safe_name or safe_name == '.':
        safe_name = "sanitized_file.jpg"

    return safe_name


def validate_file_path(file_path: str) -> bool:
    """
    Validate that file path is within receipts directory
    Prevents directory traversal attacks

    Args:
        file_path: Path to validate

    Returns:
        True if path is safe, False otherwise
    """
    try:
        # Get absolute paths
        receipts_dir = os.path.abspath(RECEIPTS_DIR)
        full_path = os.path.abspath(file_path)

        # Check if file path is within receipts directory
        # Use os.path.commonpath to ensure no traversal
        common = os.path.commonpath([receipts_dir, full_path])
        return common == receipts_dir
    except (ValueError, TypeError):
        return False


def generate_receipt_filename(date: datetime.date, merchant: str, amount: float, extension: str) -> str:
    """
    Auto-generate receipt filename in format: YYYYMMDD_merchant_amount.ext

    Security: All inputs are sanitized to prevent path traversal

    Args:
        date: Transaction/expense date
        merchant: Merchant/supplier name
        amount: Transaction amount
        extension: File extension (png, jpg, pdf)

    Returns:
        Sanitized filename

    Example:
        >>> generate_receipt_filename(datetime(2024, 3, 15).date(), "Tesco", 45.99, "jpg")
        '20240315_tesco_45-99.jpg'
    """
    # Format date as YYYYMMDD
    date_str = date.strftime('%Y%m%d') if hasattr(date, 'strftime') else str(date).replace('-', '')

    # Clean merchant name (remove special chars, convert to lowercase)
    # Security: Only allow alphanumeric and spaces
    merchant_clean = ''.join(c for c in merchant if c.isalnum() or c.isspace()).strip()
    merchant_clean = merchant_clean.replace(' ', '_').lower()[:30]  # Limit to 30 chars

    # Fallback if merchant name becomes empty after sanitization
    if not merchant_clean:
        merchant_clean = "unknown"

    # Format amount (replace . with -)
    # Security: Validate amount is a number
    try:
        amount_str = f"{float(amount):.2f}".replace('.', '-')
    except (ValueError, TypeError):
        amount_str = "0-00"

    # Ensure extension doesn't have leading dot and is allowed
    ext = extension.lower().lstrip('.')
    if ext not in ALLOWED_EXTENSIONS:
        ext = 'jpg'  # Default to jpg if invalid extension

    # Check if file exists, if so add counter
    base_filename = f"{date_str}_{merchant_clean}_{amount_str}"
    filename = f"{base_filename}.{ext}"

    # Security: Sanitize the final filename
    filename = sanitize_filename(filename)

    counter = 1
    while os.path.exists(os.path.join(RECEIPTS_DIR, filename)):
        filename = sanitize_filename(f"{base_filename}_{counter}.{ext}")
        counter += 1
        # Prevent infinite loop
        if counter > 1000:
            filename = sanitize_filename(f"{base_filename}_{os.urandom(4).hex()}.{ext}")
            break

    return filename


def save_receipt(uploaded_file, date: datetime.date, merchant: str, amount: float) -> Optional[str]:
    """
    Save uploaded receipt to receipts directory

    Security measures:
    - Validates file size
    - Validates file extension against whitelist
    - Sanitizes filename
    - Validates final path is within receipts directory
    - Sets restrictive file permissions (0o600)

    Args:
        uploaded_file: Streamlit UploadedFile object
        date: Transaction/expense date
        merchant: Merchant/supplier name
        amount: Transaction amount

    Returns:
        Relative path to saved file (relative to project root), or None on error

    Example:
        >>> path = save_receipt(file, datetime(2024, 3, 15).date(), "Tesco", 45.99)
        >>> print(path)  # 'receipts/20240315_tesco_45-99.jpg'
    """
    try:
        # Ensure directory exists
        ensure_receipts_directory()

        # Security: Validate file size
        if uploaded_file.size > MAX_FILE_SIZE_BYTES:
            st.error(f"File size ({uploaded_file.size / 1024 / 1024:.1f}MB) exceeds maximum allowed ({MAX_FILE_SIZE_MB}MB)")
            return None

        # Security: Validate file size is not zero
        if uploaded_file.size == 0:
            st.error("File is empty")
            return None

        # Security: Get and validate file extension
        if '.' not in uploaded_file.name:
            st.error("File must have an extension")
            return None

        file_ext = uploaded_file.name.split('.')[-1].lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            st.error(f"File type '.{file_ext}' not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}")
            return None

        # Security: Generate and sanitize filename
        filename = generate_receipt_filename(date, merchant, amount, file_ext)
        file_path = os.path.join(RECEIPTS_DIR, filename)

        # Security: Validate the final path is safe
        if not validate_file_path(file_path):
            st.error("Invalid file path detected")
            return None

        # Save file with restrictive permissions
        with open(file_path, 'wb') as f:
            f.write(uploaded_file.getbuffer())

        # Security: Set file permissions to 0o600 (owner read/write only)
        os.chmod(file_path, 0o600)

        # Return relative path
        relative_path = os.path.join('receipts', filename)
        return relative_path

    except Exception as e:
        # Security: Don't expose system paths or detailed error info
        st.error("Error saving receipt. Please try again.")
        # Log the actual error for debugging (but don't show to user)
        import logging
        logging.error(f"Receipt save error: {str(e)}")
        return None


def upload_receipt(
    expense_id: Optional[int] = None,
    transaction_id: Optional[int] = None,
    date: Optional[datetime.date] = None,
    merchant: str = "Unknown",
    amount: float = 0.0,
    session=None,
    key_suffix: str = ""
) -> Optional[str]:
    """
    Render receipt upload widget with drag & drop support

    Args:
        expense_id: ID of expense record to link receipt to
        transaction_id: ID of transaction record to link receipt to
        date: Date for filename generation
        merchant: Merchant name for filename generation
        amount: Amount for filename generation
        session: SQLAlchemy session for database updates
        key_suffix: Unique suffix for widget key to avoid conflicts

    Returns:
        Relative path to uploaded receipt, or None

    Usage:
        # In expense editing form
        receipt_path = upload_receipt(
            expense_id=expense.id,
            date=expense.date,
            merchant=expense.supplier,
            amount=expense.amount,
            session=session,
            key_suffix=f"expense_{expense.id}"
        )
    """
    from models import Expense, Transaction

    # Use current date if not provided
    if date is None:
        date = datetime.now().date()

    st.markdown("### Upload Receipt")
    st.caption(f"Drag & drop or click to upload (Max {MAX_FILE_SIZE_MB}MB, {', '.join(ALLOWED_EXTENSIONS).upper()})")

    # File uploader with drag & drop
    uploaded_file = st.file_uploader(
        "Choose receipt file",
        type=ALLOWED_EXTENSIONS,
        key=f"receipt_uploader_{key_suffix}",
        label_visibility="collapsed"
    )

    if uploaded_file is not None:
        # Show file info
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.info(f"📎 **{uploaded_file.name}**")
        with col2:
            st.metric("Size", f"{uploaded_file.size / 1024:.1f} KB")
        with col3:
            st.metric("Type", uploaded_file.type)

        # Preview for images
        if uploaded_file.type.startswith('image/'):
            try:
                image = Image.open(uploaded_file)
                st.image(image, caption=uploaded_file.name, use_container_width=True)
                # Reset file pointer after reading for preview
                uploaded_file.seek(0)
            except Exception as e:
                st.warning(f"Could not preview image: {str(e)}")

        # Save button
        if st.button("💾 Save Receipt", key=f"save_receipt_{key_suffix}", type="primary"):
            receipt_path = save_receipt(uploaded_file, date, merchant, amount)

            if receipt_path and session:
                # Update database with receipt path
                try:
                    if expense_id:
                        expense = session.query(Expense).filter(Expense.id == expense_id).first()
                        if expense:
                            # Handle multiple receipts (JSON array)
                            existing_receipts = []
                            if expense.receipt_link:
                                try:
                                    existing_receipts = json.loads(expense.receipt_link)
                                    if not isinstance(existing_receipts, list):
                                        existing_receipts = [expense.receipt_link]
                                except (json.JSONDecodeError, TypeError):
                                    existing_receipts = [expense.receipt_link]

                            existing_receipts.append(receipt_path)
                            expense.receipt_link = json.dumps(existing_receipts)
                            session.commit()
                            st.success(f"✅ Receipt saved and linked to expense!")

                    elif transaction_id:
                        # For transactions, store in notes field temporarily
                        # (could add a receipts field to Transaction model)
                        transaction = session.query(Transaction).filter(Transaction.id == transaction_id).first()
                        if transaction:
                            notes = transaction.notes or ""
                            receipt_tag = f"[RECEIPT: {receipt_path}]"
                            if receipt_tag not in notes:
                                transaction.notes = f"{notes}\n{receipt_tag}".strip()
                                session.commit()
                                st.success(f"✅ Receipt saved and linked to transaction!")

                    return receipt_path

                except Exception as e:
                    st.error(f"Error linking receipt to database: {str(e)}")
                    session.rollback()

            elif receipt_path:
                st.success(f"✅ Receipt saved: {receipt_path}")
                return receipt_path

    return None


def get_receipt_paths(receipt_link: Optional[str]) -> List[str]:
    """
    Parse receipt_link field and return list of receipt paths
    Handles both single path strings and JSON arrays

    Args:
        receipt_link: Value from database receipt_link field

    Returns:
        List of receipt paths
    """
    if not receipt_link:
        return []

    try:
        # Try parsing as JSON array
        paths = json.loads(receipt_link)
        if isinstance(paths, list):
            return paths
        else:
            return [paths]
    except (json.JSONDecodeError, TypeError):
        # Single path string
        return [receipt_link]


def render_receipt_gallery(
    receipt_link: Optional[str],
    session=None,
    record_id: Optional[int] = None,
    record_type: str = "expense",
    key_suffix: str = ""
) -> None:
    """
    Render gallery of receipt thumbnails with view/delete options

    Args:
        receipt_link: Receipt path(s) from database (single path or JSON array)
        session: SQLAlchemy session for delete operations
        record_id: ID of expense/transaction record
        record_type: Type of record ('expense' or 'transaction')
        key_suffix: Unique suffix for widget keys

    Usage:
        # Show receipts for an expense
        render_receipt_gallery(
            expense.receipt_link,
            session=session,
            record_id=expense.id,
            record_type="expense",
            key_suffix=f"exp_{expense.id}"
        )
    """
    from models import Expense, Transaction

    receipt_paths = get_receipt_paths(receipt_link)

    if not receipt_paths:
        st.caption("📎 No receipts attached")
        return

    st.markdown(f"### 📎 Receipts ({len(receipt_paths)})")

    # Display receipts in grid
    cols_per_row = 3
    for i in range(0, len(receipt_paths), cols_per_row):
        cols = st.columns(cols_per_row)

        for j, col in enumerate(cols):
            idx = i + j
            if idx >= len(receipt_paths):
                break

            receipt_path = receipt_paths[idx]
            full_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), receipt_path)

            # Security: Validate path before processing
            if not validate_file_path(full_path):
                continue  # Skip invalid paths silently

            with col:
                # Receipt card
                with st.container():
                    st.markdown(
                        f"""
                        <div style="border: 1px solid #ddd; border-radius: 8px; padding: 10px; margin-bottom: 10px;">
                        """,
                        unsafe_allow_html=True
                    )

                    # Show thumbnail or icon
                    if os.path.exists(full_path):
                        file_ext = receipt_path.split('.')[-1].lower()

                        # Security: Validate file extension
                        if file_ext not in ALLOWED_EXTENSIONS:
                            st.warning("Invalid file type")
                            continue

                        if file_ext in ['png', 'jpg', 'jpeg']:
                            try:
                                img = Image.open(full_path)
                                img.thumbnail(THUMBNAIL_SIZE)
                                st.image(img, use_container_width=True)
                            except Exception as e:
                                st.error("Could not load image")

                        elif file_ext == 'pdf':
                            st.markdown("📄 PDF Document")
                            st.caption(os.path.basename(receipt_path))

                        # File info
                        file_size = os.path.getsize(full_path)
                        st.caption(f"Size: {file_size / 1024:.1f} KB")

                        # Action buttons
                        action_col1, action_col2 = st.columns(2)

                        with action_col1:
                            # View button
                            if st.button("👁️ View", key=f"view_{key_suffix}_{idx}", use_container_width=True):
                                view_receipt_fullsize(receipt_path, key_suffix=f"{key_suffix}_{idx}")

                        with action_col2:
                            # Delete button
                            if st.button("🗑️ Delete", key=f"delete_{key_suffix}_{idx}", use_container_width=True):
                                if delete_receipt(receipt_path, receipt_paths, session, record_id, record_type):
                                    st.rerun()

                    else:
                        st.warning(f"File not found: {os.path.basename(receipt_path)}")
                        if st.button("🗑️ Remove", key=f"remove_{key_suffix}_{idx}", use_container_width=True):
                            if delete_receipt(receipt_path, receipt_paths, session, record_id, record_type):
                                st.rerun()

                    st.markdown("</div>", unsafe_allow_html=True)


def view_receipt_fullsize(receipt_path: str, key_suffix: str = "") -> None:
    """
    Display receipt in full size modal

    Security: Validates file path before access

    Args:
        receipt_path: Relative path to receipt file
        key_suffix: Unique suffix for widget keys
    """
    full_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), receipt_path)

    # Security: Validate the path is safe
    if not validate_file_path(full_path):
        st.error("Invalid file path")
        return

    if not os.path.exists(full_path):
        st.error("Receipt file not found")
        return

    file_ext = receipt_path.split('.')[-1].lower()

    # Security: Validate file extension
    if file_ext not in ALLOWED_EXTENSIONS:
        st.error("Invalid file type")
        return

    # Use expander for full-size view
    # Security: Use sanitized basename for display
    safe_basename = sanitize_filename(os.path.basename(receipt_path))
    with st.expander(f"📋 {safe_basename}", expanded=True):
        if file_ext in ['png', 'jpg', 'jpeg']:
            try:
                img = Image.open(full_path)
                st.image(img, use_container_width=True)
            except Exception as e:
                st.error("Could not load image")

        elif file_ext == 'pdf':
            st.info("PDF viewing in browser - download to view full document")

            # Provide download button
            with open(full_path, 'rb') as f:
                pdf_bytes = f.read()
                st.download_button(
                    label="⬇️ Download PDF",
                    data=pdf_bytes,
                    file_name=os.path.basename(receipt_path),
                    mime="application/pdf",
                    key=f"download_pdf_{key_suffix}"
                )

        # Download button for images too
        if file_ext in ['png', 'jpg', 'jpeg']:
            with open(full_path, 'rb') as f:
                img_bytes = f.read()
                st.download_button(
                    label="⬇️ Download Image",
                    data=img_bytes,
                    file_name=os.path.basename(receipt_path),
                    mime=f"image/{file_ext}",
                    key=f"download_img_{key_suffix}"
                )


def delete_receipt(
    receipt_path: str,
    all_receipt_paths: List[str],
    session,
    record_id: Optional[int],
    record_type: str
) -> bool:
    """
    Delete receipt file and remove from database

    Security: Validates file path before deletion

    Args:
        receipt_path: Path to receipt to delete
        all_receipt_paths: All receipt paths for this record
        session: SQLAlchemy session
        record_id: ID of expense/transaction record
        record_type: Type of record ('expense' or 'transaction')

    Returns:
        True if successful, False otherwise
    """
    from models import Expense, Transaction

    try:
        # Delete physical file
        full_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), receipt_path)

        # Security: Validate the path is safe before deletion
        if not validate_file_path(full_path):
            st.error("Invalid file path")
            return False

        if os.path.exists(full_path):
            os.remove(full_path)

        # Update database
        if session and record_id:
            # Remove from list
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
                    # Remove receipt tag from notes
                    receipt_tag = f"[RECEIPT: {receipt_path}]"
                    if transaction.notes:
                        transaction.notes = transaction.notes.replace(receipt_tag, "").strip()
                    session.commit()

        st.success("Receipt deleted successfully!")
        return True

    except Exception as e:
        st.error(f"Error deleting receipt: {str(e)}")
        if session:
            session.rollback()
        return False


def render_receipt_indicator(receipt_link: Optional[str]) -> str:
    """
    Render small receipt indicator badge for transaction cards

    Args:
        receipt_link: Receipt path(s) from database

    Returns:
        HTML string for badge

    Usage:
        # In transaction list
        if transaction.notes and '[RECEIPT:' in transaction.notes:
            st.markdown(render_receipt_indicator(transaction.notes), unsafe_allow_html=True)
    """
    receipt_paths = get_receipt_paths(receipt_link)

    if not receipt_paths:
        return ""

    count = len(receipt_paths)
    badge_html = f"""
    <span style="
        background-color: #36c7a0;
        color: white;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: bold;
        margin-left: 8px;
    ">
        📎 {count}
    </span>
    """
    return badge_html


def extract_receipts_from_notes(notes: Optional[str]) -> List[str]:
    """
    Extract receipt paths from transaction notes field
    Looks for [RECEIPT: path] tags

    Args:
        notes: Transaction notes field

    Returns:
        List of receipt paths
    """
    if not notes:
        return []

    import re
    pattern = r'\[RECEIPT: ([^\]]+)\]'
    matches = re.findall(pattern, notes)
    return matches


# Database schema changes needed (add to migration if implementing)
SCHEMA_CHANGES_NEEDED = """
-- Option 1: Keep existing receipt_link in Expense (supports JSON array - already compatible)
-- No changes needed for Expense table

-- Option 2: Add receipt_link to Transaction table (recommended)
ALTER TABLE transactions ADD COLUMN receipt_link TEXT;

-- Note: The current implementation stores receipts in Transaction.notes field as [RECEIPT: path] tags
-- This works but adding a dedicated column would be cleaner
"""


# Example usage documentation
USAGE_EXAMPLES = """
===========================================
RECEIPT UPLOAD COMPONENT - USAGE EXAMPLES
===========================================

1. UPLOAD RECEIPT IN EXPENSE FORM
----------------------------------
from components.receipt_upload import upload_receipt

# When adding/editing an expense
with st.form("expense_form"):
    date = st.date_input("Date")
    supplier = st.text_input("Supplier")
    amount = st.number_input("Amount")

    # ... other fields ...

    if st.form_submit_button("Save"):
        # Save expense first
        expense = Expense(
            date=date,
            supplier=supplier,
            amount=amount,
            # ... other fields ...
        )
        session.add(expense)
        session.commit()

        # Then upload receipt
        receipt_path = upload_receipt(
            expense_id=expense.id,
            date=expense.date,
            merchant=expense.supplier,
            amount=expense.amount,
            session=session,
            key_suffix=f"new_expense"
        )


2. SHOW RECEIPT GALLERY
------------------------
from components.receipt_upload import render_receipt_gallery

# Display receipts for an expense
expense = session.query(Expense).filter(Expense.id == expense_id).first()
render_receipt_gallery(
    expense.receipt_link,
    session=session,
    record_id=expense.id,
    record_type="expense",
    key_suffix=f"exp_{expense.id}"
)


3. SHOW RECEIPT INDICATOR ON TRANSACTION CARD
----------------------------------------------
from components.receipt_upload import render_receipt_indicator, extract_receipts_from_notes

# In transaction list view
for transaction in transactions:
    col1, col2, col3 = st.columns([3, 2, 1])

    with col1:
        st.write(transaction.description)

    with col2:
        st.write(format_currency(transaction.paid_out))

    with col3:
        # Show receipt indicator if receipts exist
        receipts = extract_receipts_from_notes(transaction.notes)
        if receipts:
            st.markdown(render_receipt_indicator(transaction.notes), unsafe_allow_html=True)


4. LINK RECEIPT TO TRANSACTION IN FINAL REVIEW
-----------------------------------------------
from components.receipt_upload import upload_receipt

# In final review page when categorizing transaction
transaction = session.query(Transaction).filter(Transaction.id == txn_id).first()

with st.expander("📎 Attach Receipt (Optional)"):
    receipt_path = upload_receipt(
        transaction_id=transaction.id,
        date=transaction.date,
        merchant=transaction.description[:50],  # Use description as merchant
        amount=transaction.paid_out or transaction.paid_in,
        session=session,
        key_suffix=f"txn_{transaction.id}"
    )


5. STANDALONE RECEIPT UPLOAD (NO DB LINKING)
---------------------------------------------
from components.receipt_upload import save_receipt

uploaded_file = st.file_uploader("Upload receipt", type=['png', 'jpg', 'jpeg', 'pdf'])
if uploaded_file:
    receipt_path = save_receipt(
        uploaded_file,
        date=datetime.now().date(),
        merchant="Test Merchant",
        amount=99.99
    )
    st.success(f"Receipt saved: {receipt_path}")
"""
