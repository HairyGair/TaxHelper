#!/usr/bin/env python3
"""
Simple example demonstrating OCR receipt scanning

This script shows the most common use case:
1. Scan a receipt image
2. Extract merchant, date, amount
3. Display results with confidence scores
4. Save to transaction if confidence is high enough

Usage:
    python example_ocr_usage.py /path/to/receipt.jpg
"""

import sys
from pathlib import Path
from datetime import date

# Import OCR components
try:
    from components.ocr_receipt import (
        quick_ocr,
        match_extracted_merchant,
        ManualCorrectionUI,
        ReceiptOCR,
        TESSERACT_AVAILABLE,
        EASYOCR_AVAILABLE,
        GOOGLE_VISION_AVAILABLE
    )
except ImportError as e:
    print(f"Error: Could not import OCR components: {e}")
    print("\nPlease ensure you have installed the required dependencies:")
    print("  pip install Pillow pytesseract")
    print("  brew install tesseract  # macOS")
    sys.exit(1)


def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 60)
    print(text.center(60))
    print("=" * 60)


def print_section(title):
    """Print section divider"""
    print(f"\n{title}")
    print("-" * 60)


def display_confidence_indicator(confidence):
    """Display confidence with visual indicator"""
    if confidence >= 90:
        indicator = "🟢"
        rating = "Excellent"
    elif confidence >= 70:
        indicator = "🟡"
        rating = "Good"
    elif confidence >= 50:
        indicator = "🟠"
        rating = "Fair"
    else:
        indicator = "🔴"
        rating = "Poor"

    return f"{indicator} {confidence}% ({rating})"


def main():
    """Main execution"""

    # Check command line arguments
    if len(sys.argv) < 2:
        print("Usage: python example_ocr_usage.py <receipt_image_path>")
        print("\nExample:")
        print("  python example_ocr_usage.py /path/to/receipt.jpg")
        sys.exit(1)

    image_path = sys.argv[1]

    # Verify file exists
    if not Path(image_path).exists():
        print(f"Error: File not found: {image_path}")
        sys.exit(1)

    print_header("OCR RECEIPT SCANNER - DEMO")

    # Check available OCR engines
    print_section("Available OCR Engines")
    print(f"  Tesseract:      {'✓ Available' if TESSERACT_AVAILABLE else '✗ Not installed'}")
    print(f"  EasyOCR:        {'✓ Available' if EASYOCR_AVAILABLE else '✗ Not installed'}")
    print(f"  Google Vision:  {'✓ Available' if GOOGLE_VISION_AVAILABLE else '✗ Not installed'}")

    if not any([TESSERACT_AVAILABLE, EASYOCR_AVAILABLE, GOOGLE_VISION_AVAILABLE]):
        print("\n❌ No OCR engine available!")
        print("\nPlease install at least one:")
        print("  - Tesseract: pip install pytesseract && brew install tesseract")
        print("  - EasyOCR: pip install easyocr")
        print("  - Google Vision: pip install google-cloud-vision")
        sys.exit(1)

    # Process receipt
    print_section("Processing Receipt")
    print(f"  Image: {image_path}")
    print("  Status: Scanning...")

    try:
        receipt = quick_ocr(image_path)
        print("  Status: ✓ Complete")
    except Exception as e:
        print(f"  Status: ✗ Failed - {e}")
        sys.exit(1)

    # Display extracted data
    print_section("Extracted Data")

    print(f"\n  Merchant:  {receipt.merchant or '[NOT FOUND]'}")
    print(f"             Confidence: {display_confidence_indicator(receipt.confidence.get('merchant', 0))}")

    print(f"\n  Date:      {receipt.date or '[NOT FOUND]'}")
    print(f"             Confidence: {display_confidence_indicator(receipt.confidence.get('date', 0))}")

    print(f"\n  Amount:    £{receipt.amount if receipt.amount else '[NOT FOUND]'}")
    print(f"             Confidence: {display_confidence_indicator(receipt.confidence.get('amount', 0))}")

    if receipt.tax_amount:
        print(f"\n  VAT:       £{receipt.tax_amount:.2f}")

    if receipt.line_items:
        print(f"\n  Line Items: {len(receipt.line_items)} items found")
        for i, item in enumerate(receipt.line_items[:5], 1):
            print(f"    {i}. {item['item']} - £{item['price']:.2f}")
        if len(receipt.line_items) > 5:
            print(f"    ... and {len(receipt.line_items) - 5} more")

    # Merchant matching
    print_section("Merchant Analysis")

    match_result = match_extracted_merchant(receipt.merchant)
    print(f"  Matched Merchant: {match_result['matched_merchant']}")
    print(f"  Match Confidence: {display_confidence_indicator(match_result['match_confidence'])}")
    print(f"  Suggested Category: {match_result['suggested_category']}")

    # Overall assessment
    print_section("Overall Assessment")

    avg_confidence = sum(receipt.confidence.values()) / len(receipt.confidence)

    print(f"  Average Confidence: {avg_confidence:.1f}%")

    if receipt.is_complete(min_confidence=70):
        print("  Status: ✓ HIGH CONFIDENCE - Ready to auto-save")
        auto_save_recommended = True
    elif receipt.is_complete(min_confidence=50):
        print("  Status: ⚠ MEDIUM CONFIDENCE - Manual review recommended")
        auto_save_recommended = False
    else:
        print("  Status: ✗ LOW CONFIDENCE - Manual entry required")
        auto_save_recommended = False

    # Recommendations
    print_section("Recommendations")

    if auto_save_recommended:
        print("  ✓ Data quality is good enough for automatic transaction creation")
        print("  ✓ Merchant, date, and amount are all reliably extracted")
        print("\n  Next steps:")
        print("    1. Save to transaction database")
        print("    2. Link receipt image")
        print("    3. Apply suggested category")
    else:
        print("  ⚠ Manual review or correction needed before saving")

        # Specific recommendations
        if receipt.confidence.get('merchant', 0) < 70:
            print("\n  Issues:")
            print("    - Merchant name uncertain or not found")
            print("    - Recommendation: Manually select from dropdown")

        if receipt.confidence.get('date', 0) < 70:
            print("\n  Issues:")
            print("    - Date extraction uncertain")
            print("    - Recommendation: Verify date format and re-enter if needed")

        if receipt.confidence.get('amount', 0) < 80:
            print("\n  Issues:")
            print("    - Amount extraction uncertain (critical field)")
            print("    - Recommendation: Manually verify total amount")

        print("\n  Next steps:")
        print("    1. Review extracted data")
        print("    2. Correct any errors")
        print("    3. Save to transaction database")

    # Raw text preview
    print_section("Raw OCR Text (First 300 chars)")
    print("\n" + receipt.raw_text[:300].strip())
    if len(receipt.raw_text) > 300:
        print("...")

    # Example code for saving
    print_section("Example: Save to Database")
    print("""
    # After verifying data is correct:
    from components.transaction_manager import TransactionManager

    tm = TransactionManager()
    transaction = tm.add_transaction(
        user_id=user_id,
        merchant_id=find_merchant_id(receipt.merchant),
        amount=receipt.amount,
        date=receipt.date,
        category=match_result['suggested_category'],
        receipt_image=image_path,
        notes=f"OCR confidence: {avg_confidence:.1f}%"
    )
    """)

    print_header("PROCESSING COMPLETE")

    # Exit with appropriate code
    sys.exit(0 if auto_save_recommended else 1)


if __name__ == "__main__":
    main()
