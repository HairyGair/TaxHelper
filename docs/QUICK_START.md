# Quick Start Guide

## First Time Setup (5 minutes)

### 1. Install Dependencies
```bash
cd "/Users/anthony/Tax Helper"
pip3 install -r requirements.txt
```

### 2. Run the App
```bash
streamlit run app.py
```

### 3. Try the Demo
- Upload `test_data.csv` in the Inbox page
- Click through the pages to see features

## Monthly Workflow (20 minutes)

### Step 1: Import Bank Statement
1. Download CSV from your bank
2. Go to **Inbox > Upload CSV**
3. Preview and click **Import Transactions**

### Step 2: Review Transactions
1. Switch to **Review Transactions** tab
2. Check the auto-categorization
3. Toggle any personal expenses
4. Click **Post All Business Transactions to Ledgers**

### Step 3: Add Manual Entries
- **Mileage**: Add business trips not in bank
- **Cash Expenses**: Add cash purchases
- **Other Income**: Add non-bank income

### Step 4: Check Dashboard
- Review your YTD totals
- Check estimated profit
- Confirm all looks correct

## Quick Page Reference

| Page | What It Does | When to Use |
|------|-------------|-------------|
| Dashboard | YTD summary & profit | Check anytime for overview |
| Inbox | Import & categorize bank statements | Monthly after downloading statement |
| Income | View/add income records | Add non-bank income, review all income |
| Expenses | View/add expense records | Add cash expenses, review all expenses |
| Mileage | Log business travel | Weekly or monthly mileage entry |
| Donations | Track Gift Aid donations | When you make charitable donations |
| Rules | Customize auto-categorization | Setup once, tweak as needed |
| Summary (HMRC) | Copy figures for tax return | Year-end tax filing |
| Settings | Configure app & backups | Initial setup, create backups |
| Export | Generate Excel workbook | Year-end archival |

## Key Keyboard Shortcuts

- **Ctrl/Cmd + R**: Refresh page (if data not updating)
- **Tab**: Navigate between form fields
- **Ctrl/Cmd + A**: Select all (for copying summary)

## Common Tasks

### How do I...

**...import a bank statement?**
Inbox > Upload CSV > Choose file > Import Transactions

**...add a cash expense?**
Expenses > Add Expense tab > Fill form > Add Expense

**...log mileage?**
Mileage > Add Mileage tab > Enter journey details > Add Mileage

**...see my year-to-date profit?**
Dashboard > Look at "Net Profit (Self-Emp)" card

**...get HMRC figures?**
Summary (HMRC) > Copy the text area content

**...export everything?**
Export > Generate Excel Export > Download file

**...create a backup?**
Settings > Database Management > Create Backup

**...customize categorization?**
Rules > Add Rule tab > Create rule > Add Rule

## Tips for Success

1. **Import Weekly**: Don't let statements pile up
2. **Review Immediately**: Categorize while fresh in memory
3. **Add Mileage Daily**: Keep a diary/calendar note
4. **Backup Monthly**: Use Settings > Create Backup
5. **Check Dashboard Weekly**: Spot issues early

## Default Categorization Rules

The app comes with 20+ rules pre-configured:

**Income**:
- CLIENT → Self-employment
- SALARY → Employment
- INTEREST → Interest
- DIVIDEND → Dividends

**Expenses**:
- SAINSBURY/STAPLES → Office costs
- UBER/TRAINLINE/TFL → Travel
- EE/VODAFONE/BT → Phone
- ACCOUNTANT → Accountancy

**Ignore (Personal)**:
- NETFLIX/SPOTIFY → Personal
- MORTGAGE → Personal
- COUNCIL TAX → Personal

You can customize these in the Rules page.

## When to Use Each Income Type

- **Employment**: PAYE salary from employer
- **Self-employment**: Freelance/business income (main category)
- **Interest**: Bank/savings account interest
- **Dividends**: Company share dividends
- **Property**: Rental income (if applicable)
- **Other**: Anything else taxable

## When to Use Each Expense Category

- **Advertising**: Marketing, ads, website costs
- **Office costs**: Stationery, software, small equipment
- **Travel**: Public transport, taxis (NOT mileage - use Mileage page)
- **Phone**: Mobile/landline business calls
- **Professional fees**: Consultants, contractors
- **Accountancy**: Accountant fees, tax advice
- **Bank charges**: Business account fees
- **Stock/Materials**: Raw materials for products
- **Legal fees**: Solicitor, legal advice
- **Insurance**: Business insurance
- **Interest**: Business loan interest
- **Depreciation**: Fixed asset depreciation
- **Other business expenses**: Anything else allowable

## Red Flags to Avoid

- Don't claim personal expenses
- Don't claim the same expense twice
- Don't claim both mileage AND fuel costs
- Don't claim more than 100% business use
- Don't forget to keep receipts (at least 5 years)

## Getting Help

1. **README.md**: Full user guide with FAQs
2. **INSTALL.md**: Installation troubleshooting
3. **PROJECT_SUMMARY.md**: Technical details
4. **HMRC Website**: Gov.uk guidance on allowable expenses
5. **Accountant**: When in doubt, ask a professional

## UK Tax Year Important Dates

- **6 April**: Tax year starts
- **5 April**: Tax year ends
- **31 October**: Paper tax return deadline
- **31 January**: Online tax return deadline
- **31 January**: Payment deadline for previous tax year
- **31 July**: Second payment on account

## Database Location

Your data is stored here:
```
/Users/anthony/Tax Helper/tax_helper.db
```

**Backup this file regularly!**

## Emergency Recovery

If something goes wrong:

1. **Data lost?** Restore from backup (Settings > Create Backup)
2. **App won't start?** Delete tax_helper.db and restart
3. **Wrong categorization?** Edit in Income/Expenses pages
4. **Duplicate transactions?** App auto-detects, or delete manually
5. **Python errors?** Reinstall dependencies: `pip3 install -r requirements.txt --force-reinstall`

## Next Steps

- Read README.md for comprehensive guide
- Try importing test_data.csv
- Customize rules for your banking descriptions
- Set up monthly routine
- Create your first backup

---

**Version**: 1.0.0
**Last Updated**: October 2025
