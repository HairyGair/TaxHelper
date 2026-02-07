# Tax Helper - Backend Architecture Plan

## Executive Summary

This document provides a comprehensive backend architecture plan for implementing 5 major features in the Tax Helper application:

1. **Bulk Operations** - Batch updates with audit trail and undo
2. **Smart Learning** - ML-based categorization improvement
3. **Progress Tracking** - Completion metrics and milestones
4. **Receipt Management** - File storage and management
5. **Search & Filter** - Indexed queries and saved presets

**Current Stack:**
- Database: SQLite (tax_helper.db)
- ORM: SQLAlchemy
- Tables: 7 (transactions, income, expenses, mileage, donations, rules, settings)
- Backend: Python with Streamlit frontend

**Key Design Principles:**
- Backward compatibility (existing databases must work)
- Scalability (handle 50k+ transactions)
- Performance (sub-second queries with indexes)
- Data integrity (ACID compliance, constraints)
- Security (SQL injection prevention, file upload validation)

---

## 1. BULK OPERATIONS

### 1.1 Database Schema Changes

**New Table: `transaction_history`**
```sql
CREATE TABLE transaction_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_id INTEGER NOT NULL,
    change_type VARCHAR(20) NOT NULL,  -- 'INSERT', 'UPDATE', 'DELETE'
    field_name VARCHAR(100),           -- Which field changed (NULL for INSERT/DELETE)
    old_value TEXT,                    -- JSON for complex values
    new_value TEXT,                    -- JSON for complex values
    changed_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    changed_by VARCHAR(100) DEFAULT 'user',  -- Future: multi-user support
    batch_id VARCHAR(36),              -- UUID for bulk operations
    FOREIGN KEY (transaction_id) REFERENCES transactions(id) ON DELETE CASCADE
);

CREATE INDEX idx_transaction_history_txn ON transaction_history(transaction_id);
CREATE INDEX idx_transaction_history_batch ON transaction_history(batch_id);
CREATE INDEX idx_transaction_history_date ON transaction_history(changed_at);
```

**New Table: `bulk_operations`**
```sql
CREATE TABLE bulk_operations (
    id VARCHAR(36) PRIMARY KEY,        -- UUID
    operation_type VARCHAR(50) NOT NULL, -- 'BULK_UPDATE', 'BULK_DELETE', etc.
    description TEXT,
    records_affected INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'COMPLETED', -- 'COMPLETED', 'UNDONE'
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    undone_at DATETIME,
    filter_criteria TEXT,              -- JSON of filter used
    changes_summary TEXT               -- JSON of changes made
);

CREATE INDEX idx_bulk_ops_created ON bulk_operations(created_at);
```

**Modified Table: `transactions`**
```sql
-- Add columns for bulk operations tracking
ALTER TABLE transactions ADD COLUMN last_modified_at DATETIME;
ALTER TABLE transactions ADD COLUMN last_modified_by VARCHAR(100) DEFAULT 'user';
ALTER TABLE transactions ADD COLUMN version INTEGER DEFAULT 1;
```

### 1.2 SQLAlchemy Model Updates

**File: `/Users/anthony/Tax Helper/models.py`** (additions)

```python
import uuid
from datetime import datetime
from sqlalchemy import ForeignKey, Index
from sqlalchemy.orm import relationship

class TransactionHistory(Base):
    """
    Audit trail for all transaction changes
    Enables undo functionality and compliance tracking
    """
    __tablename__ = 'transaction_history'

    id = Column(Integer, primary_key=True, autoincrement=True)
    transaction_id = Column(Integer, ForeignKey('transactions.id', ondelete='CASCADE'), nullable=False)
    change_type = Column(String(20), nullable=False)  # INSERT, UPDATE, DELETE
    field_name = Column(String(100))  # NULL for INSERT/DELETE
    old_value = Column(Text)  # JSON for complex values
    new_value = Column(Text)  # JSON for complex values
    changed_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    changed_by = Column(String(100), default='user')
    batch_id = Column(String(36))  # UUID for bulk operations

    # Relationship
    transaction = relationship("Transaction", backref="history")

    __table_args__ = (
        Index('idx_transaction_history_txn', 'transaction_id'),
        Index('idx_transaction_history_batch', 'batch_id'),
        Index('idx_transaction_history_date', 'changed_at'),
    )


class BulkOperation(Base):
    """
    Track bulk operations for undo functionality
    """
    __tablename__ = 'bulk_operations'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    operation_type = Column(String(50), nullable=False)
    description = Column(Text)
    records_affected = Column(Integer, default=0)
    status = Column(String(20), default='COMPLETED')  # COMPLETED, UNDONE
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    undone_at = Column(DateTime)
    filter_criteria = Column(Text)  # JSON
    changes_summary = Column(Text)  # JSON

    __table_args__ = (
        Index('idx_bulk_ops_created', 'created_at'),
    )


# Update Transaction model to include audit fields
class Transaction(Base):
    # ... existing fields ...

    last_modified_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_modified_by = Column(String(100), default='user')
    version = Column(Integer, default=1)  # Optimistic locking
```

### 1.3 API/Function Signatures

**File: `/Users/anthony/Tax Helper/bulk_operations.py`** (NEW)

```python
"""
Bulk operations module for Tax Helper
Handles batch updates, audit trails, and undo functionality
"""

from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from datetime import datetime
import uuid
import json


def bulk_update_transactions(
    session: Session,
    transaction_ids: List[int],
    updates: Dict[str, Any],
    description: str = None
) -> Tuple[int, str]:
    """
    Update multiple transactions at once with audit trail

    Args:
        session: SQLAlchemy session
        transaction_ids: List of transaction IDs to update
        updates: Dictionary of field:value pairs to update
        description: Human-readable description of operation

    Returns:
        (records_affected, batch_id)

    Example:
        count, batch_id = bulk_update_transactions(
            session,
            [1, 2, 3],
            {'reviewed': True, 'guessed_type': 'Expense'},
            "Mark tech purchases as reviewed expenses"
        )
    """
    pass


def undo_bulk_operation(
    session: Session,
    batch_id: str
) -> int:
    """
    Undo a bulk operation by reverting all changes

    Args:
        session: SQLAlchemy session
        batch_id: UUID of the bulk operation to undo

    Returns:
        Number of records reverted

    Raises:
        ValueError: If batch_id not found or already undone
    """
    pass


def get_transaction_history(
    session: Session,
    transaction_id: int,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """
    Get change history for a specific transaction

    Args:
        session: SQLAlchemy session
        transaction_id: Transaction ID
        limit: Maximum number of history records to return

    Returns:
        List of history records (newest first)
    """
    pass


def get_bulk_operations(
    session: Session,
    limit: int = 20,
    status: str = None
) -> List[Dict[str, Any]]:
    """
    Get list of recent bulk operations

    Args:
        session: SQLAlchemy session
        limit: Maximum number of operations to return
        status: Filter by status ('COMPLETED', 'UNDONE')

    Returns:
        List of bulk operation records
    """
    pass


def record_change(
    session: Session,
    transaction_id: int,
    change_type: str,
    field_name: str = None,
    old_value: Any = None,
    new_value: Any = None,
    batch_id: str = None
) -> None:
    """
    Record a single change in the audit trail
    Internal helper function
    """
    pass
```

### 1.4 Data Migration Script

**File: `/Users/anthony/Tax Helper/migrations/001_add_bulk_operations.py`** (NEW)

```python
"""
Migration: Add bulk operations and audit trail support
Version: 001
Date: 2025-10-17
"""

import sqlite3
from datetime import datetime


def upgrade(db_path: str):
    """Apply migration"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Create transaction_history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transaction_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                transaction_id INTEGER NOT NULL,
                change_type VARCHAR(20) NOT NULL,
                field_name VARCHAR(100),
                old_value TEXT,
                new_value TEXT,
                changed_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                changed_by VARCHAR(100) DEFAULT 'user',
                batch_id VARCHAR(36),
                FOREIGN KEY (transaction_id) REFERENCES transactions(id) ON DELETE CASCADE
            )
        ''')

        # Create indexes
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_transaction_history_txn
            ON transaction_history(transaction_id)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_transaction_history_batch
            ON transaction_history(batch_id)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_transaction_history_date
            ON transaction_history(changed_at)
        ''')

        # Create bulk_operations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bulk_operations (
                id VARCHAR(36) PRIMARY KEY,
                operation_type VARCHAR(50) NOT NULL,
                description TEXT,
                records_affected INTEGER DEFAULT 0,
                status VARCHAR(20) DEFAULT 'COMPLETED',
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                undone_at DATETIME,
                filter_criteria TEXT,
                changes_summary TEXT
            )
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_bulk_ops_created
            ON bulk_operations(created_at)
        ''')

        # Add columns to transactions table (if not exist)
        try:
            cursor.execute('ALTER TABLE transactions ADD COLUMN last_modified_at DATETIME')
        except sqlite3.OperationalError:
            pass  # Column already exists

        try:
            cursor.execute('ALTER TABLE transactions ADD COLUMN last_modified_by VARCHAR(100) DEFAULT "user"')
        except sqlite3.OperationalError:
            pass

        try:
            cursor.execute('ALTER TABLE transactions ADD COLUMN version INTEGER DEFAULT 1')
        except sqlite3.OperationalError:
            pass

        # Update existing records
        cursor.execute('''
            UPDATE transactions
            SET last_modified_at = CURRENT_TIMESTAMP,
                version = 1
            WHERE last_modified_at IS NULL
        ''')

        conn.commit()
        print("✓ Migration 001 applied successfully")

    except Exception as e:
        conn.rollback()
        raise Exception(f"Migration 001 failed: {e}")

    finally:
        conn.close()


def downgrade(db_path: str):
    """Rollback migration"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        cursor.execute('DROP TABLE IF EXISTS transaction_history')
        cursor.execute('DROP TABLE IF EXISTS bulk_operations')

        # Note: SQLite doesn't support DROP COLUMN easily
        # You'd need to recreate the transactions table to remove columns

        conn.commit()
        print("✓ Migration 001 rolled back successfully")

    except Exception as e:
        conn.rollback()
        raise Exception(f"Rollback 001 failed: {e}")

    finally:
        conn.close()


if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print("Usage: python 001_add_bulk_operations.py <db_path>")
        sys.exit(1)

    upgrade(sys.argv[1])
```

