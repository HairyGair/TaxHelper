"""
OCR Receipt Scanning System
Automatic data extraction from receipt images with multiple OCR provider support

Features:
- Multiple OCR engines (Tesseract, EasyOCR, Google Cloud Vision)
- Smart field extraction with confidence scoring
- UK-specific receipt patterns
- Image preprocessing for better accuracy
- Batch processing support
- Manual correction interface
"""

import re
import os
from datetime import datetime, date
from typing import Dict, List, Optional, Tuple, Callable, Any
from dataclasses import dataclass, asdict
from pathlib import Path
import logging

# Image processing
try:
    from PIL import Image, ImageEnhance, ImageFilter, ImageOps
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    logging.warning("Pillow not available - image preprocessing disabled")

# OCR engines
try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    logging.info("Tesseract not available")

try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False
    logging.info("EasyOCR not available")

try:
    from google.cloud import vision
    GOOGLE_VISION_AVAILABLE = True
except ImportError:
    GOOGLE_VISION_AVAILABLE = False
    logging.info("Google Cloud Vision not available")


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ReceiptData:
    """Structured receipt data"""
    merchant: Optional[str] = None
    date: Optional[date] = None
    amount: Optional[float] = None
    raw_text: str = ""
    confidence: Dict[str, int] = None
    line_items: List[Dict[str, Any]] = None
    tax_amount: Optional[float] = None
    payment_method: Optional[str] = None

    def __post_init__(self):
        if self.confidence is None:
            self.confidence = {'merchant': 0, 'date': 0, 'amount': 0}
        if self.line_items is None:
            self.line_items = []

    def to_dict(self):
        """Convert to dictionary with date serialization"""
        data = asdict(self)
        if self.date:
            data['date'] = self.date.isoformat()
        return data

    def is_complete(self, min_confidence: int = 70) -> bool:
        """Check if all essential fields are extracted with sufficient confidence"""
        return (
            self.merchant is not None and
            self.date is not None and
            self.amount is not None and
            self.confidence.get('merchant', 0) >= min_confidence and
            self.confidence.get('date', 0) >= min_confidence and
            self.confidence.get('amount', 0) >= min_confidence
        )


# UK-specific patterns and merchant lists
UK_SUPERMARKETS = [
    'TESCO', 'SAINSBURY', 'SAINSBURYS', 'ASDA', 'MORRISONS', 'WAITROSE',
    'ALDI', 'LIDL', 'MARKS & SPENCER', 'M&S', 'ICELAND', 'CO-OP', 'COOP'
]

UK_RESTAURANTS = [
    'COSTA', 'GREGGS', 'PRET', 'PRET A MANGER', 'NANDOS', "NANDO'S",
    'MCDONALDS', "MCDONALD'S", 'KFC', 'SUBWAY', 'STARBUCKS', 'CAFE NERO',
    'PIZZA HUT', 'DOMINOS', "DOMINO'S", 'WAGAMAMA', 'NANDOS'
]

UK_RETAILERS = [
    'BOOTS', 'SUPERDRUG', 'ARGOS', 'CURRYS', 'JOHN LEWIS', 'NEXT',
    'PRIMARK', 'H&M', 'ZARA', 'DEBENHAMS', 'HOUSE OF FRASER'
]

ALL_UK_MERCHANTS = UK_SUPERMARKETS + UK_RESTAURANTS + UK_RETAILERS

# Date patterns (UK formats)
DATE_PATTERNS = [
    (r'(\d{2})[/-](\d{2})[/-](\d{4})', 'DD/MM/YYYY'),  # 17/10/2024 or 17-10-2024
    (r'(\d{2})[/-](\d{2})[/-](\d{2})', 'DD/MM/YY'),    # 17/10/24
    (r'(\d{2})\s+(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)[A-Z]*\s+(\d{4})', 'DD MMM YYYY'),  # 17 OCT 2024
    (r'(\d{4})[/-](\d{2})[/-](\d{2})', 'YYYY/MM/DD'),  # 2024/10/17 (ISO format)
]

MONTH_MAP = {
    'JAN': 1, 'FEB': 2, 'MAR': 3, 'APR': 4, 'MAY': 5, 'JUN': 6,
    'JUL': 7, 'AUG': 8, 'SEP': 9, 'OCT': 10, 'NOV': 11, 'DEC': 12
}

