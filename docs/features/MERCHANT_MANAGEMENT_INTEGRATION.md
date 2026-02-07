# Merchant Management Integration Guide

Complete guide for integrating the Merchant Management UI into your Tax Helper application.

## File Locations

- **Main Component**: `/Users/anthony/Tax Helper/components/merchant_management.py`
- **Examples**: `/Users/anthony/Tax Helper/components/merchant_management_examples.py`
- **This Guide**: `/Users/anthony/Tax Helper/MERCHANT_MANAGEMENT_INTEGRATION.md`

## Features Overview

### 1. Add New Merchants
User-friendly form with:
- Merchant name (required)
- Aliases (comma-separated variations)
- Default type (Income/Expense)
- Default category
- Personal/Business flag
- Industry classification
- Confidence boost (0-30 points)

### 2. Browse & Manage Merchants
- Paginated list (20 per page)
- Search by name or alias
- Filter by type, personal/business, industry
- Edit any merchant
- Delete with confirmation
- View usage statistics

### 3. Import/Export
- Export all merchants to CSV
- Import merchants from CSV
- Duplicate detection
- Batch operations

### 4. Statistics Dashboard
- Total merchants count
- System vs custom breakdown
- Most used merchants
- Recently added merchants
- Industry distribution

### 5. Quick-Add Modal
- Simplified form for fast additions
- Can be triggered from anywhere
- Pre-fills suggested merchant name

---

## Step-by-Step Integration

### Step 1: Verify Database Schema

The `Merchant` model should already exist in your `models.py`. Verify it includes these fields:

```python
class Merchant(Base):
    __tablename__ = 'merchants'

    id = Column(Integer, primary_key=True)
    name = Column(String(200), unique=True, nullable=False)
    aliases = Column(Text)  # JSON array
    default_category = Column(String(100))
    default_type = Column(String(20))  # Income or Expense
    is_personal = Column(Boolean, default=False)
    industry = Column(String(100))
    confidence_boost = Column(Integer, default=20)
    usage_count = Column(Integer, default=0)
    created_date = Column(DateTime, default=datetime.now)
    last_used_date = Column(DateTime)
```

If the table doesn't exist, run:

```python
from models import init_db
engine, Session = init_db('tax_helper.db')
```

### Step 2: Add Imports to app.py

At the top of your `app.py`, add:

```python
# Add to existing component imports
from components.merchant_management import (
    render_merchant_management_page,
    quick_add_merchant_button,
    render_quick_add_merchant_modal
)
```

### Step 3: Add Merchant Tab to Settings Page

Find your Settings page section (usually around line 2500+ in app.py) and modify:

**BEFORE:**
```python
if page == "Settings":
    st.title("Settings")

    tab1, tab2, tab3 = st.tabs([
        "General",
        "CSV Mapping",
        "Rules"
    ])
```

**AFTER:**
```python
if page == "Settings":
    st.title("Settings")

    tab1, tab2, tab3, tab4 = st.tabs([
        "General",
        "CSV Mapping",
        "Rules",
        "Merchants"  # NEW TAB
    ])

    # ... existing tab content ...

    with tab4:
        # NEW: Merchant Management
        render_merchant_management_page(session)
```

### Step 4: Add Quick-Add Modal Handler

In your main app loop, after page navigation but before rendering content:

```python
# Add after sidebar navigation
# Usually after: page = st.sidebar.radio(...)

# Handle quick-add merchant modal
if st.session_state.get('show_quick_add_merchant'):
    with st.container():
        render_quick_add_merchant_modal(session)
```

### Step 5: Add Quick-Add Button to Transaction Review

When users are reviewing transactions with low confidence, suggest adding the merchant.

Find your transaction review section and add:

```python
# In transaction review/edit section
if transaction.confidence_score < 60:
    st.warning("⚠️ Low confidence - merchant not recognized")

    # Extract likely merchant name from description
    likely_merchant = " ".join(transaction.description.split()[:3])

    # Show quick-add button
    quick_add_merchant_button(session, likely_merchant)
```

### Step 6: Add to Import Process (Optional)

After importing CSV transactions, analyze for unknown merchants:

```python
# After successful CSV import
from components.merchant_db import find_merchant_match

# Find unknown merchants
unknown_merchants = set()

for txn in newly_imported_transactions:
    match = find_merchant_match(txn.description, confidence_threshold=70.0)

    if not match:
        # Extract likely merchant name (first few words)
        likely_name = " ".join(txn.description.split()[:3])
        unknown_merchants.add(likely_name)

# Show unknown merchants
if unknown_merchants:
    st.info(f"ℹ️ Found {len(unknown_merchants)} unknown merchants")

    with st.expander("Add Unknown Merchants"):
        for merchant_name in unknown_merchants:
            col1, col2 = st.columns([3, 1])

            with col1:
                st.write(f"**{merchant_name}**")

            with col2:
                quick_add_merchant_button(session, merchant_name)
```

