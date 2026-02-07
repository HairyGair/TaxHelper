-- Migration: Add Performance Indexes
-- Purpose: Optimize query performance for large datasets
-- Date: 2025-10-17

-- ============================================================================
-- TRANSACTIONS TABLE INDEXES
-- ============================================================================

-- Index on date for date range queries
CREATE INDEX IF NOT EXISTS idx_transactions_date
ON transactions(date);

-- Index on reviewed status for filtering reviewed/unreviewed
CREATE INDEX IF NOT EXISTS idx_transactions_reviewed
ON transactions(reviewed);

-- Index on description for text search
CREATE INDEX IF NOT EXISTS idx_transactions_description
ON transactions(description);

-- Index on merchant_id for joins
CREATE INDEX IF NOT EXISTS idx_transactions_merchant
ON transactions(merchant_id);

-- Index on amount for filtering/sorting
CREATE INDEX IF NOT EXISTS idx_transactions_amount
ON transactions(amount);

-- Composite index for year-based queries
CREATE INDEX IF NOT EXISTS idx_transactions_year
ON transactions(strftime('%Y', date));

-- Composite index for common filters (year + reviewed)
CREATE INDEX IF NOT EXISTS idx_transactions_year_reviewed
ON transactions(strftime('%Y', date), reviewed);

-- ============================================================================
-- EXPENSES TABLE INDEXES
-- ============================================================================

-- Index on date for date range queries
CREATE INDEX IF NOT EXISTS idx_expenses_date
ON expenses(date);

-- Index on category for filtering
CREATE INDEX IF NOT EXISTS idx_expenses_category
ON expenses(category);

-- Index on transaction_id for joins
CREATE INDEX IF NOT EXISTS idx_expenses_transaction
ON expenses(transaction_id);

-- Composite index for year-based queries
CREATE INDEX IF NOT EXISTS idx_expenses_year
ON expenses(strftime('%Y', date));

-- Composite index for year + category queries
CREATE INDEX IF NOT EXISTS idx_expenses_year_category
ON expenses(strftime('%Y', date), category);

-- Index on amount for calculations
CREATE INDEX IF NOT EXISTS idx_expenses_amount
ON expenses(amount);

-- ============================================================================
-- INCOME TABLE INDEXES
-- ============================================================================

-- Index on date for date range queries
CREATE INDEX IF NOT EXISTS idx_income_date
ON income(date);

-- Index on income_type for filtering
CREATE INDEX IF NOT EXISTS idx_income_type
ON income(income_type);

-- Index on transaction_id for joins
CREATE INDEX IF NOT EXISTS idx_income_transaction
ON income(transaction_id);

-- Composite index for year-based queries
CREATE INDEX IF NOT EXISTS idx_income_year
ON income(strftime('%Y', date));

-- Composite index for year + type queries
CREATE INDEX IF NOT EXISTS idx_income_year_type
ON income(strftime('%Y', date), income_type);

-- Index on amount for calculations
CREATE INDEX IF NOT EXISTS idx_income_amount
ON income(amount);

-- ============================================================================
-- AUDIT LOG TABLE INDEXES
-- ============================================================================

-- Index on timestamp for time-based queries
CREATE INDEX IF NOT EXISTS idx_audit_log_timestamp
ON audit_log(timestamp);

-- Composite index for record lookups
CREATE INDEX IF NOT EXISTS idx_audit_log_record
ON audit_log(record_type, record_id);

-- Index on user for filtering by user
CREATE INDEX IF NOT EXISTS idx_audit_log_user
ON audit_log(user);

-- Index on action for filtering by action type
CREATE INDEX IF NOT EXISTS idx_audit_log_action
ON audit_log(action);

-- Composite index for date-based audit queries
CREATE INDEX IF NOT EXISTS idx_audit_log_date
ON audit_log(strftime('%Y-%m-%d', timestamp));

-- ============================================================================
-- MERCHANTS TABLE INDEXES
-- ============================================================================

-- Index on name for lookups and matching
CREATE INDEX IF NOT EXISTS idx_merchants_name
ON merchants(name);

-- Index on category for filtering
CREATE INDEX IF NOT EXISTS idx_merchants_category
ON merchants(category);

-- Index on confidence for quality filtering
CREATE INDEX IF NOT EXISTS idx_merchants_confidence
ON merchants(confidence);

-- ============================================================================
-- CATEGORIZATION RULES TABLE INDEXES
-- ============================================================================

-- Composite index for active rules by priority
CREATE INDEX IF NOT EXISTS idx_rules_active_priority
ON categorization_rules(active, priority DESC);

-- Index on pattern for rule matching
CREATE INDEX IF NOT EXISTS idx_rules_pattern
ON categorization_rules(pattern);

-- Index on category for filtering
CREATE INDEX IF NOT EXISTS idx_rules_category
ON categorization_rules(category);

-- ============================================================================
-- RECEIPTS TABLE INDEXES (if exists)
-- ============================================================================

-- Index on expense_id for joins
CREATE INDEX IF NOT EXISTS idx_receipts_expense
ON receipts(expense_id);

-- Index on created_at for sorting
CREATE INDEX IF NOT EXISTS idx_receipts_created
ON receipts(created_at);

-- ============================================================================
-- PERFORMANCE LOG TABLE (for monitoring)
-- ============================================================================

-- Create performance log table if it doesn't exist
CREATE TABLE IF NOT EXISTS performance_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    query_name TEXT NOT NULL,
    duration REAL NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    params TEXT
);

-- Index on timestamp for cleanup
CREATE INDEX IF NOT EXISTS idx_performance_log_timestamp
ON performance_log(timestamp);

-- Index on query_name for analysis
CREATE INDEX IF NOT EXISTS idx_performance_log_query
ON performance_log(query_name);

-- Index on duration for slow query detection
CREATE INDEX IF NOT EXISTS idx_performance_log_duration
ON performance_log(duration);

-- ============================================================================
-- ANALYZE TABLES FOR QUERY PLANNER
-- ============================================================================

-- Update statistics for query optimizer
ANALYZE;

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- Count indexes created
-- SELECT COUNT(*) as index_count FROM sqlite_master WHERE type='index' AND name LIKE 'idx_%';

-- List all indexes
-- SELECT name, tbl_name FROM sqlite_master WHERE type='index' AND name LIKE 'idx_%' ORDER BY tbl_name, name;

-- Check index usage (requires query execution)
-- EXPLAIN QUERY PLAN SELECT * FROM transactions WHERE date BETWEEN '2024-01-01' AND '2024-12-31';