# Amount patterns
AMOUNT_PATTERNS = [
    (r'TOTAL[:\s]+£?(\d+[.,]\d{2})', 'TOTAL'),
    (r'BALANCE[:\s]+£?(\d+[.,]\d{2})', 'BALANCE'),
    (r'AMOUNT\s+DUE[:\s]+£?(\d+[.,]\d{2})', 'AMOUNT DUE'),
    (r'TO\s+PAY[:\s]+£?(\d+[.,]\d{2})', 'TO PAY'),
    (r'GRAND\s+TOTAL[:\s]+£?(\d+[.,]\d{2})', 'GRAND TOTAL'),
    (r'£(\d+[.,]\d{2})', 'CURRENCY'),  # Generic £ amount
    (r'GBP\s*(\d+[.,]\d{2})', 'GBP'),
]

# Tax patterns
TAX_PATTERNS = [
    r'VAT[:\s]+£?(\d+[.,]\d{2})',
    r'TAX[:\s]+£?(\d+[.,]\d{2})',
    r'20%[:\s]+£?(\d+[.,]\d{2})',
]


class OCREngine:
    """Base class for OCR engines"""

    @staticmethod
    def extract_text_tesseract(image_path: str) -> str:
        """Extract text using Tesseract OCR"""
        if not TESSERACT_AVAILABLE:
            raise ImportError("Tesseract not available. Install: pip install pytesseract")
        if not PIL_AVAILABLE:
            raise ImportError("Pillow not available. Install: pip install Pillow")

        try:
            image = Image.open(image_path)
            # Use config optimized for receipts
            config = '--psm 6 --oem 3'  # Assume uniform block of text
            text = pytesseract.image_to_string(image, config=config)
            logger.info(f"Tesseract extracted {len(text)} characters")
            return text
        except Exception as e:
            logger.error(f"Tesseract OCR failed: {e}")
            return ""

    @staticmethod
    def extract_text_easyocr(image_path: str) -> str:
        """Extract text using EasyOCR"""
        if not EASYOCR_AVAILABLE:
            raise ImportError("EasyOCR not available. Install: pip install easyocr")

        try:
            reader = easyocr.Reader(['en'], gpu=False, verbose=False)
            results = reader.readtext(image_path)
            # Combine text with newlines to preserve structure
            text = '\n'.join([result[1] for result in results])
            logger.info(f"EasyOCR extracted {len(results)} text blocks")
            return text
        except Exception as e:
            logger.error(f"EasyOCR failed: {e}")
            return ""

    @staticmethod
    def extract_text_google_vision(image_path: str) -> str:
        """Extract text using Google Cloud Vision"""
        if not GOOGLE_VISION_AVAILABLE:
            raise ImportError("Google Cloud Vision not available. Install: pip install google-cloud-vision")

        try:
            client = vision.ImageAnnotatorClient()
            with open(image_path, 'rb') as f:
                content = f.read()

            image = vision.Image(content=content)
            response = client.text_detection(image=image)

            if response.error.message:
                raise Exception(f"Google Vision API error: {response.error.message}")

            if response.text_annotations:
                text = response.text_annotations[0].description
                logger.info(f"Google Vision extracted {len(text)} characters")
                return text
            else:
                logger.warning("Google Vision found no text")
                return ""
        except Exception as e:
            logger.error(f"Google Vision OCR failed: {e}")
            return ""


class ImagePreprocessor:
    """Image preprocessing for better OCR results"""

    @staticmethod
    def preprocess_image(image_path: str, output_path: Optional[str] = None) -> Image.Image:
        """
        Enhance image for better OCR results

        Args:
            image_path: Path to original image
            output_path: Optional path to save preprocessed image

        Returns:
            Preprocessed PIL Image
        """
        if not PIL_AVAILABLE:
            raise ImportError("Pillow not available. Install: pip install Pillow")

        try:
            image = Image.open(image_path)
            logger.info(f"Original image size: {image.size}, mode: {image.mode}")

            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')

            # Auto-orient based on EXIF data
            image = ImageOps.exif_transpose(image)

            # Convert to grayscale
            image = image.convert('L')

            # Resize if too small (OCR works better with larger images)
            if image.width < 1000:
                scale = 1000 / image.width
                new_size = (int(image.width * scale), int(image.height * scale))
                image = image.resize(new_size, Image.LANCZOS)
                logger.info(f"Resized to: {new_size}")

            # Increase contrast
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(2.0)

            # Increase sharpness
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(1.5)

            # Apply sharpening filter
            image = image.filter(ImageFilter.SHARPEN)

            # Optional: threshold to black and white for very clear text
            # Uncomment if needed for low-quality images
            # threshold = 128
            # image = image.point(lambda p: 255 if p > threshold else 0)

            if output_path:
                image.save(output_path)
                logger.info(f"Preprocessed image saved to: {output_path}")

            return image
        except Exception as e:
            logger.error(f"Image preprocessing failed: {e}")
            # Return original image if preprocessing fails
            return Image.open(image_path)


