"""
Batch Receipt Upload Demo Application

Demonstrates all features of the batch receipt upload system:
- Multi-file upload interface
- OCR processing with progress tracking
- Smart transaction matching
- Batch review and editing
- Multiple workflow options
"""

import streamlit as st
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from components.batch_receipt_upload import (
    main_batch_upload_interface,
    quick_batch_upload,
    initialize_session_state
)


def main():
    """Main demo application"""
    st.set_page_config(
        page_title="Batch Receipt Upload Demo",
        page_icon="📎",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Custom CSS for enhanced UI
    st.markdown("""
    <style>
    /* Main container styling */
    .main {
        padding: 2rem;
    }

    /* Button hover effects */
    .stButton button {
        transition: all 0.3s ease;
        border-radius: 8px;
    }
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }

    /* Metric styling */
    div[data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: bold;
    }

    /* Card styling */
    .success-card {
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        padding: 1.5rem;
        margin: 1rem 0;
        border-radius: 4px;
    }
    .warning-card {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 1.5rem;
        margin: 1rem 0;
        border-radius: 4px;
    }
    .info-card {
        background-color: #d1ecf1;
        border-left: 4px solid #17a2b8;
        padding: 1.5rem;
        margin: 1rem 0;
        border-radius: 4px;
    }

    /* Progress bar styling */
    .stProgress > div > div > div {
        background-color: #28a745;
    }

    /* File uploader styling */
    .uploadedFile {
        border-radius: 8px;
        border: 1px solid #e0e0e0;
    }

    /* Expander styling */
    .streamlit-expanderHeader {
        font-weight: 600;
        font-size: 1.1rem;
    }
    </style>
    """, unsafe_allow_html=True)

    # Sidebar navigation
    with st.sidebar:
        st.title("📎 Batch Upload Demo")

        demo_mode = st.radio(
            "Demo Mode",
            [
                "Full Interface",
                "Quick Upload Widget",
                "Feature Tour",
                "Integration Examples"
            ]
        )

        st.markdown("---")

        # Configuration options
        st.markdown("### ⚙️ Configuration")

        enable_matching = st.checkbox("Enable Transaction Matching", value=True)
        show_sample_data = st.checkbox("Use Sample Transactions", value=True)

        st.markdown("---")

        # Statistics
        st.markdown("### 📊 Session Stats")
        initialize_session_state()

        if st.session_state.batch_upload_results:
            results = st.session_state.batch_upload_results
            total = len(results)
            successful = len([r for r in results if r['status'] == 'success'])

            st.metric("Files Processed", total)
            st.metric("Success Rate", f"{(successful/total*100):.0f}%")

            avg_time = sum(r['processing_time'] for r in results) / total
            st.metric("Avg Processing Time", f"{avg_time:.2f}s")
        else:
            st.info("No files processed yet")

        st.markdown("---")

        # Help section
        with st.expander("❓ Help"):
            st.markdown("""
            **How to use:**

            1. Upload receipt images (PNG, JPG, PDF)
            2. Choose workflow
            3. Process receipts
            4. Review and edit results
            5. Accept or reject items

            **Keyboard shortcuts:**
            - `Ctrl+V` - Paste image from clipboard
            - `Ctrl+Z` - Undo last action
            """)

    # Sample transaction data
    sample_transactions = None
    if show_sample_data and enable_matching:
        sample_transactions = generate_sample_transactions()

    # Render selected demo mode
    if demo_mode == "Full Interface":
        render_full_interface(sample_transactions)
    elif demo_mode == "Quick Upload Widget":
        render_quick_upload_demo()
    elif demo_mode == "Feature Tour":
        render_feature_tour()
    else:
        render_integration_examples()


def generate_sample_transactions():
    """Generate sample transaction data for demo"""
    return [
        {
            'id': 1,
            'date': datetime.now().strftime('%Y-%m-%d'),
            'amount': -45.99,
            'description': 'TESCO STORES 2847',
            'reviewed': False,
            'category': 'Groceries'
        },
        {
            'id': 2,
            'date': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'),
            'amount': -12.50,
            'description': 'COSTA COFFEE',
            'reviewed': False,
            'category': 'Meals'
        },
        {
            'id': 3,
            'date': (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d'),
            'amount': -156.00,
            'description': 'AMAZON.CO.UK',
            'reviewed': False,
            'category': 'Office Supplies'
        },
        {
            'id': 4,
            'date': (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d'),
            'amount': -89.99,
            'description': 'SHELL PETROL STATION',
            'reviewed': False,
            'category': 'Travel'
        },
        {
            'id': 5,
            'date': (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d'),
            'amount': -23.75,
            'description': 'SAINSBURYS S/MKTS',
            'reviewed': False,
            'category': 'Groceries'
        }
    ]


def render_full_interface(transactions):
    """Render the full batch upload interface"""
    st.markdown("""
    <div class="info-card">
    <h3>🚀 Full Batch Upload Interface</h3>
    <p>This is the complete batch receipt upload system with all features enabled.</p>
    </div>
    """, unsafe_allow_html=True)

    # Run main interface
    main_batch_upload_interface(session=None, transactions=transactions)


def render_quick_upload_demo():
    """Render quick upload widget demo"""
    st.title("⚡ Quick Upload Widget")

    st.markdown("""
    <div class="info-card">
    <h3>Embedded Upload Widget</h3>
    <p>This lightweight widget can be embedded in any page for quick receipt uploads.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Demo the quick upload widget
    st.markdown("### Example: Expense Form Integration")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("**Expense Details:**")
        expense_desc = st.text_input("Description", "Office supplies")
        expense_amount = st.number_input("Amount (£)", value=45.99, min_value=0.0)
        expense_date = st.date_input("Date", value=datetime.now())

    with col2:
        st.markdown("**Category:**")
        category = st.selectbox("Select", ["Office Supplies", "Travel", "Meals", "Equipment"])

    st.markdown("---")

    st.markdown("### Attach Receipts")

    # Quick upload widget
    results = quick_batch_upload(session=None, entity_type="expense", entity_id=1)

    if results:
        st.success(f"✅ Receipts uploaded and processed!")

        # Show results summary
        with st.expander("View Processing Results", expanded=True):
            for result in results:
                if result['status'] == 'success':
                    st.success(f"✅ {result['filename']} - {result['confidence']}% confidence")
                else:
                    st.error(f"❌ {result['filename']} - {result['error']}")


def render_feature_tour():
    """Render interactive feature tour"""
    st.title("🎯 Feature Tour")

    st.markdown("""
    <div class="info-card">
    <h3>Explore All Features</h3>
    <p>Interactive tour of the batch receipt upload system capabilities.</p>
    </div>
    """, unsafe_allow_html=True)

    # Feature tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📤 Upload",
        "🔍 OCR Processing",
        "🔗 Smart Matching",
        "✏️ Batch Review",
        "📊 Export"
    ])

    with tab1:
        st.markdown("### 📤 Multi-File Upload")
        st.markdown("""
        **Features:**
        - Drag & drop up to 20 files
        - File validation (format, size)
        - Thumbnail previews
        - Total size tracking
        - Individual file removal

        **Supported Formats:**
        - PNG, JPG, JPEG (images)
        - PDF (documents)

        **Limits:**
        - Max 10 MB per file
        - Max 100 MB total
        """)

        st.image("https://via.placeholder.com/800x400/4CAF50/FFFFFF?text=Drag+%26+Drop+Upload+Interface",
                 caption="Beautiful drag & drop interface")

    with tab2:
        st.markdown("### 🔍 OCR Processing")
        st.markdown("""
        **Automatic Data Extraction:**
        - Merchant name
        - Date
        - Total amount
        - Line items (if available)

        **Processing Features:**
        - Real-time progress tracking
        - Estimated time remaining
        - Individual file status
        - Cancel anytime

        **Performance:**
        - 10 receipts in ~30-60 seconds
        - Parallel processing support
        - Error recovery
        """)

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Average Accuracy", "85%")
            st.metric("Avg Processing Time", "3.5s")
        with col2:
            st.metric("Success Rate", "92%")
            st.metric("Files per Batch", "15")

    with tab3:
        st.markdown("### 🔗 Smart Transaction Matching")
        st.markdown("""
        **Matching Criteria:**
        - Date (exact or within ±3 days)
        - Amount (exact or within £0.10)
        - Merchant (fuzzy text matching)

        **Match Confidence:**
        - 90-100%: High confidence (auto-link)
        - 70-89%: Medium confidence (review)
        - <70%: Low confidence (manual)

        **Benefits:**
        - Automatic receipt-transaction linking
        - Reduces manual data entry
        - Improves accuracy
        """)

        # Demo matching algorithm
        st.markdown("**Example Match:**")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            **Receipt:**
            - Merchant: TESCO
            - Date: 17/10/2024
            - Amount: £45.99
            """)
        with col2:
            st.markdown("""
            **Transaction:**
            - Description: TESCO STORES 2847
            - Date: 17/10/2024
            - Amount: -£45.99
            """)

        st.success("✅ Match Confidence: 95% (exact date + exact amount + merchant match)")

    with tab4:
        st.markdown("### ✏️ Batch Review Interface")
        st.markdown("""
        **Review Features:**
        - Filter by confidence level
        - Sort by multiple criteria
        - Inline editing
        - Bulk actions

        **Individual Actions:**
        - Accept (save as-is)
        - Edit (modify data)
        - Reject (exclude)
        - Retry (re-process)

        **Bulk Actions:**
        - Accept all high confidence
        - Link to transactions
        - Create expenses
        - Export to CSV
        """)

        # Sample review cards
        st.markdown("**High Confidence Result:**")
        st.success("""
        ✅ receipt1.jpg (95% confidence)
        - Merchant: TESCO
        - Date: 17/10/2024
        - Amount: £45.99
        """)

        st.markdown("**Needs Review:**")
        st.warning("""
        ⚠️ receipt2.jpg (45% confidence)
        - Merchant: COSTA__ (needs correction)
        - Date: 17/10/2024 ✓
        - Amount: £4.50 ✓
        """)

    with tab5:
        st.markdown("### 📊 Export & Reporting")
        st.markdown("""
        **Export Options:**
        - CSV (all data)
        - Excel (formatted)
        - JSON (structured)
        - PDF (printable report)

        **Export Data Includes:**
        - Filename
        - Extracted data (merchant, date, amount)
        - Confidence scores
        - Match results
        - Categories
        - Action taken

        **Use Cases:**
        - Accounting system import
        - Backup records
        - Audit trail
        - Compliance reporting
        """)

        # Sample CSV preview
        st.markdown("**Sample CSV Output:**")
        st.code("""
Filename,Status,Confidence,Merchant,Date,Amount,Category,Action,Matched
receipt1.jpg,success,95,TESCO,2024-10-17,45.99,Groceries,accept,True
receipt2.jpg,success,85,COSTA,2024-10-16,4.50,Meals,accept,False
receipt3.jpg,success,72,AMAZON,2024-10-15,156.00,Office,edit,True
        """, language="csv")


def render_integration_examples():
    """Render integration code examples"""
    st.title("🔧 Integration Examples")

    st.markdown("""
    <div class="info-card">
    <h3>How to Integrate</h3>
    <p>Code examples for integrating the batch upload system into your application.</p>
    </div>
    """, unsafe_allow_html=True)

    # Example tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "Basic Usage",
        "Custom Workflow",
        "Database Integration",
        "API Usage"
    ])

    with tab1:
        st.markdown("### Basic Integration")
        st.markdown("Add batch upload to any Streamlit page:")

        st.code("""
import streamlit as st
from components.batch_receipt_upload import main_batch_upload_interface

def expenses_page():
    st.title("Expense Management")

    # Add batch upload section
    with st.expander("📎 Batch Upload Receipts", expanded=False):
        main_batch_upload_interface(
            session=get_db_session(),
            transactions=get_unreviewed_transactions()
        )

    # Rest of your expense page...
        """, language="python")

    with tab2:
        st.markdown("### Custom Workflow")
        st.markdown("Create a custom workflow with specific requirements:")

        st.code("""
from components.batch_receipt_upload import (
    render_upload_interface,
    batch_process_receipts,
    render_batch_results_review
)

def custom_receipt_workflow():
    # Step 1: Upload
    files = render_upload_interface()

    if files and st.button("Process"):
        # Step 2: Custom pre-processing
        filtered_files = apply_custom_filters(files)

        # Step 3: OCR processing
        progress = st.empty()
        results = batch_process_receipts(filtered_files, progress)

        # Step 4: Custom validation
        validated_results = custom_validation(results)

        # Step 5: Review
        render_batch_results_review(validated_results)

        # Step 6: Custom post-processing
        if st.button("Finalize"):
            save_to_custom_system(validated_results)
        """, language="python")

    with tab3:
        st.markdown("### Database Integration")
        st.markdown("Integrate with SQLAlchemy models:")

        st.code("""
from sqlalchemy.orm import Session
from components.batch_receipt_upload import batch_accept_high_confidence
from models import Receipt, Expense, Transaction

def save_batch_results(session: Session, results: List[Dict]):
    '''Save batch upload results to database'''

    for result in results:
        if result.get('action') == 'accept' and result['status'] == 'success':
            data = result['data']

            # Create receipt record
            receipt = Receipt(
                filename=result['filename'],
                merchant=data['merchant'],
                date=data['date'],
                amount=data['total'],
                confidence=result['confidence']
            )
            session.add(receipt)

            # Link to transaction if matched
            if result.get('match') and result['match']['matched']:
                trans = session.query(Transaction).get(
                    result['match']['transaction_id']
                )
                trans.receipt_id = receipt.id
                trans.reviewed = True
            else:
                # Create new expense
                expense = Expense(
                    description=data['merchant'],
                    amount=data['total'],
                    date=data['date'],
                    category=data.get('category', 'Uncategorized'),
                    receipt_id=receipt.id
                )
                session.add(expense)

    session.commit()
        """, language="python")

    with tab4:
        st.markdown("### REST API Integration")
        st.markdown("Expose batch upload via API:")

        st.code("""
from fastapi import FastAPI, UploadFile, File
from typing import List
from components.batch_receipt_upload import process_single_receipt

app = FastAPI()

@app.post("/api/receipts/batch-upload")
async def batch_upload_receipts(
    files: List[UploadFile] = File(...),
    workflow: str = "create_expenses"
):
    '''Batch upload receipts via API'''

    results = []

    for file in files:
        # Process each file
        result = process_single_receipt(
            file=file,
            filename=file.filename,
            session=get_db_session()
        )
        results.append(result)

    # Apply workflow
    if workflow == "create_expenses":
        count = batch_create_expenses(get_db_session(), results)
    elif workflow == "link_transactions":
        count = batch_link_to_transactions(
            get_db_session(),
            results,
            get_transactions()
        )

    return {
        "total": len(results),
        "successful": len([r for r in results if r['status'] == 'success']),
        "failed": len([r for r in results if r['status'] == 'failed']),
        "results": results
    }
        """, language="python")

    st.markdown("---")

    # Quick reference
    st.markdown("### 📚 Quick Reference")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        **Main Functions:**
        - `main_batch_upload_interface()` - Full UI
        - `quick_batch_upload()` - Simple widget
        - `batch_process_receipts()` - Core processing
        - `smart_match_receipts_to_transactions()` - Matching
        """)

    with col2:
        st.markdown("""
        **Helper Functions:**
        - `validate_file()` - File validation
        - `calculate_confidence_score()` - OCR confidence
        - `export_results_to_csv()` - Export data
        - `batch_accept_high_confidence()` - Bulk accept
        """)


if __name__ == "__main__":
    main()
