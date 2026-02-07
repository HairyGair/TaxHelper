# Report Formats Reference Guide

Quick reference for all compliance report formats and structures.

---

## 1. AUDIT TRAIL REPORT (PDF)

### Structure

```
┌─────────────────────────────────────────┐
│         AUDIT TRAIL REPORT              │
│                                         │
│      Tax Year 2024/25                   │
│  (6 April 2024 - 5 April 2025)          │
│                                         │
│  Generated: 17 October 2024 at 14:30    │
│         Tax Helper v3.0                 │
└─────────────────────────────────────────┘

══════════════════════════════════════════
SUMMARY
══════════════════════════════════════════

┌──────────────────────────┬───────────┐
│ Metric                   │ Count     │
├──────────────────────────┼───────────┤
│ Total Transactions       │ 1,234     │
│ Income Records           │ 45        │
│ Expense Records          │ 432       │
│ Total Changes Logged     │ 567       │
│ Audit Log Entries        │ 1,456     │
└──────────────────────────┴───────────┘

══════════════════════════════════════════
DETAILED AUDIT LOG
══════════════════════════════════════════

2024-10-17 14:32:15 | Transaction #123
Action: UPDATE
Before: {"type": null, "category": null, "reviewed": false}
After: {"type": "Expense", "category": "Office costs", "reviewed": true}
Summary: Categorized as Expense: Office costs

2024-10-17 14:30:45 | Transaction #122
Action: CREATE
Before: null
After: {"merchant": "TESCO", "amount": -45.99, "date": "2024-10-17"}
Summary: Transaction created from bank import

[... continues for all changes ...]

══════════════════════════════════════════
METHODOLOGY
══════════════════════════════════════════

This audit trail was generated using Tax Helper v3.0,
a comprehensive tax record management system designed
for HMRC compliance.

Data Collection:
All changes to transaction records are logged
automatically with precise timestamps, before/after
values, and descriptive change summaries.

Data Integrity:
The audit log is immutable once written. All entries
are stored with transaction integrity guarantees.

Compliance:
This report meets HMRC Making Tax Digital (MTD)
requirements for record keeping and audit trail
documentation.

──────────────────────────────────────────
Page 1          Generated: 17 October 2024
```

### CSV Format

```csv
Timestamp,Transaction ID,Action,Before Value,After Value,Change Summary
2024-10-17 14:32:15,123,UPDATE,"{""category"": null}","{""category"": ""Office costs""}",Categorized as Expense: Office costs
2024-10-17 14:30:45,122,CREATE,,"{""merchant"": ""TESCO"", ""amount"": -45.99}",Transaction created from bank import
```

---

## 2. RECEIPT SUMMARY REPORT (PDF)

### Structure

```
┌─────────────────────────────────────────┐
│       RECEIPT SUMMARY REPORT            │
│                                         │
│         Tax Year 2024/25                │
│  (6 April 2024 - 5 April 2025)          │
│                                         │
│  Generated: 17 October 2024 at 14:30    │
└─────────────────────────────────────────┘

══════════════════════════════════════════
SUMMARY
══════════════════════════════════════════

Total Receipts: 25
Total Amount: £2,483.49
Categories: 5

══════════════════════════════════════════
OFFICE COSTS - Total: £1,245.99 (12 receipts)
══════════════════════════════════════════

┌────────────┬──────────────┬──────────┬────────────────────────────┐
│ Date       │ Merchant     │ Amount   │ Receipt File               │
├────────────┼──────────────┼──────────┼────────────────────────────┤
│ 17/10/2024 │ STAPLES      │ £125.99  │ 20241017_staples_125-99.jpg│
│ 15/10/2024 │ AMAZON       │ £89.99   │ 20241015_amazon_89-99.pdf  │
│ 12/10/2024 │ OFFICEWORKS  │ £249.00  │ 20241012_office_249-00.jpg │
│ 08/10/2024 │ WHSmith      │ £45.50   │ 20241008_whsmith_45-50.jpg │
└────────────┴──────────────┴──────────┴────────────────────────────┘

══════════════════════════════════════════
TRAVEL - Total: £892.50 (8 receipts)
══════════════════════════════════════════

┌────────────┬──────────────┬──────────┬────────────────────────────┐
│ Date       │ Merchant     │ Amount   │ Receipt File               │
├────────────┼──────────────┼──────────┼────────────────────────────┤
│ 16/10/2024 │ BP           │ £65.00   │ 20241016_bp_65-00.jpg      │
│ 14/10/2024 │ SHELL        │ £72.50   │ 20241014_shell_72-50.jpg   │
│ 10/10/2024 │ Trainline    │ £145.00  │ 20241010_trainline_145.pdf │
└────────────┴──────────────┴──────────┴────────────────────────────┘

[... continues for all categories ...]
```

