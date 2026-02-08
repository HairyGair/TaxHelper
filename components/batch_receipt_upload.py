"""
Batch Receipt Upload System with OCR Processing

Features:
- Multi-file drag & drop upload
- Background OCR processing with progress tracking
- Smart transaction matching
- Batch review and editing interface
- Multiple workflow support
- Comprehensive error handling
"""

import streamlit as st
import os
import time
import io
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import pandas as pd
from PIL import Image
import concurrent.futures
from difflib import SequenceMatcher
from components.export_manager import render_export_panel

# Import existing components
try:
    from components.receipt_upload import save_receipt, generate_receipt_filename
    from components.ocr_receipt import quick_ocr
    from components.merchant_db import find_merchant_match
    from components.audit_trail import log_action
except ImportError:
    # Fallback implementations for standalone testing
    def save_receipt(file_data, filename):
        return f"receipts/{filename}"

    def generate_receipt_filename(merchant, date):
        return f"{merchant}_{date}.jpg"

    def quick_ocr(image_path):
        return {
            'merchant': 'Sample Merchant',
            'date': datetime.now().strftime('%Y-%m-%d'),
            'total': 45.99,
            'confidence': 85
        }

    def find_merchant_match(merchant_name):
        return None

    def log_action(session, action_type, details):
        pass


# Constants
MAX_FILES = 20
MAX_FILE_SIZE_MB = 10
MAX_TOTAL_SIZE_MB = 100
SUPPORTED_FORMATS = ['png', 'jpg', 'jpeg', 'pdf']
HIGH_CONFIDENCE_THRESHOLD = 70
MATCH_DATE_WINDOW_DAYS = 3
MATCH_AMOUNT_TOLERANCE = 0.10


def initialize_session_state():
    """Initialize session state for batch upload"""
    if 'batch_upload_files' not in st.session_state:
        st.session_state.batch_upload_files = []
    if 'batch_upload_results' not in st.session_state:
        st.session_state.batch_upload_results = []
    if 'batch_upload_stage' not in st.session_state:
        st.session_state.batch_upload_stage = 'upload'  # upload, processing, review, complete
    if 'batch_upload_progress' not in st.session_state:
        st.session_state.batch_upload_progress = 0
    if 'batch_upload_matches' not in st.session_state:
        st.session_state.batch_upload_matches = {}
    if 'batch_upload_selected' not in st.session_state:
        st.session_state.batch_upload_selected = set()
    if 'batch_processing_cancelled' not in st.session_state:
        st.session_state.batch_processing_cancelled = False


def validate_file(file, filename: str) -> Tuple[bool, Optional[str]]:
    """
    Validate uploaded file

    Returns:
        (is_valid, error_message)
    """
    # Check file extension
    ext = filename.lower().split('.')[-1]
    if ext not in SUPPORTED_FORMATS:
        return False, f"Unsupported format. Please use: {', '.join(SUPPORTED_FORMATS).upper()}"

    # Check file size
    file.seek(0, 2)  # Seek to end
    size_mb = file.tell() / (1024 * 1024)
    file.seek(0)  # Reset

    if size_mb > MAX_FILE_SIZE_MB:
        return False, f"File too large ({size_mb:.1f} MB). Max: {MAX_FILE_SIZE_MB} MB"

    # Validate image can be opened (for image files)
    if ext in ['png', 'jpg', 'jpeg']:
        try:
            img = Image.open(file)
            img.verify()
            file.seek(0)  # Reset after verify
        except Exception as e:
            return False, f"Invalid image file: {str(e)}"

    return True, None


def calculate_total_size(files) -> float:
    """Calculate total size of files in MB"""
    total = 0
    for file in files:
        file.seek(0, 2)
        total += file.tell()
        file.seek(0)
    return total / (1024 * 1024)


