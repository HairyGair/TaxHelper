# Testing Guide - UI Enhancements

## Quick Start

### 1. Backup Your Current Database (Recommended)
```bash
cd "/Users/anthony/Tax Helper"
cp tax_helper.db tax_helper_backup_$(date +%Y%m%d).db
```

### 2. Run the Application
```bash
cd "/Users/anthony/Tax Helper"
streamlit run app.py
```

### 3. Test with Sample Data (Optional)
A test database with 6 sample transactions has been created at:
```bash
test_tax_helper.db
```

To test with sample data without affecting your main database:
```bash
# Temporarily rename your database
mv tax_helper.db tax_helper_production.db

# Use test database
cp test_tax_helper.db tax_helper.db

# Run Streamlit
streamlit run app.py

# When done testing, restore production database
mv tax_helper_production.db tax_helper.db
```

---

## Test Scenarios

### Dashboard Page Tests

#### Test 1: View Categorization Confidence
**Steps:**
1. Navigate to Dashboard page
2. Scroll down past income/expense sections
3. Locate "📊 Categorization Confidence" section

**Expected Results:**
- 4 metric boxes displayed
- Each shows count and percentage
- Emojis: 🟢 🟡 🔴 ⚠️
- Percentages add up to 100% (excluding needs review)

**Pass Criteria:**
- [ ] All 4 metrics visible
- [ ] Numbers and percentages displayed
- [ ] Emojis render correctly

#### Test 2: View Pattern Detection Summary
**Steps:**
1. Stay on Dashboard page
2. Scroll down to "🔍 Pattern Detection Summary"

**Expected Results:**
- Displays count for each detected pattern type
- Shows pattern emoji + label
- Shows percentage of total
- Handles "no patterns" gracefully

**Pass Criteria:**
- [ ] Pattern counts accurate
- [ ] Emojis render correctly
- [ ] If no patterns: shows info message

---

### Inbox Page Tests

#### Test 3: Filter by Confidence Level
**Steps:**
1. Navigate to Inbox page
2. Click "Review Transactions" tab
3. Test each confidence filter:
   - Click "High Confidence"
   - Click "Medium"
   - Click "Low"
   - Click "Needs Review"
   - Click "All"

**Expected Results:**
- Transaction count updates when filter changes
- Only matching transactions displayed
- Page resets to page 1 when filter changes

**Pass Criteria:**
- [ ] Filter buttons respond to clicks
- [ ] Transaction list updates
- [ ] "Showing X of Y" count is accurate

#### Test 4: Sort by Confidence
**Steps:**
1. On Inbox page, Review Transactions tab
2. Open "Sort by" dropdown
3. Select "Confidence (High to Low)"
4. Observe transaction order
5. Select "Confidence (Low to High)"
6. Observe transaction order

**Expected Results:**
- Transactions reorder by confidence score
- High to Low: 95%, 88%, 55%, 35%, etc.
- Low to High: 35%, 55%, 88%, 95%, etc.

**Pass Criteria:**
- [ ] Sort dropdown has all 5 options
- [ ] Sorting works correctly
- [ ] Page resets to page 1

#### Test 5: View Confidence Badges in Transaction List
**Steps:**
1. Find a transaction with high confidence (≥70%)
2. Find a transaction with medium confidence (40-69%)
3. Find a transaction with low confidence (<40%)

**Expected Results:**
- High: 🟢 Green badge with "High X%"
- Medium: 🟡 Amber badge with "Medium X%"
- Low: 🔴 Red badge with "Low X%"
- Badge appears after "Confidence Score:" label

**Pass Criteria:**
- [ ] Badges have correct colors
- [ ] Emojis render correctly
- [ ] Percentages match database values

#### Test 6: View Confidence Breakdown
**Steps:**
1. Expand a transaction with merchant_confidence and pattern_confidence
2. Look for "Breakdown:" text under confidence badge

**Expected Results:**
- Shows "Merchant: X% | Pattern: Y%"
- Both percentages displayed
- Appears in gray caption text

**Pass Criteria:**
- [ ] Breakdown line visible
- [ ] Both percentages shown
- [ ] Format is clean and readable

#### Test 7: View Pattern Information
**Steps:**
1. Find transaction with pattern_type (e.g., recurring_payment)
2. Expand the transaction
3. Look for blue info box

**Expected Results:**
- Blue info box with emoji + description
- Shows pattern type (e.g., "🔁 Pattern Detected: Recurring payment detected")
- If metadata exists: shows frequency and occurrence count
- Example: "(monthly) - 12 times"

**Pass Criteria:**
- [ ] Info box appears
- [ ] Correct emoji for pattern type
- [ ] Description is human-readable
- [ ] Metadata displayed if available

#### Test 8: View Review Flags
**Steps:**
1. Find transaction with requires_review=True
2. Look at transaction title in list
3. Expand the transaction