---

## User Workflows

### Workflow 1: Add New Merchant

1. User goes to **Settings → Merchants** tab
2. Clicks **"Add Merchant"** tab
3. Fills in form:
   - Name: "Joe's Coffee Shop"
   - Aliases: "JOES COFFEE, JOE'S, JOES"
   - Type: Expense
   - Category: "Office costs"
   - Personal: No
   - Industry: Restaurant
   - Confidence: 20
4. Clicks **"Add Merchant"**
5. Success! Future transactions auto-match

### Workflow 2: Edit Existing Merchant

1. User goes to **Settings → Merchants**
2. Searches for merchant (e.g., "TESCO")
3. Clicks **"Edit"** button
4. Updates fields (e.g., change category)
5. Clicks **"Save Changes"**
6. Updated!

### Workflow 3: Import Merchant List

1. User prepares CSV file (see format below)
2. Goes to **Settings → Merchants → Import/Export** tab
3. Uploads CSV file
4. Reviews preview
5. Clicks **"Import from CSV"**
6. Sees summary: "Added 25, Skipped 3"

### Workflow 4: Quick-Add During Review

1. User reviewing transaction: "LOCAL CAFE £4.50"
2. System shows low confidence warning
3. User clicks **"+ Add Custom Merchant"**
4. Quick modal appears with "LOCAL CAFE" pre-filled
5. Selects category, clicks **"Add"**
6. Done! Can continue reviewing

### Workflow 5: Export for Backup

1. User goes to **Settings → Merchants → Import/Export**
2. Clicks **"Export to CSV"**
3. Downloads `merchants_export_20251017.csv`
4. Safe backup created!

---

## CSV Format Reference

### Export Format

```csv
name,aliases,default_category,default_type,is_personal,industry,confidence_boost
"JOE'S COFFEE","JOES COFFEE,JOE'S","Office costs","Expense",FALSE,"Restaurant",20
"TESCO","TESCO STORES,TESCO EXPRESS","Office costs","Expense",TRUE,"Supermarket",25
"ACME LTD","ACME,ACME LIMITED","Professional fees","Expense",FALSE,"Software",30
"CLIENT ABC","CLIENT ABC LTD,ABC","Self-employment","Income",FALSE,"Professional Services",30
```

### Import Format

Same as export. Required fields:
- `name` - Merchant name (required, unique)
- `default_category` - Must match EXPENSE_CATEGORIES or INCOME_TYPES
- `default_type` - Must be "Income" or "Expense"

Optional fields:
- `aliases` - Comma-separated alternative names
- `is_personal` - TRUE or FALSE (default: FALSE)
- `industry` - Industry name (default: "Other")
- `confidence_boost` - 0-30 (default: 20)

---

## API Reference

### Main Functions

#### `render_merchant_management_page(session)`
Full-featured merchant management interface with tabs for browse, add, stats, and import/export.

**Parameters:**
- `session` - SQLAlchemy database session

**Usage:**
```python
render_merchant_management_page(st.session_state.db_session)
```

#### `quick_add_merchant_button(session, suggested_name=None)`
Show a "+ Add Custom Merchant" button that opens quick-add modal.

**Parameters:**
- `session` - Database session
- `suggested_name` - Pre-fill merchant name (optional)

**Usage:**
```python
quick_add_merchant_button(session, "LOCAL CAFE")
```

#### `render_quick_add_merchant_modal(session)`
Render simplified add merchant modal for quick additions.

**Parameters:**
- `session` - Database session

**Returns:**
- `Merchant` object if created, `None` otherwise

**Usage:**
```python
if st.session_state.get('show_quick_add_merchant'):
    merchant = render_quick_add_merchant_modal(session)
```

### Database Functions

#### `add_custom_merchant(session, name, aliases, default_category, default_type, is_personal, industry, confidence_boost)`
Add new merchant to database.

**Returns:** `Merchant` object

#### `update_merchant(session, merchant_id, **kwargs)`
Update existing merchant. Only provided fields are updated.

**Returns:** Updated `Merchant` object

#### `delete_merchant(session, merchant_id)`
Delete merchant from database.

**Returns:** `True` if successful

#### `search_merchants(session, query=None, filter_type="All", filter_personal="All", filter_industry="All", page=1, page_size=20)`
Search merchants with filters and pagination.

