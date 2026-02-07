"""
Reports UI Component
User interface for compliance report generation
"""

import os
from pathlib import Path
from datetime import datetime
from typing import Optional

from components.compliance_reports import (
    generate_audit_trail_report,
    generate_receipt_summary,
    generate_categorization_report,
    generate_high_confidence_report,
    generate_requires_review_report,
    export_sa103s_format,
    generate_excel_workbook,
    get_tax_year_dates,
    get_current_tax_year,
    list_archived_reports,
    REPORTS_DIR
)


def clear_screen():
    """Clear terminal screen."""
    os.system('clear' if os.name != 'nt' else 'cls')


def print_header(title: str):
    """Print formatted header."""
    print("\n" + "="*70)
    print(title.center(70))
    print("="*70 + "\n")


def print_section(title: str):
    """Print section header."""
    print("\n" + "-"*70)
    print(title)
    print("-"*70)


def format_file_size(bytes_size: float) -> str:
    """Format file size in human-readable format."""
    if bytes_size < 1024:
        return f"{bytes_size:.0f} B"
    elif bytes_size < 1024 * 1024:
        return f"{bytes_size / 1024:.1f} KB"
    else:
        return f"{bytes_size / (1024 * 1024):.2f} MB"


def get_tax_year_input() -> tuple[datetime, datetime, str]:
    """
    Get tax year from user input.

    Returns:
        (start_date, end_date, tax_year_string)
    """
    current_tax_year = get_current_tax_year()

    print(f"\nCurrent Tax Year: {current_tax_year}")
    print("Enter tax year (YYYY/YY format) or press Enter for current year")

    while True:
        tax_year = input(f"Tax Year [{current_tax_year}]: ").strip() or current_tax_year

        try:
            start_date, end_date = get_tax_year_dates(tax_year)
            print(f"\nSelected: {tax_year}")
            print(f"Period: {start_date.strftime('%d %B %Y')} to {end_date.strftime('%d %B %Y')}")

            confirm = input("\nContinue with this tax year? (y/n): ").strip().lower()
            if confirm == 'y':
                return start_date, end_date, tax_year

        except Exception as e:
            print(f"\nError: Invalid tax year format. Use YYYY/YY (e.g., 2024/25)")
            print("Please try again.\n")


def show_report_success(filepath: str, report_name: str):
    """Display success message after report generation."""
    file_size = os.path.getsize(filepath)

    print("\n" + "="*70)
    print("REPORT GENERATED SUCCESSFULLY".center(70))
    print("="*70)

    print(f"\nReport Type: {report_name}")
    print(f"File: {Path(filepath).name}")
    print(f"Size: {format_file_size(file_size)}")
    print(f"Location: {filepath}")

    print("\n" + "-"*70)
    input("\nPress Enter to continue...")


def show_generation_error(error: Exception, report_name: str):
    """Display error message if report generation fails."""
    print("\n" + "="*70)
    print("ERROR GENERATING REPORT".center(70))
    print("="*70)

    print(f"\nReport Type: {report_name}")
    print(f"Error: {str(error)}")

    print("\n" + "-"*70)
    input("\nPress Enter to continue...")


def reports_main_menu(session):
    """
    Main reports menu with all report options.

    Args:
        session: Database session
    """
    while True:
        clear_screen()
        print_header("COMPLIANCE REPORTS GENERATOR")

        print("Generate Reports:")
        print("  1. Audit Trail Report (PDF)")
        print("  2. Receipt Summary (PDF)")
        print("  3. Categorization Report (PDF)")
        print("  4. High Confidence Transactions (CSV)")
        print("  5. Requires Review Report (CSV)")
        print("  6. SA103S Export for HMRC (CSV)")
        print("  7. Complete Excel Workbook")
        print()
        print("Other Options:")
        print("  8. Generate All Reports")
        print("  9. View Generated Reports")
        print("  0. Back to Main Menu")

        choice = input("\nEnter choice (0-9): ").strip()

        if choice == '0':
            break

        elif choice == '1':
            generate_audit_trail_ui(session)

        elif choice == '2':
            generate_receipt_summary_ui(session)

        elif choice == '3':
            generate_categorization_ui(session)

        elif choice == '4':
            generate_high_confidence_ui(session)

        elif choice == '5':
            generate_requires_review_ui(session)

        elif choice == '6':
            generate_sa103s_ui(session)

        elif choice == '7':
            generate_workbook_ui(session)

        elif choice == '8':
            generate_all_reports_ui(session)

        elif choice == '9':
            view_archived_reports_ui()

        else:
            print("\nInvalid choice. Please try again.")
            input("\nPress Enter to continue...")


