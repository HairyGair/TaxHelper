# Batch Receipt Upload Workflows

Visual guide to the three main workflows supported by the batch upload system.

## Overview

The system supports three distinct workflows to handle different use cases:

1. **Workflow A**: Create New Expenses
2. **Workflow B**: Link to Transactions
3. **Workflow C**: Hybrid (Auto-match + Create)

---

## Workflow A: Create New Expenses

**Use Case**: You have receipts but no corresponding bank transactions (e.g., cash purchases, manual expense tracking)

```
┌─────────────────────────────────────────────────────────────┐
│                    WORKFLOW A: CREATE NEW EXPENSES           │
└─────────────────────────────────────────────────────────────┘

Step 1: Upload Receipts
┌──────────────────────┐
│  📤 Upload           │
│  - receipt1.jpg      │
│  - receipt2.jpg      │
│  - receipt3.jpg      │
└──────────────────────┘
          ↓
Step 2: OCR Processing
┌──────────────────────┐
│  🔍 Extract Data     │
│  ✓ Merchant          │
│  ✓ Date              │
│  ✓ Amount            │
│  ✓ Confidence        │
└──────────────────────┘
          ↓
Step 3: Review Results
┌──────────────────────┐
│  📊 Review           │
│  - High confidence   │
│  - Needs review      │
│  - Failed            │
└──────────────────────┘
          ↓
Step 4: Accept Items
┌──────────────────────┐
│  ✅ Accept           │
│  - All high conf     │
│  - Selected items    │
│  - Edit if needed    │
└──────────────────────┘
          ↓
Step 5: Create Expenses
┌──────────────────────┐
│  💾 Save to DB       │
│  ✓ Expense records   │
│  ✓ Receipt files     │
│  ✓ Audit trail       │
└──────────────────────┘

Result: New expense records created in database
```

### Code Example

```python
from components.batch_receipt_upload import (
    main_batch_upload_interface,
    batch_create_expenses
)

# Step 1-4: Upload and review
main_batch_upload_interface(
    session=db_session,
    transactions=None  # No matching
)

# Step 5: Create expenses
results = st.session_state.batch_upload_results
count = batch_create_expenses(db_session, results)
st.success(f"Created {count} new expense records")
```

### When to Use

- ✅ Cash purchases
- ✅ Manual expense tracking
- ✅ No bank integration
- ✅ Historical receipts
- ✅ Petty cash

---

## Workflow B: Link to Transactions

**Use Case**: You have bank transactions and want to match receipts to them

```
┌─────────────────────────────────────────────────────────────┐
│                 WORKFLOW B: LINK TO TRANSACTIONS             │
└─────────────────────────────────────────────────────────────┘

Step 1: Load Transactions
┌──────────────────────┐
│  📊 Query DB         │
│  - Unreviewed only   │
│  - Recent            │
│  - Needs receipts    │
└──────────────────────┘
          ↓
Step 2: Upload Receipts
┌──────────────────────┐
│  📤 Upload           │
│  - receipt1.jpg      │
│  - receipt2.jpg      │
│  - receipt3.jpg      │
└──────────────────────┘
          ↓
Step 3: OCR Processing
┌──────────────────────┐
│  🔍 Extract Data     │
│  ✓ Merchant          │
│  ✓ Date              │
│  ✓ Amount            │
└──────────────────────┘
          ↓
Step 4: Smart Matching
┌──────────────────────┐
│  🔗 Match Algorithm  │
│  - Date ±3 days      │
│  - Amount ±£0.10     │
│  - Fuzzy merchant    │
│  - Score 0-100%      │
└──────────────────────┘
          ↓
Step 5: Review Matches
┌──────────────────────────────────────┐
│  📊 Review Matches                    │
│  ✅ receipt1.jpg → Trans #123 (95%)  │
│  ⚠️ receipt2.jpg → Trans #124 (65%)  │
│  ❌ receipt3.jpg → No match (0%)     │
└──────────────────────────────────────┘
          ↓
Step 6: Accept & Link
┌──────────────────────┐
│  🔗 Link             │
│  ✓ Update trans      │
│  ✓ Attach receipt    │
│  ✓ Mark reviewed     │
└──────────────────────┘

Result: Receipts linked to existing transactions
```

### Code Example

