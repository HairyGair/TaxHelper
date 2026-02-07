# Technical Implementation Guide

## Database Schema Changes Required

### New Tables to Add

```python
# In models.py

class TransactionPattern(Base):
    """Store detected recurring patterns"""
    __tablename__ = 'transaction_patterns'
    id = Column(Integer, primary_key=True)
    transaction_id = Column(Integer, ForeignKey('transactions.id'))
    pattern_type = Column(String(50))  # 'daily', 'weekly', 'monthly', etc.
    pattern_group_id = Column(String(100), index=True)
    merchant_name = Column(String(200))
    expected_amount = Column(Float)
    amount_variance = Column(Float)
    expected_day_of_cycle = Column(Integer)
    last_occurrence = Column(Date)
    next_expected_date = Column(Date)
    occurrences = Column(Integer)
    confidence = Column(Integer)
    is_active = Column(Boolean, default=True)
    created_date = Column(DateTime, default=datetime.now)


class TransactionSplit(Base):
    """Allow splitting transactions across categories"""
    __tablename__ = 'transaction_splits'
    id = Column(Integer, primary_key=True)
    transaction_id = Column(Integer, ForeignKey('transactions.id'), index=True)
    split_amount = Column(Float, nullable=False)
    split_percentage = Column(Float)
    split_category = Column(String(100))
    split_type = Column(String(20))  # 'Income', 'Expense'
    split_is_personal = Column(Boolean, default=False)
    split_notes = Column(Text)
    created_date = Column(DateTime, default=datetime.now)


class Receipt(Base):
    """Store receipt metadata and links to transactions"""
    __tablename__ = 'receipts'
    id = Column(Integer, primary_key=True)
    file_path = Column(String(500), unique=True)
    file_hash = Column(String(64))  # SHA256 for duplicate detection
    uploaded_date = Column(DateTime, default=datetime.now)

    # OCR extracted data
    ocr_merchant = Column(String(200))
    ocr_amount = Column(Float)
    ocr_date = Column(Date)
    ocr_confidence = Column(Integer)

    # Links
    transaction_id = Column(Integer, ForeignKey('transactions.id'))
    expense_id = Column(Integer, ForeignKey('expenses.id'))

    # Validation
    amount_matches = Column(Boolean)
    date_matches = Column(Boolean)
    is_validated = Column(Boolean, default=False)


class Payee(Base):
    """Validated list of business payees and income sources"""
    __tablename__ = 'payees'
    id = Column(Integer, primary_key=True)
    name = Column(String(200), unique=True, nullable=False, index=True)
    type = Column(String(20))  # 'supplier', 'client', 'tax_authority'
    category = Column(String(100))
    total_paid = Column(Float, default=0.0)
    transaction_count = Column(Integer, default=0)
    is_hmrc = Column(Boolean, default=False)
    notes = Column(Text)
    created_date = Column(DateTime, default=datetime.now)


class StatementReconciliation(Base):
    """Track reconciliation of imported bank statements"""
    __tablename__ = 'statement_reconciliations'
    id = Column(Integer, primary_key=True)
    account_name = Column(String(100), index=True)
    statement_start_date = Column(Date)
    statement_end_date = Column(Date)
    opening_balance = Column(Float)
    closing_balance = Column(Float)
    total_in = Column(Float)
    total_out = Column(Float)
    calculated_balance = Column(Float)
    balance_difference = Column(Float)
    is_reconciled = Column(Boolean, default=False)
    transaction_count = Column(Integer)
    reviewed_count = Column(Integer)
    unreviewed_count = Column(Integer)
    reconciliation_date = Column(DateTime, default=datetime.now)
    notes = Column(Text)


class AuditSnapshot(Base):
    """Store complete snapshots of tax data at key points"""
    __tablename__ = 'audit_snapshots'
    id = Column(Integer, primary_key=True)
    snapshot_date = Column(DateTime, default=datetime.now, index=True)
    snapshot_type = Column(String(50))  # 'import', 'review', 'submission'
    tax_year = Column(String(10))

    # Complete data snapshot (JSON)
    income_snapshot = Column(JSON)
    expense_snapshot = Column(JSON)
    mileage_snapshot = Column(JSON)
    donation_snapshot = Column(JSON)
    summary_totals = Column(JSON)

    # Metadata
    user_id = Column(String(100))
    ip_address = Column(String(50))
    data_hash = Column(String(64))  # SHA256 for integrity
    notes = Column(Text)
    hmrc_submission_id = Column(String(100))
    submitted_to_hmrc = Column(Boolean, default=False)
```

### Enhanced Transaction Model