class ReceiptParser:
    """Smart receipt data extraction"""

    @staticmethod
    def find_merchant_name(text: str) -> Tuple[Optional[str], int]:
        """
        Extract merchant name from receipt text

        Returns:
            (merchant_name, confidence_score)
        """
        lines = [line.strip().upper() for line in text.split('\n') if line.strip()]
        if not lines:
            return None, 0

        # Check first 5 lines for known merchants
        for i, line in enumerate(lines[:5]):
            for merchant in ALL_UK_MERCHANTS:
                if merchant in line:
                    # Higher confidence if found in first 2 lines
                    confidence = 100 if i < 2 else 90
                    logger.info(f"Matched merchant: {merchant} (confidence: {confidence})")
                    return merchant, confidence

        # Fuzzy matching for first line (usually merchant name)
        if lines:
            first_line = lines[0]
            # Check if it looks like a merchant name (mostly letters, not numbers)
            if len(first_line) > 2 and sum(c.isalpha() for c in first_line) > len(first_line) * 0.5:
                # Use first line as merchant with lower confidence
                confidence = 50
                logger.info(f"Using first line as merchant: {first_line} (confidence: {confidence})")
                return first_line, confidence

        return None, 0

    @staticmethod
    def find_date(text: str) -> Tuple[Optional[date], int]:
        """
        Extract transaction date from receipt text

        Returns:
            (date_object, confidence_score)
        """
        text_upper = text.upper()

        for pattern, format_name in DATE_PATTERNS:
            matches = re.finditer(pattern, text_upper)
            for match in matches:
                try:
                    if format_name == 'DD/MM/YYYY':
                        day, month, year = int(match.group(1)), int(match.group(2)), int(match.group(3))
                    elif format_name == 'DD/MM/YY':
                        day, month, year = int(match.group(1)), int(match.group(2)), 2000 + int(match.group(3))
                    elif format_name == 'DD MMM YYYY':
                        day = int(match.group(1))
                        month = MONTH_MAP.get(match.group(2)[:3], 0)
                        year = int(match.group(3))
                    elif format_name == 'YYYY/MM/DD':
                        year, month, day = int(match.group(1)), int(match.group(2)), int(match.group(3))
                    else:
                        continue

                    # Validate date
                    parsed_date = date(year, month, day)

                    # Check if date is reasonable (not in future, not too old)
                    today = date.today()
                    if parsed_date <= today and (today.year - parsed_date.year) <= 10:
                        confidence = 100 if format_name != 'DD/MM/YY' else 85
                        logger.info(f"Found date: {parsed_date} (confidence: {confidence})")
                        return parsed_date, confidence
                except (ValueError, KeyError) as e:
                    continue

        return None, 0

    @staticmethod
    def find_amount(text: str) -> Tuple[Optional[float], int]:
        """
        Extract total amount from receipt text

        Returns:
            (amount, confidence_score)
        """
        text_upper = text.upper()
        found_amounts = []

        for pattern, label in AMOUNT_PATTERNS:
            matches = re.finditer(pattern, text_upper)
            for match in matches:
                try:
                    amount_str = match.group(1).replace(',', '.')
                    amount = float(amount_str)

                    # Confidence based on context
                    if label in ['TOTAL', 'BALANCE', 'AMOUNT DUE', 'TO PAY', 'GRAND TOTAL']:
                        confidence = 100
                    elif label == 'CURRENCY':
                        confidence = 70  # Generic £ amount
                    else:
                        confidence = 80

                    found_amounts.append((amount, confidence, label))
                    logger.debug(f"Found amount: £{amount} ({label}, confidence: {confidence})")
                except (ValueError, IndexError):
                    continue

        if not found_amounts:
            return None, 0

        # Sort by confidence, then by amount (largest)
        found_amounts.sort(key=lambda x: (x[1], x[0]), reverse=True)
        best_amount, best_confidence, best_label = found_amounts[0]

        logger.info(f"Selected amount: £{best_amount} ({best_label}, confidence: {best_confidence})")
        return best_amount, best_confidence

    @staticmethod
    def find_tax_amount(text: str) -> Optional[float]:
        """Extract VAT/tax amount"""
        text_upper = text.upper()

        for pattern in TAX_PATTERNS:
            match = re.search(pattern, text_upper)
            if match:
                try:
                    tax_str = match.group(1).replace(',', '.')
                    tax = float(tax_str)
                    logger.info(f"Found tax: £{tax}")
                    return tax
                except (ValueError, IndexError):
                    continue

        return None

    @staticmethod
    def extract_line_items(text: str) -> List[Dict[str, Any]]:
        """
        Extract individual line items from receipt

        Returns:
            List of {item: str, quantity: int, price: float}
        """
        # This is complex and receipt-specific
        # Basic implementation: look for lines with item name and price
        line_items = []
        lines = text.split('\n')

        # Pattern: item description followed by price
        item_pattern = r'(.+?)\s+£?(\d+[.,]\d{2})$'

        for line in lines:
            match = re.search(item_pattern, line.strip())
            if match:
                item_name = match.group(1).strip()
                price_str = match.group(2).replace(',', '.')
                try:
                    price = float(price_str)
                    # Filter out likely total lines
                    if not any(keyword in item_name.upper() for keyword in ['TOTAL', 'BALANCE', 'CHANGE', 'CASH', 'CARD']):
                        line_items.append({
                            'item': item_name,
                            'price': price,
                            'quantity': 1
                        })
                except ValueError:
                    continue

        logger.info(f"Extracted {len(line_items)} line items")
        return line_items