```python
from components.batch_receipt_upload import (
    main_batch_upload_interface,
    smart_match_receipts_to_transactions,
    batch_link_to_transactions
)

# Step 1: Get transactions
transactions = db_session.query(Transaction).filter(
    Transaction.reviewed == False
).all()

# Step 2-5: Upload, process, and match
main_batch_upload_interface(
    session=db_session,
    transactions=transactions
)

# Step 6: Link high-confidence matches
results = st.session_state.batch_upload_results
count = batch_link_to_transactions(db_session, results, transactions)
st.success(f"Linked {count} receipts to transactions")
```

### Matching Example

```
Receipt Data:                Transaction Data:
┌─────────────────┐         ┌─────────────────────┐
│ TESCO           │    ←→   │ TESCO STORES 2847   │
│ 17/10/2024      │    ←→   │ 17/10/2024          │
│ £45.99          │    ←→   │ -£45.99             │
└─────────────────┘         └─────────────────────┘

Match Score: 95%
Reason: exact date + exact amount + merchant match
Action: Auto-link
```

### When to Use

- ✅ Bank imports available
- ✅ Want to link receipts to transactions
- ✅ Need audit trail
- ✅ Automated reconciliation
- ✅ Tax compliance

---

## Workflow C: Hybrid (Auto-match + Create)

**Use Case**: Mixed batch - some receipts match transactions, others don't

```
┌─────────────────────────────────────────────────────────────┐
│                WORKFLOW C: HYBRID (AUTO-MATCH + CREATE)      │
└─────────────────────────────────────────────────────────────┘

Step 1: Upload Receipts
┌──────────────────────┐
│  📤 Upload           │
│  - receipt1.jpg      │  (will match)
│  - receipt2.jpg      │  (will match)
│  - receipt3.jpg      │  (no match - create)
│  - receipt4.jpg      │  (no match - create)
└──────────────────────┘
          ↓
Step 2: OCR Processing
┌──────────────────────┐
│  🔍 Extract Data     │
│  ✓ All receipts      │
└──────────────────────┘
          ↓
Step 3: Smart Matching
┌─────────────────────────────────────┐
│  🔗 Try to Match All                │
│  ✓ receipt1 → Trans #123 (95%)     │
│  ✓ receipt2 → Trans #124 (88%)     │
│  ⚠️ receipt3 → No match (0%)        │
│  ⚠️ receipt4 → No match (0%)        │
└─────────────────────────────────────┘
          ↓
Step 4: Decision Tree
┌─────────────────────────────────────┐
│  📊 For Each Receipt:               │
│                                      │
│  IF match confidence > 80%:         │
│     → Link to transaction           │
│                                      │
│  ELSE IF match confidence 60-80%:   │
│     → Flag for manual review        │
│                                      │
│  ELSE (no match):                   │
│     → Create new expense            │
└─────────────────────────────────────┘
          ↓
Step 5: Parallel Processing
┌────────────────────┐    ┌────────────────────┐
│  🔗 Link Matches   │    │  💾 Create New     │
│  receipt1 → #123   │    │  receipt3 → Exp #1 │
│  receipt2 → #124   │    │  receipt4 → Exp #2 │
└────────────────────┘    └────────────────────┘
          ↓                        ↓
Step 6: Review Low Confidence
┌─────────────────────────────────────┐
│  ⚠️ Manual Review Queue             │
│  - Low confidence matches           │
│  - Ambiguous data                   │
│  - Edit and accept/reject           │
└─────────────────────────────────────┘

Result: Optimal mix of automated linking and new expense creation
```

### Code Example

```python
from components.batch_receipt_upload import (
    main_batch_upload_interface,
    smart_match_receipts_to_transactions,
    batch_link_to_transactions,
    batch_create_expenses
)

# Get all transactions (recent)
transactions = get_recent_transactions(days=30)

# Upload and process
main_batch_upload_interface(
    session=db_session,
    transactions=transactions
)

# Hybrid processing
results = st.session_state.batch_upload_results

matched_count = 0
created_count = 0
review_count = 0

for result in results:
    if result['status'] == 'success':
        # Try to match
        match = smart_match_receipts_to_transactions(
            db_session, result['data'], transactions
        )

        if match['matched'] and match['confidence'] >= 80:
            # High confidence - auto link
            link_receipt_to_transaction(result, match)
            matched_count += 1

        elif match['matched'] and match['confidence'] >= 60:
            # Medium confidence - flag for review
            flag_for_review(result, match)
            review_count += 1

        else:
            # No match - create expense
            create_expense_from_receipt(db_session, result)
            created_count += 1

st.success(f"""
Processed {len(results)} receipts:
- Matched: {matched_count}
- Created: {created_count}
- Review: {review_count}
""")
```

### Decision Matrix

