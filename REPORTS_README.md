# Compliance & Audit Reports - Quick Start

HMRC-ready compliance reports for Tax Helper application.

## Quick Installation

### 1. Install Dependencies

```bash
cd "/Users/anthony/Tax Helper"
pip install reportlab openpyxl pandas
```

### 2. Test Report Generation

```bash
python examples/generate_sample_reports.py
```

This will:
- Create sample transactions, receipts, and audit logs
- Generate all 7 report types
- Display file paths and sizes

### 3. Check Generated Reports

```bash
open reports/
```

You should see 7 files:
- `audit_trail_2024_25_*.pdf`
- `receipt_summary_2024_25_*.pdf`
- `categorization_report_2024_25_*.pdf`
- `high_confidence_2024_25_*.csv`
- `requires_review_2024_25_*.csv`
- `sa103s_export_2024_25_*.csv`
- `complete_workbook_2024_25_*.xlsx`

## Quick Integration

### Add to Main Menu

Edit your `main.py` or `app.py`:

```python
from components.reports_ui import reports_main_menu

def main():
    # ... existing code ...

    print("  9. Generate Compliance Reports")

    if choice == '9':
        reports_main_menu(session)
```

### Quick Access Functions

For dashboard or quick actions:

```python
from components.reports_ui import (
    quick_audit_trail,
    quick_sa103s_export,
    quick_excel_workbook
)

# Generate current tax year reports
filepath = quick_audit_trail(session)
filepath = quick_sa103s_export(session)
filepath = quick_excel_workbook(session)
```

## Available Reports

### 1. Audit Trail Report (PDF)
Complete change history for HMRC compliance.

```python
from components.compliance_reports import generate_audit_trail_report, get_tax_year_dates

start, end = get_tax_year_dates("2024/25")
filepath = generate_audit_trail_report(session, start, end, 'PDF')
```

### 2. Receipt Summary (PDF)
All receipts organized by category.

```python
from components.compliance_reports import generate_receipt_summary

filepath = generate_receipt_summary(session, start, end, 'PDF')
```

### 3. Categorization Report (PDF)
Classification methodology and confidence analysis.

```python
from components.compliance_reports import generate_categorization_report

filepath = generate_categorization_report(session, start, end)
```

### 4. High Confidence Transactions (CSV)
Transactions with confidence >= 70%.

```python
from components.compliance_reports import generate_high_confidence_report

filepath = generate_high_confidence_report(session, start, end, min_confidence=70)
```

### 5. Requires Review Report (CSV)
Low-confidence transactions needing verification.

```python
from components.compliance_reports import generate_requires_review_report

filepath = generate_requires_review_report(session, start, end, max_confidence=40)
```

### 6. SA103S Export (CSV)
HMRC Self-Assessment SA103S format.

```python
from components.compliance_reports import export_sa103s_format

filepath = export_sa103s_format(session, start, end)
```

### 7. Complete Excel Workbook
Multi-sheet comprehensive workbook.

```python
from components.compliance_reports import generate_excel_workbook

filepath = generate_excel_workbook(session, start, end)
```

## File Structure

```
/Users/anthony/Tax Helper/
├── components/
│   ├── compliance_reports.py    # Core report generation
│   └── reports_ui.py            # User interface
├── examples/
│   └── generate_sample_reports.py
├── reports/                      # Generated reports (auto-created)
│   ├── audit_trail_*.pdf
│   ├── receipt_summary_*.pdf
│   └── ...
├── COMPLIANCE_REPORTS_INTEGRATION.md  # Full integration guide
├── REPORT_FORMATS_REFERENCE.md        # Report format details
└── REPORTS_README.md                  # This file
```

## Common Use Cases

### HMRC Submission Workflow

```python
from components.compliance_reports import *

# 1. Check what needs review
start, end = get_tax_year_dates("2024/25")
review_file = generate_requires_review_report(session, start, end)

# 2. After fixing issues, get high confidence transactions
high_conf_file = generate_high_confidence_report(session, start, end)

# 3. Generate SA103S export for submission
sa103s_file = export_sa103s_format(session, start, end)

# 4. Generate audit trail for compliance
audit_file = generate_audit_trail_report(session, start, end)
```

### Year-End Archive

