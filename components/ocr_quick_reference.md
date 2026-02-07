# OCR Receipt Scanner - Quick Reference Card

## Installation (Choose One Engine)

```bash
# Option 1: Tesseract (Recommended - Fast, Free, Local)
pip install Pillow pytesseract
brew install tesseract  # macOS
# or: apt-get install tesseract-ocr  # Ubuntu

# Option 2: EasyOCR (Better accuracy, slower)
pip install Pillow easyocr

# Option 3: Google Vision (Best accuracy, paid)
pip install Pillow google-cloud-vision
```

## Common Use Cases

### 1. Quick Single Receipt Scan

```python
from components.ocr_receipt import quick_ocr

receipt = quick_ocr('/path/to/receipt.jpg')

print(f"Merchant: {receipt.merchant}")
print(f"Date: {receipt.date}")
print(f"Amount: £{receipt.amount}")
```

### 2. Scan with Specific Engine

```python
from components.ocr_receipt import ReceiptOCR

processor = ReceiptOCR(ocr_engine='easyocr')
receipt = processor.process_receipt('/path/to/receipt.jpg')
```

### 3. Batch Process Multiple Receipts

```python
from components.ocr_receipt import batch_ocr

receipts = batch_ocr([
    '/receipts/r1.jpg',
    '/receipts/r2.jpg',
    '/receipts/r3.jpg'
])

for r in receipts:
    print(f"{r.merchant}: £{r.amount}")
```

### 4. Check Confidence & Review

```python
from components.ocr_receipt import quick_ocr, ManualCorrectionUI

receipt = quick_ocr('/path/to/receipt.jpg')

# Check if needs review
if not receipt.is_complete(min_confidence=70):
    print("⚠ Low confidence - needs review")
    print(ManualCorrectionUI.format_review_prompt(receipt))
else:
    print("✓ High confidence")
```

### 5. Match to Merchant Database

```python
from components.ocr_receipt import quick_ocr, match_extracted_merchant

receipt = quick_ocr('/path/to/receipt.jpg')

match = match_extracted_merchant(receipt.merchant)
print(f"Matched: {match['matched_merchant']}")
print(f"Category: {match['suggested_category']}")
print(f"Confidence: {match['match_confidence']}%")
```

### 6. Streamlit Form Integration

```python
import streamlit as st
from components.ocr_receipt import quick_ocr

uploaded = st.file_uploader("Upload Receipt", type=['jpg', 'png'])

if uploaded:
    # Save temp
    with open('/tmp/receipt.jpg', 'wb') as f:
        f.write(uploaded.getbuffer())

    # Scan
    receipt = quick_ocr('/tmp/receipt.jpg')

    # Pre-fill form
    merchant = st.text_input("Merchant", value=receipt.merchant or "")
    date = st.date_input("Date", value=receipt.date)
    amount = st.number_input("Amount", value=float(receipt.amount or 0))

    # Show confidence
    if receipt.is_complete(70):
        st.success("✓ High confidence")
    else:
        st.warning("⚠ Please verify data")
```

### 7. Process with Progress Callback

```python
from components.ocr_receipt import ReceiptOCR

processor = ReceiptOCR()

def progress(current, total, receipt):
    print(f"[{current}/{total}] {receipt.merchant}")

results = processor.batch_process(image_paths, callback=progress)
```

### 8. Save Results to Database

```python
from components.ocr_receipt import quick_ocr
from components.transaction_manager import TransactionManager

receipt = quick_ocr('/path/to/receipt.jpg')

if receipt.is_complete(min_confidence=80):
    tm = TransactionManager()
    tm.add_transaction(
        user_id=user_id,
        merchant_id=find_merchant_id(receipt.merchant),
        amount=receipt.amount,
        date=receipt.date,
        category=categorize_merchant(receipt.merchant),
        receipt_image='/path/to/receipt.jpg'
    )
```

### 9. Export Batch Results to JSON

```python
from components.ocr_receipt import batch_ocr
import json

receipts = batch_ocr(image_paths)

export_data = [
    {
        'merchant': r.merchant,
        'date': str(r.date),
        'amount': r.amount,
        'confidence': r.confidence
    }
    for r in receipts if r.is_complete(70)
]

with open('receipts_export.json', 'w') as f:
    json.dump(export_data, f, indent=2)
```

### 10. Custom Preprocessing

```python
from components.ocr_receipt import ReceiptOCR, ImagePreprocessor
from PIL import Image, ImageEnhance

# Preprocess manually
preprocessor = ImagePreprocessor()
image = Image.open('/path/to/receipt.jpg')

# Extra contrast boost
enhancer = ImageEnhance.Contrast(image)
enhanced = enhancer.enhance(3.0)
enhanced.save('/tmp/enhanced.jpg')

# Process enhanced image
processor = ReceiptOCR(preprocess=False)
receipt = processor.process_receipt('/tmp/enhanced.jpg')
```

## Confidence Thresholds

```python
# Conservative (fewer errors, more manual reviews)
min_confidence = 85

# Balanced (recommended)
min_confidence = 70

# Aggressive (more auto-accept, some errors)
min_confidence = 50
```