```python
# Add to existing Transaction class:

fuzzy_match_score = Column(Integer, default=0)  # 0-100 match confidence
potential_duplicate_id = Column(Integer)
duplicate_status = Column(String(50))  # 'exact', 'fuzzy', 'none'

# Payee validation
payee_validated = Column(Boolean, default=False)
payee_validation_score = Column(Integer, default=0)
```

### Enhanced Merchant Model

```python
# Add to existing Merchant class:

accuracy_percentage = Column(Integer, default=100)
total_matches = Column(Integer, default=0)
correct_matches = Column(Integer, default=0)
incorrect_matches = Column(Integer, default=0)
correction_history = Column(JSON)
last_corrected_date = Column(DateTime)
```

### Enhanced Rule Model

```python
# Add to existing Rule class:

effectiveness_score = Column(Integer, default=100)
times_applied = Column(Integer, default=0)
times_confirmed = Column(Integer, default=0)
times_corrected = Column(Integer, default=0)
last_correction_date = Column(DateTime)
correction_history = Column(JSON)
```

---

## New Utility Functions (utils.py)

```python
# Advanced duplicate detection
def detect_fuzzy_duplicates(df, session, Transaction, threshold=85):
    """See full implementation in ANALYSIS_RECOMMENDATIONS.md"""
    pass

# Payee validation
def validate_payee(description, payee_type, session):
    """See full implementation in ANALYSIS_RECOMMENDATIONS.md"""
    pass

# Completeness checking
def validate_completeness(session, tax_year_start, tax_year_end):
    """See full implementation in ANALYSIS_RECOMMENDATIONS.md"""
    pass

# Anomaly detection
def detect_anomalies_and_red_flags(session, tax_year_start, tax_year_end):
    """See full implementation in ANALYSIS_RECOMMENDATIONS.md"""
    pass

# Pattern detection
def analyze_recurring_patterns(session, lookback_months=12):
    """See full implementation in ANALYSIS_RECOMMENDATIONS.md"""
    pass

# Cash flow forecasting
def forecast_tax_liability_and_cash_flow(session, tax_year_start, tax_year_end):
    """See full implementation in ANALYSIS_RECOMMENDATIONS.md"""
    pass

# Tax optimization
def analyze_tax_optimization_opportunities(session, tax_year_start, tax_year_end):
    """See full implementation in ANALYSIS_RECOMMENDATIONS.md"""
    pass

# Audit snapshots
def create_audit_snapshot(session, tax_year, snapshot_type, user_id=None):
    """See full implementation in ANALYSIS_RECOMMENDATIONS.md"""
    pass

# Business metrics
def calculate_business_metrics(session, tax_year_start, tax_year_end):
    """See full implementation in ANALYSIS_RECOMMENDATIONS.md"""
    pass
```

---

## UI Components to Create

### 1. Duplicate Detection Alert Component
```python
# components/duplicate_detector.py
def show_duplicate_warning(duplicates, session):
    """
    Display list of detected duplicates with action buttons
    """
    pass

def show_fuzzy_duplicate_options(fuzzy_matches):
    """
    Show fuzzy matches with similarity scores
    """
    pass
```

### 2. Anomaly Detection Dashboard
```python
# components/anomaly_dashboard.py
def render_anomaly_alerts(red_flags):
    """
    Render audit risk assessment dashboard
    """
    pass

def render_anomaly_details(red_flag):
    """
    Show detailed explanation and remediation steps
    """
    pass
```

### 3. Recurring Transaction Manager
```python
# components/recurring_transactions.py
def show_detected_patterns(patterns):
    """
    Display detected recurring patterns
    """
    pass

def show_missing_occurrences(missing):
    """
    Alert user about overdue recurring transactions
    """
    pass

def auto_create_dialog(pattern):
    """
    Dialog to confirm auto-creating next occurrence
    """
    pass
```

### 4. Tax Optimization Recommendations
```python
# components/tax_optimization.py
def show_optimization_opportunities(opportunities):
    """
    Display tax saving opportunities with impact
    """
    pass

def show_opportunity_detail(opportunity):
    """
    Detailed view with implementation guide
    """
    pass
```

### 5. Cash Flow Forecasting
```python
# components/cash_flow.py
def show_cash_flow_projection(forecast):
    """
    Display quarterly cash flow forecast
    """
    pass

def show_payment_schedule(tax_liability):
    """
    Show payment on account dates and amounts
    """
    pass
```

### 6. Receipt Validation
```python
# components/receipt_validation.py
def show_receipt_validation_status(receipt, transaction):
    """
    Display OCR validation results
    """
    pass

def show_validation_warnings(warnings):
    """
    Highlight amount/date/merchant mismatches
    """
    pass
```

### 7. Audit Snapshot Viewer
```python
# components/audit_snapshot_viewer.py
def show_snapshot_history(snapshots):
    """
    Display list of audit snapshots
    """
    pass

def compare_snapshots(snapshot1, snapshot2):
    """
    Show changes between two snapshots
    """
    pass
```