def generate_audit_trail_ui(session):
    """UI for generating audit trail report."""
    clear_screen()
    print_header("AUDIT TRAIL REPORT")

    print("Complete change history for HMRC compliance.")
    print("\nIncludes:")
    print("  - Summary of all transactions and changes")
    print("  - Detailed chronological log")
    print("  - Before/after values for all changes")
    print("  - Methodology documentation")

    start_date, end_date, tax_year = get_tax_year_input()

    print("\nSelect format:")
    print("  1. PDF (recommended for HMRC)")
    print("  2. CSV (for spreadsheet analysis)")
    print("  3. Excel (formatted workbook)")

    format_choice = input("\nChoice (1-3): ").strip()

    format_map = {'1': 'PDF', '2': 'CSV', '3': 'Excel'}
    format_type = format_map.get(format_choice, 'PDF')

    print(f"\nGenerating {format_type} audit trail report...")

    try:
        filepath = generate_audit_trail_report(session, start_date, end_date, format_type)
        show_report_success(filepath, f"Audit Trail Report ({format_type})")
    except Exception as e:
        show_generation_error(e, "Audit Trail Report")


def generate_receipt_summary_ui(session):
    """UI for generating receipt summary report."""
    clear_screen()
    print_header("RECEIPT SUMMARY REPORT")

    print("All receipts organized by category.")
    print("\nIncludes:")
    print("  - Receipts grouped by expense category")
    print("  - Category totals and counts")
    print("  - Receipt file references")
    print("  - Summary statistics")

    start_date, end_date, tax_year = get_tax_year_input()

    print("\nSelect format:")
    print("  1. PDF (recommended)")
    print("  2. CSV")
    print("  3. Excel")

    format_choice = input("\nChoice (1-3): ").strip()

    format_map = {'1': 'PDF', '2': 'CSV', '3': 'Excel'}
    format_type = format_map.get(format_choice, 'PDF')

    print(f"\nGenerating {format_type} receipt summary...")

    try:
        filepath = generate_receipt_summary(session, start_date, end_date, format_type)
        show_report_success(filepath, f"Receipt Summary ({format_type})")
    except Exception as e:
        show_generation_error(e, "Receipt Summary")


def generate_categorization_ui(session):
    """UI for generating categorization report."""
    clear_screen()
    print_header("CATEGORIZATION REPORT")

    print("Classification methodology and confidence analysis.")
    print("\nIncludes:")
    print("  - Auto vs. manual categorization breakdown")
    print("  - Confidence score distribution")
    print("  - Top merchants analysis")
    print("  - Category statistics")

    start_date, end_date, tax_year = get_tax_year_input()

    print("\nGenerating categorization report (PDF)...")

    try:
        filepath = generate_categorization_report(session, start_date, end_date)
        show_report_success(filepath, "Categorization Report (PDF)")
    except Exception as e:
        show_generation_error(e, "Categorization Report")