```
Confidence Score    Action                Example
─────────────────────────────────────────────────────
90-100%            Auto-link              Exact match all fields
80-89%             Auto-link              Close match, very likely
70-79%             Auto-link (optional)   Good match, probably correct
60-69%             Manual review          Moderate match, needs check
50-59%             Manual review          Weak match, likely wrong
<50%               Create new expense     No match found
```

### When to Use

- ✅ Mixed batch of receipts
- ✅ Want maximum automation
- ✅ Some transactions imported, some not
- ✅ Balance speed vs accuracy
- ✅ Regular use (ongoing reconciliation)

---

## Comparison Table

| Feature | Workflow A | Workflow B | Workflow C |
|---------|-----------|-----------|-----------|
| **Needs Transactions** | No | Yes | Yes |
| **Creates Expenses** | Yes | No | Yes (unmatched) |
| **Links to Transactions** | No | Yes | Yes (matched) |
| **Automation Level** | Medium | High | Very High |
| **Manual Review** | Moderate | Low | Minimal |
| **Best For** | Cash expenses | Bank reconciliation | Mixed batches |
| **Processing Time** | Fast | Medium | Medium |
| **Accuracy Required** | Medium | High | High |

---

## Advanced Workflow: Multi-Stage Processing

For complex scenarios, combine workflows:

```
┌─────────────────────────────────────────────────────────────┐
│              ADVANCED: MULTI-STAGE WORKFLOW                  │
└─────────────────────────────────────────────────────────────┘

Stage 1: Import & Categorize
┌─────────────────────┐
│  📊 Analyze Batch   │
│  - Scan all files   │
│  - Pre-categorize   │
│  - Group similar    │
└─────────────────────┘
          ↓
Stage 2: Process by Category
┌───────────────────────────────────────────┐
│  📤 Split Processing                      │
│  ┌─────────────┐  ┌─────────────┐        │
│  │ Likely      │  │ Likely      │        │
│  │ Matches     │  │ New Expense │        │
│  │ (10 files)  │  │ (5 files)   │        │
│  └─────────────┘  └─────────────┘        │
└───────────────────────────────────────────┘
          ↓                    ↓
Stage 3: Parallel Processing
┌─────────────────┐  ┌─────────────────┐
│  Workflow B     │  │  Workflow A     │
│  (Match)        │  │  (Create)       │
└─────────────────┘  └─────────────────┘
          ↓                    ↓
Stage 4: Merge Results
┌─────────────────────────────────────┐
│  📊 Combined Results                │
│  ✓ 10 receipts linked               │
│  ✓ 5 expenses created               │
│  ⚠️ 2 need manual review            │
└─────────────────────────────────────┘
```

---

## Workflow Selection Guide

### Choose Workflow A if:
- You don't have bank transaction data
- You're tracking cash expenses
- You want simple expense creation
- You don't need reconciliation

### Choose Workflow B if:
- You have bank transactions to match
- You want automated reconciliation
- You need audit trail
- Accuracy is critical

### Choose Workflow C if:
- You have mixed receipt types
- You want maximum automation
- You can review exceptions
- This is regular/ongoing work

---

## Tips for Each Workflow

### Workflow A Tips
1. **Pre-categorize** receipts before upload
2. **Batch similar** items together
3. **Use consistent** merchant names
4. **Review carefully** - no auto-validation

### Workflow B Tips
1. **Import transactions first** - fresh data
2. **Use recent window** - last 30 days
3. **Clean merchant names** - better matching
4. **Review low scores** - verify matches

### Workflow C Tips
1. **Adjust thresholds** based on accuracy needs
2. **Monitor stats** - track auto-match success
3. **Review patterns** - improve over time
4. **Use regularly** - builds confidence

---

## Performance Comparison

| Metric | Workflow A | Workflow B | Workflow C |
|--------|-----------|-----------|-----------|
| Processing Speed | ⚡⚡⚡ Fast | ⚡⚡ Medium | ⚡⚡ Medium |
| Accuracy | ⭐⭐⭐ Good | ⭐⭐⭐⭐ High | ⭐⭐⭐⭐ High |
| Automation | 🤖 Manual | 🤖🤖 Semi-auto | 🤖🤖🤖 Auto |
| Complexity | Simple | Medium | Complex |
| Time Saved | ⏱️ Medium | ⏱️⏱️ High | ⏱️⏱️⏱️ Very High |

---

**More Info**:
- Full documentation: `BATCH_UPLOAD_README.md`
- Quick start: `BATCH_UPLOAD_QUICK_START.md`
- Demo: `streamlit run components/batch_upload_demo.py`