---

## Migration Script

```python
# migrations/003_add_recommendations.py

from datetime import datetime
from models import (
    TransactionPattern, TransactionSplit, Receipt, Payee,
    StatementReconciliation, AuditSnapshot
)

def upgrade(session):
    """Apply schema changes"""
    # Create new tables
    Base.metadata.create_all(engine)

    # Add columns to existing tables
    # (SQLAlchemy handles most of this via metadata)

    print("✓ Migration 003: Added recommendation features")

def downgrade(session):
    """Rollback schema changes"""
    # Drop new tables
    Base.metadata.drop_all(engine)

    print("✓ Rolled back migration 003")
```

---

## Integration Points

### When Importing Transactions
1. Run `detect_fuzzy_duplicates()` before saving
2. Flag any fuzzy matches for user review
3. Create `StatementReconciliation` after import completes
4. Store snapshot via `create_audit_snapshot()`

### When Categorizing Transactions
1. Call `validate_payee()` for income/expense
2. Record feedback via `record_merchant_feedback()`
3. Call `record_rule_feedback()` for rules
4. Run `suggest_new_rules_from_corrections()`

### When Reviewing Transactions
1. Run `detect_anomalies_and_red_flags()`
2. Show anomalies to user
3. Record final `AuditSnapshot` when review complete

### When Generating Summary
1. Run `validate_completeness()`
2. Run `detect_anomalies_and_red_flags()`
3. Run `analyze_tax_optimization_opportunities()`
4. Run `forecast_tax_liability_and_cash_flow()`
5. Display all in appropriate tabs

### When Submitting to HMRC
1. Run `validate_hmrc_boxes()`
2. Create final `AuditSnapshot` with submission ID
3. Store copy of submitted data

---

## Performance Considerations

### Query Optimization
- Use indexes on frequently filtered columns (date, category, merchant, reviewed)
- Batch queries in loops (use `in_()` instead of multiple individual queries)
- Use `session.query(...).all()` once and iterate in Python rather than multiple queries

### Caching Strategies
```python
# Cache frequently-used lookups
@st.cache_data(ttl=3600)
def get_merchants(session):
    return session.query(Merchant).all()

@st.cache_data(ttl=3600)
def get_rules(session):
    return session.query(Rule).filter(Rule.enabled == True).all()
```

### Processing Heavy Functions
- Run `analyze_recurring_patterns()` once during import, not repeatedly
- Cache anomaly detection results
- Run expensive calculations only when tax year changes

### Database Maintenance
```python
# Periodic cleanup
def vacuum_database(session):
    """Optimize database"""
    session.execute("VACUUM")
    session.commit()

# Run monthly or after large imports
```

---

## Testing Strategy

### Unit Tests
```python
# tests/test_recommendations.py

def test_fuzzy_duplicate_detection():
    """Test fuzzy matching with 85% threshold"""
    pass

def test_recurring_pattern_detection():
    """Test monthly/weekly pattern detection"""
    pass

def test_anomaly_detection():
    """Test red flag detection"""
    pass

def test_tax_calculation():
    """Verify HMRC box calculations"""
    pass

def test_completeness_checker():
    """Test required field validation"""
    pass
```

### Integration Tests
```python
# tests/integration/test_workflows.py

def test_import_to_summary_workflow():
    """Test full workflow from import to summary"""
    pass

def test_categorization_feedback_loop():
    """Test that corrections improve categorization"""
    pass
```

### Data Validation Tests
```python
# tests/test_data_validation.py

def test_duplicate_detection_accuracy():
    """Verify duplicate detection is accurate"""
    pass

def test_payee_validation():
    """Test payee matching accuracy"""
    pass
```

---

## Deployment Checklist

- [ ] All database migrations tested
- [ ] New UI components styled and responsive
- [ ] All calculations verified against HMRC specs
- [ ] Performance tested with 10k+ transactions
- [ ] Duplicate detection tested with real duplicates
- [ ] Anomaly detection reviewed by tax expert
- [ ] Documentation updated
- [ ] User guide created for new features
- [ ] Backup system in place
- [ ] Rollback plan documented

---

## Maintenance & Monitoring

### Key Metrics to Track
1. Duplicate detection accuracy rate
2. Categorization accuracy (user corrections)
3. Anomaly detection false positive rate
4. Tax optimization value per user
5. User engagement with recommendations

### Monthly Review
- Check rule effectiveness scores
- Identify recurring pattern changes
- Review anomaly detection tuning
- Calculate tax optimization effectiveness

### Quarterly Updates
- Update merchant database with new merchants
- Adjust anomaly detection thresholds based on data
- Refresh tax rates and HMRC box limits
- Review and improve pattern detection