### 1.5 Performance Optimization

1. **Indexes**: Already created on foreign keys and frequently queried columns
2. **Batch Processing**: Use `session.bulk_update_mappings()` for 100+ records
3. **Transaction Batching**: Wrap bulk operations in single transaction
4. **Lazy Loading**: Use `joinedload()` for related records

```python
# Example optimized bulk update
from sqlalchemy import update

def optimized_bulk_update(session, transaction_ids, updates):
    """Use SQLAlchemy Core for maximum performance"""
    stmt = (
        update(Transaction)
        .where(Transaction.id.in_(transaction_ids))
        .values(**updates)
    )
    result = session.execute(stmt)
    return result.rowcount
```

### 1.6 Data Integrity

1. **Foreign Key Constraints**: CASCADE on delete ensures orphaned records are removed
2. **Optimistic Locking**: Use `version` field to prevent concurrent update conflicts
3. **Transaction Isolation**: Use `session.begin_nested()` for savepoints
4. **Validation**: Check transaction IDs exist before bulk operations

```python
def validate_transaction_ids(session, transaction_ids):
    """Ensure all IDs exist before bulk operation"""
    existing = session.query(Transaction.id).filter(
        Transaction.id.in_(transaction_ids)
    ).all()
    existing_ids = {row.id for row in existing}
    invalid_ids = set(transaction_ids) - existing_ids

    if invalid_ids:
        raise ValueError(f"Invalid transaction IDs: {invalid_ids}")
```

---

## 2. SMART LEARNING

### 2.1 Database Schema Changes

**New Table: `merchant_mappings`**
```sql
CREATE TABLE merchant_mappings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    merchant_name VARCHAR(200) NOT NULL UNIQUE,  -- Normalized name
    raw_descriptions TEXT,                       -- JSON array of variants
    category VARCHAR(100) NOT NULL,
    is_personal BOOLEAN DEFAULT FALSE,
    confidence INTEGER DEFAULT 0,                -- 0-100
    usage_count INTEGER DEFAULT 0,               -- How many times applied
    correction_count INTEGER DEFAULT 0,          -- How many times user corrected
    last_used_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_merchant_name ON merchant_mappings(merchant_name);
CREATE INDEX idx_merchant_usage ON merchant_mappings(usage_count DESC);
```

**New Table: `categorization_corrections`**
```sql
CREATE TABLE categorization_corrections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_id INTEGER NOT NULL,
    merchant_name VARCHAR(200),
    original_category VARCHAR(100),
    corrected_category VARCHAR(100),
    original_is_personal BOOLEAN,
    corrected_is_personal BOOLEAN,
    correction_source VARCHAR(50),               -- 'USER_MANUAL', 'BULK_UPDATE', etc.
    corrected_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    applied_to_merchant BOOLEAN DEFAULT FALSE,   -- Whether this updated merchant_mappings
    FOREIGN KEY (transaction_id) REFERENCES transactions(id) ON DELETE CASCADE
);

CREATE INDEX idx_corrections_merchant ON categorization_corrections(merchant_name);
CREATE INDEX idx_corrections_date ON categorization_corrections(corrected_at);
```

**New Table: `similar_transactions`**
```sql
CREATE TABLE similar_transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_id INTEGER NOT NULL,
    similar_transaction_id INTEGER NOT NULL,
    similarity_score FLOAT NOT NULL,             -- 0.0 to 1.0
    similarity_type VARCHAR(50),                 -- 'MERCHANT', 'AMOUNT', 'PATTERN'
    computed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (transaction_id) REFERENCES transactions(id) ON DELETE CASCADE,
    FOREIGN KEY (similar_transaction_id) REFERENCES transactions(id) ON DELETE CASCADE,
    UNIQUE(transaction_id, similar_transaction_id)
);

CREATE INDEX idx_similar_txn ON similar_transactions(transaction_id);
CREATE INDEX idx_similar_score ON similar_transactions(similarity_score DESC);
```

### 2.2 SQLAlchemy Model Updates

**File: `/Users/anthony/Tax Helper/models.py`** (additions)

```python
class MerchantMapping(Base):
    """
    Learned merchant categorizations
    Built from user corrections and transaction patterns
    """
    __tablename__ = 'merchant_mappings'

    id = Column(Integer, primary_key=True, autoincrement=True)
    merchant_name = Column(String(200), nullable=False, unique=True)
    raw_descriptions = Column(Text)  # JSON array
    category = Column(String(100), nullable=False)
    is_personal = Column(Boolean, default=False)
    confidence = Column(Integer, default=0)  # 0-100
    usage_count = Column(Integer, default=0)
    correction_count = Column(Integer, default=0)
    last_used_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index('idx_merchant_name', 'merchant_name'),
        Index('idx_merchant_usage', 'usage_count'),
    )


class CategorizationCorrection(Base):
    """
    Track user corrections to learn from mistakes
    """
    __tablename__ = 'categorization_corrections'

    id = Column(Integer, primary_key=True, autoincrement=True)
    transaction_id = Column(Integer, ForeignKey('transactions.id', ondelete='CASCADE'), nullable=False)
    merchant_name = Column(String(200))
    original_category = Column(String(100))
    corrected_category = Column(String(100))
    original_is_personal = Column(Boolean)
    corrected_is_personal = Column(Boolean)
    correction_source = Column(String(50))  # USER_MANUAL, BULK_UPDATE, etc.
    corrected_at = Column(DateTime, default=datetime.utcnow)
    applied_to_merchant = Column(Boolean, default=False)

    transaction = relationship("Transaction")

    __table_args__ = (
        Index('idx_corrections_merchant', 'merchant_name'),
        Index('idx_corrections_date', 'corrected_at'),
    )


class SimilarTransaction(Base):
    """
    Pre-computed transaction similarity for bulk suggestions
    """
    __tablename__ = 'similar_transactions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    transaction_id = Column(Integer, ForeignKey('transactions.id', ondelete='CASCADE'), nullable=False)
    similar_transaction_id = Column(Integer, ForeignKey('transactions.id', ondelete='CASCADE'), nullable=False)
    similarity_score = Column(Float, nullable=False)  # 0.0 to 1.0
    similarity_type = Column(String(50))  # MERCHANT, AMOUNT, PATTERN
    computed_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index('idx_similar_txn', 'transaction_id'),
        Index('idx_similar_score', 'similarity_score'),
    )
```

### 2.3 API/Function Signatures

**File: `/Users/anthony/Tax Helper/smart_learning.py`** (NEW)

```python
"""
Smart learning module for Tax Helper
Learns from user corrections and suggests bulk categorizations
"""

from typing import List, Dict, Tuple, Optional
from sqlalchemy.orm import Session
from difflib import SequenceMatcher
import re


def normalize_merchant_name(description: str) -> str:
    """
    Extract normalized merchant name from transaction description

    Examples:
        "AMAZON.CO.UK 123456" -> "AMAZON"
        "TESCO STORE 1234" -> "TESCO"
        "PAYPAL *NETFLIX" -> "NETFLIX"

    Args:
        description: Raw transaction description

    Returns:
        Normalized merchant name
    """
    pass


def find_similar_transactions(
    session: Session,
    transaction_id: int,
    threshold: float = 0.8,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """
    Find transactions similar to given transaction

    Args:
        session: SQLAlchemy session
        transaction_id: Base transaction ID
        threshold: Minimum similarity score (0.0 to 1.0)
        limit: Maximum results to return

    Returns:
        List of similar transactions with similarity scores

    Example:
        [
            {
                'id': 123,
                'description': 'AMAZON.CO.UK Purchase',
                'similarity_score': 0.95,
                'similarity_type': 'MERCHANT',
                'guessed_category': 'Office costs'
            },
            ...
        ]
    """
    pass


def suggest_bulk_categorization(
    session: Session,
    merchant_name: str = None,
    transaction_ids: List[int] = None
) -> Dict[str, Any]:
    """
    Suggest categorization for similar uncategorized transactions

    Args:
        session: SQLAlchemy session
        merchant_name: Optional merchant to filter by
        transaction_ids: Optional specific transaction IDs

    Returns:
        Dictionary with suggestion details:
        {
            'merchant_name': 'AMAZON',
            'category': 'Office costs',
            'is_personal': False,
            'confidence': 85,
            'transaction_count': 15,
            'transaction_ids': [1, 2, 3, ...],
            'reasoning': 'Based on 12 previous corrections'
        }
    """
    pass


def record_correction(
    session: Session,
    transaction_id: int,
    old_category: str,
    new_category: str,
    old_is_personal: bool,
    new_is_personal: bool,
    source: str = 'USER_MANUAL'
) -> None:
    """
    Record a user correction and update merchant mappings

    Args:
        session: SQLAlchemy session
        transaction_id: Transaction that was corrected
        old_category: Original category
        new_category: Corrected category
        old_is_personal: Original is_personal flag
        new_is_personal: Corrected is_personal flag
        source: Source of correction
    """
    pass


def learn_from_corrections(
    session: Session,
    min_corrections: int = 3
) -> int:
    """
    Analyze corrections and update merchant mappings

    Args:
        session: SQLAlchemy session
        min_corrections: Minimum corrections needed to update mapping

    Returns:
        Number of merchant mappings updated
    """
    pass


def compute_similarities(
    session: Session,
    batch_size: int = 100
) -> int:
    """
    Pre-compute transaction similarities for faster suggestions
    Background job that should run periodically

    Args:
        session: SQLAlchemy session
        batch_size: Number of transactions to process per batch

    Returns:
        Number of similarity records created
    """
    pass


def get_merchant_stats(
    session: Session,
    merchant_name: str
) -> Dict[str, Any]:
    """
    Get statistics for a specific merchant

    Returns:
        {
            'total_transactions': 50,
            'categorized': 45,
            'uncategorized': 5,
            'most_common_category': 'Office costs',
            'confidence': 90,
            'correction_rate': 0.1  # 10% corrections
        }
    """
    pass
```

