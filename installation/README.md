# 💷 Tax Helper - UK Self-Assessment Assistant

A simple, offline application to help UK self-employed individuals manage their tax records and prepare for HMRC Self-Assessment (SA103 form).

## Features

- 📥 Import bank statement CSV files with smart categorization
- 🔍 Final Review with bulk pattern detection (e.g., "You were paid £1000 12 times")
- 💼 Automatic posting to Income and Expense ledgers
- 🚗 Mileage tracking with HMRC-approved rates (45p/mile)
- 🎁 Gift Aid donation records
- 📊 HMRC-compliant tax calculations (2024/25 tax year)
- 📝 Export to Excel for accountant submission
- 💡 Built-in HMRC guidance for allowable expenses

## Quick Start Installation

### For Windows:

1. **Check Python Installation:**
   - Open Command Prompt (search for "cmd" in Start menu)
   - Type: `python --version` and press Enter
   - If you see a version number (e.g., "Python 3.11.5"), you're good to go!
   - If not, download Python from: https://www.python.org/downloads/
   - ⚠️ **IMPORTANT**: During installation, check the box "Add Python to PATH"

2. **Install Tax Helper:**
   - Double-click the file `INSTALL.bat`
   - Wait for the installation to complete (may take 1-2 minutes)
   - You should see "✅ Installation complete!"

3. **Run Tax Helper:**
   - Double-click the file `RUN.bat`
   - Your web browser will open automatically with the Tax Helper app
   - If it doesn't open, go to: http://localhost:8501

### For Mac/Linux:

1. **Check Python Installation:**
   - Open Terminal (search for "Terminal" in Spotlight)
   - Type: `python3 --version` and press Enter
   - Python 3 is usually pre-installed on Mac
   - If not, download from: https://www.python.org/downloads/

2. **Make Scripts Executable:**
   - In Terminal, navigate to the Tax Helper folder:
     ```bash
     cd "/Users/anthony/Tax Helper"
     ```
   - Make the scripts executable:
     ```bash
     chmod +x INSTALL.sh RUN.sh
     ```

3. **Install Tax Helper:**
   - Run: `./INSTALL.sh`
   - Wait for installation to complete

4. **Run Tax Helper:**
   - Run: `./RUN.sh`
   - Your browser will open with the app

## How to Export Bank Statements from NatWest

1. Log in to your NatWest online banking
2. Navigate to your business current account
3. Click on "Statements" or "Download transactions"
4. Select the date range (typically last month or quarter)
5. Choose format: **CSV (Comma Separated Values)**
6. Download the file to your computer
7. Upload the CSV file in the **Inbox** page of this application

### Expected CSV Format
```csv
Date,Type,Description,Paid out,Paid in,Balance
01/04/2025,POS,SAINSBURYS 1234,12.50,,1234.56
02/04/2025,CR,CLIENT PAYMENT,,450.00,1684.56
```

**Note**: If your bank uses different column names (e.g., "Debit Amount" instead of "Paid out"), you can configure the column mappings in **Settings > Column Mappings**.

## How to Use Tax Helper (Monthly Workflow)

### Step 1: Import Your Bank Statement

1. **Download your bank statement** as a CSV file from your online banking
2. Launch Tax Helper (double-click RUN.bat or RUN.sh)
3. Click **📥 Import Statements** in the sidebar
4. Click **Browse files** and select your CSV file
5. Click **Import Transactions**

The app will automatically categorize transactions based on rules it learns.

### Step 2: Review with Bulk Actions (The Smart Way!)

1. Click **🔍 Final Review** in the sidebar
2. **Look for bulk patterns** at the top:
   - Example: "💼 ANTHONY GAIR | 12 transactions | £12,000 total"
   - Select "Business Income" and category "Self-employment"
   - Click **"Process All 12 Transactions"**
   - Done! All 12 transactions are now posted to your Income ledger

3. **Review remaining individual transactions:**
   - For each transaction, choose:
     - **Business Income** → automatically posts to Income ledger
     - **Business Expense** → automatically posts to Expenses ledger
     - **Personal** → ignored for tax purposes
   - Click **"Save & Next"**

**Pro Tip:** The app learns from your choices and will categorize similar transactions automatically next time!

### Step 3: Add Additional Items

1. **Mileage**: Click **Mileage** in sidebar
   - Add business trips (45p/mile automatically calculated)

2. **Cash Expenses**: Click **Expenses** in sidebar
   - Add expenses not in bank statements (e.g., cash purchases)

3. **Donations**: Click **Donations** in sidebar
   - Add Gift Aid donations for tax relief