### CSV Format

```csv
Category,Date,Merchant,Amount,Receipt File,File Path
Office costs,2024-10-17,STAPLES,125.99,20241017_staples_125-99.jpg,/Users/anthony/Tax Helper/receipts/20241017_staples_125-99.jpg
Office costs,2024-10-15,AMAZON,89.99,20241015_amazon_89-99.pdf,/Users/anthony/Tax Helper/receipts/20241015_amazon_89-99.pdf
Travel,2024-10-16,BP,65.00,20241016_bp_65-00.jpg,/Users/anthony/Tax Helper/receipts/20241016_bp_65-00.jpg
```

---

## 3. CATEGORIZATION REPORT (PDF)

### Structure

```
┌─────────────────────────────────────────┐
│      CATEGORIZATION REPORT              │
│                                         │
│         Tax Year 2024/25                │
│  (6 April 2024 - 5 April 2025)          │
│                                         │
│  Generated: 17 October 2024 at 14:30    │
└─────────────────────────────────────────┘

══════════════════════════════════════════
CLASSIFICATION METHODS
══════════════════════════════════════════

Total Transactions: 1,234

Auto-Categorized: 892 (72%)
    Merchant Match: 456 (37%)
    Rule Match: 234 (19%)
    Pattern Learning: 202 (16%)

Manual Categorization: 342 (28%)

══════════════════════════════════════════
CONFIDENCE BREAKDOWN
══════════════════════════════════════════

┌──────────────────┬───────┬────────────┐
│ Confidence Level │ Count │ Percentage │
├──────────────────┼───────┼────────────┤
│ High (70-100%)   │ 756   │ 61.3%      │
│ Medium (40-69%)  │ 234   │ 19.0%      │
│ Low (10-39%)     │ 102   │ 8.3%       │
│ None (0-9%)      │ 142   │ 11.5%      │
└──────────────────┴───────┴────────────┘

══════════════════════════════════════════
TOP MERCHANTS
══════════════════════════════════════════

┌──────┬──────────────┬──────────────┐
│ Rank │ Merchant     │ Transactions │
├──────┼──────────────┼──────────────┤
│ 1    │ TESCO        │ 87           │
│ 2    │ AMAZON       │ 52           │
│ 3    │ COSTA        │ 34           │
│ 4    │ SHELL        │ 28           │
│ 5    │ SAINSBURYS   │ 23           │
└──────┴──────────────┴──────────────┘

══════════════════════════════════════════
CATEGORIZATION BY CATEGORY
══════════════════════════════════════════

┌──────────────────┬───────┬────────┬────────────────┐
│ Category         │ Count │ Pct    │ Avg Confidence │
├──────────────────┼───────┼────────┼────────────────┤
│ Office Costs     │ 234   │ 19.0%  │ 78%            │
│ Travel           │ 189   │ 15.3%  │ 82%            │
│ Phone            │ 67    │ 5.4%   │ 95%            │
│ Marketing        │ 54    │ 4.4%   │ 88%            │
│ Accountancy      │ 12    │ 1.0%   │ 100%           │
└──────────────────┴───────┴────────┴────────────────┘
```

---

## 4. HIGH CONFIDENCE TRANSACTIONS (CSV)

### Format

```csv
Date,Merchant,Description,Amount,Type,Category,Confidence,Method
2024-10-17,STAPLES,Office supplies,-125.99,Expense,Office costs,95%,merchant_match
2024-10-16,BP,Fuel - Client meeting,-65.00,Expense,Travel,78%,pattern_learning
2024-10-15,AMAZON,Printer ink,-89.99,Expense,Office costs,88%,merchant_match
2024-10-14,EE,Mobile phone,-45.00,Expense,Phone,98%,merchant_match
2024-10-13,Client Payment,Invoice #001,2500.00,Income,Freelance Income,100%,manual
```

### Usage

Filter for transactions with confidence >= 70% (or custom threshold):
- Ready for HMRC submission
- High reliability
- Minimal review needed

---

## 5. REQUIRES REVIEW REPORT (CSV)

### Format

```csv
Transaction ID,Date,Merchant,Description,Amount,Type,Category,Confidence,Reason
123,2024-10-15,Unknown Merchant,Payment,-125.00,Expense,,15%,Low confidence; No category
124,2024-10-14,MISC PURCHASE,Item,-89.50,Expense,Uncategorized,25%,Low confidence
125,2024-10-13,Cash Withdrawal,ATM,-100.00,,,10%,No category; No type
126,2024-10-12,,Bank transfer,-250.00,Expense,,5%,No merchant; No category; Low confidence
```