**Expected Results:**
- Title ends with "⚠️ REVIEW"
- Inside card: yellow warning box
- Warning text: "⚠️ This transaction requires manual review"

**Pass Criteria:**
- [ ] Review flag in title
- [ ] Warning box inside card
- [ ] Warning is prominent and visible

#### Test 9: Pattern Emojis in Transaction Titles
**Steps:**
1. Find transactions with different pattern types
2. Check for emoji before description in title

**Expected Results:**
- recurring_payment: 🔁
- government_benefit: 🏛️
- round_up: 💰
- large_purchase: ⚠️
- internal_transfer: ↔️
- recurring_small_amount: ☕

**Pass Criteria:**
- [ ] Emoji appears before description
- [ ] Correct emoji for each pattern type
- [ ] No emoji if no pattern

---

## Edge Cases to Test

### Test 10: Transactions with NULL Confidence
**Steps:**
1. Find transaction with confidence_score = NULL or 0
2. Expand the transaction

**Expected Results:**
- No confidence badge displayed
- No error or broken layout
- Rest of transaction displays normally

**Pass Criteria:**
- [ ] No badge or score shown
- [ ] No errors in browser console
- [ ] Transaction displays correctly

### Test 11: Transactions with NULL Pattern
**Steps:**
1. Find transaction with pattern_type = NULL
2. Expand the transaction

**Expected Results:**
- No pattern emoji in title
- No pattern info box
- Rest of transaction displays normally

**Pass Criteria:**
- [ ] No pattern indicator
- [ ] No info box
- [ ] Transaction displays correctly

### Test 12: Empty Transaction List
**Steps:**
1. Set filters to show only "High Confidence"
2. If database has no high confidence items, list should be empty

**Expected Results:**
- Shows "No transactions to review" message
- Filter options still visible
- No errors

**Pass Criteria:**
- [ ] Info message displayed
- [ ] UI remains functional
- [ ] Can change filters

---

## Browser Compatibility Tests

### Test 13: Chrome/Edge
- [ ] All emojis render correctly
- [ ] Colored badges display properly
- [ ] Filters work smoothly
- [ ] No console errors

### Test 14: Firefox
- [ ] All emojis render correctly
- [ ] Colored badges display properly
- [ ] Filters work smoothly
- [ ] No console errors

### Test 15: Safari (Mac)
- [ ] All emojis render correctly
- [ ] Colored badges display properly
- [ ] Filters work smoothly
- [ ] No console errors

---

## Performance Tests

### Test 16: Large Dataset (>1000 transactions)
**Steps:**
1. Import CSV with 1000+ transactions
2. Navigate to Dashboard
3. Navigate to Inbox
4. Apply various filters

**Expected Results:**
- Dashboard loads in <3 seconds
- Inbox loads in <2 seconds
- Filtering is instant (<500ms)
- Sorting is instant (<500ms)
- Pagination works smoothly

**Pass Criteria:**
- [ ] No noticeable lag
- [ ] Smooth filtering
- [ ] Smooth sorting
- [ ] No timeout errors

---

## Functionality Tests (Existing Features)

### Test 17: Existing Features Still Work
**Steps:**
1. Test CSV upload (Upload CSV tab)
2. Test transaction editing (Update button)
3. Test mark as reviewed (Mark Reviewed button)
4. Test delete transaction (Delete button)
5. Test bulk actions (bottom of page)
6. Test pagination (First, Prev, Next, Last)

**Expected Results:**
- All existing features work as before
- No breaking changes
- No errors

**Pass Criteria:**
- [ ] CSV upload works
- [ ] Transaction updates save
- [ ] Mark reviewed works
- [ ] Delete works
- [ ] Bulk actions work
- [ ] Pagination works

---

## Data Integrity Tests

### Test 18: Confidence Score Validation
**Steps:**
1. Check transactions in database
2. Verify confidence_score is 0-100

**SQL Query:**
```sql
SELECT id, description, confidence_score
FROM transactions
WHERE confidence_score NOT BETWEEN 0 AND 100;
```

**Expected Results:**
- No rows returned (all scores valid)

**Pass Criteria:**
- [ ] All scores in valid range

### Test 19: Pattern Type Validation
**Steps:**
1. Check transactions in database
2. Verify pattern_type values

**SQL Query:**
```sql
SELECT DISTINCT pattern_type
FROM transactions
WHERE pattern_type IS NOT NULL;
```

**Expected Results:**
- Only valid pattern types:
  - recurring_payment
  - government_benefit
  - internal_transfer
  - round_up
  - recurring_small_amount
  - large_purchase

**Pass Criteria:**
- [ ] All pattern types are valid

---

## Test Data Reference

### Sample Transactions in test_tax_helper.db

1. **Netflix Subscription**
   - Confidence: 95% (High)
   - Pattern: recurring_payment (monthly, 12 times)
   - Type: Ignore (Personal)
   - Amount: £15.99 out

