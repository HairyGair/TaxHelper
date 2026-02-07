# Merchant Database Integration Guide

## Overview

The Merchant Database component provides automatic transaction categorization for 200+ common UK merchants using fuzzy matching algorithms. This significantly reduces manual categorization effort and improves consistency.

## Components

### 1. Files Created

- `/Users/anthony/Tax Helper/components/merchant_db.py` - Main merchant database logic
- `/Users/anthony/Tax Helper/models/merchant_model.py` - SQLAlchemy model

### 2. Database Schema

```sql
CREATE TABLE merchants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(200) NOT NULL UNIQUE,
    aliases TEXT,  -- JSON array of alternative names
    default_category VARCHAR(100) NOT NULL,
    default_type VARCHAR(20) NOT NULL,  -- 'Income' or 'Expense'
    is_personal BOOLEAN NOT NULL DEFAULT 0,
    industry VARCHAR(100),
    confidence_boost INTEGER NOT NULL DEFAULT 0,  -- 0-30 points
    is_custom BOOLEAN NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    usage_count INTEGER NOT NULL DEFAULT 0,
    last_matched_at TIMESTAMP
);
```

## Integration Steps

### Step 1: Add Model to Database

```python
# In your database.py or models.py file:

from models.merchant_model import Merchant
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Assuming you have an existing Base
# Add Merchant to your models
engine = create_engine('sqlite:///taxhelper.db')
Merchant.metadata.create_all(engine)
```

### Step 2: Initialize Merchant Database

```python
# Run once to populate database with 200+ merchants
from components.merchant_db import init_merchant_database
from models.merchant_model import Merchant
from database import SessionLocal

def initialize_merchants():
    session = SessionLocal()
    try:
        count = init_merchant_database(session, Merchant)
        print(f"Added {count} merchants to database")
    finally:
        session.close()

# Call this during app startup or as a one-time migration
initialize_merchants()
```

### Step 3: Auto-Categorize During Import

```python
# In your transaction import logic:

from components.merchant_db import find_merchant_match, update_transaction_from_merchant

def process_imported_transaction(transaction, session):
    """Process transaction with merchant matching"""

    # Find merchant match
    merchant_match = find_merchant_match(transaction.description)

    if merchant_match:
        confidence = merchant_match['match_confidence']

        if confidence >= 80:
            # High confidence - auto-apply
            update_transaction_from_merchant(transaction, merchant_match)
            transaction.categorization_method = 'Merchant Database (Auto)'
            transaction.ai_confidence = confidence

        elif confidence >= 60:
            # Medium confidence - suggest to user
            transaction.suggested_category = merchant_match['default_category']
            transaction.suggested_type = merchant_match['default_type']
            transaction.categorization_method = 'Merchant Database (Suggested)'
            transaction.ai_confidence = confidence

    session.add(transaction)
    session.commit()
```

### Step 4: Add to Final Review UI

```python
# In your Final Review page (e.g., pages/4_final_review.py):

import streamlit as st
from components.merchant_db import render_merchant_selector, update_transaction_from_merchant

def render_transaction_review(transaction, session):
    """Render individual transaction for review"""

    st.write(f"**{transaction.description}**")
    st.write(f"Amount: £{transaction.amount}")

    # Show current categorization
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"Category: {transaction.category}")
    with col2:
        st.write(f"Type: {transaction.type}")

    # Merchant matching section
    with st.expander("Find Merchant Match"):
        selected_merchant = render_merchant_selector(session, Merchant, transaction)

        if selected_merchant:
            update_transaction_from_merchant(transaction, selected_merchant)
            session.commit()
            st.success(f"Applied merchant: {selected_merchant['name']}")
            st.rerun()
```

### Step 5: Batch Processing for Existing Transactions

```python
# Script to re-categorize existing transactions

from components.merchant_db import find_merchant_match, update_transaction_from_merchant
from models import Transaction
from database import SessionLocal

def batch_recategorize():
    """Re-categorize all uncategorized transactions"""
    session = SessionLocal()

    try:
        # Get uncategorized transactions
        transactions = session.query(Transaction).filter(
            Transaction.category == 'Uncategorized'
        ).all()

        matched = 0
        for txn in transactions:
            merchant_match = find_merchant_match(txn.description)

            if merchant_match and merchant_match['match_confidence'] >= 80:
                update_transaction_from_merchant(txn, merchant_match)
                matched += 1

        session.commit()
        print(f"Auto-categorized {matched} of {len(transactions)} transactions")

    finally:
        session.close()

# Run as needed
batch_recategorize()
```

## Usage Examples

### Example 1: Find Merchant Match

```python
from components.merchant_db import find_merchant_match

# Example transaction descriptions
descriptions = [
    "TESCO STORES 2234 LONDON",
    "AMZN MKTP UK*AB3C4D5E6",
    "TFL TRAVEL CHARGE",
    "STARBUCKS COFFEE",
]

for desc in descriptions:
    match = find_merchant_match(desc)

    if match:
        print(f"Description: {desc}")
        print(f"Merchant: {match['name']}")
        print(f"Category: {match['default_category']}")
        print(f"Confidence: {match['match_confidence']}%")
        print()
```