def generate_high_confidence_ui(session):
    """UI for generating high confidence transactions report."""
    clear_screen()
    print_header("HIGH CONFIDENCE TRANSACTIONS")

    print("Transactions with high confidence scores.")
    print("\nThese transactions:")
    print("  - Have confidence >= 70% (customizable)")
    print("  - Are ready for HMRC submission")
    print("  - Require minimal manual review")

    start_date, end_date, tax_year = get_tax_year_input()

    print("\nMinimum confidence threshold:")
    print("  1. 70% (Standard)")
    print("  2. 80% (High)")
    print("  3. 90% (Very High)")
    print("  4. Custom")

    threshold_choice = input("\nChoice (1-4): ").strip()

    threshold_map = {'1': 70, '2': 80, '3': 90}
    threshold = threshold_map.get(threshold_choice)

    if threshold is None:
        try:
            threshold = int(input("Enter custom threshold (0-100): ").strip())
            if not 0 <= threshold <= 100:
                threshold = 70
        except ValueError:
            threshold = 70

    print(f"\nGenerating report with threshold >= {threshold}%...")

    try:
        filepath = generate_high_confidence_report(session, start_date, end_date, threshold)
        show_report_success(filepath, f"High Confidence Transactions (>={threshold}%)")
    except Exception as e:
        show_generation_error(e, "High Confidence Transactions")


def generate_requires_review_ui(session):
    """UI for generating requires review report."""
    clear_screen()
    print_header("REQUIRES REVIEW REPORT")

    print("Transactions that need manual verification.")
    print("\nFlags transactions with:")
    print("  - Low confidence scores")
    print("  - Missing categories")
    print("  - Missing required fields")
    print("  - Uncategorized items")

    start_date, end_date, tax_year = get_tax_year_input()

    print("\nMaximum confidence threshold:")
    print("  1. 40% (Standard)")
    print("  2. 50% (Include medium confidence)")
    print("  3. 30% (Only very low)")
    print("  4. Custom")

    threshold_choice = input("\nChoice (1-4): ").strip()

    threshold_map = {'1': 40, '2': 50, '3': 30}
    threshold = threshold_map.get(threshold_choice)

    if threshold is None:
        try:
            threshold = int(input("Enter custom threshold (0-100): ").strip())
            if not 0 <= threshold <= 100:
                threshold = 40
        except ValueError:
            threshold = 40

    print(f"\nGenerating report for transactions with confidence < {threshold}%...")

    try:
        filepath = generate_requires_review_report(session, start_date, end_date, threshold)
        show_report_success(filepath, f"Requires Review (<{threshold}%)")
    except Exception as e:
        show_generation_error(e, "Requires Review Report")


def generate_sa103s_ui(session):
    """UI for generating SA103S export."""
    clear_screen()
    print_header("SA103S EXPORT FOR HMRC")

    print("HMRC Self-Assessment SA103S format export.")
    print("\nThis export:")
    print("  - Maps expenses to SA103S box numbers (17-29)")
    print("  - Calculates totals for each category")
    print("  - Ready for copy/paste to HMRC online form")
    print("  - CSV format for easy import")

    start_date, end_date, tax_year = get_tax_year_input()

    print("\nGenerating SA103S export (CSV)...")

    try:
        filepath = export_sa103s_format(session, start_date, end_date)
        show_report_success(filepath, "SA103S Export (CSV)")

        print("\nNext steps:")
        print("  1. Open the CSV file in a spreadsheet")
        print("  2. Copy the amounts for each box number")
        print("  3. Paste into your HMRC Self-Assessment form")
        print("  4. Or import into your tax software")

        input("\nPress Enter to continue...")

    except Exception as e:
        show_generation_error(e, "SA103S Export")