2. **Client Payment ABC Ltd**
   - Confidence: 88% (High)
   - Pattern: None
   - Type: Income (Self-employment)
   - Amount: £2,500.00 in

3. **Unknown Merchant XYZ**
   - Confidence: 35% (Low)
   - Pattern: None
   - Type: Expense
   - Requires Review: Yes
   - Amount: £150.00 out

4. **Savings Round Up**
   - Confidence: 92% (High)
   - Pattern: round_up (daily, 234 times)
   - Type: Ignore (Personal)
   - Amount: £2.45 out

5. **Government Universal Credit**
   - Confidence: 98% (High)
   - Pattern: government_benefit (monthly, 6 times)
   - Type: Income (Other)
   - Amount: £450.00 in

6. **Amazon Purchase**
   - Confidence: 55% (Medium)
   - Pattern: large_purchase
   - Type: Expense (Office costs)
   - Requires Review: Yes
   - Amount: £850.00 out

---

## Troubleshooting

### Issue: Badges Not Showing
**Possible Causes:**
- confidence_score is NULL or 0
- HTML rendering disabled

**Solution:**
- Check database: `SELECT confidence_score FROM transactions LIMIT 10;`
- Verify `unsafe_allow_html=True` in st.markdown()

### Issue: Patterns Not Showing
**Possible Causes:**
- pattern_type is NULL
- pattern_metadata is invalid JSON

**Solution:**
- Check database: `SELECT pattern_type, pattern_metadata FROM transactions LIMIT 10;`
- Verify JSON format

### Issue: Filters Not Working
**Possible Causes:**
- Session state issues
- Query building error

**Solution:**
- Clear Streamlit cache: Press 'C' in browser
- Restart Streamlit app
- Check browser console for errors

### Issue: Emojis Not Rendering
**Possible Causes:**
- Browser doesn't support emoji
- Font issues

**Solution:**
- Update browser to latest version
- Test in different browser
- Check system emoji support

---

## Reporting Issues

When reporting issues, please include:
1. **Browser:** Name and version
2. **Screen:** Dashboard or Inbox
3. **Action:** What you were doing
4. **Expected:** What should happen
5. **Actual:** What actually happened
6. **Console:** Any browser console errors
7. **Data:** Sample transaction data (if relevant)

---

## Success Criteria

All enhancements are working correctly if:

✅ **Dashboard:**
- [x] Categorization Confidence section displays
- [x] Pattern Detection Summary displays
- [x] Metrics show correct counts and percentages

✅ **Inbox:**
- [x] Confidence filter buttons work
- [x] Sort by confidence works
- [x] Confidence badges display with correct colors
- [x] Confidence breakdowns show
- [x] Pattern info boxes display
- [x] Pattern emojis appear in titles
- [x] Review flags appear for flagged transactions

✅ **Overall:**
- [x] No errors in browser console
- [x] No breaking changes to existing features
- [x] Performance is acceptable (<3s load times)
- [x] All emojis render correctly

---

## Next Steps After Testing

1. **If all tests pass:**
   - Mark as production-ready
   - Document any observations
   - Consider user training/documentation

2. **If issues found:**
   - Document specific failing test
   - Provide error messages
   - Include steps to reproduce
   - Check troubleshooting section

3. **Future enhancements:**
   - Add confidence score editing
   - Add pattern group management
   - Add confidence trends over time
   - Export with confidence scores

---

## Test Report Template

```
Test Date: _______________
Tester: _______________
Environment: Production / Test Database

Dashboard Tests:
[ ] Test 1: Categorization Confidence - PASS / FAIL
[ ] Test 2: Pattern Detection Summary - PASS / FAIL

Inbox Tests:
[ ] Test 3: Filter by Confidence - PASS / FAIL
[ ] Test 4: Sort by Confidence - PASS / FAIL
[ ] Test 5: Confidence Badges - PASS / FAIL
[ ] Test 6: Confidence Breakdown - PASS / FAIL
[ ] Test 7: Pattern Information - PASS / FAIL
[ ] Test 8: Review Flags - PASS / FAIL
[ ] Test 9: Pattern Emojis - PASS / FAIL

Edge Cases:
[ ] Test 10: NULL Confidence - PASS / FAIL
[ ] Test 11: NULL Pattern - PASS / FAIL
[ ] Test 12: Empty List - PASS / FAIL

Browser Tests:
[ ] Test 13: Chrome/Edge - PASS / FAIL
[ ] Test 14: Firefox - PASS / FAIL
[ ] Test 15: Safari - PASS / FAIL

Performance:
[ ] Test 16: Large Dataset - PASS / FAIL

Regression:
[ ] Test 17: Existing Features - PASS / FAIL

Data Integrity:
[ ] Test 18: Confidence Validation - PASS / FAIL
[ ] Test 19: Pattern Validation - PASS / FAIL

Overall Result: PASS / FAIL

Notes:
_______________________________________________________
_______________________________________________________
_______________________________________________________
```