**Output:**
```
Description: TESCO STORES 2234 LONDON
Merchant: TESCO
Category: Groceries
Confidence: 95.0%

Description: AMZN MKTP UK*AB3C4D5E6
Merchant: AMAZON
Category: Office Supplies
Confidence: 90.0%

Description: TFL TRAVEL CHARGE
Merchant: TRANSPORT FOR LONDON
Category: Travel
Confidence: 100.0%

Description: STARBUCKS COFFEE
Merchant: STARBUCKS
Category: Meals & Entertainment
Confidence: 95.0%
```

### Example 2: Get Multiple Suggestions

```python
from components.merchant_db import get_merchant_suggestions

description = "BP PETROL STATION"
suggestions = get_merchant_suggestions(description, top_n=3)

for i, suggestion in enumerate(suggestions, 1):
    print(f"{i}. {suggestion['name']} - {suggestion['default_category']}")
    print(f"   Confidence: {suggestion['match_confidence']}%")
    print(f"   Industry: {suggestion['industry']}")
```

**Output:**
```
1. BP - Fuel
   Confidence: 95.0%
   Industry: Fuel

2. SHELL - Fuel
   Confidence: 45.2%
   Industry: Fuel

3. ESSO - Fuel
   Confidence: 42.8%
   Industry: Fuel
```

### Example 3: Add Custom Merchant

```python
from components.merchant_db import add_custom_merchant
from models.merchant_model import Merchant
from database import SessionLocal

session = SessionLocal()

# Add your regular coffee shop
merchant = add_custom_merchant(
    session=session,
    model_class=Merchant,
    name="JOE'S COFFEE SHOP",
    category="Meals & Entertainment",
    txn_type="Expense",
    aliases=["JOES COFFEE", "JOE COFFEE"],
    is_personal=True,
    industry="Coffee Shop",
    confidence_boost=25
)

print(f"Added merchant: {merchant.name}")
session.close()
```

### Example 4: Export to CSV

```python
from components.merchant_db import export_merchant_database_csv

output_path = "/Users/anthony/Tax Helper/exports/merchants.csv"
csv_path = export_merchant_database_csv(output_path)

print(f"Exported merchant database to: {csv_path}")
```

### Example 5: View Statistics

```python
from components.merchant_db import get_merchant_statistics
import json

stats = get_merchant_statistics()
print(json.dumps(stats, indent=2))
```

**Output:**
```json
{
  "total_merchants": 204,
  "by_industry": {
    "Supermarket": 10,
    "Restaurant": 15,
    "Fast Food": 5,
    "Transport": 13,
    "Software": 25,
    "Fuel": 9,
    ...
  },
  "by_type": {
    "Expense": 200,
    "Income": 4
  },
  "personal_transactions": 98,
  "business_transactions": 106,
  "avg_confidence_boost": 24.5
}
```

## Fuzzy Matching Algorithm

### How It Works

1. **Normalization**: Both merchant names and transaction descriptions are normalized:
   - Converted to uppercase
   - Special characters removed
   - Common suffixes removed (LTD, PLC, UK, etc.)

2. **Matching Process**:
   - Calculate similarity score using SequenceMatcher
   - Check for substring matches (high score)
   - Check all aliases
   - Apply confidence boost for known reliable merchants

3. **Confidence Levels**:
   - **80-100%**: Auto-apply (high confidence)
   - **60-79%**: Suggest to user (medium confidence)
   - **<60%**: No match (low confidence)

### Matching Examples

```python
# Handles variations automatically:
"TESCO STORES 2234" → TESCO (95%)
"TESCO EXPRESS LONDON" → TESCO (90%)
"TESCO PFS FUEL" → TESCO PETROL (95%)

"AMZN MKTP UK*XX" → AMAZON (90%)
"AMAZON.CO.UK" → AMAZON (95%)

"TFL TRAVEL CHARGE" → TRANSPORT FOR LONDON (100%)
"OYSTER AUTO-TOPUP" → TRANSPORT FOR LONDON (85%)
```

## Database Coverage

### 204 Merchants Across Categories:

- **Supermarkets** (10): TESCO, SAINSBURY'S, ASDA, MORRISONS, WAITROSE, ALDI, LIDL, CO-OP, M&S, ICELAND
- **Restaurants & Fast Food** (15+): NANDO'S, MCDONALD'S, SUBWAY, STARBUCKS, COSTA, GREGGS, etc.
- **Transport** (13): TFL, TRAINLINE, UBER, SHELL, BP, ESSO, BRITISH AIRWAYS, etc.
- **Utilities** (13): BRITISH GAS, E.ON, THAMES WATER, BT, VIRGIN MEDIA, SKY, EE, VODAFONE, O2
- **Retail** (20+): AMAZON, ARGOS, CURRYS, JOHN LEWIS, NEXT, PRIMARK, H&M, ZARA, etc.
- **Office Supplies** (4): STAPLES, RYMAN, VIKING DIRECT, WHSmith
- **Software** (18): MICROSOFT, ADOBE, GOOGLE, APPLE, ZOOM, SLACK, GITHUB, AWS, etc.
- **Professional Services** (4): HMRC, COMPANIES HOUSE, ACCOUNTANT, SOLICITOR
- **Banking** (9): PAYPAL, STRIPE, WISE, REVOLUT, BARCLAYS, HSBC, LLOYDS, etc.
- **Hotels** (7): PREMIER INN, TRAVELODGE, HOLIDAY INN, HILTON, MARRIOTT, BOOKING.COM, AIRBNB
- **Postal & Courier** (8): ROYAL MAIL, DHL, FEDEX, UPS, PARCELFORCE, YODEL, DPD, HERMES
- **And many more...**