def generate_workbook_ui(session):
    """UI for generating complete Excel workbook."""
    clear_screen()
    print_header("COMPLETE EXCEL WORKBOOK")

    print("Comprehensive multi-sheet Excel workbook.")
    print("\nIncludes 6 sheets:")
    print("  1. Summary (totals and statistics)")
    print("  2. Income (all income transactions)")
    print("  3. Expenses by Category (grouped analysis)")
    print("  4. All Transactions (complete list)")
    print("  5. Audit Trail (change history)")
    print("  6. Receipts (receipt references)")

    start_date, end_date, tax_year = get_tax_year_input()

    print("\nGenerating complete Excel workbook...")

    try:
        filepath = generate_excel_workbook(session, start_date, end_date)
        show_report_success(filepath, "Complete Excel Workbook")

        print("\nThis workbook contains all your tax data in one file.")
        print("Perfect for:")
        print("  - Sending to your accountant")
        print("  - Annual tax record archiving")
        print("  - Detailed data analysis")

        input("\nPress Enter to continue...")

    except Exception as e:
        show_generation_error(e, "Complete Excel Workbook")


def generate_all_reports_ui(session):
    """UI for generating all reports at once."""
    clear_screen()
    print_header("GENERATE ALL REPORTS")

    print("Generate all 7 report types at once.")
    print("\nThis will create:")
    print("  1. Audit Trail Report (PDF)")
    print("  2. Receipt Summary (PDF)")
    print("  3. Categorization Report (PDF)")
    print("  4. High Confidence Transactions (CSV)")
    print("  5. Requires Review Report (CSV)")
    print("  6. SA103S Export (CSV)")
    print("  7. Complete Excel Workbook")

    start_date, end_date, tax_year = get_tax_year_input()

    print("\n" + "="*70)
    print("WARNING: This will generate 7 reports.")
    print("This may take a few moments for large datasets.")
    print("="*70)

    confirm = input("\nContinue? (y/n): ").strip().lower()

    if confirm != 'y':
        return

    reports_generated = []
    reports_failed = []

    # 1. Audit Trail
    print("\n[1/7] Generating Audit Trail Report...")
    try:
        filepath = generate_audit_trail_report(session, start_date, end_date, 'PDF')
        reports_generated.append(("Audit Trail (PDF)", filepath))
        print("      Done")
    except Exception as e:
        reports_failed.append(("Audit Trail", str(e)))
        print(f"      Error: {e}")

    # 2. Receipt Summary
    print("[2/7] Generating Receipt Summary...")
    try:
        filepath = generate_receipt_summary(session, start_date, end_date, 'PDF')
        reports_generated.append(("Receipt Summary (PDF)", filepath))
        print("      Done")
    except Exception as e:
        reports_failed.append(("Receipt Summary", str(e)))
        print(f"      Error: {e}")

    # 3. Categorization
    print("[3/7] Generating Categorization Report...")
    try:
        filepath = generate_categorization_report(session, start_date, end_date)
        reports_generated.append(("Categorization (PDF)", filepath))
        print("      Done")
    except Exception as e:
        reports_failed.append(("Categorization", str(e)))
        print(f"      Error: {e}")

    # 4. High Confidence
    print("[4/7] Generating High Confidence Report...")
    try:
        filepath = generate_high_confidence_report(session, start_date, end_date, 70)
        reports_generated.append(("High Confidence (CSV)", filepath))
        print("      Done")
    except Exception as e:
        reports_failed.append(("High Confidence", str(e)))
        print(f"      Error: {e}")

    # 5. Requires Review
    print("[5/7] Generating Requires Review Report...")
    try:
        filepath = generate_requires_review_report(session, start_date, end_date, 40)
        reports_generated.append(("Requires Review (CSV)", filepath))
        print("      Done")
    except Exception as e:
        reports_failed.append(("Requires Review", str(e)))
        print(f"      Error: {e}")

    # 6. SA103S
    print("[6/7] Generating SA103S Export...")
    try:
        filepath = export_sa103s_format(session, start_date, end_date)
        reports_generated.append(("SA103S Export (CSV)", filepath))
        print("      Done")
    except Exception as e:
        reports_failed.append(("SA103S Export", str(e)))
        print(f"      Error: {e}")

    # 7. Excel Workbook
    print("[7/7] Generating Complete Workbook...")
    try:
        filepath = generate_excel_workbook(session, start_date, end_date)
        reports_generated.append(("Complete Workbook (Excel)", filepath))
        print("      Done")
    except Exception as e:
        reports_failed.append(("Complete Workbook", str(e)))
        print(f"      Error: {e}")

    # Summary
    print("\n" + "="*70)
    print("GENERATION COMPLETE".center(70))
    print("="*70)

    print(f"\nSuccessfully Generated: {len(reports_generated)} reports")

    for report_name, filepath in reports_generated:
        size = format_file_size(os.path.getsize(filepath))
        print(f"\n  {report_name}")
        print(f"  {Path(filepath).name}")
        print(f"  {size}")

    if reports_failed:
        print(f"\n\nFailed: {len(reports_failed)} reports")
        for report_name, error in reports_failed:
            print(f"\n  {report_name}: {error}")

    print("\n" + "-"*70)
    input("\nPress Enter to continue...")