class ReceiptOCR:
    """Main OCR receipt processing class"""

    def __init__(self, ocr_engine: str = 'auto', preprocess: bool = True):
        """
        Initialize OCR processor

        Args:
            ocr_engine: 'tesseract', 'easyocr', 'google_vision', or 'auto'
            preprocess: Whether to preprocess images before OCR
        """
        self.ocr_engine = ocr_engine
        self.preprocess = preprocess
        self.preprocessor = ImagePreprocessor()
        self.parser = ReceiptParser()

        # Auto-select best available engine
        if ocr_engine == 'auto':
            if GOOGLE_VISION_AVAILABLE:
                self.ocr_engine = 'google_vision'
            elif EASYOCR_AVAILABLE:
                self.ocr_engine = 'easyocr'
            elif TESSERACT_AVAILABLE:
                self.ocr_engine = 'tesseract'
            else:
                raise RuntimeError("No OCR engine available. Install pytesseract, easyocr, or google-cloud-vision")

        logger.info(f"Initialized OCR with engine: {self.ocr_engine}")

    def extract_text(self, image_path: str) -> str:
        """Extract text from image using configured OCR engine"""
        # Preprocess if enabled
        if self.preprocess and PIL_AVAILABLE:
            try:
                # Save preprocessed image temporarily
                preprocessed_path = str(Path(image_path).parent / f"preprocessed_{Path(image_path).name}")
                self.preprocessor.preprocess_image(image_path, preprocessed_path)
                ocr_image_path = preprocessed_path
            except Exception as e:
                logger.warning(f"Preprocessing failed, using original: {e}")
                ocr_image_path = image_path
        else:
            ocr_image_path = image_path

        # Run OCR
        try:
            if self.ocr_engine == 'tesseract':
                text = OCREngine.extract_text_tesseract(ocr_image_path)
            elif self.ocr_engine == 'easyocr':
                text = OCREngine.extract_text_easyocr(ocr_image_path)
            elif self.ocr_engine == 'google_vision':
                text = OCREngine.extract_text_google_vision(ocr_image_path)
            else:
                raise ValueError(f"Unknown OCR engine: {self.ocr_engine}")

            # Clean up preprocessed image
            if self.preprocess and ocr_image_path != image_path:
                try:
                    os.remove(ocr_image_path)
                except:
                    pass

            return text
        except Exception as e:
            logger.error(f"OCR extraction failed: {e}")
            return ""

    def process_receipt(self, image_path: str) -> ReceiptData:
        """
        Full receipt processing pipeline

        Args:
            image_path: Path to receipt image

        Returns:
            ReceiptData with extracted fields and confidence scores
        """
        logger.info(f"Processing receipt: {image_path}")

        # Extract text
        raw_text = self.extract_text(image_path)

        if not raw_text:
            logger.warning("No text extracted from image")
            return ReceiptData(raw_text=raw_text)

        # Parse structured data
        merchant, merchant_conf = self.parser.find_merchant_name(raw_text)
        date_val, date_conf = self.parser.find_date(raw_text)
        amount, amount_conf = self.parser.find_amount(raw_text)
        tax_amount = self.parser.find_tax_amount(raw_text)
        line_items = self.parser.extract_line_items(raw_text)

        receipt_data = ReceiptData(
            merchant=merchant,
            date=date_val,
            amount=amount,
            raw_text=raw_text,
            confidence={
                'merchant': merchant_conf,
                'date': date_conf,
                'amount': amount_conf
            },
            line_items=line_items,
            tax_amount=tax_amount
        )

        logger.info(f"Extraction complete - Merchant: {merchant} ({merchant_conf}%), "
                   f"Date: {date_val} ({date_conf}%), Amount: £{amount} ({amount_conf}%)")

        return receipt_data

    def batch_process(
        self,
        image_paths: List[str],
        callback: Optional[Callable[[int, int, ReceiptData], None]] = None
    ) -> List[ReceiptData]:
        """
        Process multiple receipts in batch

        Args:
            image_paths: List of receipt image paths
            callback: Optional callback(current, total, receipt_data) called after each receipt

        Returns:
            List of ReceiptData objects
        """
        results = []
        total = len(image_paths)

        logger.info(f"Starting batch processing of {total} receipts")

        for i, path in enumerate(image_paths, 1):
            try:
                data = self.process_receipt(path)
                results.append(data)

                if callback:
                    callback(i, total, data)

                logger.info(f"Batch progress: {i}/{total}")
            except Exception as e:
                logger.error(f"Failed to process {path}: {e}")
                # Add failed result
                results.append(ReceiptData(raw_text=f"ERROR: {str(e)}"))

        logger.info(f"Batch processing complete: {len(results)} receipts processed")
        return results