```python
# Generate complete workbook for accountant
workbook_file = generate_excel_workbook(session, start, end)

# Archive for 5+ years
import shutil
archive_dir = Path("/Users/anthony/Tax Helper/archive/2024-25")
archive_dir.mkdir(parents=True, exist_ok=True)
shutil.copy(workbook_file, archive_dir)
```

### Monthly Report Automation

```python
from datetime import datetime
from calendar import monthrange

def generate_monthly_reports(session, year, month):
    """Generate reports for specific month."""
    start = datetime(year, month, 1)
    last_day = monthrange(year, month)[1]
    end = datetime(year, month, last_day, 23, 59, 59)

    return {
        'audit': generate_audit_trail_report(session, start, end),
        'receipts': generate_receipt_summary(session, start, end),
        'workbook': generate_excel_workbook(session, start, end)
    }

# Usage
reports = generate_monthly_reports(session, 2024, 10)
```

## Troubleshooting

### Module Not Found

```bash
# Make sure you're in the right directory
cd "/Users/anthony/Tax Helper"

# Reinstall dependencies
pip install reportlab openpyxl pandas
```

### Permission Denied

```bash
# Check reports directory
ls -la reports/

# Fix permissions if needed
chmod 755 reports/
```

### Empty Reports

```python
# Check if transactions exist
from models import Transaction
from datetime import datetime

start = datetime(2024, 4, 6)
end = datetime(2025, 4, 5)

count = session.query(Transaction).filter(
    Transaction.date >= start,
    Transaction.date <= end
).count()

print(f"Transactions in range: {count}")
```

### Test with Sample Data

```bash
# This creates sample data if database is empty
python examples/generate_sample_reports.py
```

## Next Steps

1. **Read Integration Guide**: `COMPLIANCE_REPORTS_INTEGRATION.md`
   - Detailed integration instructions
   - All report types explained
   - Customization options

2. **Check Report Formats**: `REPORT_FORMATS_REFERENCE.md`
   - Visual examples of each report
   - SA103S box number mapping
   - File naming conventions

3. **Integrate into Application**:
   - Add to main menu
   - Add to dashboard
   - Add to settings page

4. **Customize**:
   - Modify SA103S category mappings
   - Adjust PDF styling
   - Add custom report types

## Support Files

- **`compliance_reports.py`** - Core functionality (1,400+ lines)
- **`reports_ui.py`** - User interface (600+ lines)
- **`generate_sample_reports.py`** - Testing utility (300+ lines)
- **Integration guide** - Complete documentation
- **Format reference** - Visual examples

## Requirements

```txt
reportlab>=4.0.0
openpyxl>=3.1.0
pandas>=2.0.0
sqlalchemy>=2.0.0
```

## Features

- 7 different report types
- PDF, CSV, and Excel formats
- HMRC SA103S compatible
- Professional PDF formatting
- Multi-sheet Excel workbooks
- UK tax year support (6 April - 5 April)
- Automatic archiving
- Interactive UI
- Batch report generation

## HMRC Compliance

All reports meet HMRC requirements:
- Making Tax Digital (MTD) compliant
- Complete audit trail
- Immutable change logs
- Timestamped records
- Before/after values
- 5+ year archiving ready

## Questions?

1. Check `COMPLIANCE_REPORTS_INTEGRATION.md` for detailed docs
2. Check `REPORT_FORMATS_REFERENCE.md` for examples
3. Run `python examples/generate_sample_reports.py` for testing
4. Review generated reports in `reports/` directory

## Quick Test

```bash
# 1. Install
pip install reportlab openpyxl pandas

# 2. Generate sample reports
python examples/generate_sample_reports.py

# 3. View reports
open reports/

# 4. Check files were created
ls -lh reports/
```

Expected output:
```
audit_trail_2024_25_20241017_143022.pdf (234 KB)
receipt_summary_2024_25_20241017_143045.pdf (187 KB)
categorization_report_2024_25_20241017_143108.pdf (156 KB)
high_confidence_2024_25_20241017_143130.csv (12 KB)
requires_review_2024_25_20241017_143152.csv (5 KB)
sa103s_export_2024_25_20241017_143215.csv (3 KB)
complete_workbook_2024_25_20241017_143237.xlsx (421 KB)
```

All set! You now have production-ready HMRC compliance reports.