### Review Reasons

- **No category** - Transaction not categorized
- **Low confidence** - Confidence score < 40%
- **No confidence score** - Not scored by AI
- **No type** - Income/Expense not set
- **No merchant** - Missing merchant name

### Usage

Internal quality control before HMRC submission:
1. Review each flagged transaction
2. Manually categorize or verify
3. Update confidence scores
4. Re-run high confidence report

---

## 6. SA103S EXPORT (CSV)

### Format

```csv
Box,Category,Amount
17,Cost of goods bought for resale or materials,0.00
18,Car, van and travel expenses,892.50
19,Wages, salaries and other staff costs,0.00
20,Rent, rates, power and insurance costs,1200.00
21,Repairs and renewals of property and equipment,0.00
22,Phone, fax, stationery and other office costs,345.00
23,Advertising and business entertainment costs,450.00
24,Interest on bank and other loans,0.00
25,Bank, credit card and other financial charges,25.50
26,Irrecoverable debts written off,0.00
27,Accountancy, legal and other professional fees,600.00
28,Depreciation and loss/profit on sale of assets,0.00
29,Other business expenses,2483.49
```

### Box Number Mapping

| Box | HMRC Category | Tax Helper Categories |
|-----|---------------|----------------------|
| 17 | Cost of goods | - |
| 18 | Travel expenses | Travel, Mileage, Fuel, Parking, Public transport |
| 19 | Staff costs | - |
| 20 | Premises costs | Rent, Insurance, Utilities |
| 21 | Repairs | Equipment, Repairs, Maintenance |
| 22 | Office costs | Office costs, Phone, Internet, Stationery, Postage |
| 23 | Marketing | Marketing, Advertising, Entertainment |
| 24 | Loan interest | - |
| 25 | Finance charges | Bank charges, Finance charges |
| 26 | Bad debts | - |
| 27 | Professional fees | Accountancy, Legal fees, Professional fees |
| 28 | Depreciation | - |
| 29 | Other | Everything else not mapped above |

### Usage

1. Generate export
2. Open CSV in spreadsheet
3. Copy amounts to HMRC online form
4. Or import into tax software

---

## 7. COMPLETE EXCEL WORKBOOK

### Sheet 1: Summary

```
┌────────────────────────────────────────┐
│  Tax Summary - 2024/25                 │
└────────────────────────────────────────┘

┌───────────────────────┬────────────────┐
│ Metric                │ Value          │
├───────────────────────┼────────────────┤
│ Total Income          │ £12,400.00     │
│ Total Expenses        │ £6,483.49      │
│ Net Profit/Loss       │ £5,916.51      │
│                       │                │
│ Income Transactions   │ 5              │
│ Expense Transactions  │ 21             │
│ Total Transactions    │ 26             │
└───────────────────────┴────────────────┘
```

### Sheet 2: Income

```
┌──────────────────────────────────────────────────────────────────────────┐
│                               Income                                      │
└──────────────────────────────────────────────────────────────────────────┘

┌────────────┬──────────────┬───────────────┬──────────┬──────┬─────────────┬────────────┬────────────┐
│ Date       │ Merchant     │ Description   │ Amount   │ Type │ Category    │ Confidence │ Method     │
├────────────┼──────────────┼───────────────┼──────────┼──────┼─────────────┼────────────┼────────────┤
│ 15/05/2024 │ Client       │ Invoice #001  │ £2,500.00│ Inc  │ Freelance   │ 100%       │ manual     │
│ 01/06/2024 │ Client       │ Invoice #002  │ £1,800.00│ Inc  │ Freelance   │ 100%       │ manual     │
│ 10/07/2024 │ Client       │ Invoice #003  │ £3,200.00│ Inc  │ Freelance   │ 100%       │ manual     │
└────────────┴──────────────┴───────────────┴──────────┴──────┴─────────────┴────────────┴────────────┘
```

### Sheet 3: Expenses by Category

```
┌────────────────────────────────────────┐
│      Expenses by Category              │
└────────────────────────────────────────┘

┌────────────────────┬───────┬────────────┐
│ Category           │ Count │ Total      │
├────────────────────┼───────┼────────────┤
│ Office Costs       │ 4     │ £510.48    │
│ Travel             │ 4     │ £294.50    │
│ Phone              │ 3     │ £135.00    │
│ Internet           │ 2     │ £70.00     │
│ Marketing          │ 3     │ £485.00    │
│ Accountancy        │ 2     │ £400.00    │
│ Uncategorized      │ 3     │ £314.50    │
├────────────────────┼───────┼────────────┤
│ TOTAL              │ 21    │ £6,483.49  │
└────────────────────┴───────┴────────────┘
```