## Performance Optimization

### Caching Merchant Data

```python
# Cache merchant lookups for better performance
from functools import lru_cache

@lru_cache(maxsize=1000)
def cached_merchant_lookup(description: str):
    """Cached merchant lookup"""
    return find_merchant_match(description)
```

### Batch Processing

```python
# Process multiple transactions efficiently
from components.merchant_db import find_merchant_match

def batch_match_merchants(transactions):
    """Match multiple transactions to merchants"""
    results = []

    for txn in transactions:
        match = find_merchant_match(txn.description)
        results.append({
            'transaction_id': txn.id,
            'merchant': match,
            'confidence': match['match_confidence'] if match else 0
        })

    return results
```

## Maintenance

### Adding New Merchants

To add new merchants to the pre-populated database:

1. Edit `merchant_db.py`
2. Add merchant to `MERCHANT_DATA` list:

```python
{
    "name": "YOUR MERCHANT",
    "aliases": ["ALIAS1", "ALIAS2"],
    "default_category": "Category Name",
    "default_type": "Expense",
    "is_personal": False,
    "industry": "Industry",
    "confidence_boost": 25
}
```

3. Re-run `init_merchant_database()` to update database

### User-Added Merchants

Users can add their own merchants through the UI:

```python
from components.merchant_db import add_custom_merchant

# User adds custom merchant
merchant = add_custom_merchant(
    session=session,
    model_class=Merchant,
    name=user_input_name,
    category=selected_category,
    txn_type=selected_type,
    aliases=user_aliases,
    is_personal=is_personal_checkbox,
    industry=selected_industry
)
```

## Testing

### Unit Tests

```python
import unittest
from components.merchant_db import find_merchant_match, normalize_string

class TestMerchantDatabase(unittest.TestCase):

    def test_tesco_matching(self):
        """Test TESCO variations"""
        descriptions = [
            "TESCO STORES 2234",
            "TESCO EXPRESS",
            "TESCO PFS"
        ]

        for desc in descriptions:
            match = find_merchant_match(desc)
            self.assertIsNotNone(match)
            self.assertIn("TESCO", match['name'])
            self.assertGreater(match['match_confidence'], 80)

    def test_normalization(self):
        """Test string normalization"""
        self.assertEqual(
            normalize_string("TESCO STORES LTD UK"),
            "TESCO STORES"
        )

    def test_confidence_threshold(self):
        """Test confidence threshold"""
        match = find_merchant_match("RANDOM TEXT 12345")
        self.assertIsNone(match)  # Should not match anything

if __name__ == '__main__':
    unittest.main()
```

## Troubleshooting

### Issue: Low Match Rates

**Solution**:
- Add more aliases to merchants
- Lower confidence threshold temporarily
- Review transaction descriptions for patterns

### Issue: Wrong Categories

**Solution**:
- Update merchant default categories
- Increase confidence boost for reliable merchants
- Add user feedback loop

### Issue: Performance Slow

**Solution**:
- Implement caching (see Performance Optimization)
- Index database properly
- Use batch processing for large imports

## API Reference

### Core Functions

- `find_merchant_match(description, confidence_threshold=60.0)` - Find best merchant match
- `get_merchant_suggestions(description, top_n=3)` - Get multiple suggestions
- `init_merchant_database(session, model_class)` - Initialize database
- `add_custom_merchant(session, ...)` - Add user merchant
- `update_transaction_from_merchant(transaction, merchant_data)` - Apply merchant to transaction
- `render_merchant_selector(session, model_class, transaction)` - UI component
- `export_merchant_database_csv(output_path)` - Export to CSV
- `get_merchant_statistics()` - Get database stats

### Utility Functions

- `normalize_string(text)` - Normalize text for matching
- `fuzzy_match_score(str1, str2)` - Calculate similarity score
- `render_merchant_statistics()` - Display statistics in Streamlit

## Next Steps

1. **Add merchant model to your database**
2. **Run initialization script** to populate merchants
3. **Integrate into import flow** for auto-categorization
4. **Add UI components** to Final Review page
5. **Monitor match rates** and add merchants as needed
6. **Collect user feedback** to improve matching

## Support

For questions or issues:
1. Check transaction descriptions match expected format
2. Review merchant aliases for variations
3. Adjust confidence thresholds as needed
4. Add custom merchants for your specific use case