class ManualCorrectionUI:
    """Manual correction interface for low-confidence extractions"""

    @staticmethod
    def needs_review(receipt_data: ReceiptData, min_confidence: int = 70) -> bool:
        """Check if receipt needs manual review"""
        return not receipt_data.is_complete(min_confidence)

    @staticmethod
    def format_review_prompt(receipt_data: ReceiptData) -> str:
        """Format extracted data for review"""
        lines = []
        lines.append("=" * 50)
        lines.append("OCR EXTRACTION REVIEW")
        lines.append("=" * 50)
        lines.append("")
        lines.append("Extracted Data:")
        lines.append(f"  Merchant: {receipt_data.merchant or '[NOT FOUND]'} "
                    f"(Confidence: {receipt_data.confidence.get('merchant', 0)}%)")
        lines.append(f"  Date:     {receipt_data.date or '[NOT FOUND]'} "
                    f"(Confidence: {receipt_data.confidence.get('date', 0)}%)")
        lines.append(f"  Amount:   £{receipt_data.amount or '[NOT FOUND]'} "
                    f"(Confidence: {receipt_data.confidence.get('amount', 0)}%)")

        if receipt_data.tax_amount:
            lines.append(f"  Tax:      £{receipt_data.tax_amount}")

        if receipt_data.line_items:
            lines.append(f"  Items:    {len(receipt_data.line_items)} line items")

        lines.append("")
        lines.append("Raw Text (first 500 chars):")
        lines.append("-" * 50)
        lines.append(receipt_data.raw_text[:500] + ("..." if len(receipt_data.raw_text) > 500 else ""))
        lines.append("-" * 50)

        return "\n".join(lines)

    @staticmethod
    def get_corrections(receipt_data: ReceiptData) -> ReceiptData:
        """
        Interactive correction prompt

        This is a simple CLI version. In a GUI app, this would show:
        - Receipt image preview
        - Editable fields with confidence indicators
        - Accept/Edit/Reject buttons
        """
        print(ManualCorrectionUI.format_review_prompt(receipt_data))
        print("\nOptions:")
        print("  1. Accept as-is")
        print("  2. Edit fields")
        print("  3. Reject receipt")

        choice = input("\nYour choice (1-3): ").strip()

        if choice == '2':
            # Edit fields
            corrected = receipt_data

            if input(f"Edit merchant? (current: {receipt_data.merchant}) [y/N]: ").lower() == 'y':
                new_merchant = input("Enter merchant name: ").strip()
                if new_merchant:
                    corrected.merchant = new_merchant
                    corrected.confidence['merchant'] = 100

            if input(f"Edit date? (current: {receipt_data.date}) [y/N]: ").lower() == 'y':
                date_str = input("Enter date (YYYY-MM-DD): ").strip()
                try:
                    corrected.date = datetime.strptime(date_str, '%Y-%m-%d').date()
                    corrected.confidence['date'] = 100
                except ValueError:
                    print("Invalid date format, keeping original")

            if input(f"Edit amount? (current: £{receipt_data.amount}) [y/N]: ").lower() == 'y':
                amount_str = input("Enter amount (e.g., 45.99): ").strip()
                try:
                    corrected.amount = float(amount_str)
                    corrected.confidence['amount'] = 100
                except ValueError:
                    print("Invalid amount format, keeping original")

            return corrected
        elif choice == '3':
            # Reject
            return ReceiptData(raw_text="REJECTED BY USER")
        else:
            # Accept
            return receipt_data