### 2.4 Data Migration Script

**File: `/Users/anthony/Tax Helper/migrations/002_add_smart_learning.py`** (NEW)

```python
"""
Migration: Add smart learning tables
Version: 002
Date: 2025-10-17
"""

import sqlite3


def upgrade(db_path: str):
    """Apply migration"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Create merchant_mappings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS merchant_mappings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                merchant_name VARCHAR(200) NOT NULL UNIQUE,
                raw_descriptions TEXT,
                category VARCHAR(100) NOT NULL,
                is_personal BOOLEAN DEFAULT FALSE,
                confidence INTEGER DEFAULT 0,
                usage_count INTEGER DEFAULT 0,
                correction_count INTEGER DEFAULT 0,
                last_used_at DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_merchant_name
            ON merchant_mappings(merchant_name)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_merchant_usage
            ON merchant_mappings(usage_count DESC)
        ''')

        # Create categorization_corrections table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categorization_corrections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                transaction_id INTEGER NOT NULL,
                merchant_name VARCHAR(200),
                original_category VARCHAR(100),
                corrected_category VARCHAR(100),
                original_is_personal BOOLEAN,
                corrected_is_personal BOOLEAN,
                correction_source VARCHAR(50),
                corrected_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                applied_to_merchant BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (transaction_id) REFERENCES transactions(id) ON DELETE CASCADE
            )
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_corrections_merchant
            ON categorization_corrections(merchant_name)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_corrections_date
            ON categorization_corrections(corrected_at)
        ''')

        # Create similar_transactions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS similar_transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                transaction_id INTEGER NOT NULL,
                similar_transaction_id INTEGER NOT NULL,
                similarity_score FLOAT NOT NULL,
                similarity_type VARCHAR(50),
                computed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (transaction_id) REFERENCES transactions(id) ON DELETE CASCADE,
                FOREIGN KEY (similar_transaction_id) REFERENCES transactions(id) ON DELETE CASCADE,
                UNIQUE(transaction_id, similar_transaction_id)
            )
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_similar_txn
            ON similar_transactions(transaction_id)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_similar_score
            ON similar_transactions(similarity_score DESC)
        ''')

        conn.commit()
        print("✓ Migration 002 applied successfully")

    except Exception as e:
        conn.rollback()
        raise Exception(f"Migration 002 failed: {e}")

    finally:
        conn.close()


def downgrade(db_path: str):
    """Rollback migration"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        cursor.execute('DROP TABLE IF EXISTS similar_transactions')
        cursor.execute('DROP TABLE IF EXISTS categorization_corrections')
        cursor.execute('DROP TABLE IF EXISTS merchant_mappings')

        conn.commit()
        print("✓ Migration 002 rolled back successfully")

    except Exception as e:
        conn.rollback()
        raise Exception(f"Rollback 002 failed: {e}")

    finally:
        conn.close()


if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print("Usage: python 002_add_smart_learning.py <db_path>")
        sys.exit(1)

    upgrade(sys.argv[1])
```

### 2.5 Performance Optimization

1. **Similarity Computation**: Run as background job, not on-demand
2. **Merchant Name Index**: B-tree index for fast lookups
3. **Caching**: Cache merchant mappings in memory (LRU cache)
4. **Batch Processing**: Compute similarities in batches of 100

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_cached_merchant_mapping(merchant_name: str) -> Optional[Dict]:
    """Cache frequently accessed merchant mappings"""
    # Query database and cache result
    pass
```

### 2.6 Data Integrity

1. **UNIQUE Constraint**: Prevent duplicate merchant names
2. **Cascade Deletes**: Remove corrections when transaction deleted
3. **Validation**: Ensure similarity scores are between 0.0 and 1.0
4. **Deduplication**: Prevent duplicate similarity records

---

## 3. PROGRESS TRACKING

### 3.1 Database Schema Changes

**New Table: `progress_metrics`**
```sql
CREATE TABLE progress_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    metric_name VARCHAR(100) NOT NULL,
    metric_value FLOAT NOT NULL,
    metric_unit VARCHAR(50),                     -- 'percentage', 'count', etc.
    computed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    tax_year VARCHAR(10),                        -- '2024/25'
    metadata TEXT                                -- JSON for additional context
);

CREATE INDEX idx_progress_metric_name ON progress_metrics(metric_name);
CREATE INDEX idx_progress_computed_at ON progress_metrics(computed_at);
CREATE INDEX idx_progress_tax_year ON progress_metrics(tax_year);
```

**New Table: `milestones`**
```sql
CREATE TABLE milestones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    category VARCHAR(50),                        -- 'REVIEW', 'CATEGORIZE', 'RECEIPTS', etc.
    target_value FLOAT,
    current_value FLOAT DEFAULT 0,
    unit VARCHAR(50),                            -- 'transactions', 'pounds', etc.
    is_completed BOOLEAN DEFAULT FALSE,
    completed_at DATETIME,
    due_date DATE,
    priority INTEGER DEFAULT 100,                -- Lower = higher priority
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_milestones_completed ON milestones(is_completed);
CREATE INDEX idx_milestones_due_date ON milestones(due_date);
CREATE INDEX idx_milestones_priority ON milestones(priority);
```

**New Table: `todos`**
```sql
CREATE TABLE todos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    category VARCHAR(50),
    priority VARCHAR(20) DEFAULT 'MEDIUM',       -- 'HIGH', 'MEDIUM', 'LOW'
    is_completed BOOLEAN DEFAULT FALSE,
    completed_at DATETIME,
    due_date DATE,
    transaction_id INTEGER,                      -- Optional link to transaction
    milestone_id INTEGER,                        -- Optional link to milestone
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (transaction_id) REFERENCES transactions(id) ON DELETE SET NULL,
    FOREIGN KEY (milestone_id) REFERENCES milestones(id) ON DELETE CASCADE
);

CREATE INDEX idx_todos_completed ON todos(is_completed);
CREATE INDEX idx_todos_priority ON todos(priority);
CREATE INDEX idx_todos_due_date ON todos(due_date);
```

### 3.2 SQLAlchemy Model Updates

**File: `/Users/anthony/Tax Helper/models.py`** (additions)

```python
class ProgressMetric(Base):
    """
    Store computed progress metrics over time
    Enables trending and historical analysis
    """
    __tablename__ = 'progress_metrics'

    id = Column(Integer, primary_key=True, autoincrement=True)
    metric_name = Column(String(100), nullable=False)
    metric_value = Column(Float, nullable=False)
    metric_unit = Column(String(50))
    computed_at = Column(DateTime, default=datetime.utcnow)
    tax_year = Column(String(10))
    metadata = Column(Text)  # JSON

    __table_args__ = (
        Index('idx_progress_metric_name', 'metric_name'),
        Index('idx_progress_computed_at', 'computed_at'),
        Index('idx_progress_tax_year', 'tax_year'),
    )


class Milestone(Base):
    """
    Track major goals and milestones
    """
    __tablename__ = 'milestones'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    category = Column(String(50))
    target_value = Column(Float)
    current_value = Column(Float, default=0)
    unit = Column(String(50))
    is_completed = Column(Boolean, default=False)
    completed_at = Column(DateTime)
    due_date = Column(Date)
    priority = Column(Integer, default=100)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    todos = relationship("Todo", back_populates="milestone")

    __table_args__ = (
        Index('idx_milestones_completed', 'is_completed'),
        Index('idx_milestones_due_date', 'due_date'),
        Index('idx_milestones_priority', 'priority'),
    )


class Todo(Base):
    """
    Action items for user to complete
    """
    __tablename__ = 'todos'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    category = Column(String(50))
    priority = Column(String(20), default='MEDIUM')
    is_completed = Column(Boolean, default=False)
    completed_at = Column(DateTime)
    due_date = Column(Date)
    transaction_id = Column(Integer, ForeignKey('transactions.id', ondelete='SET NULL'))
    milestone_id = Column(Integer, ForeignKey('milestones.id', ondelete='CASCADE'))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    transaction = relationship("Transaction")
    milestone = relationship("Milestone", back_populates="todos")

    __table_args__ = (
        Index('idx_todos_completed', 'is_completed'),
        Index('idx_todos_priority', 'priority'),
        Index('idx_todos_due_date', 'due_date'),
    )
```

### 3.3 API/Function Signatures

**File: `/Users/anthony/Tax Helper/progress_tracking.py`** (NEW)

```python
"""
Progress tracking module for Tax Helper
Calculate completion metrics, track milestones, generate todos
"""

from typing import List, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime, date


def calculate_all_metrics(
    session: Session,
    tax_year: str = None
) -> Dict[str, Any]:
    """
    Calculate all progress metrics

    Returns:
        {
            'transactions_reviewed': {'value': 450, 'total': 500, 'percentage': 90.0},
            'transactions_categorized': {'value': 475, 'total': 500, 'percentage': 95.0},
            'expenses_with_receipts': {'value': 120, 'total': 200, 'percentage': 60.0},
            'income_recorded': {'value': 15000.0, 'unit': 'GBP'},
            'expenses_recorded': {'value': 8000.0, 'unit': 'GBP'},
            'completion_overall': 85.5
        }
    """
    pass