**Returns:** `(merchants_list, total_count)`

#### `get_merchant_usage_count(session, merchant_id)`
Get actual usage count by searching transaction descriptions.

**Returns:** `int` - number of matching transactions

### Validation Functions

#### `validate_merchant_data(name, category, txn_type, confidence_boost=20)`
Validate merchant data before saving.

**Returns:** `(is_valid: bool, error_message: str)`

#### `check_duplicate_merchant(session, name, exclude_id=None)`
Check if merchant with same name exists.

**Returns:** Existing `Merchant` or `None`

#### `find_similar_merchants(session, name, threshold=0.7)`
Find merchants with similar names (potential duplicates).

**Returns:** `List[Merchant]`

### Import/Export Functions

#### `export_merchants_to_csv(session)`
Export all merchants to CSV string.

**Returns:** `str` - CSV content

#### `import_merchants_from_csv(session, csv_content, skip_duplicates=True)`
Import merchants from CSV.

**Returns:** `Dict` with stats: `{total, added, skipped, errors}`

### Statistics Functions

#### `get_merchant_statistics(session)`
Get comprehensive merchant statistics.

**Returns:** `Dict` with counts, breakdowns, most used, recently added

---

## Error Handling

All functions include comprehensive error handling:

### Validation Errors
```python
# Empty name
validate_merchant_data("", "Office costs", "Expense", 20)
# Returns: (False, "Merchant name cannot be empty")

# Invalid confidence boost
validate_merchant_data("TEST", "Office costs", "Expense", 50)
# Returns: (False, "Confidence boost must be between 0 and 30")
```

### Duplicate Detection
```python
# Attempting to add duplicate
merchant = add_custom_merchant(session, "TESCO", ...)
# Raises: ValueError or shows error in UI

# Check before adding
existing = check_duplicate_merchant(session, "TESCO")
if existing:
    st.error(f"Merchant '{existing.name}' already exists!")
```

### Import Errors
```python
stats = import_merchants_from_csv(session, csv_content)

# Check for errors
if stats['errors']:
    st.warning("Some merchants had errors:")
    for error in stats['errors']:
        st.write(f"- {error}")
```

---

## Testing

### Test 1: Basic Add/Edit/Delete

```python
from components.merchant_management import (
    add_custom_merchant,
    update_merchant,
    delete_merchant
)

# Add merchant
merchant = add_custom_merchant(
    session=session,
    name="TEST CAFE",
    aliases=["TEST", "CAFE"],
    default_category="Office costs",
    default_type="Expense",
    is_personal=False,
    industry="Restaurant",
    confidence_boost=20
)

print(f"Created: {merchant.id} - {merchant.name}")

# Update merchant
updated = update_merchant(
    session=session,
    merchant_id=merchant.id,
    default_category="Meals & Entertainment"
)

print(f"Updated category: {updated.default_category}")

# Delete merchant
success = delete_merchant(session, merchant.id)
print(f"Deleted: {success}")
```

### Test 2: Search and Filter

```python
from components.merchant_management import search_merchants

# Search for "COFFEE"
merchants, total = search_merchants(
    session=session,
    query="COFFEE",
    filter_type="Expense"
)

print(f"Found {total} coffee-related merchants")
for m in merchants:
    print(f"- {m.name}: {m.default_category}")
```

### Test 3: Import/Export

```python
from components.merchant_management import (
    export_merchants_to_csv,
    import_merchants_from_csv
)

# Export
csv_content = export_merchants_to_csv(session)
print(f"Exported {len(csv_content.splitlines())} lines")

# Import
stats = import_merchants_from_csv(session, csv_content)
print(f"Imported: {stats['added']} added, {stats['skipped']} skipped")
```

---

## Troubleshooting

### Issue: Merchant tab not appearing in Settings

**Solution:** Verify you added the 4th tab correctly:

```python
tab1, tab2, tab3, tab4 = st.tabs([...])  # Must have 4 tabs

with tab4:
    render_merchant_management_page(session)
```

### Issue: Quick-add modal not showing

**Solution:** Ensure modal handler is in main app loop:

```python
# Must be BEFORE page content rendering
if st.session_state.get('show_quick_add_merchant'):
    render_quick_add_merchant_modal(session)
```

### Issue: Import fails with "Category not found"

**Solution:** Ensure CSV categories match `EXPENSE_CATEGORIES` or `INCOME_TYPES`:

```python
# Check valid categories
from models import EXPENSE_CATEGORIES, INCOME_TYPES
print(EXPENSE_CATEGORIES)
```

### Issue: Merchants not matching transactions

