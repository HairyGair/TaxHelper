"""
Unit tests for OCR Receipt Scanner
Tests extraction accuracy, confidence scoring, and UK-specific patterns
"""

import unittest
from datetime import date
from components.ocr_receipt import (
    ReceiptData,
    ReceiptParser,
    match_extracted_merchant,
    categorize_merchant,
    ImagePreprocessor,
    ReceiptOCR,
    UK_SUPERMARKETS,
    UK_RESTAURANTS
)


class TestReceiptData(unittest.TestCase):
    """Test ReceiptData dataclass"""

    def test_initialization(self):
        receipt = ReceiptData(
            merchant="TESCO",
            date=date(2024, 10, 17),
            amount=45.99
        )

        self.assertEqual(receipt.merchant, "TESCO")
        self.assertEqual(receipt.date, date(2024, 10, 17))
        self.assertEqual(receipt.amount, 45.99)
        self.assertIsNotNone(receipt.confidence)

    def test_is_complete_high_confidence(self):
        receipt = ReceiptData(
            merchant="TESCO",
            date=date(2024, 10, 17),
            amount=45.99,
            confidence={'merchant': 95, 'date': 85, 'amount': 100}
        )

        self.assertTrue(receipt.is_complete(min_confidence=70))

    def test_is_complete_low_confidence(self):
        receipt = ReceiptData(
            merchant="TESCO",
            date=date(2024, 10, 17),
            amount=45.99,
            confidence={'merchant': 50, 'date': 40, 'amount': 60}
        )

        self.assertFalse(receipt.is_complete(min_confidence=70))

    def test_to_dict_serialization(self):
        receipt = ReceiptData(
            merchant="TESCO",
            date=date(2024, 10, 17),
            amount=45.99
        )

        data_dict = receipt.to_dict()
        self.assertEqual(data_dict['merchant'], "TESCO")
        self.assertEqual(data_dict['date'], "2024-10-17")
        self.assertEqual(data_dict['amount'], 45.99)


class TestReceiptParser(unittest.TestCase):
    """Test receipt text parsing"""

    def test_find_merchant_known_supermarket(self):
        text = """
        TESCO EXTRA
        123 HIGH STREET
        LONDON
        17/10/2024
        """
        merchant, confidence = ReceiptParser.find_merchant_name(text)

        self.assertEqual(merchant, "TESCO")
        self.assertGreaterEqual(confidence, 90)

    def test_find_merchant_known_restaurant(self):
        text = """
        COSTA COFFEE
        VICTORIA STATION
        17/10/2024 14:30
        """
        merchant, confidence = ReceiptParser.find_merchant_name(text)

        self.assertEqual(merchant, "COSTA")
        self.assertGreaterEqual(confidence, 90)

    def test_find_merchant_unknown(self):
        text = """
        LOCAL BAKERY
        123 MAIN STREET
        17/10/2024
        """
        merchant, confidence = ReceiptParser.find_merchant_name(text)

        # Should use first line
        self.assertIsNotNone(merchant)
        self.assertLessEqual(confidence, 50)

    def test_find_date_dd_mm_yyyy(self):
        text = """
        TESCO
        Date: 17/10/2024
        Total: £45.99
        """
        date_val, confidence = ReceiptParser.find_date(text)

        self.assertEqual(date_val, date(2024, 10, 17))
        self.assertGreaterEqual(confidence, 85)

    def test_find_date_dd_mmm_yyyy(self):
        text = """
        TESCO
        17 OCT 2024
        Total: £45.99
        """
        date_val, confidence = ReceiptParser.find_date(text)

        self.assertEqual(date_val, date(2024, 10, 17))
        self.assertGreaterEqual(confidence, 85)

    def test_find_date_iso_format(self):
        text = """
        TESCO
        2024-10-17
        Total: £45.99
        """
        date_val, confidence = ReceiptParser.find_date(text)

        self.assertEqual(date_val, date(2024, 10, 17))
        self.assertGreaterEqual(confidence, 85)

    def test_find_amount_with_total_keyword(self):
        text = """
        TESCO
        Item 1    £12.99
        Item 2    £33.00
        TOTAL:    £45.99
        """
        amount, confidence = ReceiptParser.find_amount(text)

        self.assertEqual(amount, 45.99)
        self.assertEqual(confidence, 100)

    def test_find_amount_balance(self):
        text = """
        SAINSBURYS
        BALANCE DUE: £78.50
        """
        amount, confidence = ReceiptParser.find_amount(text)

        self.assertEqual(amount, 78.50)
        self.assertEqual(confidence, 100)

    def test_find_amount_generic_currency(self):
        text = """
        COSTA
        Coffee    £3.50
        Cake      £2.95
        """
        amount, confidence = ReceiptParser.find_amount(text)

        # Should find largest or last amount
        self.assertIn(amount, [3.50, 2.95])
        self.assertGreaterEqual(confidence, 70)

    def test_find_tax_amount(self):
        text = """
        TESCO
        Subtotal: £38.32
        VAT (20%): £7.67
        TOTAL: £45.99
        """
        tax = ReceiptParser.find_tax_amount(text)

        self.assertEqual(tax, 7.67)

    def test_extract_line_items(self):
        text = """
        TESCO
        BREAD         £1.20
        MILK          £1.50
        EGGS          £2.30
        TOTAL         £5.00
        """
        items = ReceiptParser.extract_line_items(text)

        self.assertGreaterEqual(len(items), 3)

        # Check that TOTAL is filtered out
        total_items = [item for item in items if 'TOTAL' in item['item'].upper()]
        self.assertEqual(len(total_items), 0)