def update_milestones(session: Session) -> int:
    """
    Update progress for all active milestones

    Returns:
        Number of milestones updated
    """
    pass


def generate_todos(
    session: Session,
    category: str = None
) -> List[Dict[str, Any]]:
    """
    Generate actionable todos based on current state

    Examples of generated todos:
        - "Review 50 uncategorized transactions"
        - "Add receipts for 10 large expenses (>£100)"
        - "Categorize Amazon purchases (15 transactions)"

    Args:
        session: SQLAlchemy session
        category: Filter by category

    Returns:
        List of todo items
    """
    pass


def get_dashboard_summary(
    session: Session,
    tax_year: str = None
) -> Dict[str, Any]:
    """
    Get comprehensive dashboard summary

    Returns:
        {
            'metrics': {...},
            'milestones': [...],
            'todos': [...],
            'alerts': [...],
            'recommendations': [...]
        }
    """
    pass


def record_metric(
    session: Session,
    metric_name: str,
    metric_value: float,
    metric_unit: str = None,
    tax_year: str = None,
    metadata: Dict = None
) -> None:
    """
    Record a progress metric for historical tracking
    """
    pass


def get_metric_history(
    session: Session,
    metric_name: str,
    days: int = 30
) -> List[Dict[str, Any]]:
    """
    Get historical data for a metric

    Returns:
        [
            {'date': '2025-10-01', 'value': 75.5},
            {'date': '2025-10-08', 'value': 82.3},
            ...
        ]
    """
    pass
```

### 3.4 Data Migration Script

**File: `/Users/anthony/Tax Helper/migrations/003_add_progress_tracking.py`** (NEW)

```python
"""
Migration: Add progress tracking tables
Version: 003
Date: 2025-10-17
"""

import sqlite3
from datetime import datetime, date, timedelta


def upgrade(db_path: str):
    """Apply migration"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Create progress_metrics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS progress_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_name VARCHAR(100) NOT NULL,
                metric_value FLOAT NOT NULL,
                metric_unit VARCHAR(50),
                computed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                tax_year VARCHAR(10),
                metadata TEXT
            )
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_progress_metric_name
            ON progress_metrics(metric_name)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_progress_computed_at
            ON progress_metrics(computed_at)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_progress_tax_year
            ON progress_metrics(tax_year)
        ''')

        # Create milestones table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS milestones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title VARCHAR(200) NOT NULL,
                description TEXT,
                category VARCHAR(50),
                target_value FLOAT,
                current_value FLOAT DEFAULT 0,
                unit VARCHAR(50),
                is_completed BOOLEAN DEFAULT FALSE,
                completed_at DATETIME,
                due_date DATE,
                priority INTEGER DEFAULT 100,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_milestones_completed
            ON milestones(is_completed)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_milestones_due_date
            ON milestones(due_date)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_milestones_priority
            ON milestones(priority)
        ''')

        # Create todos table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS todos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title VARCHAR(200) NOT NULL,
                description TEXT,
                category VARCHAR(50),
                priority VARCHAR(20) DEFAULT 'MEDIUM',
                is_completed BOOLEAN DEFAULT FALSE,
                completed_at DATETIME,
                due_date DATE,
                transaction_id INTEGER,
                milestone_id INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (transaction_id) REFERENCES transactions(id) ON DELETE SET NULL,
                FOREIGN KEY (milestone_id) REFERENCES milestones(id) ON DELETE CASCADE
            )
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_todos_completed
            ON todos(is_completed)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_todos_priority
            ON todos(priority)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_todos_due_date
            ON todos(due_date)
        ''')

        # Seed default milestones
        tax_year_end = date(2026, 4, 5)  # Assuming 2025/26 tax year

        default_milestones = [
            ('Review all transactions', 'Review and categorize all imported transactions', 'REVIEW', 100, 0, 'percentage', tax_year_end, 10),
            ('Add receipts for large expenses', 'Add receipts for all expenses over £100', 'RECEIPTS', 100, 0, 'percentage', tax_year_end, 20),
            ('Complete tax return', 'Submit self-assessment tax return', 'FILING', 1, 0, 'tasks', tax_year_end, 5),
        ]

        for title, desc, cat, target, current, unit, due, priority in default_milestones:
            cursor.execute('''
                INSERT INTO milestones
                (title, description, category, target_value, current_value, unit, due_date, priority)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (title, desc, cat, target, current, unit, due, priority))

        conn.commit()
        print("✓ Migration 003 applied successfully")

    except Exception as e:
        conn.rollback()
        raise Exception(f"Migration 003 failed: {e}")

    finally:
        conn.close()


def downgrade(db_path: str):
    """Rollback migration"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        cursor.execute('DROP TABLE IF EXISTS todos')
        cursor.execute('DROP TABLE IF EXISTS milestones')
        cursor.execute('DROP TABLE IF EXISTS progress_metrics')

        conn.commit()
        print("✓ Migration 003 rolled back successfully")

    except Exception as e:
        conn.rollback()
        raise Exception(f"Rollback 003 failed: {e}")

    finally:
        conn.close()


if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print("Usage: python 003_add_progress_tracking.py <db_path>")
        sys.exit(1)

    upgrade(sys.argv[1])
```

### 3.5 Performance Optimization

1. **Denormalization**: Store computed values in `milestones.current_value`
2. **Caching**: Cache metrics for 5 minutes to avoid recomputation
3. **Aggregation**: Use SQLAlchemy's `func.count()` and `func.sum()` for efficiency
4. **Background Jobs**: Compute metrics periodically, not on every page load

```python
import time
from functools import wraps

_metrics_cache = {}
_cache_duration = 300  # 5 minutes

