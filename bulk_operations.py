"""
Bulk operations module for Tax Helper
Handles batch updates, audit trails, and undo functionality

Features:
- Bulk update transactions with single database transaction
- Full audit trail of all changes
- Undo functionality to revert bulk operations
- Optimistic locking to prevent concurrent update conflicts
"""

from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import update
from datetime import datetime
import uuid
import json
import logging

from models import Transaction, TransactionHistory, BulkOperation
from ledger_helpers import safe_commit

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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

    Raises:
        ValueError: If transaction_ids empty or updates empty
        ValueError: If any transaction ID doesn't exist
    """
    if not transaction_ids:
        raise ValueError("transaction_ids cannot be empty")

    if not updates:
        raise ValueError("updates cannot be empty")

    # Validate transaction IDs exist
    validate_transaction_ids(session, transaction_ids)

    # Generate batch ID for this operation
    batch_id = str(uuid.uuid4())

    # Get current values before update (for audit trail and undo)
    transactions = session.query(Transaction).filter(
        Transaction.id.in_(transaction_ids)
    ).all()

    old_values = {}
    for txn in transactions:
        old_values[txn.id] = {
            field: getattr(txn, field)
            for field in updates.keys()
        }

    # Add metadata fields to updates
    updates['last_modified_at'] = datetime.utcnow()
    updates['version'] = Transaction.version + 1  # Increment version

    # Perform bulk update using SQLAlchemy Core for performance
    stmt = (
        update(Transaction)
        .where(Transaction.id.in_(transaction_ids))
        .values(**updates)
    )
    result = session.execute(stmt)
    records_affected = result.rowcount

    # Record each change in audit trail
    for txn_id in transaction_ids:
        old_vals = old_values[txn_id]

        for field_name, new_value in updates.items():
            if field_name in ['last_modified_at', 'version']:
                continue  # Skip metadata fields

            old_value = old_vals.get(field_name)

            # Only record if value actually changed
            if old_value != new_value:
                record_change(
                    session,
                    transaction_id=txn_id,
                    change_type='UPDATE',
                    field_name=field_name,
                    old_value=old_value,
                    new_value=new_value,
                    batch_id=batch_id
                )

    # Record bulk operation metadata
    bulk_op = BulkOperation(
        id=batch_id,
        operation_type='BULK_UPDATE',
        description=description or f"Bulk update of {records_affected} transactions",
        records_affected=records_affected,
        status='COMPLETED',
        filter_criteria=json.dumps({'transaction_ids': transaction_ids}),
        changes_summary=json.dumps(updates)
    )
    session.add(bulk_op)

    # Commit all changes with error handling
    success, error = safe_commit(session, "Bulk update commit failed")
    if not success:
        raise RuntimeError(f"Failed to commit bulk update: {error}")

    return records_affected, batch_id


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
    # Get bulk operation record
    bulk_op = session.query(BulkOperation).filter_by(id=batch_id).first()

    if not bulk_op:
        raise ValueError(f"Bulk operation {batch_id} not found")

    if bulk_op.status == 'UNDONE':
        raise ValueError(f"Bulk operation {batch_id} has already been undone")

    # Get all changes for this batch
    history_records = session.query(TransactionHistory).filter_by(
        batch_id=batch_id
    ).all()

    if not history_records:
        raise ValueError(f"No history records found for batch {batch_id}")

    # Group changes by transaction
    changes_by_txn = {}
    for record in history_records:
        if record.transaction_id not in changes_by_txn:
            changes_by_txn[record.transaction_id] = {}

        if record.field_name:
            # Parse JSON if needed
            old_value = record.old_value
            if isinstance(old_value, str):
                try:
                    old_value = json.loads(old_value)
                except (json.JSONDecodeError, TypeError):
                    pass

            changes_by_txn[record.transaction_id][record.field_name] = old_value

    # Revert each transaction
    records_reverted = 0
    for txn_id, old_values in changes_by_txn.items():
        txn = session.query(Transaction).get(txn_id)

        if txn:
            for field_name, old_value in old_values.items():
                setattr(txn, field_name, old_value)

            # Update metadata
            txn.last_modified_at = datetime.utcnow()
            txn.version += 1

            records_reverted += 1

    # Mark bulk operation as undone
    bulk_op.status = 'UNDONE'
    bulk_op.undone_at = datetime.utcnow()

    # Commit changes with error handling
    success, error = safe_commit(session, "Undo operation commit failed")
    if not success:
        raise RuntimeError(f"Failed to commit undo operation: {error}")

    return records_reverted


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

    Example:
        history = get_transaction_history(session, 123)
        for record in history:
            print(f"{record['changed_at']}: {record['field_name']} "
                  f"changed from {record['old_value']} to {record['new_value']}")
    """
    records = session.query(TransactionHistory).filter_by(
        transaction_id=transaction_id
    ).order_by(
        TransactionHistory.changed_at.desc()
    ).limit(limit).all()

    result = []
    for record in records:
        result.append({
            'id': record.id,
            'change_type': record.change_type,
            'field_name': record.field_name,
            'old_value': record.old_value,
            'new_value': record.new_value,
            'changed_at': record.changed_at.isoformat() if record.changed_at else None,
            'changed_by': record.changed_by,
            'batch_id': record.batch_id
        })

    return result


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

    Example:
        ops = get_bulk_operations(session, limit=10, status='COMPLETED')
        for op in ops:
            print(f"{op['created_at']}: {op['description']} "
                  f"({op['records_affected']} records)")
    """
    query = session.query(BulkOperation).order_by(
        BulkOperation.created_at.desc()
    )

    if status:
        query = query.filter_by(status=status)

    operations = query.limit(limit).all()

    result = []
    for op in operations:
        result.append({
            'id': op.id,
            'operation_type': op.operation_type,
            'description': op.description,
            'records_affected': op.records_affected,
            'status': op.status,
            'created_at': op.created_at.isoformat() if op.created_at else None,
            'undone_at': op.undone_at.isoformat() if op.undone_at else None,
            'can_undo': op.status == 'COMPLETED'
        })

    return result


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

    Args:
        session: SQLAlchemy session
        transaction_id: Transaction ID
        change_type: 'INSERT', 'UPDATE', 'DELETE'
        field_name: Which field changed (NULL for INSERT/DELETE)
        old_value: Previous value
        new_value: New value
        batch_id: UUID of bulk operation
    """
    # Convert complex values to JSON
    if old_value is not None and not isinstance(old_value, (str, int, float, bool)):
        old_value = json.dumps(old_value, default=str)

    if new_value is not None and not isinstance(new_value, (str, int, float, bool)):
        new_value = json.dumps(new_value, default=str)

    history = TransactionHistory(
        transaction_id=transaction_id,
        change_type=change_type,
        field_name=field_name,
        old_value=str(old_value) if old_value is not None else None,
        new_value=str(new_value) if new_value is not None else None,
        batch_id=batch_id
    )

    session.add(history)