def view_archived_reports_ui():
    """UI for viewing archived reports."""
    clear_screen()
    print_header("GENERATED REPORTS ARCHIVE")

    reports = list_archived_reports()

    if not reports:
        print("No reports found in archive.")
        print(f"\nReports directory: {REPORTS_DIR}")
        input("\nPress Enter to continue...")
        return

    print(f"Found {len(reports)} reports\n")
    print(f"Archive location: {REPORTS_DIR}\n")

    print_section("Recent Reports (Last 20)")

    for idx, report in enumerate(reports[:20], 1):
        print(f"\n{idx}. {report['filename']}")
        print(f"   Type: {report['type']}")
        print(f"   Size: {format_file_size(report['size_mb'] * 1024 * 1024)}")
        print(f"   Created: {report['created'].strftime('%d %B %Y at %H:%M')}")

    if len(reports) > 20:
        print(f"\n... and {len(reports) - 20} more reports")

    print("\n" + "-"*70)
    print("\nOptions:")
    print("  1. Open reports directory")
    print("  0. Back")

    choice = input("\nChoice: ").strip()

    if choice == '1':
        import subprocess
        try:
            # Open in Finder (macOS)
            subprocess.run(['open', str(REPORTS_DIR)])
        except Exception:
            print(f"\nCould not open directory automatically.")
            print(f"Please navigate to: {REPORTS_DIR}")
            input("\nPress Enter to continue...")


# ============================================================================
# QUICK ACCESS FUNCTIONS
# ============================================================================

def quick_audit_trail(session):
    """Quick generate audit trail for current tax year."""
    tax_year = get_current_tax_year()
    start, end = get_tax_year_dates(tax_year)

    print(f"\nGenerating audit trail for {tax_year}...")

    try:
        filepath = generate_audit_trail_report(session, start, end, 'PDF')
        print(f"Generated: {filepath}")
        return filepath
    except Exception as e:
        print(f"Error: {e}")
        return None


def quick_sa103s_export(session):
    """Quick generate SA103S export for current tax year."""
    tax_year = get_current_tax_year()
    start, end = get_tax_year_dates(tax_year)

    print(f"\nGenerating SA103S export for {tax_year}...")

    try:
        filepath = export_sa103s_format(session, start, end)
        print(f"Generated: {filepath}")
        return filepath
    except Exception as e:
        print(f"Error: {e}")
        return None


def quick_excel_workbook(session):
    """Quick generate Excel workbook for current tax year."""
    tax_year = get_current_tax_year()
    start, end = get_tax_year_dates(tax_year)

    print(f"\nGenerating Excel workbook for {tax_year}...")

    try:
        filepath = generate_excel_workbook(session, start, end)
        print(f"Generated: {filepath}")
        return filepath
    except Exception as e:
        print(f"Error: {e}")
        return None


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    from database import SessionLocal

    session = SessionLocal()
    try:
        reports_main_menu(session)
    finally:
        session.close()