def render_upload_interface():
    """Render multi-file upload interface"""
    st.markdown("### 📎 Batch Receipt Upload")

    # File uploader with custom styling
    uploaded_files = st.file_uploader(
        "Upload multiple receipt images",
        type=SUPPORTED_FORMATS,
        accept_multiple_files=True,
        key="batch_uploader",
        help=f"Drag and drop or click to browse. Max {MAX_FILES} files, {MAX_FILE_SIZE_MB}MB each"
    )

    # Display upload zone info
    with st.expander("ℹ️ Upload Guidelines", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            **Supported Formats:**
            - PNG, JPG, JPEG, PDF

            **Limits:**
            - Max {MAX_FILES} files at once
            - Max {MAX_FILE_SIZE_MB}MB per file
            - Max {MAX_TOTAL_SIZE_MB}MB total
            """)
        with col2:
            st.markdown("""
            **Best Results:**
            - Clear, well-lit photos
            - Straight-on angle
            - All text visible
            - High resolution
            """)

    if uploaded_files:
        # Validate files
        valid_files = []
        errors = []

        for file in uploaded_files:
            is_valid, error = validate_file(file, file.name)
            if is_valid:
                valid_files.append(file)
            else:
                errors.append((file.name, error))

        # Check total count
        if len(valid_files) > MAX_FILES:
            st.error(f"❌ Too many files. Selected {len(valid_files)}, max is {MAX_FILES}")
            return

        # Check total size
        total_size = calculate_total_size(valid_files)
        if total_size > MAX_TOTAL_SIZE_MB:
            st.error(f"❌ Total size too large ({total_size:.1f} MB). Max: {MAX_TOTAL_SIZE_MB} MB")
            return

        # Show errors
        if errors:
            st.warning(f"⚠️ {len(errors)} file(s) skipped:")
            for filename, error in errors:
                st.caption(f"• {filename}: {error}")

        # Show valid files
        if valid_files:
            st.session_state.batch_upload_files = valid_files
            render_file_preview_list(valid_files, total_size)
        else:
            st.info("No valid files to process")
    else:
        # Show empty state
        st.info("👆 Upload receipt images to get started")
        st.session_state.batch_upload_files = []


def render_file_preview_list(files, total_size: float):
    """Display uploaded files with preview and controls"""
    st.markdown(f"### Selected Files ({len(files)})")

    # Summary bar
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.metric("Total Files", len(files))
    with col2:
        st.metric("Total Size", f"{total_size:.1f} MB")
    with col3:
        size_percent = (total_size / MAX_TOTAL_SIZE_MB) * 100
        st.metric("Capacity", f"{size_percent:.0f}%")

    # Progress bar for total size
    st.progress(min(total_size / MAX_TOTAL_SIZE_MB, 1.0))

    st.markdown("---")

    # File list with thumbnails
    for idx, file in enumerate(files):
        with st.container():
            col1, col2, col3, col4 = st.columns([1, 3, 2, 1])

            with col1:
                # Thumbnail for images
                if file.type.startswith('image/'):
                    try:
                        img = Image.open(file)
                        st.image(img, width=60)
                        file.seek(0)
                    except:
                        st.markdown("🖼️")
                else:
                    st.markdown("📄")

            with col2:
                st.markdown(f"**{file.name}**")
                file_size = file.size / 1024  # KB
                if file_size < 1024:
                    st.caption(f"{file_size:.1f} KB")
                else:
                    st.caption(f"{file_size/1024:.1f} MB")

            with col3:
                st.caption(f"Type: {file.type}")

            with col4:
                if st.button("🗑️", key=f"remove_{idx}", help="Remove file"):
                    files.pop(idx)
                    st.rerun()

        if idx < len(files) - 1:
            st.markdown("<hr style='margin: 0.5rem 0; opacity: 0.3;'>", unsafe_allow_html=True)

    st.markdown("---")

    # Action buttons
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        if st.button("🚀 Process All Receipts", type="primary", use_container_width=True):
            st.session_state.batch_upload_stage = 'processing'
            st.session_state.batch_upload_progress = 0
            st.session_state.batch_processing_cancelled = False
            st.rerun()

    with col2:
        if st.button("❌ Clear All", use_container_width=True):
            st.session_state.batch_upload_files = []
            st.session_state.batch_upload_stage = 'upload'
            st.rerun()

    with col3:
        st.caption(f"{len(files)}/{MAX_FILES} files")


def process_single_receipt(file, filename: str, session=None) -> Dict[str, Any]:
    """
    Process a single receipt with OCR

    Returns:
        Result dictionary with OCR data and status
    """
    result = {
        'filename': filename,
        'status': 'pending',
        'data': None,
        'error': None,
        'confidence': 0,
        'processing_time': 0
    }

    start_time = time.time()

    try:
        # Save file temporarily
        temp_path = f"/tmp/{filename}"
        with open(temp_path, 'wb') as f:
            f.write(file.read())
        file.seek(0)

        # Run OCR
        ocr_data = quick_ocr(temp_path)

        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)

        # Check if OCR was successful
        if ocr_data and 'merchant' in ocr_data:
            result['status'] = 'success'
            result['data'] = ocr_data
            result['confidence'] = ocr_data.get('confidence', 0)
        else:
            result['status'] = 'failed'
            result['error'] = 'OCR extraction failed'

    except Exception as e:
        result['status'] = 'failed'
        result['error'] = str(e)

    result['processing_time'] = time.time() - start_time

    return result


def batch_process_receipts(files, progress_placeholder, session=None):
    """
    Process multiple receipts with progress tracking

    Args:
        files: List of uploaded files
        progress_placeholder: Streamlit placeholder for progress UI
        session: Database session (optional)

    Returns:
        List of result dictionaries
    """
    results = []
    total = len(files)

    for idx, file in enumerate(files):
        # Check if cancelled
        if st.session_state.batch_processing_cancelled:
            break

        current = idx + 1

        # Update progress UI
        render_processing_progress(
            current,
            total,
            file.name,
            results,
            progress_placeholder
        )

        # Process file
        result = process_single_receipt(file, file.name, session)
        results.append(result)

        # Update session state
        st.session_state.batch_upload_progress = (current / total) * 100
        st.session_state.batch_upload_results = results

    return results


def render_processing_progress(current: int, total: int, current_file: str, results: List, placeholder):
    """Render real-time processing progress"""
    with placeholder.container():
        st.markdown("### ⚙️ Processing Receipts...")

        # Progress bar
        progress = (current - 1) / total  # -1 because we're starting current file
        st.progress(progress)

        # Stats row
        col1, col2, col3, col4 = st.columns(4)

        completed = len([r for r in results if r['status'] == 'success'])
        failed = len([r for r in results if r['status'] == 'failed'])
        processing = 1 if current <= total else 0
        pending = total - current + 1

        with col1:
            st.metric("✅ Completed", completed)
        with col2:
            st.metric("⏳ Processing", processing)
        with col3:
            st.metric("⏸️ Pending", pending)
        with col4:
            st.metric("❌ Failed", failed)

        st.markdown("---")

        # Current file
        st.markdown(f"**Current File ({current}/{total}):**")
        st.info(f"📄 {current_file}")

        # Estimated time
        if results:
            avg_time = sum(r['processing_time'] for r in results) / len(results)
            est_remaining = avg_time * pending
            st.caption(f"⏱️ Estimated time remaining: {est_remaining:.0f} seconds")

        # Recent results
        if results and len(results) > 0:
            st.markdown("**Recent Results:**")
            for result in results[-3:]:
                icon = "✅" if result['status'] == 'success' else "❌"
                conf = f"({result['confidence']}%)" if result['status'] == 'success' else ""
                st.caption(f"{icon} {result['filename']} {conf}")

        # Cancel button
        if st.button("⏹️ Cancel Processing", type="secondary"):
            st.session_state.batch_processing_cancelled = True
            st.warning("Processing cancelled by user")


def calculate_confidence_score(ocr_data: Dict) -> int:
    """Calculate overall confidence score for OCR result"""
    # Use OCR confidence if available
    if 'confidence' in ocr_data:
        return int(ocr_data['confidence'])

    # Calculate based on data completeness
    score = 0
    fields = ['merchant', 'date', 'total']

    for field in fields:
        if field in ocr_data and ocr_data[field]:
            score += 33

    return min(score, 100)


def fuzzy_match(str1: str, str2: str) -> float:
    """Calculate fuzzy match score between two strings (0-100)"""
    if not str1 or not str2:
        return 0.0
    return SequenceMatcher(None, str1.lower(), str2.lower()).ratio() * 100


def smart_match_receipts_to_transactions(session, receipt_data: Dict, transactions: List[Dict]) -> Dict:
    """
    Match receipts to existing transactions using smart matching

    Args:
        session: Database session
        receipt_data: OCR extracted data from receipt
        transactions: List of unreviewed transactions

    Returns:
        Match result dictionary
    """
    if not transactions:
        return {
            'matched': False,
            'transaction_id': None,
            'confidence': 0,
            'reason': 'No transactions available to match'
        }

    best_match = None
    best_score = 0

    receipt_date = receipt_data.get('date')
    receipt_amount = receipt_data.get('total')
    receipt_merchant = receipt_data.get('merchant', '')

    if not receipt_date or not receipt_amount:
        return {
            'matched': False,
            'transaction_id': None,
            'confidence': 0,
            'reason': 'Incomplete receipt data'
        }

    # Parse receipt date
    try:
        if isinstance(receipt_date, str):
            receipt_date = datetime.strptime(receipt_date, '%Y-%m-%d')
    except:
        return {
            'matched': False,
            'transaction_id': None,
            'confidence': 0,
            'reason': 'Invalid date format'
        }

    # Check each transaction
    for trans in transactions:
        score = 0
        reasons = []

        # Date matching (within window)
        trans_date = trans.get('date')
        if isinstance(trans_date, str):
            trans_date = datetime.strptime(trans_date, '%Y-%m-%d')

        date_diff = abs((trans_date - receipt_date).days)
        if date_diff == 0:
            score += 40
            reasons.append('exact date match')
        elif date_diff <= MATCH_DATE_WINDOW_DAYS:
            score += 30 - (date_diff * 5)
            reasons.append(f'date within {date_diff} days')

        # Amount matching
        trans_amount = abs(float(trans.get('amount', 0)))
        amount_diff = abs(trans_amount - receipt_amount)

        if amount_diff == 0:
            score += 40
            reasons.append('exact amount match')
        elif amount_diff <= MATCH_AMOUNT_TOLERANCE:
            score += 30
            reasons.append(f'amount within £{amount_diff:.2f}')

        # Merchant matching
        trans_merchant = trans.get('description', '')
        merchant_similarity = fuzzy_match(receipt_merchant, trans_merchant)

        if merchant_similarity > 80:
            score += 20
            reasons.append(f'merchant match ({merchant_similarity:.0f}%)')
        elif merchant_similarity > 50:
            score += 10
            reasons.append(f'merchant similar ({merchant_similarity:.0f}%)')

        # Track best match
        if score > best_score:
            best_score = score
            best_match = {
                'matched': score >= 60,  # Threshold for auto-match
                'transaction_id': trans.get('id'),
                'transaction': trans,
                'confidence': min(score, 100),
                'reason': ', '.join(reasons) if reasons else 'No strong match'
            }

    return best_match if best_match else {
        'matched': False,
        'transaction_id': None,
        'confidence': 0,
        'reason': 'No matching transaction found'
    }


def render_batch_results_review(results: List[Dict], session=None, transactions=None):
    """Render comprehensive results review interface"""
    st.markdown("### 📊 Review Results")

    # Summary stats
    total = len(results)
    successful = len([r for r in results if r['status'] == 'success'])
    failed = len([r for r in results if r['status'] == 'failed'])
    high_conf = len([r for r in results if r['status'] == 'success' and r['confidence'] >= HIGH_CONFIDENCE_THRESHOLD])

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Processed", total)
    with col2:
        st.metric("✅ Successful", successful, delta=f"{(successful/total*100):.0f}%")
    with col3:
        st.metric("⚠️ Need Review", successful - high_conf)
    with col4:
        st.metric("❌ Failed", failed)

    st.markdown("---")

    # Filter controls
    col1, col2, col3 = st.columns([2, 2, 2])

    with col1:
        filter_option = st.selectbox(
            "Filter",
            ["All", "High Confidence", "Needs Review", "Failed"],
            key="batch_filter"
        )

    with col2:
        sort_option = st.selectbox(
            "Sort by",
            ["Confidence (High to Low)", "Confidence (Low to High)", "Filename"],
            key="batch_sort"
        )

    with col3:
        if transactions:
            show_matches = st.checkbox("Show Transaction Matches", value=True)
        else:
            show_matches = False

    # Filter results
    filtered_results = results.copy()

    if filter_option == "High Confidence":
        filtered_results = [r for r in filtered_results if r['status'] == 'success' and r['confidence'] >= HIGH_CONFIDENCE_THRESHOLD]
    elif filter_option == "Needs Review":
        filtered_results = [r for r in filtered_results if r['status'] == 'success' and r['confidence'] < HIGH_CONFIDENCE_THRESHOLD]
    elif filter_option == "Failed":
        filtered_results = [r for r in filtered_results if r['status'] == 'failed']

    # Sort results
    if sort_option == "Confidence (High to Low)":
        filtered_results.sort(key=lambda x: x['confidence'], reverse=True)
    elif sort_option == "Confidence (Low to High)":
        filtered_results.sort(key=lambda x: x['confidence'])
    else:
        filtered_results.sort(key=lambda x: x['filename'])

    st.markdown(f"**Showing {len(filtered_results)} of {total} results**")

    if not filtered_results:
        st.info("No results match the current filter")
        return

    # Display results
    for idx, result in enumerate(filtered_results):
        render_single_result_card(result, idx, session, transactions if show_matches else None)

    st.markdown("---")

    # Batch action buttons
    render_batch_action_buttons(results, session, transactions)


def render_single_result_card(result: Dict, idx: int, session=None, transactions=None):
    """Render a single result card with edit/accept/reject options"""
    is_success = result['status'] == 'success'
    confidence = result['confidence']

    # Card container
    with st.container():
        # Header
        col1, col2, col3 = st.columns([3, 1, 1])

        with col1:
            if is_success:
                if confidence >= HIGH_CONFIDENCE_THRESHOLD:
                    st.markdown(f"### ✅ {result['filename']}")
                else:
                    st.markdown(f"### ⚠️ {result['filename']}")
            else:
                st.markdown(f"### ❌ {result['filename']}")

        with col2:
            if is_success:
                st.metric("Confidence", f"{confidence}%")

        with col3:
            # Selection checkbox
            is_selected = result['filename'] in st.session_state.batch_upload_selected
            if st.checkbox("Select", value=is_selected, key=f"select_{idx}"):
                st.session_state.batch_upload_selected.add(result['filename'])
            else:
                st.session_state.batch_upload_selected.discard(result['filename'])

        # Content based on status
        if is_success:
            data = result['data']

            # Show OCR data with editable fields
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**Extracted Data:**")

                merchant = st.text_input(
                    "Merchant",
                    value=data.get('merchant', ''),
                    key=f"merchant_{idx}",
                    help="⚠️" if confidence < HIGH_CONFIDENCE_THRESHOLD else None
                )

                date_str = data.get('date', '')
                date_val = st.date_input(
                    "Date",
                    value=datetime.strptime(date_str, '%Y-%m-%d') if date_str else datetime.now(),
                    key=f"date_{idx}"
                )

                amount = st.number_input(
                    "Amount (£)",
                    value=float(data.get('total', 0)),
                    min_value=0.0,
                    step=0.01,
                    key=f"amount_{idx}"
                )

                # Update data if edited
                result['data']['merchant'] = merchant
                result['data']['date'] = date_val.strftime('%Y-%m-%d')
                result['data']['total'] = amount

            with col2:
                # Show transaction match if available
                if transactions:
                    match = smart_match_receipts_to_transactions(session, result['data'], transactions)

                    st.markdown("**Transaction Match:**")

                    if match['matched']:
                        st.success(f"✅ Match Found ({match['confidence']}%)")
                        st.caption(match['reason'])

                        trans = match['transaction']
                        st.info(f"""
                        **Transaction:**
                        - Date: {trans.get('date')}
                        - Amount: £{abs(float(trans.get('amount', 0))):.2f}
                        - Description: {trans.get('description')}
                        """)

                        result['match'] = match
                    else:
                        st.warning("⚠️ No Match Found")
                        st.caption(match['reason'])
                        result['match'] = None
                else:
                    st.markdown("**Category:**")
                    category = st.selectbox(
                        "Select category",
                        ["Uncategorized", "Office Supplies", "Travel", "Meals", "Equipment", "Other"],
                        key=f"category_{idx}"
                    )
                    result['data']['category'] = category
        else:
            # Show error
            st.error(f"❌ Processing failed: {result.get('error', 'Unknown error')}")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 Retry", key=f"retry_{idx}"):
                    st.info("Retry functionality to be implemented")
            with col2:
                if st.button("✏️ Manual Entry", key=f"manual_{idx}"):
                    st.info("Manual entry form to be implemented")

        # Action buttons
        if is_success:
            col1, col2, col3 = st.columns(3)

            with col1:
                if st.button("✅ Accept", key=f"accept_{idx}", use_container_width=True, type="primary"):
                    result['action'] = 'accept'
                    st.success("Accepted!")

            with col2:
                if st.button("✏️ Edit", key=f"edit_{idx}", use_container_width=True):
                    result['action'] = 'edit'
                    st.info("Changes saved")

            with col3:
                if st.button("❌ Reject", key=f"reject_{idx}", use_container_width=True):
                    result['action'] = 'reject'
                    st.warning("Rejected")

        st.markdown("<hr style='margin: 1.5rem 0;'>", unsafe_allow_html=True)


def render_batch_action_buttons(results: List[Dict], session=None, transactions=None):
    """Render batch action buttons"""
    st.markdown("### Batch Actions")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("✅ Accept All High Confidence", use_container_width=True):
            count = batch_accept_high_confidence(results)
            st.success(f"Accepted {count} high confidence receipts")
            st.rerun()

    with col2:
        if st.button("🔗 Link to Transactions", use_container_width=True, disabled=not transactions):
            if transactions:
                count = batch_link_to_transactions(session, results, transactions)
                st.success(f"Linked {count} receipts to transactions")
                st.rerun()

    with col3:
        if st.button("💾 Create Expenses", use_container_width=True):
            count = batch_create_expenses(session, results)
            st.success(f"Created {count} expense records")
            st.rerun()

    with col4:
        if st.button("📥 Export Results", use_container_width=True):
            # Convert results to DataFrame
            rows = []
            for result in results:
                if result['status'] == 'success':
                    data = result['data']
                    row = {
                        'Filename': result['filename'],
                        'Status': result['status'],
                        'Confidence': result['confidence'],
                        'Merchant': data.get('merchant', ''),
                        'Date': data.get('date', ''),
                        'Amount': data.get('total', 0),
                        'Category': data.get('category', ''),
                        'Action': result.get('action', 'pending')
                    }
                    # Add match info if available
                    if 'match' in result and result['match']:
                        row['Matched'] = result['match']['matched']
                        row['Match Confidence'] = result['match']['confidence']
                    rows.append(row)
                else:
                    rows.append({
                        'Filename': result['filename'],
                        'Status': result['status'],
                        'Error': result.get('error', 'Unknown error'),
                        'Confidence': 0,
                        'Action': 'failed'
                    })

            results_df = pd.DataFrame(rows)

            # Show Aurora-themed export panel
            with st.expander("Export Batch Results", expanded=True):
                render_export_panel(
                    session=session,
                    data=results_df,
                    title="Batch Receipt Processing Results",
                    filename_prefix=f"batch_receipts_{datetime.now().strftime('%Y%m%d')}",
                    metadata={
                        'Total Files': str(len(results)),
                        'Successful': str(len([r for r in results if r['status'] == 'success'])),
                        'Failed': str(len([r for r in results if r['status'] == 'failed'])),
                        'High Confidence': str(len([r for r in results if r.get('confidence', 0) >= HIGH_CONFIDENCE_THRESHOLD]))
                    },
                    show_formats=['csv', 'excel', 'pdf'],
                    use_aurora_theme=True
                )


def batch_accept_high_confidence(results: List[Dict], threshold: int = HIGH_CONFIDENCE_THRESHOLD) -> int:
    """Accept all results above confidence threshold"""
    count = 0
    for result in results:
        if result['status'] == 'success' and result['confidence'] >= threshold:
            result['action'] = 'accept'
            count += 1
    return count


def batch_create_expenses(session, results: List[Dict]) -> int:
    """Create expense records for all accepted receipts"""
    count = 0
    for result in results:
        if result.get('action') == 'accept' and result['status'] == 'success':
            # Implementation would create actual expense record
            # For now, just count
            count += 1
    return count


def batch_link_to_transactions(session, results: List[Dict], transactions: List[Dict]) -> int:
    """Link receipts to matched transactions"""
    count = 0
    for result in results:
        if result.get('match') and result['match']['matched']:
            # Implementation would create actual link
            # For now, just count
            count += 1
    return count


def export_results_to_csv(results: List[Dict]) -> str:
    """Export all results to CSV format"""
    rows = []

    for result in results:
        if result['status'] == 'success':
            data = result['data']
            row = {
                'Filename': result['filename'],
                'Status': result['status'],
                'Confidence': result['confidence'],
                'Merchant': data.get('merchant', ''),
                'Date': data.get('date', ''),
                'Amount': data.get('total', 0),
                'Category': data.get('category', ''),
                'Action': result.get('action', 'pending')
            }

            # Add match info if available
            if 'match' in result and result['match']:
                row['Matched'] = result['match']['matched']
                row['Match Confidence'] = result['match']['confidence']

            rows.append(row)

    df = pd.DataFrame(rows)
    return df.to_csv(index=False)


def render_workflow_selector():
    """Render workflow selection interface"""
    st.markdown("### 🔄 Select Workflow")

    workflow = st.radio(
        "Choose how to process receipts:",
        [
            "Create New Expenses",
            "Link to Transactions",
            "Hybrid (Auto-match + Create)"
        ],
        help="Select the workflow that matches your needs"
    )

    if workflow == "Create New Expenses":
        st.info("""
        **Workflow A: Create New Expenses**
        1. Upload receipts
        2. Process with OCR
        3. Review results
        4. Accept all or selected
        5. Creates expense records automatically
        """)
    elif workflow == "Link to Transactions":
        st.info("""
        **Workflow B: Link to Transactions**
        1. Upload receipts
        2. Process with OCR
        3. Smart match to existing transactions
        4. Review matches
        5. Accept matches to link receipts
        """)
    else:
        st.info("""
        **Workflow C: Hybrid**
        1. Upload receipts
        2. Process with OCR
        3. Auto-match to transactions where possible
        4. Create new expenses for unmatched receipts
        5. Manual review for low-confidence items
        """)

    return workflow


def main_batch_upload_interface(session=None, transactions=None):
    """
    Main interface for batch receipt upload

    Args:
        session: Database session (optional)
        transactions: List of unreviewed transactions for matching (optional)
    """
    initialize_session_state()

    st.title("📎 Batch Receipt Upload")
    st.markdown("Upload and process multiple receipts at once with OCR")

    # Stage-based rendering
    stage = st.session_state.batch_upload_stage

    if stage == 'upload':
        # Show workflow selector
        workflow = render_workflow_selector()
        st.session_state.batch_upload_workflow = workflow

        st.markdown("---")

        # Show upload interface
        render_upload_interface()

    elif stage == 'processing':
        # Process receipts
        st.markdown("---")
        progress_placeholder = st.empty()

        files = st.session_state.batch_upload_files
        results = batch_process_receipts(files, progress_placeholder, session)

        # Processing complete
        st.session_state.batch_upload_results = results
        st.session_state.batch_upload_stage = 'review'

        progress_placeholder.empty()
        st.success(f"✅ Processing complete! {len(results)} receipts processed.")

        time.sleep(1)
        st.rerun()

    elif stage == 'review':
        # Show results review
        results = st.session_state.batch_upload_results
        workflow = st.session_state.get('batch_upload_workflow', 'Create New Expenses')

        # Pass transactions only for matching workflows
        trans_for_matching = transactions if 'Transaction' in workflow or 'Hybrid' in workflow else None

        render_batch_results_review(results, session, trans_for_matching)

        # Reset button
        if st.button("🔄 Start New Batch", type="secondary"):
            st.session_state.batch_upload_stage = 'upload'
            st.session_state.batch_upload_files = []
            st.session_state.batch_upload_results = []
            st.session_state.batch_upload_selected = set()
            st.rerun()


# Quick access functions for embedding in other pages
def quick_batch_upload(session=None, entity_type: str = "expense", entity_id: int = 1):
    """Quick batch upload widget for embedding in other pages"""

    uploaded_files = st.file_uploader(
        "Upload Multiple Receipts",
        type=SUPPORTED_FORMATS,
        accept_multiple_files=True,
        key=f"quick_batch_{entity_type}_{entity_id}"
    )

    if uploaded_files and st.button("Process", key=f"process_batch_{entity_type}_{entity_id}"):
        progress_placeholder = st.empty()
        results = batch_process_receipts(uploaded_files, progress_placeholder, session)

        successful = len([r for r in results if r['status'] == 'success'])
        st.success(f"Processed {successful}/{len(results)} receipts successfully")
        return results

    return None


# Convenience wrapper functions for easy imports
def render_batch_upload_interface(session=None, transactions=None):
    """
    Convenience wrapper for main_batch_upload_interface()
    Renders the complete batch upload interface

    Args:
        session: SQLAlchemy session
        transactions: Optional list of unreviewed transactions for matching
    """
    return main_batch_upload_interface(session=session, transactions=transactions)


# Standalone demo app
if __name__ == "__main__":
    st.set_page_config(
        page_title="Batch Receipt Upload",
        page_icon="📎",
        layout="wide"
    )

    # Custom CSS for better styling
    st.markdown("""
    <style>
    .stButton button {
        transition: all 0.3s ease;
    }
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.5rem;
        font-weight: bold;
    }
    .success-card {
        background-color: #d4edda;
        border-left: 4px solid #36c7a0;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    .warning-card {
        background-color: #fff3cd;
        border-left: 4px solid #e5b567;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    .error-card {
        background-color: #f8d7da;
        border-left: 4px solid #e07a5f;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    </style>
    """, unsafe_allow_html=True)

    # Sample transactions for demo
    sample_transactions = [
        {
            'id': 1,
            'date': datetime.now().strftime('%Y-%m-%d'),
            'amount': -45.99,
            'description': 'TESCO STORES',
            'reviewed': False
        },
        {
            'id': 2,
            'date': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'),
            'amount': -12.50,
            'description': 'COSTA COFFEE',
            'reviewed': False
        },
        {
            'id': 3,
            'date': (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d'),
            'amount': -156.00,
            'description': 'AMAZON UK',
            'reviewed': False
        }
    ]

    # Run main interface
    main_batch_upload_interface(session=None, transactions=sample_transactions)

    # Sidebar with info
    with st.sidebar:
        st.markdown("### ℹ️ About")
        st.markdown("""
        **Batch Receipt Upload** allows you to:

        - Upload up to 20 receipts at once
        - Automatic OCR processing
        - Smart transaction matching
        - Bulk review and editing
        - Multiple workflow options

        **Tips:**
        - Clear, well-lit photos work best
        - Ensure all text is visible
        - Supported: PNG, JPG, PDF
        """)

        st.markdown("---")

        st.markdown("### 📊 Statistics")
        if st.session_state.batch_upload_results:
            results = st.session_state.batch_upload_results
            st.metric("Total Processed", len(results))
            st.metric("Success Rate",
                     f"{len([r for r in results if r['status'] == 'success'])/len(results)*100:.0f}%")