## Field-Specific Checks

```python
receipt = quick_ocr('/path/to/receipt.jpg')

# Check individual field confidence
if receipt.confidence['merchant'] < 60:
    print("⚠ Merchant uncertain")

if receipt.confidence['date'] < 60:
    print("⚠ Date uncertain")

if receipt.confidence['amount'] < 80:
    print("⚠ Amount uncertain - critical field")
```

## Common Patterns

### UK Supermarket Receipt

```python
# Typical extraction for Tesco/Sainsbury's/Asda
# Expected fields:
# - merchant: "TESCO" (90-100% confidence)
# - date: DD/MM/YYYY format (80-95% confidence)
# - amount: Total with "TOTAL" keyword (95-100% confidence)
# - tax_amount: VAT line (if present)
# - line_items: 5-20 items typically
```

### UK Restaurant Receipt

```python
# Typical extraction for Costa/Greggs/Pret
# Expected fields:
# - merchant: "COSTA" (90-100% confidence)
# - date: DD/MM/YYYY or DD-MM-YYYY (75-90% confidence)
# - amount: Total with "TOTAL" or "BALANCE" (90-100% confidence)
# - line_items: 1-5 items typically
```

### Fuel Receipt

```python
# Special handling for fuel receipts
receipt = quick_ocr('/path/to/fuel_receipt.jpg')

# Usually have "FUEL" or "PETROL" in line items
if any('FUEL' in item['item'].upper() for item in receipt.line_items):
    category = "Fuel"
```

## Error Handling

```python
from components.ocr_receipt import ReceiptOCR

processor = ReceiptOCR()

try:
    receipt = processor.process_receipt('/path/to/receipt.jpg')

    if not receipt.raw_text:
        print("No text extracted - image may be blank")
    elif not receipt.is_complete(70):
        print("Low confidence extraction")
    else:
        print("Success!")

except Exception as e:
    print(f"OCR failed: {e}")
```

## Performance Tips

```python
# For batch processing, use batch method (faster)
receipts = batch_ocr(image_paths)  # Optimized

# NOT:
receipts = [quick_ocr(p) for p in image_paths]  # Slower

# For very large batches, use parallel processing
from concurrent.futures import ThreadPoolExecutor

processor = ReceiptOCR()
with ThreadPoolExecutor(max_workers=4) as executor:
    results = list(executor.map(processor.process_receipt, image_paths))
```

## Validation

```python
from datetime import date

def validate_receipt(receipt):
    """Validate extracted data for anomalies"""

    # Check amount is reasonable
    if receipt.amount and receipt.amount > 10000:
        return False, "Amount too high"

    # Check date not in future
    if receipt.date and receipt.date > date.today():
        return False, "Future date"

    # Check merchant exists
    if not receipt.merchant:
        return False, "No merchant"

    return True, "OK"

is_valid, message = validate_receipt(receipt)
```

## Demo App

```bash
# Run interactive Streamlit demo
streamlit run components/ocr_demo_app.py

# Features:
# - Single receipt upload
# - Batch processing
# - Confidence visualization
# - Manual correction
# - Export to JSON
```

## Testing

```bash
# Run test suite
python components/ocr_receipt_test.py

# Expected output:
# - 20+ unit tests
# - All passing
# - Accuracy benchmarks displayed
```

## Quick Debugging

```python
from components.ocr_receipt import quick_ocr, ManualCorrectionUI

receipt = quick_ocr('/path/to/problematic_receipt.jpg')

# Print formatted review
print(ManualCorrectionUI.format_review_prompt(receipt))

# Shows:
# - Extracted fields with confidence
# - Raw OCR text
# - Helpful for debugging extraction issues
```

## Check Available Engines

```python
from components.ocr_receipt import (
    TESSERACT_AVAILABLE,
    EASYOCR_AVAILABLE,
    GOOGLE_VISION_AVAILABLE
)

print(f"Tesseract: {TESSERACT_AVAILABLE}")
print(f"EasyOCR: {EASYOCR_AVAILABLE}")
print(f"Google Vision: {GOOGLE_VISION_AVAILABLE}")
```

## Expected Accuracy by Receipt Type

| Receipt Type | Merchant | Date | Amount | Overall |
|--------------|----------|------|--------|---------|
| Supermarket (clear) | 90-95% | 85-90% | 95-98% | 90-95% |
| Restaurant (clear) | 85-90% | 80-85% | 90-95% | 85-90% |
| Fuel (clear) | 80-85% | 80-85% | 90-95% | 85-90% |
| Faded/crumpled | 60-70% | 50-65% | 70-80% | 60-70% |

## Engine Selection Guide

**Use Tesseract if:**
- Processing locally
- High volume (>100 receipts/day)
- Cost-sensitive
- Clear receipt images

**Use EasyOCR if:**
- Need better accuracy than Tesseract
- OK with slower processing
- Cost-sensitive
- Mixed quality images

**Use Google Vision if:**
- Need best accuracy
- Have API budget
- Processing critical receipts
- Poor quality images
