"""
Streamlit Demo Application for OCR Receipt Scanner
Interactive demo showing all OCR features
"""

import streamlit as st
import os
from pathlib import Path
from datetime import datetime
import json

# Import OCR components
try:
    from components.ocr_receipt import (
        ReceiptOCR,
        ManualCorrectionUI,
        match_extracted_merchant,
        categorize_merchant,
        ReceiptData,
        TESSERACT_AVAILABLE,
        EASYOCR_AVAILABLE,
        GOOGLE_VISION_AVAILABLE
    )
    OCR_AVAILABLE = True
except ImportError as e:
    OCR_AVAILABLE = False
    st.error(f"OCR module import failed: {e}")


def main():
    st.set_page_config(
        page_title="Receipt OCR Scanner Demo",
        page_icon="📝",
        layout="wide"
    )

    st.title("📝 Receipt OCR Scanner Demo")
    st.markdown("Automatic data extraction from receipt images")

    if not OCR_AVAILABLE:
        st.error("OCR components not available. Please check installation.")
        return

    # Sidebar - OCR Configuration
    with st.sidebar:
        st.header("⚙️ Configuration")

        # Check available engines
        available_engines = []
        if TESSERACT_AVAILABLE:
            available_engines.append("tesseract")
        if EASYOCR_AVAILABLE:
            available_engines.append("easyocr")
        if GOOGLE_VISION_AVAILABLE:
            available_engines.append("google_vision")

        if not available_engines:
            st.error("No OCR engines available!")
            st.info(
                "Install at least one:\n"
                "- `pip install pytesseract`\n"
                "- `pip install easyocr`\n"
                "- `pip install google-cloud-vision`"
            )
            return

        available_engines.insert(0, "auto")

        ocr_engine = st.selectbox(
            "OCR Engine",
            options=available_engines,
            index=0,
            help="Auto selects best available engine"
        )

        preprocess = st.checkbox(
            "Enable Image Preprocessing",
            value=True,
            help="Enhance image quality before OCR"
        )

        min_confidence = st.slider(
            "Minimum Confidence (%)",
            min_value=0,
            max_value=100,
            value=70,
            help="Minimum confidence to auto-accept extraction"
        )

        st.divider()

        st.subheader("Available Engines")
        st.write(f"✓ Tesseract" if TESSERACT_AVAILABLE else "✗ Tesseract")
        st.write(f"✓ EasyOCR" if EASYOCR_AVAILABLE else "✗ EasyOCR")
        st.write(f"✓ Google Vision" if GOOGLE_VISION_AVAILABLE else "✗ Google Vision")

    # Initialize OCR processor
    if 'ocr_processor' not in st.session_state:
        try:
            st.session_state.ocr_processor = ReceiptOCR(
                ocr_engine=ocr_engine,
                preprocess=preprocess
            )
        except Exception as e:
            st.error(f"Failed to initialize OCR: {e}")
            return

    # Main content tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📤 Single Receipt",
        "📦 Batch Upload",
        "📊 Results History",
        "ℹ️ Help & Info"
    ])

    # Tab 1: Single Receipt Upload
    with tab1:
        st.header("Upload Single Receipt")

        uploaded_file = st.file_uploader(
            "Choose receipt image",
            type=['jpg', 'jpeg', 'png'],
            key="single_upload"
        )

        if uploaded_file:
            col1, col2 = st.columns([1, 1])

            with col1:
                st.subheader("Original Image")
                st.image(uploaded_file, use_container_width=True)

            with col2:
                st.subheader("Extracted Data")

                # Save temporary file
                temp_dir = Path("/tmp/receipt_ocr")
                temp_dir.mkdir(exist_ok=True)
                temp_path = temp_dir / f"receipt_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"

                with open(temp_path, 'wb') as f:
                    f.write(uploaded_file.getbuffer())

                # Process with OCR
                if st.button("🔍 Scan Receipt", type="primary"):
                    with st.spinner(f"Processing with {ocr_engine}..."):
                        try:
                            receipt = st.session_state.ocr_processor.process_receipt(str(temp_path))
                            st.session_state.current_receipt = receipt

                            # Save to history
                            if 'receipt_history' not in st.session_state:
                                st.session_state.receipt_history = []
                            st.session_state.receipt_history.append({
                                'filename': uploaded_file.name,
                                'timestamp': datetime.now().isoformat(),
                                'receipt': receipt
                            })

                        except Exception as e:
                            st.error(f"OCR processing failed: {e}")

                # Display results
                if 'current_receipt' in st.session_state:
                    receipt = st.session_state.current_receipt

                    # Confidence indicator
                    if receipt.is_complete(min_confidence):
                        st.success("✓ High confidence extraction")
                    else:
                        st.warning("⚠ Low confidence - please review")

                    # Editable fields
                    st.divider()

                    merchant = st.text_input(
                        "Merchant",
                        value=receipt.merchant or "",
                        help=f"Confidence: {receipt.confidence.get('merchant', 0)}%"
                    )

                    date_val = st.date_input(
                        "Date",
                        value=receipt.date if receipt.date else None,
                        help=f"Confidence: {receipt.confidence.get('date', 0)}%"
                    )

                    amount = st.number_input(
                        "Amount (£)",
                        value=float(receipt.amount) if receipt.amount else 0.0,
                        min_value=0.0,
                        step=0.01,
                        format="%.2f",
                        help=f"Confidence: {receipt.confidence.get('amount', 0)}%"
                    )

                    if receipt.tax_amount:
                        st.text_input(
                            "VAT Amount",
                            value=f"£{receipt.tax_amount:.2f}",
                            disabled=True
                        )

                    # Merchant matching
                    st.divider()
                    match_result = match_extracted_merchant(merchant)

                    st.text_input(
                        "Suggested Category",
                        value=match_result['suggested_category'],
                        disabled=True
                    )

                    st.metric(
                        "Merchant Match Confidence",
                        f"{match_result['match_confidence']}%"
                    )

                    # Confidence scores
                    st.divider()
                    st.subheader("Confidence Scores")

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        conf_merchant = receipt.confidence.get('merchant', 0)
                        color = "normal" if conf_merchant >= min_confidence else "inverse"
                        st.metric(
                            "Merchant",
                            f"{conf_merchant}%",
                            delta="✓" if conf_merchant >= min_confidence else "⚠"
                        )

                    with col2:
                        conf_date = receipt.confidence.get('date', 0)
                        st.metric(
                            "Date",
                            f"{conf_date}%",
                            delta="✓" if conf_date >= min_confidence else "⚠"
                        )

                    with col3:
                        conf_amount = receipt.confidence.get('amount', 0)
                        st.metric(
                            "Amount",
                            f"{conf_amount}%",
                            delta="✓" if conf_amount >= min_confidence else "⚠"
                        )

                    # Line items
                    if receipt.line_items:
                        st.divider()
                        st.subheader("Line Items")
                        for i, item in enumerate(receipt.line_items, 1):
                            st.text(f"{i}. {item['item']} - £{item['price']:.2f}")

                    # Raw OCR text
                    with st.expander("📄 View Raw OCR Text"):
                        st.text_area(
                            "Raw Text",
                            value=receipt.raw_text,
                            height=200,
                            disabled=True
                        )

                    # Action buttons
                    st.divider()
                    col1, col2 = st.columns(2)

                    with col1:
                        if st.button("✓ Accept & Save", type="primary", use_container_width=True):
                            # Update receipt with edited values
                            receipt.merchant = merchant
                            receipt.date = date_val
                            receipt.amount = amount

                            st.success("Receipt accepted and saved!")

                            # Here you would save to database
                            # transaction_manager.add_transaction(...)

                    with col2:
                        if st.button("✗ Reject", use_container_width=True):
                            st.warning("Receipt rejected")
                            del st.session_state.current_receipt

    # Tab 2: Batch Upload
    with tab2:
        st.header("Batch Receipt Upload")

        uploaded_files = st.file_uploader(
            "Choose multiple receipt images",
            type=['jpg', 'jpeg', 'png'],
            accept_multiple_files=True,
            key="batch_upload"
        )

        if uploaded_files:
            st.info(f"{len(uploaded_files)} files selected")

            if st.button("🔍 Scan All Receipts", type="primary"):
                progress_bar = st.progress(0)
                status_text = st.empty()

                temp_dir = Path("/tmp/receipt_ocr")
                temp_dir.mkdir(exist_ok=True)

                batch_results = []

                for i, file in enumerate(uploaded_files):
                    status_text.text(f"Processing {file.name}... ({i+1}/{len(uploaded_files)})")

                    # Save temp file
                    temp_path = temp_dir / f"batch_{i}_{file.name}"
                    with open(temp_path, 'wb') as f:
                        f.write(file.getbuffer())

                    # Process
                    try:
                        receipt = st.session_state.ocr_processor.process_receipt(str(temp_path))
                        batch_results.append({
                            'filename': file.name,
                            'receipt': receipt,
                            'status': 'success'
                        })
                    except Exception as e:
                        batch_results.append({
                            'filename': file.name,
                            'receipt': None,
                            'status': 'error',
                            'error': str(e)
                        })

                    progress_bar.progress((i + 1) / len(uploaded_files))

                status_text.text("✓ Batch processing complete!")

                # Store results
                st.session_state.batch_results = batch_results

                # Summary
                successful = sum(1 for r in batch_results if r['status'] == 'success')
                st.success(f"Successfully processed {successful}/{len(uploaded_files)} receipts")

            # Display batch results
            if 'batch_results' in st.session_state:
                st.divider()
                st.subheader("Batch Results")

                for i, result in enumerate(st.session_state.batch_results):
                    with st.expander(f"{i+1}. {result['filename']} - {result['status'].upper()}"):
                        if result['status'] == 'success':
                            receipt = result['receipt']

                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Merchant", receipt.merchant or "N/A")
                            with col2:
                                st.metric("Date", str(receipt.date) if receipt.date else "N/A")
                            with col3:
                                st.metric("Amount", f"£{receipt.amount:.2f}" if receipt.amount else "N/A")

                            # Confidence
                            st.caption(
                                f"Confidence: Merchant {receipt.confidence.get('merchant', 0)}%, "
                                f"Date {receipt.confidence.get('date', 0)}%, "
                                f"Amount {receipt.confidence.get('amount', 0)}%"
                            )

                            if not receipt.is_complete(min_confidence):
                                st.warning("⚠ Needs review")

                        else:
                            st.error(f"Error: {result.get('error', 'Unknown error')}")

                # Export results
                st.divider()
                if st.button("📥 Export to JSON"):
                    export_data = []
                    for result in st.session_state.batch_results:
                        if result['status'] == 'success':
                            export_data.append({
                                'filename': result['filename'],
                                'merchant': result['receipt'].merchant,
                                'date': str(result['receipt'].date) if result['receipt'].date else None,
                                'amount': result['receipt'].amount,
                                'confidence': result['receipt'].confidence
                            })

                    json_str = json.dumps(export_data, indent=2)
                    st.download_button(
                        "Download JSON",
                        json_str,
                        file_name=f"receipts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json"
                    )

    # Tab 3: Results History
    with tab3:
        st.header("Processing History")

        if 'receipt_history' in st.session_state and st.session_state.receipt_history:
            st.info(f"Total receipts processed: {len(st.session_state.receipt_history)}")

            for i, entry in enumerate(reversed(st.session_state.receipt_history)):
                with st.expander(f"{entry['filename']} - {entry['timestamp']}"):
                    receipt = entry['receipt']

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Merchant", receipt.merchant or "N/A")
                    with col2:
                        st.metric("Date", str(receipt.date) if receipt.date else "N/A")
                    with col3:
                        st.metric("Amount", f"£{receipt.amount:.2f}" if receipt.amount else "N/A")

            # Clear history
            if st.button("🗑️ Clear History"):
                st.session_state.receipt_history = []
                st.rerun()

        else:
            st.info("No receipts processed yet")

    # Tab 4: Help & Info
    with tab4:
        st.header("Help & Information")

        st.subheader("🎯 Expected Accuracy")
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Clear Receipts**")
            st.metric("Merchant", "85-95%")
            st.metric("Date", "80-90%")
            st.metric("Amount", "90-98%")

        with col2:
            st.markdown("**Degraded Quality**")
            st.metric("Merchant", "60-75%")
            st.metric("Date", "50-70%")
            st.metric("Amount", "70-85%")

        st.divider()

        st.subheader("⚡ OCR Engine Comparison")
        comparison_data = {
            "Engine": ["Tesseract", "EasyOCR", "Google Vision"],
            "Speed": ["Fast (1-2s)", "Medium (3-5s)", "Fast (1-2s)"],
            "Accuracy": ["70-80%", "80-90%", "90-95%"],
            "Cost": ["Free", "Free", "Paid ($1.50/1000)"],
            "Best For": ["High volume", "Best free option", "Best accuracy"]
        }
        st.table(comparison_data)

        st.divider()

        st.subheader("💡 Tips for Better Results")
        st.markdown("""
        **Image Quality:**
        - Minimum 1000px width
        - Even lighting, no shadows
        - Straight-on angle, not tilted
        - Sharp focus, not blurry

        **Receipt Condition:**
        - Unfold and flatten before scanning
        - Avoid wrinkled or torn receipts
        - Ensure text is not faded

        **Processing:**
        - Enable image preprocessing (recommended)
        - Try different OCR engines if results are poor
        - Always review low-confidence extractions
        """)

        st.divider()

        st.subheader("🔧 Supported Formats")
        st.markdown("""
        **UK Receipt Patterns:**
        - Date formats: DD/MM/YYYY, DD-MM-YYYY, DD MMM YYYY
        - Currency: £ (GBP)
        - Known merchants: Tesco, Sainsbury's, Asda, Morrisons, Waitrose, Costa, Greggs, and more

        **Extracted Fields:**
        - Merchant name
        - Transaction date
        - Total amount
        - VAT/tax amount
        - Individual line items
        - Payment method
        """)


if __name__ == "__main__":
    main()
