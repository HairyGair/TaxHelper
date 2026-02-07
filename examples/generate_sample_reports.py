"""
Example: Generate Sample Compliance Reports
Demonstrates report generation with sample data
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import datetime, timedelta
from database import SessionLocal, init_db
from models import Transaction, AuditLog, Receipt, TransactionType
from components.compliance_reports import (
    generate_audit_trail_report,
    generate_receipt_summary,
    generate_categorization_report,
    generate_high_confidence_report,
    generate_requires_review_report,
    export_sa103s_format,
    generate_excel_workbook,
    get_tax_year_dates,
    render_report_generator_ui
)


def create_sample_data(session):
    """Create sample transactions for demonstration."""
    print("Creating sample data...")

    # Tax year dates
    tax_year_start = datetime(2024, 4, 6)

    # Sample income transactions
    income_data = [
        ("2024-05-15", "Client Payment", "Invoice #001", 2500.00),
        ("2024-06-01", "Client Payment", "Invoice #002", 1800.00),
        ("2024-07-10", "Client Payment", "Invoice #003", 3200.00),
        ("2024-08-05", "Client Payment", "Invoice #004", 2100.00),
        ("2024-09-15", "Client Payment", "Invoice #005", 2800.00),
    ]

    for date_str, merchant, desc, amount in income_data:
        trans = Transaction(
            date=datetime.strptime(date_str, "%Y-%m-%d"),
            merchant=merchant,
            description=desc,
            amount=amount,
            type=TransactionType.INCOME,
            category="Freelance Income",
            confidence_score=100,
            categorization_method="manual",
            reviewed=True
        )
        session.add(trans)

    # Sample expense transactions
    expense_data = [
        # Office costs
        ("2024-05-20", "STAPLES", "Office supplies", -125.99, "Office costs", 95, "merchant_match"),
        ("2024-06-15", "AMAZON", "Printer ink", -89.99, "Office costs", 88, "merchant_match"),
        ("2024-07-05", "OFFICEWORKS", "Desk chair", -249.00, "Office costs", 92, "merchant_match"),
        ("2024-08-10", "WHSmith", "Stationery", -45.50, "Office costs", 85, "rule_match"),

        # Travel
        ("2024-05-25", "BP", "Fuel - Client meeting", -65.00, "Travel", 78, "pattern_learning"),
        ("2024-06-12", "SHELL", "Fuel", -72.50, "Travel", 82, "merchant_match"),
        ("2024-07-18", "Trainline", "Train to London", -145.00, "Travel", 95, "merchant_match"),
        ("2024-08-22", "NCP Car Park", "Parking", -12.00, "Travel", 75, "rule_match"),

        # Phone & Internet
        ("2024-05-01", "EE", "Mobile phone", -45.00, "Phone", 98, "merchant_match"),
        ("2024-06-01", "EE", "Mobile phone", -45.00, "Phone", 98, "merchant_match"),
        ("2024-07-01", "EE", "Mobile phone", -45.00, "Phone", 98, "merchant_match"),
        ("2024-05-15", "BT", "Business broadband", -35.00, "Internet", 95, "merchant_match"),
        ("2024-06-15", "BT", "Business broadband", -35.00, "Internet", 95, "merchant_match"),

        # Marketing
        ("2024-06-10", "Google Ads", "Online advertising", -250.00, "Marketing", 100, "merchant_match"),
        ("2024-07-15", "Facebook Ads", "Social media ads", -150.00, "Marketing", 100, "merchant_match"),
        ("2024-08-20", "Vistaprint", "Business cards", -85.00, "Marketing", 88, "merchant_match"),

        # Professional fees
        ("2024-05-30", "Accountant Ltd", "Quarterly bookkeeping", -200.00, "Accountancy", 100, "manual"),
        ("2024-08-31", "Accountant Ltd", "Quarterly bookkeeping", -200.00, "Accountancy", 100, "manual"),

        # Low confidence / requires review
        ("2024-06-22", "Unknown Merchant", "Payment", -125.00, None, 15, None),
        ("2024-07-28", "MISC PURCHASE", "Item", -89.50, None, 25, None),
        ("2024-08-15", "Cash Withdrawal", "ATM", -100.00, None, 10, None),
    ]

    receipt_transactions = []

    for date_str, merchant, desc, amount, category, confidence, method in expense_data:
        trans = Transaction(
            date=datetime.strptime(date_str, "%Y-%m-%d"),
            merchant=merchant,
            description=desc,
            amount=amount,
            type=TransactionType.EXPENSE,
            category=category,
            confidence_score=confidence,
            categorization_method=method,
            reviewed=(confidence and confidence >= 70)
        )
        session.add(trans)

        # Add receipts for some expenses
        if category in ["Office costs", "Travel", "Marketing"]:
            receipt_transactions.append(trans)

    session.flush()

    # Create sample receipts
    receipts_dir = Path("/Users/anthony/Tax Helper/receipts")
    receipts_dir.mkdir(exist_ok=True)

    for trans in receipt_transactions[:10]:  # Add receipts to first 10 eligible
        receipt = Receipt(
            transaction_id=trans.id,
            file_path=str(receipts_dir / f"{trans.date.strftime('%Y%m%d')}_{trans.merchant.replace(' ', '_')}_{abs(trans.amount):.2f}.jpg"),
            upload_date=trans.date
        )
        session.add(receipt)

    # Create sample audit logs
    print("Creating audit log entries...")

    audit_entries = [
        ("2024-05-20", 1, "UPDATE", '{"category": null}', '{"category": "Office costs"}', "Categorized as Expense: Office costs"),
        ("2024-05-25", 5, "UPDATE", '{"reviewed": false}', '{"reviewed": true}', "Marked as reviewed"),
        ("2024-06-15", 8, "UPDATE", '{"category": null, "type": null}', '{"category": "Travel", "type": "Expense"}', "Auto-categorized by merchant match"),
        ("2024-06-22", 18, "CREATE", None, '{"merchant": "Unknown Merchant", "amount": -125.00}', "Transaction created from bank import"),
        ("2024-07-10", 3, "UPDATE", '{"description": "Payment"}', '{"description": "Invoice #003"}', "Updated description"),
    ]

    for date_str, trans_id, action, before, after, summary in audit_entries:
        log = AuditLog(
            transaction_id=trans_id,
            timestamp=datetime.strptime(date_str, "%Y-%m-%d"),
            action=action,
            before_value=before,
            after_value=after,
            change_summary=summary
        )
        session.add(log)

    session.commit()
    print(f"Created {len(income_data)} income transactions")
    print(f"Created {len(expense_data)} expense transactions")
    print(f"Created 10 sample receipts")
    print(f"Created {len(audit_entries)} audit log entries\n")


def generate_all_sample_reports(session):
    """Generate all report types with sample data."""
    print("\n" + "="*70)
    print("GENERATING SAMPLE COMPLIANCE REPORTS".center(70))
    print("="*70 + "\n")

    # Tax year 2024/25
    tax_year_start, tax_year_end = get_tax_year_dates("2024/25")

    reports_generated = []

    # 1. Audit Trail Report (PDF)
    print("1. Generating Audit Trail Report (PDF)...")
    try:
        filepath = generate_audit_trail_report(session, tax_year_start, tax_year_end, 'PDF')
        reports_generated.append(("Audit Trail (PDF)", filepath))
        print(f"   ✓ Generated: {filepath}\n")
    except Exception as e:
        print(f"   ✗ Error: {e}\n")

    # 2. Receipt Summary Report (PDF)
    print("2. Generating Receipt Summary Report (PDF)...")
    try:
        filepath = generate_receipt_summary(session, tax_year_start, tax_year_end, 'PDF')
        reports_generated.append(("Receipt Summary (PDF)", filepath))
        print(f"   ✓ Generated: {filepath}\n")
    except Exception as e:
        print(f"   ✗ Error: {e}\n")

    # 3. Categorization Report (PDF)
    print("3. Generating Categorization Report (PDF)...")
    try:
        filepath = generate_categorization_report(session, tax_year_start, tax_year_end)
        reports_generated.append(("Categorization Report (PDF)", filepath))
        print(f"   ✓ Generated: {filepath}\n")
    except Exception as e:
        print(f"   ✗ Error: {e}\n")

    # 4. High Confidence Transactions (CSV)
    print("4. Generating High Confidence Transactions (CSV)...")
    try:
        filepath = generate_high_confidence_report(session, tax_year_start, tax_year_end, 70)
        reports_generated.append(("High Confidence (CSV)", filepath))
        print(f"   ✓ Generated: {filepath}\n")
    except Exception as e:
        print(f"   ✗ Error: {e}\n")

    # 5. Requires Review Report (CSV)
    print("5. Generating Requires Review Report (CSV)...")
    try:
        filepath = generate_requires_review_report(session, tax_year_start, tax_year_end, 40)
        reports_generated.append(("Requires Review (CSV)", filepath))
        print(f"   ✓ Generated: {filepath}\n")
    except Exception as e:
        print(f"   ✗ Error: {e}\n")

    # 6. SA103S Export (CSV)
    print("6. Generating SA103S Export (CSV)...")
    try:
        filepath = export_sa103s_format(session, tax_year_start, tax_year_end)
        reports_generated.append(("SA103S Export (CSV)", filepath))
        print(f"   ✓ Generated: {filepath}\n")
    except Exception as e:
        print(f"   ✗ Error: {e}\n")

    # 7. Complete Excel Workbook
    print("7. Generating Complete Excel Workbook...")
    try:
        filepath = generate_excel_workbook(session, tax_year_start, tax_year_end)
        reports_generated.append(("Complete Workbook (Excel)", filepath))
        print(f"   ✓ Generated: {filepath}\n")
    except Exception as e:
        print(f"   ✗ Error: {e}\n")

    # Summary
    print("\n" + "="*70)
    print("GENERATION COMPLETE".center(70))
    print("="*70 + "\n")

    print(f"Successfully generated {len(reports_generated)} reports:\n")
    for report_type, filepath in reports_generated:
        size_mb = Path(filepath).stat().st_size / (1024 * 1024)
        print(f"  • {report_type}")
        print(f"    {filepath}")
        print(f"    Size: {size_mb:.2f} MB\n")


def main():
    """Main entry point."""
    print("\n" + "="*70)
    print("COMPLIANCE REPORTS - SAMPLE DATA GENERATOR".center(70))
    print("="*70 + "\n")

    # Initialize database
    init_db()
    session = SessionLocal()

    try:
        # Check if we should create sample data
        transaction_count = session.query(Transaction).count()

        if transaction_count == 0:
            print("No transactions found. Creating sample data...\n")
            create_sample_data(session)
        else:
            print(f"Found {transaction_count} existing transactions.")
            create_new = input("Create additional sample data? (y/n): ").strip().lower()
            if create_new == 'y':
                create_sample_data(session)

        # Generate reports
        print("\nReady to generate reports.")
        choice = input("Generate all sample reports? (y/n): ").strip().lower()

        if choice == 'y':
            generate_all_sample_reports(session)
        else:
            print("\nLaunching interactive report generator...\n")
            render_report_generator_ui(session)

    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()


if __name__ == "__main__":
    main()
