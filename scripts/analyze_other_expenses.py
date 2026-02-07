#!/usr/bin/env python3
"""
Analyze "Other business expenses" category in detail
"""

import sys
sys.path.insert(0, '/Users/anthony/Tax Helper')

from models import init_db, Expense
from collections import Counter
import re

print("=" * 80)
print("ANALYZING 'OTHER BUSINESS EXPENSES' CATEGORY")
print("=" * 80)
print()

# Initialize database
engine, SessionLocal = init_db()
session = SessionLocal()

# Get all "Other business expenses"
other_expenses = session.query(Expense).filter(
    Expense.category == 'Other business expenses'
).order_by(Expense.date.desc()).all()

if not other_expenses:
    print("No expenses in 'Other business expenses' category")
    session.close()
    sys.exit(0)

print(f"Found {len(other_expenses)} transactions in 'Other business expenses'")
print(f"Total amount: £{sum(e.amount for e in other_expenses):,.2f}")
print()

# Categorize by supplier patterns
supplier_patterns = {}

for expense in other_expenses:
    supplier = expense.supplier.upper()

    # Extract key words from supplier name
    # Remove common payment method prefixes
    cleaned = re.sub(r'(VIA MOBILE|MOBILE BANKING|FASTER PAYMENT|FP \d+/\d+/\d+|DD|SO|,|\s+\d+)', '', supplier)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()

    # Get first few meaningful words
    words = cleaned.split()
    if len(words) >= 2:
        key = ' '.join(words[:2])
    elif len(words) == 1:
        key = words[0]
    else:
        key = 'UNKNOWN'

    if key not in supplier_patterns:
        supplier_patterns[key] = []
    supplier_patterns[key].append(expense)

# Sort by total amount
pattern_totals = {key: sum(e.amount for e in expenses) for key, expenses in supplier_patterns.items()}
sorted_patterns = sorted(pattern_totals.items(), key=lambda x: x[1], reverse=True)

print("📊 TOP 30 MERCHANT PATTERNS IN 'OTHER BUSINESS EXPENSES':")
print("-" * 80)
print(f"{'Merchant Pattern':<40} {'Count':>6} {'Total':>12}")
print("-" * 80)

for pattern, total in sorted_patterns[:30]:
    count = len(supplier_patterns[pattern])
    print(f"{pattern[:39]:<40} {count:>6} £{total:>10,.2f}")

print()

# Identify likely personal expenses
personal_keywords = [
    'TESCO', 'SAINSBURY', 'ASDA', 'MORRISONS', 'LIDL', 'ALDI', 'WAITROSE', 'MARKS',
    'COSTA', 'STARBUCKS', 'GREGGS', 'MCDONALD', 'KFC', 'SUBWAY', 'PIZZA',
    'NETFLIX', 'SPOTIFY', 'AMAZON PRIME', 'SKY', 'VIRGIN',
    'GYM', 'FITNESS', 'SPORT',
    'CLOTHING', 'FASHION', 'SHOES',
    'PHARMACY', 'BOOTS', 'SUPERDRUG',
    'CINEMA', 'THEATRE', 'ENTERTAINMENT'
]

likely_personal = []
for expense in other_expenses:
    supplier_upper = expense.supplier.upper()
    if any(keyword in supplier_upper for keyword in personal_keywords):
        likely_personal.append(expense)

if likely_personal:
    personal_total = sum(e.amount for e in likely_personal)
    print("⚠️  LIKELY PERSONAL EXPENSES:")
    print("-" * 80)
    print(f"Count: {len(likely_personal)} | Total: £{personal_total:,.2f}")
    print()

    # Group by keyword
    keyword_groups = {}
    for expense in likely_personal:
        supplier_upper = expense.supplier.upper()
        matched_keyword = None
        for keyword in personal_keywords:
            if keyword in supplier_upper:
                matched_keyword = keyword
                break

        if matched_keyword not in keyword_groups:
            keyword_groups[matched_keyword] = []
        keyword_groups[matched_keyword].append(expense)

    print("Breakdown by type:")
    for keyword in sorted(keyword_groups.keys(), key=lambda k: sum(e.amount for e in keyword_groups[k]), reverse=True):
        group = keyword_groups[keyword]
        group_total = sum(e.amount for e in group)
        print(f"  {keyword:<20} {len(group):>4} txns | £{group_total:>8,.2f}")
    print()

# Look for round-ups (should be savings, not expenses)
roundups = [e for e in other_expenses if 'ROUND UP' in e.supplier.upper() or e.amount < 1.0]
if roundups:
    roundup_total = sum(e.amount for e in roundups)
    print("⚠️  ROUND-UP TRANSACTIONS:")
    print(f"   Count: {len(roundups)} | Total: £{roundup_total:,.2f}")
    print()

# Look for small frequent transactions (coffee, snacks, etc)
small_frequent = [e for e in other_expenses if e.amount < 10.0]
if small_frequent:
    small_total = sum(e.amount for e in small_frequent)
    print("💰 SMALL TRANSACTIONS (<£10):")
    print(f"   Count: {len(small_frequent)} | Total: £{small_total:,.2f}")

    # Sample some
    print("   Examples:")
    for e in small_frequent[:10]:
        print(f"      {e.date} | £{e.amount:>6,.2f} | {e.supplier[:55]}")
    print()

# Large transactions (might be legitimate business expenses)
large_expenses = [e for e in other_expenses if e.amount >= 100.0]
if large_expenses:
    large_total = sum(e.amount for e in large_expenses)
    print("💼 LARGE TRANSACTIONS (≥£100):")
    print(f"   Count: {len(large_expenses)} | Total: £{large_total:,.2f}")
    print("   Examples:")
    for e in sorted(large_expenses, key=lambda x: x.amount, reverse=True)[:10]:
        print(f"      {e.date} | £{e.amount:>8,.2f} | {e.supplier[:50]}")
    print()

print("=" * 80)
print("💡 RECOMMENDATIONS:")
print("-" * 80)
print()
print("1. Review transactions marked as likely personal expenses")
print("2. Consider re-categorizing large transactions into specific categories")
print("3. Small frequent transactions (<£10) might be coffee/snacks - check if business related")
print("4. Round-up transactions should be removed (they're savings, not expenses)")
print()
print("Suggested workflow:")
print("  • Go to Streamlit app → Expenses page")
print("  • Filter by 'Other business expenses'")
print("  • Review and re-categorize or mark as personal")
print("  • Use the Edit function to change categories to more specific ones:")
print("    - Travel, Office costs, Marketing, Professional fees, etc.")

session.close()
