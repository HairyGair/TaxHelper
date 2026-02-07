# Confidence Tooltips Component

Beautiful, informative tooltips that explain AI confidence scores for transaction categorization in the Tax Helper application.

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.7%2B-blue)
![Streamlit](https://img.shields.io/badge/streamlit-1.0%2B-red)

---

## Overview

The Confidence Tooltips component provides visual, interactive explanations of how the AI assigns confidence scores to transaction categorizations. It breaks down the scoring into four key factors:

1. **Merchant Match (0-40 points)** - Database matching
2. **Rule Match (0-30 points)** - Custom rule application
3. **Pattern Learning (0-20 points)** - Historical transaction analysis
4. **Amount Consistency (0-10 points)** - Amount variance checking

**Total Score:** 0-100%

---

## Features

- 📊 **Visual Breakdown** - Progress bars showing each factor's contribution
- 🎨 **Beautiful Design** - Gradient cards with smooth animations
- 🟢 **Color-Coded Levels** - Green (High), Amber (Medium), Orange/Red (Low)
- 📱 **Responsive** - Works on mobile, tablet, and desktop
- ♿ **Accessible** - ARIA labels, keyboard navigation, high contrast support
- 🚀 **Performance** - Optimized calculations with minimal overhead
- 🎯 **Flexible** - Multiple display modes (badge, compact, full breakdown)
- 📚 **Educational** - Built-in help modal explaining the system

---

## Quick Start

### Basic Usage

```python
from components.confidence_tooltips import quick_render_full

# Show confidence with expandable breakdown
quick_render_full(transaction, session)
```

That's it! This single line renders a confidence badge with an expandable breakdown.

---

## Display Modes

### 1. Full Badge with Breakdown (Recommended)

```python
from components.confidence_tooltips import quick_render_full

quick_render_full(transaction, session)
```

**Output:**
- Confidence badge (e.g., 🟢 High 85%)
- Expandable "See breakdown" section
- Detailed card with all 4 factors

**Use cases:** Transaction detail views, review pages

---

### 2. Compact Badge

```python
from components.confidence_tooltips import quick_render_compact

quick_render_compact(85)
```

**Output:** 🟢 85%

**Use cases:** Transaction lists, tables, compact displays

---

### 3. Standard Badge

```python
from components.confidence_tooltips import quick_render_badge

quick_render_badge(85)
```

**Output:** 🟢 High 85%

**Use cases:** Headers, summary cards

---

### 4. Manual Breakdown

```python
from components.confidence_tooltips import (
    calculate_confidence_breakdown,
    render_confidence_breakdown_card
)

breakdown = calculate_confidence_breakdown(transaction, session)
render_confidence_breakdown_card(breakdown)
```

**Output:** Full breakdown card with all factors

**Use cases:** Custom layouts, detailed analysis pages

---

## API Reference

### Core Functions

#### `calculate_confidence_breakdown(transaction, session)`

Calculate detailed confidence breakdown.

**Parameters:**
- `transaction` (Transaction): Transaction object
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

#### `render_confidence_with_breakdown(transaction, session, key_prefix="")`

Render badge with expandable breakdown (all-in-one solution).

**Parameters:**
- `transaction` (Transaction): Transaction object
- `session` (Session): SQLAlchemy session
- `key_prefix` (str): Unique prefix for widgets (prevents conflicts)

**Example:**
```python
render_confidence_with_breakdown(transaction, session, key_prefix="txn_123")
```

---

#### `render_bulk_confidence_stats(transactions, session)`

Show statistics for multiple transactions.

**Parameters:**
- `transactions` (List[Transaction]): List of transactions
- `session` (Session): SQLAlchemy session

**Example:**
```python
selected_txns = session.query(Transaction).filter(...).all()
render_bulk_confidence_stats(selected_txns, session)
```

**Output:**
- Average confidence score
- Count by level (High/Medium/Low)
- Visual statistics card

---

#### `render_help_modal()`

Display comprehensive help explaining confidence scoring.

**Example:**
```python
if st.button("How Does Confidence Work?"):
    render_help_modal()
```

---

### Helper Functions

#### `get_confidence_level(score)`

Get level information for a score.

**Returns:**
```python
{
    'level': 'High',
    'color': '#28a745',
    'emoji': '🟢',
    'description': "We're very confident this is correct"
}
```

---

#### `get_confidence_explanation(score)`

Get human-readable explanation.

**Returns:** String like "We're very confident this categorization is correct"

---

## Integration Examples

### Example 1: Final Review Page

```python
# In your transaction review loop
for idx, txn in enumerate(transactions):
    col1, col2, col3 = st.columns([2, 3, 2])

    with col1:
        st.write(txn.date.strftime('%d/%m/%Y'))

    with col2:
        st.write(txn.description[:40])

    with col3:
        from components.confidence_tooltips import quick_render_compact
        quick_render_compact(txn.confidence_score)
```

---

### Example 2: Transaction Detail

```python
# In transaction detail expander
with st.expander(f"Transaction #{txn.id}", expanded=True):
    # ... transaction details ...

    st.markdown("### Confidence Analysis")
    from components.confidence_tooltips import quick_render_full
    quick_render_full(txn, session)
```

---

### Example 3: Bulk Operations

```python
# Before bulk operation
from components.confidence_tooltips import render_bulk_confidence_stats

selected = get_selected_transactions()
render_bulk_confidence_stats(selected, session)

if st.button("Apply to All"):
    # ... perform bulk operation ...
    pass
```

---

### Example 4: Settings/Help Page

```python
# Add help section
st.header("Confidence Scoring Help")
from components.confidence_tooltips import render_help_modal
render_help_modal()
```

---

## Confidence Levels Explained

### 🟢 High (70-100%)

**Meaning:** We're very confident this categorization is correct

**Examples:**
- Known merchant (TESCO, NETFLIX)
- High-priority rule match
- 15+ similar transactions
- Typical amount for merchant

**Action:** Can be auto-posted to ledgers

---

### 🟡 Medium (40-69%)

**Meaning:** This looks likely based on patterns

**Examples:**
- Medium-priority rule match
- 5-9 similar transactions
- Amount within normal range

**Action:** Quick review recommended

---

### 🟠 Low (10-39%)

**Meaning:** This is our best guess

**Examples:**
- Low-priority rule match
- 1-4 similar transactions
- Unusual amount

**Action:** Manual review required

---

### 🔴 None (0-9%)

**Meaning:** No strong matches found

**Examples:**
- No merchant match
- No rule match
- No similar transactions

**Action:** Manual categorization required

---

## Scoring Breakdown

### Factor 1: Merchant Match (0-40 points)

Matches transaction against 500+ UK merchants in database.

**Scoring:**
- **40 points:** 100% certain (TESCO, NETFLIX, government benefits)
- **35 points:** 90% certain (known business suppliers)
- **28 points:** 70% certain (could be business or personal)
- **20 points:** 50% certain (ambiguous)

---

### Factor 2: Rule Match (0-30 points)

Checks custom categorization rules.

**Scoring:**
- **30 points:** High-priority rule (1-20)
- **25 points:** Medium-priority rule (21-50)
- **15 points:** Low-priority rule (51-100)

**Priority-based:** Higher priority rules contribute more points.

---

### Factor 3: Pattern Learning (0-20 points)

Analyzes similar historical transactions.

**Scoring:**
- **20 points:** 15+ similar transactions
- **15 points:** 10-14 similar transactions
- **10 points:** 5-9 similar transactions
- **5 points:** 1-4 similar transactions

**Consistency bonus:** +5 points if categorization is consistent.

---

### Factor 4: Amount Consistency (0-10 points)

Checks if amount is typical for merchant.

**Scoring:**
- **10 points:** Within 10% of average
- **7 points:** Within 25% of average
- **4 points:** Within 50% of average
- **2 points:** Significantly different

---

## Customization

### Change Colors

Edit `get_confidence_level()` in `confidence_tooltips.py`:

```python
def get_confidence_level(score: int) -> Dict:
    if score >= 70:
        return {
            'level': 'High',
            'color': '#28a745',  # Change to your color
            'emoji': '🟢',
            'description': "Your custom description"
        }
```

---

### Custom Thresholds

Modify score ranges:

```python
# Change from 70-100% to 80-100% for "High"
if score >= 80:  # was 70
    return {'level': 'High', ...}
```

---

### Custom Styling

See [`CONFIDENCE_TOOLTIPS_STYLING.md`](/Users/anthony/Tax Helper/docs/CONFIDENCE_TOOLTIPS_STYLING.md) for complete CSS reference.

---

## Performance Considerations

### Caching Breakdowns

For performance, cache breakdown calculations:

```python
# Cache in session state
if f'breakdown_{txn.id}' not in st.session_state:
    st.session_state[f'breakdown_{txn.id}'] = (
        calculate_confidence_breakdown(txn, session)
    )

breakdown = st.session_state[f'breakdown_{txn.id}']
render_confidence_breakdown_card(breakdown)
```

---

### Lazy Loading

Only calculate when needed:

```python
with st.expander("See breakdown"):
    # Only calculates when expanded
    breakdown = calculate_confidence_breakdown(txn, session)
    render_confidence_breakdown_card(breakdown)
```

---

### Batch Processing

Process multiple transactions efficiently:

```python
# Instead of calculating one-by-one
for txn in transactions:
    breakdown = calculate_confidence_breakdown(txn, session)  # Slow

# Use bulk stats instead
render_bulk_confidence_stats(transactions, session)  # Fast
```

---

## Troubleshooting

### Issue: No merchant match

**Solution:** Add merchant to `scripts/merchant_database.py`

```python
SUPERMARKETS = {
    'NEW_MERCHANT': MerchantCategory(
        'Merchant Name',
        True,  # is_personal
        'Category',
        CONFIDENCE_CERTAIN
    )
}
```

---

### Issue: Low scores for known merchants

**Solution:**
1. Check merchant database spelling
2. Verify rule priorities
3. Review similar transactions

---

### Issue: Performance slow

**Solution:**
1. Use `quick_render_compact()` in lists
2. Cache breakdown calculations
3. Only calculate when expanded

---

## File Structure

```
/Users/anthony/Tax Helper/
├── components/
│   ├── confidence_tooltips.py              # Main component
│   ├── confidence_tooltips_examples.py     # Usage examples
│   └── CONFIDENCE_TOOLTIPS_README.md       # This file
├── docs/
│   ├── CONFIDENCE_TOOLTIPS_INTEGRATION.md  # Integration guide
│   └── CONFIDENCE_TOOLTIPS_STYLING.md      # CSS styling guide
└── scripts/
    └── merchant_database.py                # Merchant database
```

---

## Dependencies

- Python 3.7+
- Streamlit 1.0+
- SQLAlchemy (for database queries)
- Tax Helper models (Transaction, Rule)

---

## Best Practices

1. ✅ Use `quick_render_compact()` in lists for performance
2. ✅ Use `quick_render_full()` in detail views for completeness
3. ✅ Show help modal on first use to educate users
4. ✅ Cache breakdown calculations when showing multiple times
5. ✅ Use bulk stats before bulk operations
6. ✅ Provide unique `key_prefix` to avoid widget conflicts
7. ✅ Test with various confidence scores (0%, 25%, 50%, 75%, 100%)

---

## Roadmap

### Planned Features

- [ ] Confidence threshold filters
- [ ] Confidence trends over time
- [ ] Merchant-specific confidence analytics
- [ ] Export confidence reports
- [ ] Machine learning model improvements
- [ ] Confidence prediction before import

---

## Support

For questions, issues, or feature requests:

1. Check the [Integration Guide](../docs/CONFIDENCE_TOOLTIPS_INTEGRATION.md)
2. Review [Styling Guide](../docs/CONFIDENCE_TOOLTIPS_STYLING.md)
3. See [Examples](confidence_tooltips_examples.py)
4. Check source code comments in `confidence_tooltips.py`

---

## License

Part of the Tax Helper application. All rights reserved.

---

## Changelog

### v1.0.0 (2025-10-17)

- Initial release
- Four-factor confidence scoring
- Beautiful gradient tooltips
- Expandable breakdown cards
- Bulk confidence statistics
- Help modal with full documentation
- Quick render functions
- Mobile-responsive design
- Accessibility features
- Comprehensive documentation

---

**Made with ❤️ for better tax management**