def cached_metrics(func):
    """Cache decorator for expensive metric calculations"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        cache_key = f"{func.__name__}_{kwargs.get('tax_year', 'all')}"

        if cache_key in _metrics_cache:
            cached_value, cached_time = _metrics_cache[cache_key]
            if time.time() - cached_time < _cache_duration:
                return cached_value

        result = func(*args, **kwargs)
        _metrics_cache[cache_key] = (result, time.time())
        return result

    return wrapper
```

### 3.6 Data Integrity

1. **Referential Integrity**: Todos link to transactions/milestones with proper FK constraints
2. **Computed Values**: Milestones auto-update when related data changes
3. **Validation**: Ensure percentages are 0-100, priorities are positive
4. **Soft Deletes**: Completed todos/milestones are marked, not deleted

---

## 4. RECEIPT MANAGEMENT

### 4.1 Database Schema Changes

**New Table: `receipts`**
```sql
CREATE TABLE receipts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL UNIQUE,
    file_size INTEGER NOT NULL,                  -- Bytes
    file_type VARCHAR(50) NOT NULL,              -- 'image/jpeg', 'application/pdf', etc.
    file_hash VARCHAR(64) NOT NULL UNIQUE,       -- SHA-256 for deduplication
    uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    uploaded_by VARCHAR(100) DEFAULT 'user',
    metadata TEXT                                -- JSON (OCR text, dimensions, etc.)
);

CREATE INDEX idx_receipts_hash ON receipts(file_hash);
CREATE INDEX idx_receipts_uploaded ON receipts(uploaded_at);
```

**New Table: `expense_receipts`**
```sql
CREATE TABLE expense_receipts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    expense_id INTEGER NOT NULL,
    receipt_id INTEGER NOT NULL,
    is_primary BOOLEAN DEFAULT FALSE,            -- Primary receipt for expense
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (expense_id) REFERENCES expenses(id) ON DELETE CASCADE,
    FOREIGN KEY (receipt_id) REFERENCES receipts(id) ON DELETE CASCADE,
    UNIQUE(expense_id, receipt_id)
);

CREATE INDEX idx_expense_receipts_expense ON expense_receipts(expense_id);
CREATE INDEX idx_expense_receipts_receipt ON expense_receipts(receipt_id);
```

**Modified Table: `expenses`**
```sql
-- Deprecate receipt_link column (keep for backward compatibility)
-- New receipts stored in receipts table
ALTER TABLE expenses ADD COLUMN receipt_count INTEGER DEFAULT 0;
```

### 4.2 SQLAlchemy Model Updates

**File: `/Users/anthony/Tax Helper/models.py`** (additions)

```python
import hashlib
from sqlalchemy.orm import backref


class Receipt(Base):
    """
    Store uploaded receipt files
    """
    __tablename__ = 'receipts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False, unique=True)
    file_size = Column(Integer, nullable=False)  # Bytes
    file_type = Column(String(50), nullable=False)  # MIME type
    file_hash = Column(String(64), nullable=False, unique=True)  # SHA-256
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    uploaded_by = Column(String(100), default='user')
    metadata = Column(Text)  # JSON (OCR text, etc.)

    # Relationships
    expenses = relationship(
        "Expense",
        secondary="expense_receipts",
        back_populates="receipt_files"
    )

    __table_args__ = (
        Index('idx_receipts_hash', 'file_hash'),
        Index('idx_receipts_uploaded', 'uploaded_at'),
    )


class ExpenseReceipt(Base):
    """
    Many-to-many relationship between expenses and receipts
    """
    __tablename__ = 'expense_receipts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    expense_id = Column(Integer, ForeignKey('expenses.id', ondelete='CASCADE'), nullable=False)
    receipt_id = Column(Integer, ForeignKey('receipts.id', ondelete='CASCADE'), nullable=False)
    is_primary = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index('idx_expense_receipts_expense', 'expense_id'),
        Index('idx_expense_receipts_receipt', 'receipt_id'),
    )


# Update Expense model
class Expense(Base):
    # ... existing fields ...

    receipt_count = Column(Integer, default=0)

    # New relationship for file-based receipts
    receipt_files = relationship(
        "Receipt",
        secondary="expense_receipts",
        back_populates="expenses"
    )
```

### 4.3 API/Function Signatures

**File: `/Users/anthony/Tax Helper/receipt_management.py`** (NEW)

```python
"""
Receipt management module for Tax Helper
Handle file uploads, storage, linking, and retrieval
"""

from typing import List, Dict, Any, Optional, BinaryIO
from sqlalchemy.orm import Session
import hashlib
import os
from pathlib import Path
import mimetypes


class ReceiptStorage:
    """
    Handle file storage operations
    Supports local filesystem and cloud storage (extensible)
    """

    def __init__(self, base_path: str = None):
        """
        Initialize receipt storage

        Args:
            base_path: Base directory for storing receipts
                      Default: ./receipts/
        """
        self.base_path = base_path or os.path.join(os.getcwd(), 'receipts')
        os.makedirs(self.base_path, exist_ok=True)

    def save_file(
        self,
        file_content: bytes,
        file_name: str
    ) -> Tuple[str, str, int]:
        """
        Save file to storage and return path, hash, size

        Args:
            file_content: Raw file bytes
            file_name: Original filename

        Returns:
            (file_path, file_hash, file_size)
        """
        pass

    def get_file(self, file_path: str) -> bytes:
        """Retrieve file contents"""
        pass

    def delete_file(self, file_path: str) -> bool:
        """Delete file from storage"""
        pass


def upload_receipt(
    session: Session,
    file_content: bytes,
    file_name: str,
    expense_id: int = None,
    storage: ReceiptStorage = None
) -> Dict[str, Any]:
    """
    Upload a receipt file and optionally link to expense

    Args:
        session: SQLAlchemy session
        file_content: Raw file bytes
        file_name: Original filename
        expense_id: Optional expense ID to link to
        storage: Storage handler (uses default if None)

    Returns:
        {
            'receipt_id': 123,
            'file_path': 'receipts/2025/10/abc123.pdf',
            'file_hash': 'sha256...',
            'is_duplicate': False
        }

    Raises:
        ValueError: If file type not allowed or file too large
    """
    pass


def link_receipt_to_expense(
    session: Session,
    receipt_id: int,
    expense_id: int,
    is_primary: bool = False
) -> None:
    """
    Link existing receipt to an expense

    Args:
        session: SQLAlchemy session
        receipt_id: Receipt ID
        expense_id: Expense ID
        is_primary: Whether this is the primary receipt
    """
    pass


def unlink_receipt_from_expense(
    session: Session,
    receipt_id: int,
    expense_id: int
) -> None:
    """Remove receipt link from expense"""
    pass


def get_expense_receipts(
    session: Session,
    expense_id: int
) -> List[Dict[str, Any]]:
    """
    Get all receipts for an expense

    Returns:
        [
            {
                'id': 123,
                'file_name': 'invoice.pdf',
                'file_size': 45678,
                'file_type': 'application/pdf',
                'uploaded_at': '2025-10-17 10:30:00',
                'is_primary': True,
                'download_url': '/api/receipts/123/download'
            },
            ...
        ]
    """
    pass


def get_orphaned_receipts(
    session: Session,
    days_old: int = 30
) -> List[Dict[str, Any]]:
    """
    Find receipts not linked to any expense
    Useful for cleanup

    Args:
        session: SQLAlchemy session
        days_old: Only return receipts older than N days

    Returns:
        List of orphaned receipt records
    """
    pass


def delete_receipt(
    session: Session,
    receipt_id: int,
    storage: ReceiptStorage = None
) -> bool:
    """
    Delete receipt file and database record
    Only succeeds if receipt has no expense links

    Args:
        session: SQLAlchemy session
        receipt_id: Receipt ID to delete
        storage: Storage handler

    Returns:
        True if deleted, False if has links

    Raises:
        ValueError: If receipt doesn't exist
    """
    pass


def calculate_file_hash(file_content: bytes) -> str:
    """Calculate SHA-256 hash of file content"""
    return hashlib.sha256(file_content).hexdigest()


def validate_file(
    file_content: bytes,
    file_name: str,
    max_size_mb: int = 10
) -> Tuple[bool, Optional[str]]:
    """
    Validate uploaded file

    Args:
        file_content: Raw file bytes
        file_name: Original filename
        max_size_mb: Maximum allowed file size

    Returns:
        (is_valid, error_message)

    Checks:
        - File size <= max_size_mb
        - File type in allowed list (jpg, png, pdf)
        - Not empty file
    """
    pass


# Allowed file types
ALLOWED_FILE_TYPES = {
    'image/jpeg': ['.jpg', '.jpeg'],
    'image/png': ['.png'],
    'application/pdf': ['.pdf'],
}

MAX_FILE_SIZE_MB = 10
```

### 4.4 Data Migration Script

**File: `/Users/anthony/Tax Helper/migrations/004_add_receipt_management.py`** (NEW)

```python
"""
Migration: Add receipt management tables
Version: 004
Date: 2025-10-17
"""

import sqlite3
import os


def upgrade(db_path: str):
    """Apply migration"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Create receipts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS receipts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_name VARCHAR(255) NOT NULL,
                file_path VARCHAR(500) NOT NULL UNIQUE,
                file_size INTEGER NOT NULL,
                file_type VARCHAR(50) NOT NULL,
                file_hash VARCHAR(64) NOT NULL UNIQUE,
                uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                uploaded_by VARCHAR(100) DEFAULT 'user',
                metadata TEXT
            )
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_receipts_hash
            ON receipts(file_hash)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_receipts_uploaded
            ON receipts(uploaded_at)
        ''')

        # Create expense_receipts junction table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS expense_receipts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                expense_id INTEGER NOT NULL,
                receipt_id INTEGER NOT NULL,
                is_primary BOOLEAN DEFAULT FALSE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (expense_id) REFERENCES expenses(id) ON DELETE CASCADE,
                FOREIGN KEY (receipt_id) REFERENCES receipts(id) ON DELETE CASCADE,
                UNIQUE(expense_id, receipt_id)
            )
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_expense_receipts_expense
            ON expense_receipts(expense_id)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_expense_receipts_receipt
            ON expense_receipts(receipt_id)
        ''')

        # Add receipt_count to expenses table
        try:
            cursor.execute('ALTER TABLE expenses ADD COLUMN receipt_count INTEGER DEFAULT 0')
        except sqlite3.OperationalError:
            pass  # Column already exists

        # Update receipt_count for existing expenses with receipt_link
        cursor.execute('''
            UPDATE expenses
            SET receipt_count = 1
            WHERE receipt_link IS NOT NULL AND receipt_link != ''
        ''')

        # Create receipts directory
        base_dir = os.path.dirname(db_path)
        receipts_dir = os.path.join(base_dir, 'receipts')
        os.makedirs(receipts_dir, exist_ok=True)

        conn.commit()
        print("✓ Migration 004 applied successfully")
        print(f"  Receipts directory: {receipts_dir}")

    except Exception as e:
        conn.rollback()
        raise Exception(f"Migration 004 failed: {e}")

    finally:
        conn.close()


def downgrade(db_path: str):
    """Rollback migration"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        cursor.execute('DROP TABLE IF EXISTS expense_receipts')
        cursor.execute('DROP TABLE IF EXISTS receipts')

        # Note: Cannot easily remove receipt_count column in SQLite

        conn.commit()
        print("✓ Migration 004 rolled back successfully")

    except Exception as e:
        conn.rollback()
        raise Exception(f"Rollback 004 failed: {e}")

    finally:
        conn.close()


if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print("Usage: python 004_add_receipt_management.py <db_path>")
        sys.exit(1)

    upgrade(sys.argv[1])
```

### 4.5 Performance Optimization

1. **File Hash Index**: Fast duplicate detection
2. **Lazy Loading**: Don't load file contents unless requested
3. **Thumbnail Generation**: Store thumbnails for image files
4. **CDN**: Use cloud storage (S3, CloudFlare R2) for production

```python
# Example: Generate thumbnails for images
from PIL import Image
import io

def generate_thumbnail(file_content: bytes, max_size: tuple = (200, 200)) -> bytes:
    """Generate thumbnail for image files"""
    img = Image.open(io.BytesIO(file_content))
    img.thumbnail(max_size)

    thumb_buffer = io.BytesIO()
    img.save(thumb_buffer, format='JPEG', quality=85)
    return thumb_buffer.getvalue()
```

### 4.6 Data Integrity & Security

1. **File Hash**: SHA-256 prevents duplicates and ensures integrity
2. **File Type Validation**: Whitelist allowed MIME types
3. **File Size Limits**: Prevent DoS via large uploads
4. **Path Sanitization**: Prevent directory traversal attacks
5. **Foreign Keys**: CASCADE deletes clean up orphaned files
6. **Virus Scanning**: Consider ClamAV for production

```python
import re

def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent directory traversal
    Remove dangerous characters
    """
    # Remove path separators
    filename = os.path.basename(filename)

    # Remove dangerous characters
    filename = re.sub(r'[^\w\s.-]', '', filename)

    # Limit length
    name, ext = os.path.splitext(filename)
    if len(name) > 100:
        name = name[:100]

    return name + ext
```

---

## 5. SEARCH & FILTER

### 5.1 Database Schema Changes

**New Table: `saved_filters`**
```sql
CREATE TABLE saved_filters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    entity_type VARCHAR(50) NOT NULL,             -- 'transactions', 'expenses', etc.
    filter_criteria TEXT NOT NULL,                -- JSON filter definition
    is_default BOOLEAN DEFAULT FALSE,
    usage_count INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_used_at DATETIME
);

CREATE INDEX idx_saved_filters_entity ON saved_filters(entity_type);
CREATE INDEX idx_saved_filters_usage ON saved_filters(usage_count DESC);
```

**Modified Tables: Add indexes for common queries**
```sql
-- Transactions indexes (for search performance)
CREATE INDEX idx_transactions_date ON transactions(date);
CREATE INDEX idx_transactions_reviewed ON transactions(reviewed);
CREATE INDEX idx_transactions_is_personal ON transactions(is_personal);
CREATE INDEX idx_transactions_guessed_type ON transactions(guessed_type);
CREATE INDEX idx_transactions_account ON transactions(account_name);