# Merchant database integration helper
def match_extracted_merchant(merchant_text: str, merchant_db: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Match OCR extracted merchant to database

    Args:
        merchant_text: Extracted merchant name
        merchant_db: Optional list of known merchants

    Returns:
        {
            'matched_merchant': str,
            'match_confidence': int,
            'suggested_category': str
        }
    """
    if not merchant_text:
        return {
            'matched_merchant': None,
            'match_confidence': 0,
            'suggested_category': None
        }

    merchant_upper = merchant_text.upper()

    # Use default UK merchants if no database provided
    if merchant_db is None:
        merchant_db = ALL_UK_MERCHANTS

    # Exact match
    for known_merchant in merchant_db:
        if known_merchant.upper() == merchant_upper:
            category = categorize_merchant(known_merchant)
            return {
                'matched_merchant': known_merchant,
                'match_confidence': 100,
                'suggested_category': category
            }

    # Partial match
    for known_merchant in merchant_db:
        if known_merchant.upper() in merchant_upper or merchant_upper in known_merchant.upper():
            category = categorize_merchant(known_merchant)
            return {
                'matched_merchant': known_merchant,
                'match_confidence': 85,
                'suggested_category': category
            }

    # No match - use extracted text
    category = categorize_merchant(merchant_text)
    return {
        'matched_merchant': merchant_text,
        'match_confidence': 50,
        'suggested_category': category
    }


def categorize_merchant(merchant: str) -> str:
    """Suggest category based on merchant"""
    merchant_upper = merchant.upper()

    if any(s in merchant_upper for s in UK_SUPERMARKETS):
        return "Groceries"
    elif any(r in merchant_upper for r in UK_RESTAURANTS):
        return "Dining"
    elif any(r in merchant_upper for r in UK_RETAILERS):
        return "Retail"
    else:
        return "General"


# Convenience functions
def quick_ocr(image_path: str, ocr_engine: str = 'auto') -> ReceiptData:
    """Quick single receipt OCR"""
    processor = ReceiptOCR(ocr_engine=ocr_engine)
    return processor.process_receipt(image_path)


def batch_ocr(image_paths: List[str], ocr_engine: str = 'auto') -> List[ReceiptData]:
    """Quick batch OCR"""
    processor = ReceiptOCR(ocr_engine=ocr_engine)
    return processor.batch_process(image_paths)


def render_ocr_review_ui(receipt_data: ReceiptData, image_path: str = None) -> Dict[str, Any]:
    """
    Render Streamlit UI for reviewing and correcting OCR results

    Args:
        receipt_data: OCR extraction results to review
        image_path: Optional path to receipt image for display

    Returns:
        Dictionary with corrected values: {'merchant': str, 'date': date, 'amount': float, 'accepted': bool}
    """
    import streamlit as st

    st.subheader("OCR Review & Correction")

    # Display image if provided
    if image_path:
        try:
            st.image(image_path, caption="Receipt Image", use_container_width=True)
        except Exception as e:
            st.warning(f"Could not display image: {e}")

    # Display confidence levels
    col1, col2, col3 = st.columns(3)
    with col1:
        merchant_conf = receipt_data.confidence.get('merchant', 0)
        conf_color = "🟢" if merchant_conf >= 80 else "🟡" if merchant_conf >= 50 else "🔴"
        st.metric("Merchant Confidence", f"{conf_color} {merchant_conf}%")
    with col2:
        date_conf = receipt_data.confidence.get('date', 0)
        conf_color = "🟢" if date_conf >= 80 else "🟡" if date_conf >= 50 else "🔴"
        st.metric("Date Confidence", f"{conf_color} {date_conf}%")
    with col3:
        amount_conf = receipt_data.confidence.get('amount', 0)
        conf_color = "🟢" if amount_conf >= 80 else "🟡" if amount_conf >= 50 else "🔴"
        st.metric("Amount Confidence", f"{conf_color} {amount_conf}%")

    # Editable fields
    st.markdown("---")
    st.markdown("**Review and correct extracted data:**")

    corrected_merchant = st.text_input(
        "Merchant Name",
        value=receipt_data.merchant or "",
        help="Extracted merchant name - edit if incorrect"
    )

    corrected_date = st.date_input(
        "Transaction Date",
        value=receipt_data.date if receipt_data.date else datetime.now().date(),
        help="Extracted date - edit if incorrect"
    )

    corrected_amount = st.number_input(
        "Amount (£)",
        value=float(receipt_data.amount) if receipt_data.amount else 0.0,
        min_value=0.0,
        step=0.01,
        format="%.2f",
        help="Extracted amount - edit if incorrect"
    )

    # Optional fields
    with st.expander("Additional Details (Optional)"):
        tax_amount = st.number_input(
            "Tax Amount (£)",
            value=float(receipt_data.tax_amount) if receipt_data.tax_amount else 0.0,
            min_value=0.0,
            step=0.01,
            format="%.2f"
        )

        payment_method = st.selectbox(
            "Payment Method",
            options=["", "Card", "Cash", "Bank Transfer", "Other"],
            index=0
        )

    # Show raw text for reference
    with st.expander("View Raw OCR Text"):
        st.text_area(
            "Raw Text",
            value=receipt_data.raw_text,
            height=200,
            disabled=True
        )

    # Action buttons
    col1, col2, col3 = st.columns(3)
    with col1:
        accept = st.button("✓ Accept", type="primary", use_container_width=True)
    with col2:
        reject = st.button("✗ Reject", use_container_width=True)
    with col3:
        skip = st.button("⏭ Skip", use_container_width=True)

    # Return results
    result = {
        'merchant': corrected_merchant,
        'date': corrected_date,
        'amount': corrected_amount,
        'tax_amount': tax_amount if 'tax_amount' in locals() else None,
        'payment_method': payment_method if 'payment_method' in locals() else None,
        'accepted': accept,
        'rejected': reject,
        'skipped': skip
    }

    return result


# Example usage
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python ocr_receipt.py <image_path> [ocr_engine]")
        print("OCR engines: tesseract, easyocr, google_vision, auto (default)")
        sys.exit(1)

    image_path = sys.argv[1]
    ocr_engine = sys.argv[2] if len(sys.argv) > 2 else 'auto'

    print(f"Processing receipt: {image_path}")
    print(f"OCR engine: {ocr_engine}")
    print()

    # Process receipt
    receipt_data = quick_ocr(image_path, ocr_engine)

    # Display results
    print(ManualCorrectionUI.format_review_prompt(receipt_data))

    # Check if review needed
    if ManualCorrectionUI.needs_review(receipt_data):
        print("\n⚠ Low confidence - manual review recommended")
    else:
        print("\n✓ High confidence extraction")

    # Match to merchant database
    match_result = match_extracted_merchant(receipt_data.merchant)
    print(f"\nMerchant Match: {match_result['matched_merchant']} "
          f"({match_result['match_confidence']}%)")
    print(f"Suggested Category: {match_result['suggested_category']}")