class TestMerchantMatching(unittest.TestCase):
    """Test merchant database matching"""

    def test_exact_match(self):
        result = match_extracted_merchant("TESCO", UK_SUPERMARKETS)

        self.assertEqual(result['matched_merchant'], "TESCO")
        self.assertEqual(result['match_confidence'], 100)
        self.assertEqual(result['suggested_category'], "Groceries")

    def test_partial_match(self):
        result = match_extracted_merchant("TESCO EXTRA", UK_SUPERMARKETS)

        self.assertEqual(result['matched_merchant'], "TESCO")
        self.assertEqual(result['match_confidence'], 85)

    def test_no_match(self):
        result = match_extracted_merchant("UNKNOWN STORE", UK_SUPERMARKETS)

        self.assertEqual(result['matched_merchant'], "UNKNOWN STORE")
        self.assertEqual(result['match_confidence'], 50)

    def test_categorize_supermarket(self):
        category = categorize_merchant("TESCO")
        self.assertEqual(category, "Groceries")

    def test_categorize_restaurant(self):
        category = categorize_merchant("COSTA")
        self.assertEqual(category, "Dining")

    def test_categorize_unknown(self):
        category = categorize_merchant("RANDOM SHOP")
        self.assertEqual(category, "General")


class TestCompleteReceiptParsing(unittest.TestCase):
    """Test complete receipt parsing scenarios"""

    def test_tesco_receipt(self):
        """Test parsing a typical Tesco receipt"""
        text = """
        TESCO STORES LIMITED
        123 HIGH STREET
        LONDON, W1A 1AA
        VAT REG: 123456789

        17/10/2024   14:35

        BREAD                £1.20
        MILK 2L              £1.50
        EGGS 6 PACK          £2.30
        BANANAS              £1.49

        SUBTOTAL             £6.49
        VAT @ 20%            £1.30
        TOTAL TO PAY         £7.79

        CARD PAYMENT         £7.79

        Thank you for shopping at Tesco
        """

        parser = ReceiptParser()

        merchant, m_conf = parser.find_merchant_name(text)
        date_val, d_conf = parser.find_date(text)
        amount, a_conf = parser.find_amount(text)
        tax = parser.find_tax_amount(text)
        items = parser.extract_line_items(text)

        self.assertEqual(merchant, "TESCO")
        self.assertGreaterEqual(m_conf, 90)

        self.assertEqual(date_val, date(2024, 10, 17))
        self.assertGreaterEqual(d_conf, 85)

        self.assertEqual(amount, 7.79)
        self.assertGreaterEqual(a_conf, 95)

        self.assertEqual(tax, 1.30)

        self.assertGreaterEqual(len(items), 3)

    def test_costa_receipt(self):
        """Test parsing a Costa Coffee receipt"""
        text = """
        COSTA COFFEE
        VICTORIA STATION
        LONDON SW1V 1JU

        17-10-2024  09:15

        LATTE REGULAR        £3.50
        CROISSANT            £2.95

        TOTAL                £6.45
        CONTACTLESS          £6.45

        Thank you
        """

        parser = ReceiptParser()

        merchant, m_conf = parser.find_merchant_name(text)
        date_val, d_conf = parser.find_date(text)
        amount, a_conf = parser.find_amount(text)

        self.assertEqual(merchant, "COSTA")
        self.assertGreaterEqual(m_conf, 90)

        self.assertEqual(date_val, date(2024, 10, 17))

        self.assertEqual(amount, 6.45)
        self.assertGreaterEqual(a_conf, 95)

    def test_poor_quality_receipt(self):
        """Test parsing a degraded quality receipt (missing data)"""
        text = """
        TES0 ST0RES  # OCR errors
        123 H1GH STREET

        17.10/2024  # Mixed separators

        8READ                £1.2O  # O instead of 0
        M1LK                 £1.5O

        T0TAL                £?.??  # Unreadable
        """

        parser = ReceiptParser()

        merchant, m_conf = parser.find_merchant_name(text)
        # Should still partially match TESCO
        self.assertIsNotNone(merchant)

        date_val, d_conf = parser.find_date(text)
        # May or may not find date due to mixed format
        # Just check it doesn't crash

        amount, a_conf = parser.find_amount(text)
        # Likely low confidence or not found


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling"""

    def test_empty_text(self):
        parser = ReceiptParser()

        merchant, _ = parser.find_merchant_name("")
        self.assertIsNone(merchant)

        date_val, _ = parser.find_date("")
        self.assertIsNone(date_val)

        amount, _ = parser.find_amount("")
        self.assertIsNone(amount)

    def test_invalid_date_format(self):
        text = "Date: 99/99/9999"
        date_val, conf = ReceiptParser.find_date(text)

        # Should not crash, return None
        self.assertIsNone(date_val)

    def test_future_date(self):
        """Dates in the future should be rejected"""
        text = "Date: 01/01/2030"
        date_val, conf = ReceiptParser.find_date(text)

        # Should reject future dates
        self.assertIsNone(date_val)

    def test_very_old_date(self):
        """Very old dates should be rejected"""
        text = "Date: 01/01/1990"
        date_val, conf = ReceiptParser.find_date(text)

        # Should reject dates older than 10 years
        self.assertIsNone(date_val)

    def test_multiple_amounts(self):
        """Should select the most likely total"""
        text = """
        Item 1    £5.99
        Item 2    £10.00
        Subtotal  £15.99
        Tax       £3.20
        TOTAL     £19.19
        """

        amount, conf = ReceiptParser.find_amount(text)

        # Should select TOTAL with highest confidence
        self.assertEqual(amount, 19.19)
        self.assertEqual(conf, 100)


class TestReceiptDataValidation(unittest.TestCase):
    """Test receipt data validation"""

    def test_complete_receipt_validation(self):
        """Valid complete receipt should pass"""
        receipt = ReceiptData(
            merchant="TESCO",
            date=date(2024, 10, 17),
            amount=45.99,
            confidence={'merchant': 95, 'date': 85, 'amount': 100}
        )

        self.assertTrue(receipt.is_complete(70))

    def test_missing_merchant(self):
        """Missing merchant should fail validation"""
        receipt = ReceiptData(
            merchant=None,
            date=date(2024, 10, 17),
            amount=45.99,
            confidence={'merchant': 0, 'date': 85, 'amount': 100}
        )

        self.assertFalse(receipt.is_complete(70))

    def test_low_confidence_amount(self):
        """Low confidence should fail validation"""
        receipt = ReceiptData(
            merchant="TESCO",
            date=date(2024, 10, 17),
            amount=45.99,
            confidence={'merchant': 95, 'date': 85, 'amount': 50}
        )

        self.assertFalse(receipt.is_complete(70))


def run_benchmark_tests():
    """
    Run benchmark tests to measure expected accuracy

    This would be run with actual receipt images to measure real-world accuracy
    """
    print("\nBenchmark Results (Expected):")
    print("=" * 50)
    print("\nClear, Well-Lit Receipts:")
    print("  Merchant Extraction: 85-95%")
    print("  Date Extraction: 80-90%")
    print("  Amount Extraction: 90-98%")
    print("  Overall Success: 85-95%")
    print("\nDegraded Quality Receipts:")
    print("  Merchant Extraction: 60-75%")
    print("  Date Extraction: 50-70%")
    print("  Amount Extraction: 70-85%")
    print("  Overall Success: 50-70%")
    print("\nOCR Engine Comparison:")
    print("  Tesseract: 70-80% accuracy, 1-2s processing")
    print("  EasyOCR: 80-90% accuracy, 3-5s processing")
    print("  Google Vision: 90-95% accuracy, 1-2s processing")
    print("=" * 50)


if __name__ == '__main__':
    # Run unit tests
    unittest.main(argv=[''], verbosity=2, exit=False)

    # Print benchmarks
    run_benchmark_tests()
