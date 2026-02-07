#!/usr/bin/env python3
"""
Analyze ledger accuracy - identify potential miscategorizations
"""

import sys
sys.path.insert(0, '/Users/anthony/Tax Helper')

from models import init_db, Income, Expense
from collections import Counter

print("=" * 80)
print("LEDGER ACCURACY ANALYSIS")
print("=" * 80)
print()

# Initialize database
engine, SessionLocal = init_db()
session = SessionLocal()

# Get all ledger entries
all_income = session.query(Income).order_by(Income.date.desc()).all()
all_expenses = session.query(Expense).order_by(Expense.date.desc()).all()

print(f"📊 CURRENT LEDGER STATE:")
print(f"   Income:   {len(all_income)} records | £{sum(i.amount_gross for i in all_income):,.2f}")
print(f"   Expenses: {len(all_expenses)} records | £{sum(e.amount for e in all_expenses):,.2f}")
print(f"   Net:      £{sum(i.amount_gross for i in all_income) - sum(e.amount for e in all_expenses):,.2f}")
print()

# Analyze expenses for potential issues
print("🔍 EXPENSE ANALYSIS - Potential Issues:")
print("-" * 80)

# 1. Check for internal transfers (SWAN JL)
swan_transfers = [e for e in all_expenses if 'SWAN' in e.supplier.upper() or 'JL' in e.supplier.upper()]
if swan_transfers:
    swan_total = sum(e.amount for e in swan_transfers)
    print(f"\n⚠️  INTERNAL TRANSFERS (Should not be expenses):")
    print(f"   Count: {len(swan_transfers)} | Total: £{swan_total:,.2f}")
    print(f"   Examples:")
    for e in swan_transfers[:5]:
        print(f"      {e.date} | £{e.amount:>8,.2f} | {e.supplier[:50]}")
    if len(swan_transfers) > 5:
        print(f"      ... and {len(swan_transfers) - 5} more")

# 2. Check for round-ups (should be savings, not expenses)
roundup_expenses = [e for e in all_expenses if 'ROUND UP' in e.supplier.upper() or e.category == 'Savings']
if roundup_expenses:
    roundup_total = sum(e.amount for e in roundup_expenses)
    print(f"\n⚠️  ROUND-UP/SAVINGS (Should not be expenses):")
    print(f"   Count: {len(roundup_expenses)} | Total: £{roundup_total:,.2f}")

# 3. Check for duplicate categories that might be personal
personal_patterns = ['TESCO', 'SAINSBURY', 'ASDA', 'MORRISONS', 'LIDL', 'ALDI', 'MARKS & SPENCER', 'WAITROSE']
potential_personal = []
for e in all_expenses:
    if any(pattern in e.supplier.upper() for pattern in personal_patterns):
        potential_personal.append(e)

if potential_personal:
    personal_total = sum(e.amount for e in potential_personal)
    print(f"\n⚠️  POTENTIAL PERSONAL EXPENSES (Groceries/Supermarkets):")
    print(f"   Count: {len(potential_personal)} | Total: £{personal_total:,.2f}")

    # Show category breakdown
    categories = Counter(e.category for e in potential_personal)
    print(f"   Category breakdown:")
    for cat, count in categories.most_common(5):
        cat_total = sum(e.amount for e in potential_personal if e.category == cat)
        print(f"      {cat:30} {count:3} txns | £{cat_total:,.2f}")

# 4. Check for refunds/credits (negative amounts or "REFUND" in description)
refunds = [e for e in all_expenses if 'REFUND' in e.supplier.upper() or 'REFUND' in (e.description or '').upper()]
if refunds:
    refund_total = sum(e.amount for e in refunds)
    print(f"\n⚠️  REFUNDS (Should be income/credits, not expenses):")
    print(f"   Count: {len(refunds)} | Total: £{refund_total:,.2f}")

# 5. Largest expense categories
print(f"\n📊 TOP 10 EXPENSE CATEGORIES:")
expense_by_category = Counter(e.category for e in all_expenses)
for category, count in expense_by_category.most_common(10):
    total = sum(e.amount for e in all_expenses if e.category == category)
    print(f"   {category:35} {count:3} txns | £{total:,.2f}")

print()

# Analyze income
print("=" * 80)
print("💰 INCOME ANALYSIS:")
print("-" * 80)

# Income by type
income_by_type = Counter(i.income_type for i in all_income)
for income_type, count in income_by_type.most_common():
    total = sum(i.amount_gross for i in all_income if i.income_type == income_type)
    print(f"   {income_type:35} {count:3} txns | £{total:,.2f}")

print()

# Check for missing self-employment income
self_emp_income = [i for i in all_income if 'SELF' in i.income_type.upper() or 'ROAD CENTRE' in i.source.upper()]
print(f"📋 SELF-EMPLOYMENT INCOME:")
print(f"   Count: {len(self_emp_income)} | Total: £{sum(i.amount_gross for i in self_emp_income):,.2f}")

if len(self_emp_income) < 20:
    print(f"   Recent entries:")
    for i in self_emp_income[:10]:
        print(f"      {i.date} | £{i.amount_gross:>8,.2f} | {i.source[:50]}")

print()
print("=" * 80)

# Calculate impact of fixing issues
print("💡 POTENTIAL CORRECTIONS:")
print("-" * 80)

issues_total = 0
if swan_transfers:
    print(f"   Remove internal transfers:      -£{swan_total:,.2f}")
    issues_total += swan_total
if roundup_expenses:
    print(f"   Remove round-up savings:        -£{roundup_total:,.2f}")
    issues_total += roundup_total
if potential_personal:
    print(f"   Review personal expenses:       -£{personal_total:,.2f} (may be legitimate)")
if refunds:
    print(f"   Move refunds to income:         -£{refund_total:,.2f}")
    issues_total += refund_total

if issues_total > 0:
    current_net = sum(i.amount_gross for i in all_income) - sum(e.amount for e in all_expenses)
    adjusted_net = sum(i.amount_gross for i in all_income) - (sum(e.amount for e in all_expenses) - issues_total)
    print()
    print(f"   Current Net:    £{current_net:,.2f}")
    print(f"   Adjusted Net:   £{adjusted_net:,.2f} (after removing obvious issues)")
else:
    print("   ✅ No obvious issues found!")

print()
print("=" * 80)

session.close()