-- Full-text search index for descriptions (SQLite FTS5)
CREATE VIRTUAL TABLE transactions_fts USING fts5(
    description,
    content=transactions,
    content_rowid=id
);

-- Triggers to keep FTS index updated
CREATE TRIGGER transactions_fts_insert AFTER INSERT ON transactions BEGIN
    INSERT INTO transactions_fts(rowid, description) VALUES (new.id, new.description);
END;

CREATE TRIGGER transactions_fts_update AFTER UPDATE ON transactions BEGIN
    UPDATE transactions_fts SET description = new.description WHERE rowid = new.id;
END;

CREATE TRIGGER transactions_fts_delete AFTER DELETE ON transactions BEGIN
    DELETE FROM transactions_fts WHERE rowid = old.id;
END;

-- Expenses indexes
CREATE INDEX idx_expenses_date ON expenses(date);
CREATE INDEX idx_expenses_category ON expenses(category);
CREATE INDEX idx_expenses_amount ON expenses(amount);
CREATE INDEX idx_expenses_supplier ON expenses(supplier);

-- Income indexes
CREATE INDEX idx_income_date ON income(date);
CREATE INDEX idx_income_type ON income(income_type);
CREATE INDEX idx_income_amount ON income(amount_gross);
```

### 5.2 SQLAlchemy Model Updates

**File: `/Users/anthony/Tax Helper/models.py`** (additions)

```python
class SavedFilter(Base):
    """
    User-defined saved filter presets
    """
    __tablename__ = 'saved_filters'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    entity_type = Column(String(50), nullable=False)  # transactions, expenses, etc.
    filter_criteria = Column(Text, nullable=False)  # JSON
    is_default = Column(Boolean, default=False)
    usage_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_used_at = Column(DateTime)

    __table_args__ = (
        Index('idx_saved_filters_entity', 'entity_type'),
        Index('idx_saved_filters_usage', 'usage_count'),
    )


# Add indexes to existing models (in __table_args__)
class Transaction(Base):
    # ... existing fields ...

    __table_args__ = (
        Index('idx_transactions_date', 'date'),
        Index('idx_transactions_reviewed', 'reviewed'),
        Index('idx_transactions_is_personal', 'is_personal'),
        Index('idx_transactions_guessed_type', 'guessed_type'),
        Index('idx_transactions_account', 'account_name'),
    )
```

### 5.3 API/Function Signatures

**File: `/Users/anthony/Tax Helper/search_filter.py`** (NEW)

```python
"""
Search and filter module for Tax Helper
Advanced querying with saved presets and full-text search
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session, Query
from sqlalchemy import and_, or_, not_, func
from datetime import date, datetime
import json


class FilterBuilder:
    """
    Build complex SQLAlchemy queries from filter criteria
    """

    def __init__(self, model):
        """
        Initialize filter builder

        Args:
            model: SQLAlchemy model class (Transaction, Expense, etc.)
        """
        self.model = model
        self.filters = []

    def add_date_range(
        self,
        start_date: date = None,
        end_date: date = None,
        field_name: str = 'date'
    ) -> 'FilterBuilder':
        """Add date range filter"""
        pass

    def add_amount_range(
        self,
        min_amount: float = None,
        max_amount: float = None,
        field_name: str = 'amount'
    ) -> 'FilterBuilder':
        """Add amount range filter"""
        pass

    def add_text_search(
        self,
        search_text: str,
        fields: List[str] = None,
        use_fts: bool = True
    ) -> 'FilterBuilder':
        """
        Add text search filter

        Args:
            search_text: Text to search for
            fields: Fields to search in (default: all text fields)
            use_fts: Use full-text search if available
        """
        pass

    def add_category_filter(
        self,
        categories: List[str],
        field_name: str = 'category'
    ) -> 'FilterBuilder':
        """Filter by categories (IN clause)"""
        pass

    def add_boolean_filter(
        self,
        field_name: str,
        value: bool
    ) -> 'FilterBuilder':
        """Filter by boolean field"""
        pass

    def build(self, session: Session) -> Query:
        """
        Build final SQLAlchemy query

        Returns:
            SQLAlchemy Query object ready for execution
        """
        pass


def search_transactions(
    session: Session,
    search_text: str = None,
    date_from: date = None,
    date_to: date = None,
    min_amount: float = None,
    max_amount: float = None,
    categories: List[str] = None,
    is_personal: bool = None,
    reviewed: bool = None,
    account_name: str = None,
    limit: int = 100,
    offset: int = 0,
    order_by: str = 'date',
    order_dir: str = 'desc'
) -> Tuple[List[Dict[str, Any]], int]:
    """
    Search transactions with complex filters

    Returns:
        (results_list, total_count)

    Example:
        results, total = search_transactions(
            session,
            search_text='amazon',
            date_from=date(2025, 4, 6),
            date_to=date(2026, 4, 5),
            categories=['Office costs', 'Travel'],
            reviewed=False,
            limit=50
        )
    """
    pass


def search_expenses(
    session: Session,
    search_text: str = None,
    date_from: date = None,
    date_to: date = None,
    min_amount: float = None,
    max_amount: float = None,
    categories: List[str] = None,
    has_receipt: bool = None,
    supplier: str = None,
    limit: int = 100,
    offset: int = 0
) -> Tuple[List[Dict[str, Any]], int]:
    """Search expenses with filters"""
    pass


def save_filter(
    session: Session,
    name: str,
    entity_type: str,
    filter_criteria: Dict[str, Any],
    description: str = None,
    is_default: bool = False
) -> int:
    """
    Save filter preset for future use

    Args:
        session: SQLAlchemy session
        name: Filter name
        entity_type: 'transactions', 'expenses', etc.
        filter_criteria: Filter parameters as dict
        description: Optional description
        is_default: Set as default filter for entity type

    Returns:
        Saved filter ID

    Example:
        filter_id = save_filter(
            session,
            name='Unreviewed Business Expenses',
            entity_type='transactions',
            filter_criteria={
                'reviewed': False,
                'is_personal': False,
                'guessed_type': 'Expense'
            }
        )
    """
    pass


def load_filter(
    session: Session,
    filter_id: int
) -> Dict[str, Any]:
    """Load saved filter by ID"""
    pass


def list_saved_filters(
    session: Session,
    entity_type: str = None
) -> List[Dict[str, Any]]:
    """
    List all saved filters

    Args:
        session: SQLAlchemy session
        entity_type: Filter by entity type

    Returns:
        List of filter records
    """
    pass


def delete_filter(
    session: Session,
    filter_id: int
) -> bool:
    """Delete saved filter"""
    pass


def get_filter_suggestions(
    session: Session,
    entity_type: str = 'transactions'
) -> List[Dict[str, Any]]:
    """
    Get suggested filters based on data

    Examples:
        - "Large expenses (>£500)"
        - "Uncategorized transactions"
        - "Missing receipts"

    Returns:
        List of suggested filter definitions
    """
    pass


def execute_filter(
    session: Session,
    filter_id: int,
    limit: int = 100,
    offset: int = 0
) -> Tuple[List[Dict[str, Any]], int]:
    """
    Execute a saved filter
    Updates usage_count and last_used_at

    Returns:
        (results_list, total_count)
    """
    pass
```

### 5.4 Data Migration Script

**File: `/Users/anthony/Tax Helper/migrations/005_add_search_filter.py`** (NEW)

```python
"""
Migration: Add search & filter support with FTS
Version: 005
Date: 2025-10-17
"""

import sqlite3


def upgrade(db_path: str):
    """Apply migration"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Create saved_filters table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS saved_filters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) NOT NULL,
                description TEXT,
                entity_type VARCHAR(50) NOT NULL,
                filter_criteria TEXT NOT NULL,
                is_default BOOLEAN DEFAULT FALSE,
                usage_count INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_used_at DATETIME
            )
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_saved_filters_entity
            ON saved_filters(entity_type)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_saved_filters_usage
            ON saved_filters(usage_count DESC)
        ''')

        # Add indexes to transactions table
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_transactions_date
            ON transactions(date)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_transactions_reviewed
            ON transactions(reviewed)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_transactions_is_personal
            ON transactions(is_personal)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_transactions_guessed_type
            ON transactions(guessed_type)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_transactions_account
            ON transactions(account_name)
        ''')

        # Create FTS5 virtual table for full-text search
        cursor.execute('''
            CREATE VIRTUAL TABLE IF NOT EXISTS transactions_fts
            USING fts5(description, content=transactions, content_rowid=id)
        ''')

        # Populate FTS index with existing data
        cursor.execute('''
            INSERT INTO transactions_fts(rowid, description)
            SELECT id, description FROM transactions
        ''')

        # Create triggers to keep FTS index updated
        cursor.execute('''
            CREATE TRIGGER IF NOT EXISTS transactions_fts_insert
            AFTER INSERT ON transactions BEGIN
                INSERT INTO transactions_fts(rowid, description)
                VALUES (new.id, new.description);
            END
        ''')

        cursor.execute('''
            CREATE TRIGGER IF NOT EXISTS transactions_fts_update
            AFTER UPDATE ON transactions BEGIN
                UPDATE transactions_fts
                SET description = new.description
                WHERE rowid = new.id;
            END
        ''')

        cursor.execute('''
            CREATE TRIGGER IF NOT EXISTS transactions_fts_delete
            AFTER DELETE ON transactions BEGIN
                DELETE FROM transactions_fts WHERE rowid = old.id;
            END
        ''')

        # Add indexes to expenses table
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_expenses_date
            ON expenses(date)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_expenses_category
            ON expenses(category)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_expenses_amount
            ON expenses(amount)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_expenses_supplier
            ON expenses(supplier)
        ''')

        # Add indexes to income table
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_income_date
            ON income(date)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_income_type
            ON income(income_type)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_income_amount
            ON income(amount_gross)
        ''')

        # Seed default filters
        default_filters = [
            ('Unreviewed Transactions', 'transactions',
             '{"reviewed": false}', 'Transactions that need review'),
            ('Business Expenses', 'transactions',
             '{"is_personal": false, "guessed_type": "Expense"}',
             'All business expense transactions'),
            ('Personal Transactions', 'transactions',
             '{"is_personal": true}', 'All personal transactions'),
            ('Large Expenses', 'expenses',
             '{"min_amount": 500}', 'Expenses over £500'),
            ('Missing Receipts', 'expenses',
             '{"receipt_count": 0}', 'Expenses without receipts'),
        ]

        for name, entity, criteria, desc in default_filters:
            cursor.execute('''
                INSERT INTO saved_filters (name, entity_type, filter_criteria, description)
                VALUES (?, ?, ?, ?)
            ''', (name, entity, criteria, desc))

        conn.commit()
        print("✓ Migration 005 applied successfully")
        print("  Full-text search enabled for transaction descriptions")
        print(f"  {len(default_filters)} default filters created")

    except Exception as e:
        conn.rollback()
        raise Exception(f"Migration 005 failed: {e}")

    finally:
        conn.close()


