# Merchant Management - Quick Start Checklist

5-minute integration guide to get merchant management working.

---

## Prerequisites Checklist

- [ ] `models.py` contains `Merchant` model (already exists ✓)
- [ ] Database initialized with merchants table (already exists ✓)
- [ ] Streamlit app running (`app.py`)
- [ ] Component file exists: `components/merchant_management.py` ✓

---

## 3-Step Integration

### Step 1: Add Imports (30 seconds)

**File:** `app.py`

**Location:** Top of file, with other component imports

**Add these lines:**
```python
from components.merchant_management import (
    render_merchant_management_page,
    quick_add_merchant_button,
    render_quick_add_merchant_modal
)
```

**Example:**
```python
# Existing imports
from components.bulk_operations import render_bulk_toolbar
from components.search_filter import render_search_bar

# NEW: Add these lines
from components.merchant_management import (
    render_merchant_management_page,
    quick_add_merchant_button,
    render_quick_add_merchant_modal
)
```

✅ **Test:** Run app, verify no import errors

---

### Step 2: Add Merchants Tab to Settings (2 minutes)

**File:** `app.py`

**Location:** Settings page section (search for "Settings" page)

**Find this code:**
```python
if page == "Settings":
    st.title("Settings")

    tab1, tab2, tab3 = st.tabs([
        "General",
        "CSV Mapping",
        "Rules"
    ])
```

**Change to:**
```python
if page == "Settings":
    st.title("Settings")

    tab1, tab2, tab3, tab4 = st.tabs([
        "General",
        "CSV Mapping",
        "Rules",
        "Merchants"  # NEW TAB
    ])

    # ... existing tab1, tab2, tab3 code ...

    with tab4:
        # NEW: Merchant Management
        render_merchant_management_page(session)
```

**Complete example:**
```python
if page == "Settings":
    st.title("Settings")

    # Add 4th tab
    tab1, tab2, tab3, tab4 = st.tabs([
        "General",
        "CSV Mapping",
        "Rules",
        "Merchants"  # NEW
    ])

    with tab1:
        # General settings (existing code)
        st.subheader("General Settings")
        # ... your existing code ...

    with tab2:
        # CSV Mapping (existing code)
        st.subheader("CSV Column Mapping")
        # ... your existing code ...

    with tab3:
        # Rules (existing code)
        st.subheader("Categorization Rules")
        # ... your existing code ...

    with tab4:
        # NEW: Merchant Management
        render_merchant_management_page(session)
```

✅ **Test:** Navigate to Settings → Merchants tab, should see merchant management interface

---

### Step 3: Add Quick-Add Modal Handler (1 minute)

**File:** `app.py`

**Location:** Main app loop, BEFORE page content rendering

**Find a good spot early in the file, after sidebar but before page rendering:**

```python
# Usually after:
# page = st.sidebar.radio("Navigate", [...])

# Add this:
# Handle quick-add merchant modal
if st.session_state.get('show_quick_add_merchant'):
    with st.container():
        render_quick_add_merchant_modal(session)
```

**Example placement:**
```python
# Sidebar navigation
page = st.sidebar.radio(
    "Navigate",
    ["Dashboard", "Import", "Review", "Settings"]
)

# NEW: Quick-add modal handler (BEFORE page rendering)
if st.session_state.get('show_quick_add_merchant'):
    with st.container():
        render_quick_add_merchant_modal(session)

# Now render pages
if page == "Dashboard":
    # ... dashboard code ...
```

✅ **Test:** Full merchant management should work!

---

## Verification Tests

### Test 1: Browse Merchants (1 minute)
1. Run app: `streamlit run app.py`
2. Navigate to: Settings → Merchants
3. Should see: Browse, Add, Statistics, Import/Export tabs
4. Click Browse: Should see merchant list
5. ✅ **Pass if:** You see merchants listed

### Test 2: Add Merchant (1 minute)
1. Click "Add Merchant" tab
2. Fill in:
   - Name: "TEST CAFE"
   - Type: Expense
   - Category: Office costs
3. Click "Add Merchant"
4. ✅ **Pass if:** Success message appears

### Test 3: Edit Merchant (1 minute)
1. Browse merchants
2. Find "TEST CAFE"
3. Click "Edit"
4. Change category
5. Click "Save Changes"
6. ✅ **Pass if:** Changes saved

### Test 4: Delete Merchant (1 minute)
1. Find "TEST CAFE"
2. Click "Delete"
3. Confirm deletion
4. ✅ **Pass if:** Merchant removed

### Test 5: Search & Filter (1 minute)
1. Browse merchants
2. Type "COFFEE" in search
3. Should see only coffee-related merchants
4. Try filters (Type, Personal, Industry)
5. ✅ **Pass if:** Filters work correctly

---

## Optional Enhancements

### Enhancement 1: Quick-Add in Transaction Review (5 minutes)

**File:** `app.py`

**Location:** Transaction review section