**Solution:** Check merchant names are normalized (uppercase) and aliases are comprehensive:

```python
# Merchant names should be uppercase
"JOE'S COFFEE" ✓
"joe's coffee" ✗

# Add all variations as aliases
["JOES COFFEE", "JOE'S", "JOES", "J COFFEE"]
```

### Issue: Duplicate merchants appearing

**Solution:** Use duplicate detection tool:

```python
from components.merchant_management import find_similar_merchants

similar = find_similar_merchants(session, "TESCO", threshold=0.75)
for merchant in similar:
    print(f"Similar: {merchant.name}")
```

---

## Advanced Usage

### Custom Industry Categories

Add new industries by modifying the industry list in the form:

```python
industries = [
    "Other", "Supermarket", "Restaurant",
    # Add your custom industries:
    "Construction", "Consulting", "E-commerce"
]
```

### Bulk Operations

Use database functions for bulk operations:

```python
from models import Merchant

# Get all personal merchants
personal = session.query(Merchant).filter(
    Merchant.is_personal == True
).all()

# Update all to new category
for merchant in personal:
    update_merchant(
        session,
        merchant.id,
        default_category="Personal expenses"
    )
```

### Custom Validation Rules

Add custom validation in `validate_merchant_data()`:

```python
# Example: Require minimum name length of 3
if len(name.strip()) < 3:
    return False, "Name must be at least 3 characters"
```

---

## Performance Considerations

### Pagination
- Default page size: 20 merchants
- Adjust in `search_merchants()` call: `page_size=50`

### Search Optimization
- Searches use SQL `ILIKE` for case-insensitive matching
- Indexes on `name` field for fast lookups

### Usage Count Calculation
- Usage counts are cached in `usage_count` field
- Recalculated on-demand via `get_merchant_usage_count()`
- Run batch update monthly:

```python
from models import Merchant

for merchant in session.query(Merchant).all():
    get_merchant_usage_count(session, merchant.id)
```

---

## Best Practices

1. **Naming Convention**
   - Use uppercase for merchant names
   - Keep names concise but unique
   - Example: "JOE'S COFFEE SHOP" not "joe's coffee shop ltd"

2. **Alias Strategy**
   - Include common misspellings
   - Include abbreviations
   - Include variations without punctuation
   - Example: ["JOES COFFEE", "JOE'S", "JOES", "JOE COFFEE"]

3. **Category Selection**
   - Use standard HMRC categories when possible
   - Be consistent across similar merchants
   - Review quarterly for accuracy

4. **Confidence Boost**
   - System merchants: 25-30
   - Frequently used custom: 20-25
   - Rarely used custom: 15-20
   - Auto-added unknown: 10-15

5. **Regular Maintenance**
   - Review usage statistics monthly
   - Run duplicate detection quarterly
   - Export backup before bulk changes
   - Update categories with business changes

---

## Support & Maintenance

### Backup Procedure

```bash
# Export merchants before major changes
Settings → Merchants → Import/Export → Export to CSV
# Save to: merchants_backup_YYYYMMDD.csv
```

### Migration from Old System

If migrating from old merchant database:

```python
# Export from old system to CSV
# Import using Import/Export tab
# Verify counts match
# Run duplicate detection
# Update usage counts
```

### Database Maintenance

```python
# Refresh usage counts
from models import Merchant
from components.merchant_management import get_merchant_usage_count

for merchant in session.query(Merchant).all():
    count = get_merchant_usage_count(session, merchant.id)
    print(f"{merchant.name}: {count} uses")
```

---

## Complete Integration Checklist

- [ ] Verify `Merchant` model exists in `models.py`
- [ ] Add imports to `app.py`
- [ ] Add Merchants tab to Settings page
- [ ] Add quick-add modal handler to main loop
- [ ] Add quick-add button to transaction review
- [ ] Test adding a merchant through UI
- [ ] Test editing a merchant
- [ ] Test deleting a merchant
- [ ] Test search and filters
- [ ] Test CSV export
- [ ] Test CSV import
- [ ] Test quick-add modal
- [ ] Add to import process (optional)
- [ ] Add stats to dashboard (optional)
- [ ] Update user documentation
- [ ] Create backup export
- [ ] Train users on new feature

---

## Questions & Feedback

For issues or questions about merchant management:

1. Check this guide's Troubleshooting section
2. Review examples in `merchant_management_examples.py`
3. Check function docstrings for detailed parameter info
4. Test with small dataset first

---

**Version:** 1.0.0
**Last Updated:** 2025-10-17
**Component:** `/Users/anthony/Tax Helper/components/merchant_management.py`