def downgrade(db_path: str):
    """Rollback migration"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Drop triggers
        cursor.execute('DROP TRIGGER IF EXISTS transactions_fts_insert')
        cursor.execute('DROP TRIGGER IF EXISTS transactions_fts_update')
        cursor.execute('DROP TRIGGER IF EXISTS transactions_fts_delete')

        # Drop FTS table
        cursor.execute('DROP TABLE IF EXISTS transactions_fts')

        # Drop saved_filters table
        cursor.execute('DROP TABLE IF EXISTS saved_filters')

        # Drop indexes (SQLite doesn't error if they don't exist)
        cursor.execute('DROP INDEX IF EXISTS idx_transactions_date')
        cursor.execute('DROP INDEX IF EXISTS idx_transactions_reviewed')
        cursor.execute('DROP INDEX IF EXISTS idx_transactions_is_personal')
        cursor.execute('DROP INDEX IF EXISTS idx_transactions_guessed_type')
        cursor.execute('DROP INDEX IF EXISTS idx_transactions_account')
        cursor.execute('DROP INDEX IF EXISTS idx_expenses_date')
        cursor.execute('DROP INDEX IF EXISTS idx_expenses_category')
        cursor.execute('DROP INDEX IF EXISTS idx_expenses_amount')
        cursor.execute('DROP INDEX IF EXISTS idx_expenses_supplier')
        cursor.execute('DROP INDEX IF EXISTS idx_income_date')
        cursor.execute('DROP INDEX IF EXISTS idx_income_type')
        cursor.execute('DROP INDEX IF EXISTS idx_income_amount')

        conn.commit()
        print("✓ Migration 005 rolled back successfully")

    except Exception as e:
        conn.rollback()
        raise Exception(f"Rollback 005 failed: {e}")

    finally:
        conn.close()


if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print("Usage: python 005_add_search_filter.py <db_path>")
        sys.exit(1)

    upgrade(sys.argv[1])
```

### 5.5 Performance Optimization

1. **Full-Text Search**: SQLite FTS5 for fast text searches (10x faster than LIKE)
2. **Composite Indexes**: Multi-column indexes for common query patterns
3. **Query Planning**: Use EXPLAIN QUERY PLAN to optimize slow queries
4. **Pagination**: Always use LIMIT/OFFSET for large result sets
5. **Index-Only Scans**: Select only indexed columns when possible

```python
# Example: Query optimization with indexes
def get_unreviewed_business_expenses(session):
    """
    Optimized query using composite index
    Uses idx_transactions_reviewed and idx_transactions_is_personal
    """
    query = session.query(Transaction).filter(
        and_(
            Transaction.reviewed == False,
            Transaction.is_personal == False,
            Transaction.guessed_type == 'Expense'
        )
    ).order_by(Transaction.date.desc())

    return query.all()


# Example: Full-text search with FTS5
def fts_search_transactions(session, search_text):
    """
    Use FTS5 for fast text search
    Much faster than: WHERE description LIKE '%search%'
    """
    # Execute raw SQL for FTS
    sql = """
        SELECT t.*
        FROM transactions t
        JOIN transactions_fts fts ON t.id = fts.rowid
        WHERE transactions_fts MATCH ?
        ORDER BY rank
        LIMIT 100
    """
    result = session.execute(sql, [search_text])
    return result.fetchall()
```

### 5.6 Data Integrity

1. **JSON Validation**: Validate filter_criteria JSON before saving
2. **Entity Type Enum**: Restrict entity_type to known values
3. **Unique Constraint**: Prevent duplicate similar_transactions records
4. **Cascading Updates**: FTS triggers keep index synchronized

---

## CROSS-CUTTING CONCERNS

### Migration Manager

**File: `/Users/anthony/Tax Helper/migration_manager.py`** (NEW)

```python
"""
Database migration manager
Tracks and applies migrations in order
"""

import sqlite3
import importlib
import os
from pathlib import Path
from typing import List


def create_migrations_table(db_path: str):
    """Create table to track applied migrations"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version INTEGER PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            applied_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()