### Step 4: Check Your Tax Summary

1. Click **Dashboard** to see year-to-date totals
2. Click **Summary (HMRC)** to see your tax calculation
3. Click **Export** to download Excel file for your accountant

### Monthly Routine

**Week 1:** Import statements + Final Review (30 minutes)
**Anytime:** Add mileage/cash expenses as they happen
**Quarter-end:** Check Dashboard, create backup in Settings
**Year-end:** Export to Excel, submit Self-Assessment

## Understanding the Pages

### Dashboard
Year-to-date overview showing:
- Self-employment turnover
- Total allowable expenses
- Net profit
- Tax estimates
- Other income sources
- Gift Aid donations

### 📥 Import Statements
Simple one-step process:
- Upload bank statement CSV files
- Auto-apply categorization rules
- Shows count of unreviewed transactions
- Directs you to Final Review for transaction processing

### 🔍 Final Review
The main transaction review page:
1. **Bulk Patterns** (top of page): Detects recurring transactions (3+ similar items)
   - Process multiple transactions at once
   - Example: 12 monthly salary payments in one click
2. **Individual Review** (below): Review remaining transactions one-by-one
   - Business transactions automatically post to Income/Expense ledgers
   - Personal transactions are excluded from tax calculations

### Income
Track all income with categories:
- **Employment**: PAYE income (records tax deducted)
- **Self-employment**: Freelance/business income (main turnover)
- **Interest**: Bank/savings interest
- **Dividends**: Company dividends
- **Property**: Rental income
- **Other**: Any other income

### Expenses
Track allowable business expenses using HMRC categories:
- Advertising
- Office costs
- Travel (excluding mileage - use Mileage page)
- Phone
- Professional fees
- Accountancy
- Bank charges
- Stock/Materials
- Legal fees
- Insurance
- Interest
- Depreciation
- Other business expenses

**Pro Tip**: Keep receipt links in cloud storage (Google Drive, Dropbox) and paste the link in the Receipt Link field.

### Mileage
Log business travel separately from travel expenses:
- HMRC rates: 45p/mile (first 10,000 miles), 25p/mile (thereafter)
- The app automatically calculates the allowable amount
- This gets added to total allowable expenses

**Important**: Don't double-count! If you log mileage, don't also claim fuel as an expense.

### Donations
Track Gift Aid donations:
- HMRC automatically grosses up by 25%
- Only claim Gift Aid-eligible donations
- You must have paid enough tax to cover the gross-up

### Rules
Customize automatic transaction categorization:
- **Match Mode**: Contains (flexible), Equals (exact), Regex (advanced)
- **Priority**: Lower number = applied first (1 = highest priority)
- **Map To**: Income, Expense, or Ignore

**Examples**:
- Contains "CLIENT" → Income (Self-employment)
- Contains "SALARY" → Income (Employment)
- Contains "SAINSBURY" → Expense (Office costs)
- Contains "NETFLIX" → Ignore (Personal)

### Summary (HMRC)
Copy-paste ready figures with box labels for HMRC Self Assessment forms:
- **SA103S**: Self-employment (Box 15 Turnover, Box 31 Expenses, Box 32 Profit)
- **Employment**: Box 1 Pay, Box 2 Tax deducted
- **Interest**: Box 1 Gross interest
- **Dividends**: Box 1 Gross dividends
- **Gift Aid**: Total donations paid

### Settings
Configure:
- Tax year (6 April - 5 April)
- Accounting basis (Cash or Accruals)
- CSV column mappings for different banks
- Mileage rates
- Database backups

### Export
Generate Excel workbook with sheets:
- Profile (your settings)
- Income (all income records)
- Expenses (all expense records)
- Mileage (all mileage logs)
- Donations (all donations)
- Summary (HMRC totals)
- Rules (categorization rules)
- Archived_Inbox (reviewed transactions)

Also export individual tables as CSV.

## UK Tax Year Dates

The UK tax year runs from **6 April to 5 April** (not calendar year).

Example:
- Tax Year 2024/25 = 6 April 2024 to 5 April 2025
- Self Assessment deadline: 31 January 2026 (online)

The app automatically filters data by tax year on the Dashboard and Summary pages.

## Data Storage

- All data is stored locally in `tax_helper.db` (SQLite database)
- No cloud sync, no external API calls
- Fully offline after installation
- Database location: `/Users/anthony/Tax Helper/tax_helper.db`

**Backup Recommendations**:
- Weekly: Use Settings > Create Backup
- Store backups in cloud storage (iCloud, Google Drive, Dropbox)
- Keep backups for at least 6 years (HMRC requirement)