### Sheet 4: All Transactions

Full transaction list (same format as Income sheet, but includes both income and expenses)

### Sheet 5: Audit Trail

```
┌────────────────────┬────────────┬────────┬───────────────┬─────────────┬────────────────┐
│ Timestamp          │ Trans ID   │ Action │ Before Value  │ After Value │ Change Summary │
├────────────────────┼────────────┼────────┼───────────────┼─────────────┼────────────────┤
│ 2024-10-17 14:32   │ 123        │ UPDATE │ {"cat": null} │ {"cat": ... │ Categorized    │
└────────────────────┴────────────┴────────┴───────────────┴─────────────┴────────────────┘
```

### Sheet 6: Receipts

```
┌────────────┬──────────────┬──────────┬──────────────┬─────────────────────────────┐
│ Date       │ Merchant     │ Amount   │ Category     │ Receipt File                │
├────────────┼──────────────┼──────────┼──────────────┼─────────────────────────────┤
│ 17/10/2024 │ STAPLES      │ £125.99  │ Office costs │ 20241017_staples_125-99.jpg │
│ 15/10/2024 │ AMAZON       │ £89.99   │ Office costs │ 20241015_amazon_89-99.pdf   │
└────────────┴──────────────┴──────────┴──────────────┴─────────────────────────────┘
```

---

## Color Coding

### PDF Reports

- **Headers**: Blue (#3498db)
- **Category Sections**: Teal (#16a085)
- **Warnings**: Orange (#e67e22)
- **Alternating Rows**: Light gray (#f8f9fa)

### Excel Workbooks

- **Headers**: Blue fill, white text
- **Summary Sheet**: Green accents
- **Income Sheet**: Blue headers
- **Expenses Sheet**: Orange headers
- **Audit Sheet**: Teal headers
- **Receipts Sheet**: Purple headers

---

## File Naming Convention

All reports follow this pattern:

```
{report_type}_{tax_year}_{timestamp}.{ext}

Examples:
- audit_trail_2024_25_20241017_143022.pdf
- receipt_summary_2024_25_20241017_143045.pdf
- categorization_report_2024_25_20241017_143108.pdf
- high_confidence_2024_25_20241017_143130.csv
- requires_review_2024_25_20241017_143152.csv
- sa103s_export_2024_25_20241017_143215.csv
- complete_workbook_2024_25_20241017_143237.xlsx
```

Format:
- **report_type**: Descriptive name (snake_case)
- **tax_year**: YYYY_YY format
- **timestamp**: YYYYMMDD_HHMMSS
- **ext**: pdf, csv, or xlsx

---

## Report Sizes (Typical)

Based on 1,000 transactions:

| Report Type | Format | Typical Size |
|-------------|--------|--------------|
| Audit Trail | PDF | 200-500 KB |
| Audit Trail | CSV | 50-100 KB |
| Receipt Summary | PDF | 150-300 KB |
| Receipt Summary | CSV | 20-50 KB |
| Categorization | PDF | 100-200 KB |
| High Confidence | CSV | 30-80 KB |
| Requires Review | CSV | 5-20 KB |
| SA103S Export | CSV | 1-3 KB |
| Complete Workbook | XLSX | 200-600 KB |

---

## API Quick Reference

```python
# Import functions
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
    list_archived_reports
)

# Get tax year
current_year = get_current_tax_year()  # "2024/25"
start, end = get_tax_year_dates("2024/25")

# Generate reports
audit_pdf = generate_audit_trail_report(session, start, end, 'PDF')
receipt_pdf = generate_receipt_summary(session, start, end, 'PDF')
categorization_pdf = generate_categorization_report(session, start, end)
high_conf_csv = generate_high_confidence_report(session, start, end, 70)
review_csv = generate_requires_review_report(session, start, end, 40)
sa103s_csv = export_sa103s_format(session, start, end)
workbook = generate_excel_workbook(session, start, end)

# List archives
reports = list_archived_reports()
for r in reports:
    print(f"{r['filename']} - {r['size_mb']:.2f} MB")
```

---

## HMRC Submission Checklist

Before submitting to HMRC:

- [ ] Generate **Requires Review Report**
- [ ] Review and fix all flagged transactions
- [ ] Generate **High Confidence Report** (verify >= 95% confidence)
- [ ] Generate **SA103S Export**
- [ ] Cross-check totals with bank statements
- [ ] Generate **Complete Workbook** for records
- [ ] Generate **Audit Trail** for compliance
- [ ] Archive all reports for 5+ years

---

## End of Reference Guide

For implementation details, see `COMPLIANCE_REPORTS_INTEGRATION.md`
For code examples, see `examples/generate_sample_reports.py`