**Add this code when showing a transaction:**
```python
# In your transaction review code
if transaction.confidence_score < 60:
    st.warning("⚠️ Low confidence - merchant not recognized")

    # Extract likely merchant name
    likely_merchant = " ".join(transaction.description.split()[:3])

    # Show quick-add button
    quick_add_merchant_button(session, likely_merchant)
```

**Benefit:** Users can instantly add unknown merchants while reviewing

---

### Enhancement 2: Unknown Merchant Detection in Import (10 minutes)

**File:** `app.py`

**Location:** After CSV import success

**Add this code:**
```python
# After successfully importing transactions
from components.merchant_db import find_merchant_match

# Find unknown merchants
unknown_merchants = set()

for txn in newly_imported_transactions:
    match = find_merchant_match(txn.description, confidence_threshold=70.0)

    if not match:
        # Extract likely merchant name
        likely_name = " ".join(txn.description.split()[:3])
        unknown_merchants.add(likely_name)

# Show unknown merchants
if unknown_merchants:
    st.info(f"ℹ️ Found {len(unknown_merchants)} unknown merchants")

    with st.expander("Add Unknown Merchants"):
        for merchant_name in list(unknown_merchants)[:10]:
            col1, col2 = st.columns([3, 1])

            with col1:
                st.write(f"**{merchant_name}**")

            with col2:
                quick_add_merchant_button(session, merchant_name)
```

**Benefit:** Batch-add merchants after import for better auto-categorization

---

## Troubleshooting

### Issue: "Module not found" error

**Solution:**
```bash
# Verify file exists
ls /Users/anthony/Tax\ Helper/components/merchant_management.py

# Should see the file listed
```

### Issue: Merchants tab doesn't appear

**Solution:**
- Check you added `tab4` to the tabs list
- Verify you have 4 tab names in the list
- Check indentation is correct

### Issue: Quick-add modal not showing

**Solution:**
- Verify modal handler is BEFORE page rendering
- Check it's not inside a page-specific if block
- Ensure `with st.container():` wrapper is used

### Issue: Database errors

**Solution:**
```python
# Re-initialize database
from models import init_db
engine, Session = init_db('/Users/anthony/Tax Helper/tax_helper.db')
```

### Issue: Import validation fails

**Solution:**
- Check CSV format matches template
- Ensure categories match EXPENSE_CATEGORIES or INCOME_TYPES
- Verify default_type is exactly "Income" or "Expense"

---

## Success Criteria

You know it's working when:

- [✓] Settings has 4 tabs (General, CSV, Rules, **Merchants**)
- [✓] Merchants tab shows full management interface
- [✓] Can browse existing merchants
- [✓] Can add new merchants
- [✓] Can edit merchants
- [✓] Can delete merchants
- [✓] Search and filters work
- [✓] Statistics tab shows data
- [✓] Import/Export works
- [✓] No console errors

---

## Quick Reference

### Files Modified
1. `/Users/anthony/Tax Helper/app.py` (3 changes)

### Files Added
1. `/Users/anthony/Tax Helper/components/merchant_management.py`
2. `/Users/anthony/Tax Helper/components/merchant_management_examples.py`
3. `/Users/anthony/Tax Helper/MERCHANT_MANAGEMENT_INTEGRATION.md`
4. `/Users/anthony/Tax Helper/MERCHANT_MANAGEMENT_SUMMARY.md`
5. `/Users/anthony/Tax Helper/MERCHANT_UI_SCREENSHOTS.md`
6. `/Users/anthony/Tax Helper/test_merchant_management.py`

### Total Integration Time
- **Core Integration:** 3-5 minutes
- **Optional Enhancements:** 15-20 minutes
- **Testing:** 5-10 minutes

**Total:** 10-35 minutes depending on enhancements

---

## Need Help?

1. **Read the docs:**
   - Integration guide: `MERCHANT_MANAGEMENT_INTEGRATION.md`
   - Summary: `MERCHANT_MANAGEMENT_SUMMARY.md`
   - Visual reference: `MERCHANT_UI_SCREENSHOTS.md`

2. **Check examples:**
   - `components/merchant_management_examples.py`

3. **Run tests:**
   ```bash
   python3 test_merchant_management.py
   ```

4. **Check docstrings:**
   ```python
   from components.merchant_management import render_merchant_management_page
   help(render_merchant_management_page)
   ```

---

## Next Steps After Integration

1. **Populate Merchants:**
   - Import merchant CSV (if you have one)
   - Or add merchants as you encounter them

2. **Train Users:**
   - Show them Settings → Merchants tab
   - Demonstrate quick-add during review
   - Explain benefit of adding merchants

3. **Regular Maintenance:**
   - Export merchants monthly (backup)
   - Check for duplicates quarterly
   - Review usage statistics

4. **Optimize:**
   - Update confidence boosts based on accuracy
   - Merge duplicate merchants
   - Add aliases for common variations

---

**You're ready to go!** 🚀

Start with the 3-step integration, test it works, then add optional enhancements as needed.

**Estimated time:** 5 minutes to working merchant management!