## Troubleshooting

### CSV Upload Issues

**Problem**: "Required column 'X' not found in CSV"
- **Solution**: Your bank uses different column names. Go to Settings > Column Mappings and update the column names to match your CSV file.

**Problem**: "Invalid dates were removed"
- **Solution**: Check your CSV date format. The app expects DD/MM/YYYY (UK format). If your bank uses a different format, you may need to pre-process the CSV in Excel.

**Problem**: "Duplicate transactions detected"
- **Solution**: This is normal! The app automatically skips duplicates. You may have already imported this statement.

### Categorization Issues

**Problem**: Transactions are categorized incorrectly
- **Solution**: Update the rules in the Rules page. Adjust priorities so more specific rules run first.

**Problem**: A transaction isn't categorized at all
- **Solution**: Add a new rule in Rules > Add Rule. Use "Contains" mode for flexibility.

### Database Issues

**Problem**: App shows old data after changes
- **Solution**: Refresh the page (F5 or Cmd+R). Streamlit caches data aggressively.

**Problem**: Need to start fresh
- **Solution**: Delete `tax_helper.db` and restart the app. It will create a fresh database with default settings.

### Performance Issues

**Problem**: App is slow with large datasets
- **Solution**: SQLite handles 10,000+ transactions fine. If you have 50,000+ transactions, consider archiving old tax years to a separate database.

## FAQ

**Q: Can I use this with banks other than NatWest?**
A: Yes! Most UK banks export similar CSV formats. Use Settings > Column Mappings to match your bank's column names.

**Q: What if I make a mistake?**
A: Every record has an Edit button. You can also delete records. Changes are immediate but you can restore from backups.

**Q: Can I import multiple bank accounts?**
A: Yes, import each CSV separately. The app merges all transactions in the same database.

**Q: How do I handle split expenses (e.g., 50% business use of phone)?**
A: Manually add the business portion to Expenses. Don't import the full amount from the bank statement (mark it as personal in the Inbox).

**Q: What about VAT?**
A: This app focuses on income tax Self Assessment. For VAT-registered businesses, you'll need additional VAT-specific accounting software.

**Q: Can I use this for multiple tax years?**
A: Yes! Change the tax year in Settings. The Dashboard and Summary automatically filter by tax year. At year-end, export to Excel and archive.

**Q: Is my data secure?**
A: Yes, all data is stored locally on your computer. No cloud sync, no external connections. Treat the database file like you would treat paper tax records - keep backups in secure locations.

**Q: Can multiple users access the same database?**
A: No, this is a single-user application. SQLite doesn't support concurrent writes. If you need multi-user, you'd need to upgrade to PostgreSQL or MySQL (requires code changes).

**Q: What about receipt storage?**
A: Store receipts in cloud storage (Google Drive, Dropbox, etc.) and paste links in the Receipt Link field. Alternatively, scan/photo receipts and name them by date (e.g., `2025-04-15_Staples.pdf`).

## HMRC Compliance Notes

This application helps you organize records for Self Assessment. Please note:

1. **Record Keeping**: HMRC requires you to keep records for at least 5 years after the 31 January submission deadline.

2. **Allowable Expenses**: Only claim expenses that are "wholly and exclusively" for business purposes. Mixed-use items (e.g., home phone) can only claim the business portion.

3. **Mileage vs Fuel**: Choose one method:
   - **Mileage allowance** (simplified): 45p/mile (10,000), 25p/mile (thereafter)
   - **Actual costs**: Fuel, insurance, repairs, etc. (more complex)
   - Don't claim both!

4. **Cash Basis vs Accruals**: Most sole traders use Cash Basis (default in this app). This means:
   - Income: Count when you receive payment
   - Expenses: Count when you pay
   - Alternative: Accruals basis (count when invoiced/billed)

5. **Personal vs Business**: Be conservative. If an expense has any personal element, either:
   - Don't claim it, or
   - Only claim the business portion

6. **Professional Advice**: This app is a record-keeping tool. For tax planning and compliance advice, consult a qualified accountant or tax adviser.

## Support and Feedback

This is an open-source project. For issues, feature requests, or contributions, please note:

- The application is provided as-is with no warranty
- Always maintain backups of your data
- Test with sample data before using for real tax records
- Consider having an accountant review your final figures

## License

This project is provided for personal use. You are free to modify and distribute it for non-commercial purposes.

---

**Version**: 1.0.0
**Last Updated**: October 2025
**Compatible With**: UK Self Assessment tax rules as of 2024/25 tax year