def get_applied_migrations(db_path: str) -> List[int]:
    """Get list of applied migration versions"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('SELECT version FROM schema_migrations ORDER BY version')
    versions = [row[0] for row in cursor.fetchall()]

    conn.close()
    return versions


def get_pending_migrations(db_path: str, migrations_dir: str) -> List[tuple]:
    """Get list of pending migrations"""
    applied = get_applied_migrations(db_path)

    # Find all migration files
    migrations_path = Path(migrations_dir)
    migration_files = sorted(migrations_path.glob('*.py'))

    pending = []
    for file_path in migration_files:
        if file_path.stem == '__init__':
            continue

        # Extract version from filename (e.g., '001_add_bulk_operations.py' -> 1)
        try:
            version = int(file_path.stem.split('_')[0])
            if version not in applied:
                pending.append((version, file_path.stem, str(file_path)))
        except (ValueError, IndexError):
            continue

    return pending


def apply_migration(db_path: str, migration_path: str, version: int, name: str):
    """Apply a single migration"""
    # Import migration module
    spec = importlib.util.spec_from_file_location("migration", migration_path)
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)

    # Run upgrade
    migration.upgrade(db_path)

    # Record migration
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO schema_migrations (version, name)
        VALUES (?, ?)
    ''', (version, name))

    conn.commit()
    conn.close()


def migrate(db_path: str, migrations_dir: str = None):
    """Apply all pending migrations"""
    if migrations_dir is None:
        migrations_dir = os.path.join(os.path.dirname(__file__), 'migrations')

    create_migrations_table(db_path)
    pending = get_pending_migrations(db_path, migrations_dir)

    if not pending:
        print("✓ Database is up to date")
        return

    print(f"Found {len(pending)} pending migration(s)")

    for version, name, path in pending:
        print(f"Applying migration {version:03d}: {name}...")
        apply_migration(db_path, path, version, name)

    print(f"✓ Successfully applied {len(pending)} migration(s)")


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print("Usage: python migration_manager.py <db_path>")
        sys.exit(1)

    migrate(sys.argv[1])
```

### Testing Strategy

**File: `/Users/anthony/Tax Helper/tests/test_bulk_operations.py`** (NEW)

```python
"""
Unit tests for bulk operations module
"""

import unittest
import tempfile
import os
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Base, Transaction, BulkOperation, TransactionHistory
from bulk_operations import (
    bulk_update_transactions,
    undo_bulk_operation,
    get_transaction_history
)


class TestBulkOperations(unittest.TestCase):

    def setUp(self):
        """Create temporary database for testing"""
        self.db_fd, self.db_path = tempfile.mkstemp()
        engine = create_engine(f'sqlite:///{self.db_path}')
        Base.metadata.create_all(engine)

        Session = sessionmaker(bind=engine)
        self.session = Session()

        # Create test transactions
        for i in range(5):
            txn = Transaction(
                date=datetime(2025, 10, i+1),
                description=f'Test Transaction {i}',
                paid_out=100.0,
                reviewed=False
            )
            self.session.add(txn)

        self.session.commit()

    def tearDown(self):
        """Clean up test database"""
        self.session.close()
        os.close(self.db_fd)
        os.unlink(self.db_path)

    def test_bulk_update(self):
        """Test bulk update functionality"""
        # Get transaction IDs
        txn_ids = [1, 2, 3]

        # Perform bulk update
        count, batch_id = bulk_update_transactions(
            self.session,
            txn_ids,
            {'reviewed': True, 'guessed_type': 'Expense'}
        )

        # Verify update
        self.assertEqual(count, 3)
        self.assertIsNotNone(batch_id)

        # Check transactions were updated
        for txn_id in txn_ids:
            txn = self.session.query(Transaction).get(txn_id)
            self.assertTrue(txn.reviewed)
            self.assertEqual(txn.guessed_type, 'Expense')

    def test_undo_operation(self):
        """Test undo functionality"""
        # Perform bulk update
        count, batch_id = bulk_update_transactions(
            self.session,
            [1, 2],
            {'reviewed': True}
        )

        # Undo operation
        reverted = undo_bulk_operation(self.session, batch_id)

        self.assertEqual(reverted, 2)

        # Verify transactions reverted
        for txn_id in [1, 2]:
            txn = self.session.query(Transaction).get(txn_id)
            self.assertFalse(txn.reviewed)

    def test_transaction_history(self):
        """Test audit trail recording"""
        # Update a transaction
        bulk_update_transactions(
            self.session,
            [1],
            {'reviewed': True}
        )

        # Get history
        history = get_transaction_history(self.session, 1)

        self.assertGreater(len(history), 0)
        self.assertEqual(history[0]['field_name'], 'reviewed')


if __name__ == '__main__':
    unittest.main()
```

### API Documentation

**File: `/Users/anthony/Tax Helper/API_DOCUMENTATION.md`** (NEW)

```markdown
# Tax Helper API Documentation

## Overview

This document describes the backend API functions for the Tax Helper application.

## Bulk Operations API

### `bulk_update_transactions()`

Update multiple transactions in a single operation with audit trail.

**Parameters:**
- `session` (Session): SQLAlchemy database session
- `transaction_ids` (List[int]): Transaction IDs to update
- `updates` (Dict[str, Any]): Field:value pairs to update
- `description` (str, optional): Human-readable description

**Returns:**
- `Tuple[int, str]`: (records_affected, batch_id)

**Example:**
```python
count, batch_id = bulk_update_transactions(
    session,
    [1, 2, 3, 4, 5],
    {
        'reviewed': True,
        'guessed_type': 'Expense',
        'guessed_category': 'Office costs'
    },
    "Mark office supply purchases as reviewed"
)
print(f"Updated {count} transactions (batch: {batch_id})")
```

**Raises:**
- `ValueError`: If transaction IDs don't exist

### `undo_bulk_operation()`

Revert a bulk operation using its batch ID.

**Parameters:**
- `session` (Session): SQLAlchemy database session
- `batch_id` (str): UUID of bulk operation

**Returns:**
- `int`: Number of records reverted

**Example:**
```python
reverted = undo_bulk_operation(session, batch_id)
print(f"Reverted {reverted} records")
```

## Smart Learning API

### `find_similar_transactions()`

Find transactions similar to a given transaction.

**Parameters:**
- `session` (Session): SQLAlchemy database session
- `transaction_id` (int): Base transaction ID
- `threshold` (float, optional): Similarity threshold (0.0-1.0), default 0.8
- `limit` (int, optional): Max results, default 50

**Returns:**
- `List[Dict]`: Similar transactions with scores

**Example:**
```python
similar = find_similar_transactions(session, 123, threshold=0.85)
for txn in similar:
    print(f"ID {txn['id']}: {txn['description']} (score: {txn['similarity_score']})")
```

## Progress Tracking API

### `calculate_all_metrics()`

Calculate all progress metrics for dashboard.

**Parameters:**
- `session` (Session): SQLAlchemy database session
- `tax_year` (str, optional): Tax year filter (e.g., '2024/25')

**Returns:**
- `Dict[str, Any]`: All metrics and percentages

**Example:**
```python
metrics = calculate_all_metrics(session, '2024/25')
print(f"Overall completion: {metrics['completion_overall']}%")
print(f"Reviewed: {metrics['transactions_reviewed']['percentage']}%")
```

## Receipt Management API

### `upload_receipt()`

Upload a receipt file and optionally link to expense.

**Parameters:**
- `session` (Session): SQLAlchemy database session
- `file_content` (bytes): Raw file bytes
- `file_name` (str): Original filename
- `expense_id` (int, optional): Expense to link to
- `storage` (ReceiptStorage, optional): Storage handler

**Returns:**
- `Dict[str, Any]`: Receipt metadata

**Example:**
```python
with open('receipt.pdf', 'rb') as f:
    receipt = upload_receipt(
        session,
        f.read(),
        'receipt.pdf',
        expense_id=456
    )
print(f"Uploaded receipt {receipt['receipt_id']}")
```

**Raises:**
- `ValueError`: If file invalid or too large

## Search & Filter API

### `search_transactions()`

Search transactions with complex filters.

**Parameters:**
- `session` (Session): SQLAlchemy database session
- `search_text` (str, optional): Text search
- `date_from` (date, optional): Start date
- `date_to` (date, optional): End date
- `min_amount` (float, optional): Minimum amount
- `max_amount` (float, optional): Maximum amount
- `categories` (List[str], optional): Category filter
- `is_personal` (bool, optional): Personal/business filter
- `reviewed` (bool, optional): Reviewed filter
- `limit` (int, optional): Results limit, default 100
- `offset` (int, optional): Pagination offset, default 0

**Returns:**
- `Tuple[List[Dict], int]`: (results, total_count)

**Example:**
```python
results, total = search_transactions(
    session,
    search_text='amazon',
    date_from=date(2025, 4, 6),
    categories=['Office costs'],
    reviewed=False,
    limit=50
)
print(f"Found {total} transactions, showing {len(results)}")
```

## Error Handling

All API functions use standard Python exceptions:

- `ValueError`: Invalid input parameters
- `FileNotFoundError`: Receipt file not found
- `sqlite3.IntegrityError`: Database constraint violation

Always wrap API calls in try-except blocks:

```python
try:
    count, batch_id = bulk_update_transactions(session, ids, updates)
except ValueError as e:
    print(f"Error: {e}")
```

## Performance Notes

- Bulk operations use single transaction for ACID compliance
- Search uses FTS5 for text searches (10x faster than LIKE)
- All queries support pagination via limit/offset
- Cached metrics expire after 5 minutes
```

---

## DEPLOYMENT CHECKLIST

### Pre-Deployment

1. **Backup Database**
   ```bash
   cp tax_helper.db tax_helper.db.backup
   ```

2. **Run Migrations**
   ```bash
   python migration_manager.py tax_helper.db
   ```

3. **Verify Migrations**
   ```bash
   sqlite3 tax_helper.db ".schema"
   ```

4. **Run Tests**
   ```bash
   python -m pytest tests/ -v
   ```

### Post-Deployment

1. **Monitor Performance**
   - Check query times for searches
   - Monitor file storage growth
   - Review error logs

2. **Optimize Indexes**
   ```sql
   ANALYZE;  -- Update SQLite query planner statistics
   ```

3. **Cleanup**
   - Delete orphaned receipts
   - Archive old audit records
   - Vacuum database

### Scaling Considerations

**50k Transactions:**
- Expected DB size: ~50MB
- Search response: <100ms with indexes
- Bulk update 1000 records: <2s

**Recommendations:**
1. Enable WAL mode for concurrent reads
   ```sql
   PRAGMA journal_mode=WAL;
   ```

2. Increase cache size
   ```sql
   PRAGMA cache_size=10000;  -- 40MB cache
   ```

3. Consider PostgreSQL if >100k transactions

### Security Checklist

- [ ] File uploads validated (type, size)
- [ ] Filenames sanitized (no directory traversal)
- [ ] SQL injection prevented (parameterized queries)
- [ ] File storage outside web root
- [ ] Database backups encrypted
- [ ] Audit trail enabled for compliance

---

## BACKWARD COMPATIBILITY

All migrations are designed to be backward compatible:

1. **Column Additions**: New columns have defaults
2. **Table Additions**: Existing tables unchanged
3. **Index Additions**: Don't affect functionality
4. **Deprecations**: Old fields kept (receipt_link)

**Upgrade Path:**
```bash
# Backup
cp tax_helper.db tax_helper.db.backup

# Run migrations
python migration_manager.py tax_helper.db

# Test application
python app.py

# If issues, rollback
cp tax_helper.db.backup tax_helper.db
```

---

## FILE STORAGE STRATEGY

### Local Storage (Development)

```
/Users/anthony/Tax Helper/
├── tax_helper.db
├── receipts/
│   ├── 2025/
│   │   ├── 10/
│   │   │   ├── abc123.pdf
│   │   │   ├── def456.jpg
│   │   └── 11/
│   └── 2026/
```

**Pros:**
- Simple, no external dependencies
- Fast access
- No API costs

**Cons:**
- Not scalable beyond single server
- Backup complexity
- No CDN

### Cloud Storage (Production)

Recommended: **AWS S3** or **CloudFlare R2**

```python
# Example S3 integration
import boto3

class S3ReceiptStorage(ReceiptStorage):
    def __init__(self, bucket_name):
        self.s3 = boto3.client('s3')
        self.bucket = bucket_name

    def save_file(self, file_content, file_name):
        key = f"receipts/{datetime.now().year}/{file_hash[:8]}_{file_name}"
        self.s3.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=file_content
        )
        return key

    def get_file(self, file_path):
        obj = self.s3.get_object(Bucket=self.bucket, Key=file_path)
        return obj['Body'].read()
```

**Pros:**
- Unlimited storage
- Built-in redundancy
- CDN integration
- Automatic backups

**Cons:**
- API latency
- Costs (minimal for small scale)
- External dependency

---

## NEXT STEPS

1. **Implement Core Functions**
   - Start with bulk_operations.py
   - Add unit tests
   - Integrate with Streamlit UI

2. **Run Migrations**
   - Apply all 5 migrations
   - Test on sample database
   - Verify backward compatibility

3. **Build UI Components**
   - Bulk edit interface
   - Progress dashboard
   - Receipt upload widget
   - Advanced search page

4. **Performance Testing**
   - Load 10k test transactions
   - Benchmark search queries
   - Profile bulk operations

5. **Documentation**
   - User guide for new features
   - Admin guide for maintenance
   - API examples

---

## SUMMARY

This architecture plan provides:

- **5 New Modules**: bulk_operations.py, smart_learning.py, progress_tracking.py, receipt_management.py, search_filter.py
- **13 New Tables**: Full schema with indexes and relationships
- **5 Migrations**: Backward-compatible database upgrades
- **Comprehensive APIs**: Well-documented functions with examples
- **Testing Strategy**: Unit tests and integration tests
- **Deployment Guide**: Step-by-step instructions
- **Scalability**: Handles 50k+ transactions efficiently
- **Security**: Input validation, SQL injection prevention

**Total Lines of Code: ~3,000**
**Estimated Implementation Time: 40-60 hours**

All designs follow SQLAlchemy best practices, maintain ACID compliance, and prioritize performance through strategic indexing.