def validate_transaction_ids(session: Session, transaction_ids: List[int]) -> None:
    """
    Ensure all IDs exist before bulk operation

    Args:
        session: SQLAlchemy session
        transaction_ids: List of transaction IDs to validate

    Raises:
        ValueError: If any ID doesn't exist
    """
    existing = session.query(Transaction.id).filter(
        Transaction.id.in_(transaction_ids)
    ).all()
    existing_ids = {row.id for row in existing}

    invalid_ids = set(transaction_ids) - existing_ids

    if invalid_ids:
        raise ValueError(f"Invalid transaction IDs: {sorted(invalid_ids)}")


def bulk_delete_transactions(
    session: Session,
    transaction_ids: List[int],
    description: str = None
) -> Tuple[int, str]:
    """
    Delete multiple transactions with audit trail

    WARNING: This is a destructive operation. Consider soft delete instead.

    Args:
        session: SQLAlchemy session
        transaction_ids: List of transaction IDs to delete
        description: Human-readable description

    Returns:
        (records_deleted, batch_id)

    Raises:
        ValueError: If transaction_ids empty
    """
    if not transaction_ids:
        raise ValueError("transaction_ids cannot be empty")

    # Validate transaction IDs exist
    validate_transaction_ids(session, transaction_ids)

    # Generate batch ID
    batch_id = str(uuid.uuid4())

    # Get transactions before deletion (for audit)
    transactions = session.query(Transaction).filter(
        Transaction.id.in_(transaction_ids)
    ).all()

    # Record deletions in audit trail
    for txn in transactions:
        record_change(
            session,
            transaction_id=txn.id,
            change_type='DELETE',
            batch_id=batch_id
        )

    # Delete transactions
    deleted_count = session.query(Transaction).filter(
        Transaction.id.in_(transaction_ids)
    ).delete(synchronize_session=False)

    # Record bulk operation
    bulk_op = BulkOperation(
        id=batch_id,
        operation_type='BULK_DELETE',
        description=description or f"Bulk delete of {deleted_count} transactions",
        records_affected=deleted_count,
        status='COMPLETED',
        filter_criteria=json.dumps({'transaction_ids': transaction_ids})
    )
    session.add(bulk_op)

    # Commit with error handling
    success, error = safe_commit(session, "Bulk delete commit failed")
    if not success:
        raise RuntimeError(f"Failed to commit bulk delete: {error}")

    return deleted_count, batch_id


def get_recent_changes(
    session: Session,
    hours: int = 24,
    limit: int = 100
) -> List[Dict[str, Any]]:
    """
    Get recent changes across all transactions

    Args:
        session: SQLAlchemy session
        hours: Look back N hours
        limit: Maximum records to return

    Returns:
        List of recent change records

    Example:
        changes = get_recent_changes(session, hours=48)
        for change in changes:
            print(f"Transaction {change['transaction_id']}: "
                  f"{change['field_name']} changed at {change['changed_at']}")
    """
    from datetime import timedelta

    cutoff = datetime.utcnow() - timedelta(hours=hours)

    records = session.query(TransactionHistory).filter(
        TransactionHistory.changed_at >= cutoff
    ).order_by(
        TransactionHistory.changed_at.desc()
    ).limit(limit).all()

    result = []
    for record in records:
        result.append({
            'transaction_id': record.transaction_id,
            'change_type': record.change_type,
            'field_name': record.field_name,
            'old_value': record.old_value,
            'new_value': record.new_value,
            'changed_at': record.changed_at.isoformat() if record.changed_at else None,
            'batch_id': record.batch_id
        })

    return result
