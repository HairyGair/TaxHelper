# Confidence Tooltips Integration Guide

Complete guide for integrating confidence tooltips into the Tax Helper application.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Integration Points](#integration-points)
3. [API Reference](#api-reference)
4. [Styling Customization](#styling-customization)
5. [Examples](#examples)
6. [Troubleshooting](#troubleshooting)

---

## Quick Start

### Installation

The confidence tooltips component is already included in your `components/` directory:

```python
from components.confidence_tooltips import (
    calculate_confidence_breakdown,
    render_confidence_tooltip,
    render_confidence_with_breakdown,
    quick_render_badge,
    quick_render_compact
)
```

### Basic Usage

**Simplest approach (recommended):**

```python
from components.confidence_tooltips import quick_render_full

# In your transaction display:
quick_render_full(transaction, session)
```

This renders a confidence badge with an expandable breakdown card.

---

## Integration Points

### 1. Final Review Page

**Location:** `app.py` - Final Review section

**Before:**
```python
st.write(f"Confidence: {transaction.confidence_score}%")
```

**After:**
```python
from components.confidence_tooltips import render_confidence_with_breakdown

render_confidence_with_breakdown(transaction, session, key_prefix=f"review_{transaction.id}")
```

**Full Integration Example:**

```python
# In your Final Review page loop
for idx, transaction in enumerate(filtered_transactions):
    with st.container():
        # Transaction header
        col1, col2, col3, col4 = st.columns([2, 3, 2, 2])

        with col1:
            st.write(transaction.date.strftime('%d/%m/%Y'))

        with col2:
            st.write(transaction.description[:50])

        with col3:
            amount = transaction.paid_in if transaction.paid_in > 0 else transaction.paid_out
            st.write(f"£{amount:,.2f}")

        with col4:
            # NEW: Add confidence badge with breakdown
            from components.confidence_tooltips import render_confidence_with_breakdown
            render_confidence_with_breakdown(
                transaction,
                session,
                key_prefix=f"final_review_{idx}"
            )
```

---

### 2. Transaction Detail View

**Location:** `app.py` - Individual transaction review

```python
# In transaction detail expander
with st.expander(f"Transaction #{transaction.id}", expanded=True):
    # ... existing transaction details ...

    # Add confidence breakdown
    st.markdown("### Confidence Analysis")
    from components.confidence_tooltips import (
        calculate_confidence_breakdown,
        render_confidence_breakdown_card
    )

    breakdown = calculate_confidence_breakdown(transaction, session)
    render_confidence_breakdown_card(breakdown)
```

---

### 3. Bulk Operations

**Location:** `components/bulk_operations.py`

```python
def apply_bulk_categorization(selected_transactions, session, category, txn_type):
    """Apply categorization to selected transactions"""

    # Before applying, show confidence stats
    from components.confidence_tooltips import render_bulk_confidence_stats

    st.subheader("📊 Confidence Overview")
    render_bulk_confidence_stats(selected_transactions, session)

    # Confirm action
    if st.button("Confirm Bulk Categorization"):
        # ... apply categorization ...
        pass
```

---

### 4. Smart Learning Modal

**Location:** `components/smart_learning.py` - `render_enhanced_modal()`

```python
def render_enhanced_modal(similar_info):
    """Render enhanced smart learning modal with confidence info"""

    # ... existing modal code ...

    # NEW: Show average confidence of similar transactions
    st.markdown("### Confidence Analysis")
    similar_txns = session.query(Transaction).filter(
        Transaction.id.in_(similar_info['txn_ids'])
    ).all()

    from components.confidence_tooltips import render_bulk_confidence_stats
    render_bulk_confidence_stats(similar_txns, session)
```

---

### 5. Transaction Table/List View

**For compact display in tables:**

```python
# In transaction list
for transaction in transactions:
    col1, col2, col3, col4 = st.columns([2, 3, 2, 1])

    with col1:
        st.write(transaction.date.strftime('%d/%m/%Y'))

    with col2:
        st.write(transaction.description[:40])

    with col3:
        amount = transaction.paid_in if transaction.paid_in > 0 else transaction.paid_out
        st.write(f"£{amount:,.2f}")

    with col4:
        # Compact confidence indicator
        from components.confidence_tooltips import quick_render_compact
        quick_render_compact(transaction.confidence_score)
```

---

### 6. Settings/Help Page

**Add a "How Confidence Works" section:**

```python
# In Settings or Help page
if st.button("ℹ️ How Does Confidence Scoring Work?"):
    from components.confidence_tooltips import render_help_modal
    render_help_modal()
```

---

## API Reference

### Functions

#### `calculate_confidence_breakdown(transaction, session) -> Dict`

Calculate detailed confidence breakdown for a transaction.

**Parameters:**
- `transaction` (Transaction): Transaction object from database
- `session` (Session): SQLAlchemy session

**Returns:**
```python
{
    'merchant_match': {
        'score': 35,
        'explanation': "Matched merchant 'TESCO' in database",
        'max': 40,
        'merchant_name': 'TESCO'
    },
    'rule_match': {
        'score': 25,
        'explanation': "Rule 'AMAZON → Office costs'",
        'max': 30,
        'rule_text': 'AMAZON'
    },
    'pattern_learning': {
        'score': 18,
        'explanation': "Very similar to 15 previous transactions",
        'max': 20,
        'similar_count': 15
    },
    'amount_consistency': {
        'score': 8,
        'explanation': "Amount typical for this merchant (±10%)",
        'max': 10
    },
    'total_score': 86,
    'explanation': "We're very confident this categorization is correct"
}
```

---

#### `render_confidence_tooltip(confidence_score, breakdown, show_badge=True)`

Render confidence tooltip with detailed breakdown.

**Parameters:**
- `confidence_score` (int): Overall confidence score (0-100)
- `breakdown` (Dict): Breakdown from `calculate_confidence_breakdown()`
- `show_badge` (bool): Whether to show confidence badge (default: True)

**Example:**
```python
breakdown = calculate_confidence_breakdown(transaction, session)
render_confidence_tooltip(transaction.confidence_score, breakdown)
```

---

#### `render_confidence_breakdown_card(breakdown)`

Render detailed confidence breakdown as a card.

**Parameters:**
- `breakdown` (Dict): Breakdown from `calculate_confidence_breakdown()`

**Example:**
```python
breakdown = calculate_confidence_breakdown(transaction, session)
render_confidence_breakdown_card(breakdown)
```

---

#### `render_confidence_with_breakdown(transaction, session, key_prefix="")`

**Recommended: All-in-one function** - Renders confidence badge with expandable breakdown.

**Parameters:**
- `transaction` (Transaction): Transaction object
- `session` (Session): SQLAlchemy session
- `key_prefix` (str): Unique prefix for widget keys (prevents conflicts)

**Example:**
```python
render_confidence_with_breakdown(transaction, session, key_prefix="txn_123")
```

---

#### `render_inline_confidence_indicator(confidence_score, compact=False)`

Render inline confidence badge.

**Parameters:**
- `confidence_score` (int): Confidence score (0-100)
- `compact` (bool): If True, show only emoji and score

**Example:**
```python
# Full badge
render_inline_confidence_indicator(85, compact=False)
# Output: 🟢 High 85%

# Compact badge
render_inline_confidence_indicator(85, compact=True)
# Output: 🟢 85%
```

---

#### `render_bulk_confidence_stats(transactions, session)`

Render confidence statistics for bulk operations.

**Parameters:**
- `transactions` (List[Transaction]): List of Transaction objects
- `session` (Session): SQLAlchemy session

**Example:**
```python
selected = session.query(Transaction).filter(Transaction.reviewed == False).all()
render_bulk_confidence_stats(selected, session)
```

---

#### `render_help_modal()`

Render help modal explaining the confidence scoring system.

**Example:**
```python
if st.button("Help: How Does Confidence Work?"):
    render_help_modal()
```

---

### Quick Access Functions

#### `quick_render_badge(score)`
Quick render confidence badge only.

```python
quick_render_badge(85)  # 🟢 High 85%
```

#### `quick_render_compact(score)`
Quick render compact confidence indicator.

```python
quick_render_compact(85)  # 🟢 85%
```

#### `quick_render_full(transaction, session)`
Quick render full confidence with breakdown.

```python
quick_render_full(transaction, session)
```

---

## Styling Customization

### Custom Colors

You can customize confidence level colors by modifying the `get_confidence_level()` function:

```python
def get_confidence_level(score: int) -> Dict:
    if score >= 70:
        return {
            'level': 'High',
            'color': '#28a745',  # Change this to your preferred green
            'emoji': '🟢',
            'description': "We're very confident this is correct"
        }
    # ... etc
```

### Custom CSS

All styling is embedded in the component. To customize:

1. Open `/Users/anthony/Tax Helper/components/confidence_tooltips.py`
2. Find the `<style>` blocks in each render function
3. Modify CSS classes as needed

**Key CSS Classes:**

- `.confidence-badge` - Main confidence badge
- `.confidence-breakdown-card` - Breakdown card container
- `.breakdown-factor` - Individual factor row
- `.progress-bar-fill` - Progress bar fill
- `.total-score` - Total score display

---

## Examples

### Example 1: Simple Badge

```python
from components.confidence_tooltips import quick_render_badge

quick_render_badge(85)
```

**Output:** 🟢 High 85%

---

### Example 2: Full Breakdown

```python
from components.confidence_tooltips import quick_render_full

transaction = session.query(Transaction).first()
quick_render_full(transaction, session)
```

**Output:** Badge with expandable breakdown showing all 4 factors.

---

### Example 3: Custom Integration

```python
from components.confidence_tooltips import (
    calculate_confidence_breakdown,
    get_confidence_level
)

# Calculate breakdown
breakdown = calculate_confidence_breakdown(transaction, session)

# Get level info
level_info = get_confidence_level(breakdown['total_score'])

# Custom display
st.markdown(f"""
**Confidence:** {level_info['emoji']} {breakdown['total_score']}%

- Merchant Match: +{breakdown['merchant_match']['score']} points
- Rule Match: +{breakdown['rule_match']['score']} points
- Pattern Learning: +{breakdown['pattern_learning']['score']} points
- Amount Consistency: +{breakdown['amount_consistency']['score']} points

**{breakdown['explanation']}**
""")
```

---

### Example 4: Conditional Display

```python
from components.confidence_tooltips import render_confidence_with_breakdown

# Only show confidence for unreviewed transactions
if not transaction.reviewed and transaction.confidence_score > 0:
    render_confidence_with_breakdown(transaction, session)
```

---

## Troubleshooting

### Issue: "No merchant match found"

**Cause:** Transaction description doesn't match merchant database.

**Solution:** Add merchant to `/Users/anthony/Tax Helper/scripts/merchant_database.py`

```python
SUPERMARKETS = {
    'YOUR_MERCHANT': MerchantCategory(
        'Your Merchant Name',
        True,  # is_personal
        'Groceries',  # category
        CONFIDENCE_CERTAIN,  # confidence level
        'Optional notes'
    )
}
```

---

### Issue: "No rule match found"

**Cause:** No categorization rule matches the transaction.

**Solution:** Create a new rule in the Rules section of the app.

---

### Issue: Tooltips not showing

**Cause:** CSS not loaded or JavaScript disabled.

**Solution:** Ensure `unsafe_allow_html=True` is set in all `st.markdown()` calls.

---

### Issue: Performance slow with many transactions

**Cause:** Calculating breakdown for every transaction is intensive.

**Solution:** Only calculate breakdown when expanded:

```python
with st.expander("See Confidence Breakdown"):
    breakdown = calculate_confidence_breakdown(transaction, session)
    render_confidence_breakdown_card(breakdown)
```

---

### Issue: KeyError when accessing breakdown

**Cause:** Breakdown calculation failed.

**Solution:** Add error handling:

```python
try:
    breakdown = calculate_confidence_breakdown(transaction, session)
    render_confidence_breakdown_card(breakdown)
except Exception as e:
    st.error(f"Could not calculate confidence: {e}")
```

---

## Best Practices

1. **Use `quick_render_compact()` in lists** - Saves space and improves performance
2. **Use `quick_render_full()` in detail views** - Provides full information
3. **Cache breakdown calculations** - Store in session state if showing multiple times
4. **Show help modal on first use** - Educate users about confidence scoring
5. **Use bulk stats before bulk operations** - Help users make informed decisions
6. **Add confidence filter** - Let users filter by confidence level (High/Medium/Low)
7. **Highlight low confidence** - Draw attention to transactions needing review

---

## Migration Checklist

- [ ] Import confidence tooltips in `app.py`
- [ ] Replace simple confidence display in Final Review
- [ ] Add breakdown to transaction detail view
- [ ] Integrate bulk stats in bulk operations
- [ ] Add help modal to Settings/Help page
- [ ] Update smart learning modal with confidence info
- [ ] Add compact indicators to transaction lists
- [ ] Test with various confidence scores
- [ ] Update user documentation

---

## Support

For questions or issues, refer to:
- `/Users/anthony/Tax Helper/components/confidence_tooltips.py` - Source code
- `/Users/anthony/Tax Helper/components/confidence_tooltips_examples.py` - Examples
- This documentation file

Happy integrating! 🎉
