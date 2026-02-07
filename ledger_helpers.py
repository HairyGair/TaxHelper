"""
Shared ledger posting logic for Tax Helper
Extracts duplicate code from app.py and bulk_operations.py
"""

from datetime import datetime
from typing import Optional
import logging

from models import Transaction, Income, Expense

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def safe_commit(session, error_message="Database commit failed"):
    """
    Safely commit database changes with error handling

    Args:
        session: Database session
        error_message: Custom error message for logging

    Returns:
        tuple: (success: bool, error: Optional[str])
    """
    try:
        session.commit()
        return True, None
    except Exception as e:
        session.rollback()
        error_msg = f"{error_message}: {str(e)}"
        logger.error(error_msg)
        return False, error_msg


def post_transaction_to_ledger(
    txn: Transaction,
    category: str,
    txn_type: str,
    session,
    check_duplicates: bool = True
) -> tuple[bool, Optional[str]]:
    """
    Post a transaction to the appropriate ledger (Income or Expense)

    Args:
        txn: Transaction object
        category: Category for the ledger entry
        txn_type: 'Income' or 'Expense'
        session: Database session
        check_duplicates: Whether to check for duplicate entries

    Returns:
        tuple: (success: bool, error_message: Optional[str])
    """
    try:
        if txn_type == 'Income' and txn.paid_in > 0:
            return _post_to_income_ledger(txn, category, session, check_duplicates)
        elif txn_type == 'Expense' and txn.paid_out > 0:
            return _post_to_expense_ledger(txn, category, session, check_duplicates)
        else:
            return False, f"Invalid transaction type or amount: {txn_type}"

    except Exception as e:
        error_msg = f"Failed to post transaction {txn.id} to ledger: {str(e)}"
        logger.error(error_msg)
        return False, error_msg


def _post_to_income_ledger(
    txn: Transaction,
    category: str,
    session,
    check_duplicates: bool
) -> tuple[bool, Optional[str]]:
    """
    Post transaction to Income ledger

    Args:
        txn: Transaction object
        category: Income category/type
        session: Database session
        check_duplicates: Whether to check for duplicates

    Returns:
        tuple: (success: bool, error_message: Optional[str])
    """
    if check_duplicates:
        # Check for duplicates
        existing = session.query(Income).filter(
            Income.date == txn.date,
            Income.source == txn.description,
            Income.amount_gross == txn.paid_in
        ).first()

        if existing:
            return True, None  # Already exists, skip

    # Create new income record
    income_record = Income(
        date=txn.date,
        source=txn.description,
        description=txn.notes or '',
        amount_gross=txn.paid_in,
        tax_deducted=0.0,
        income_type=category or 'Other'
    )
    session.add(income_record)
    logger.info(f"Posted income transaction {txn.id} to ledger")
    return True, None


def _post_to_expense_ledger(
    txn: Transaction,
    category: str,
    session,
    check_duplicates: bool
) -> tuple[bool, Optional[str]]:
    """
    Post transaction to Expense ledger

    Args:
        txn: Transaction object
        category: Expense category
        session: Database session
        check_duplicates: Whether to check for duplicates

    Returns:
        tuple: (success: bool, error_message: Optional[str])
    """
    if check_duplicates:
        # Check for duplicates
        existing = session.query(Expense).filter(
            Expense.date == txn.date,
            Expense.supplier == txn.description,
            Expense.amount == txn.paid_out
        ).first()

        if existing:
            return True, None  # Already exists, skip

    # Create new expense record
    expense_record = Expense(
        date=txn.date,
        supplier=txn.description,
        description=txn.notes or '',
        category=category or 'Other business expenses',
        amount=txn.paid_out,
        receipt_link=''
    )
    session.add(expense_record)
    logger.info(f"Posted expense transaction {txn.id} to ledger")
    return True, None


def bulk_post_to_ledger(
    transactions: list[Transaction],
    category: str,
    txn_type: str,
    session,
    check_duplicates: bool = True
) -> tuple[int, int, list[str]]:
    """
    Post multiple transactions to ledger in bulk

    Args:
        transactions: List of Transaction objects
        category: Category for all transactions
        txn_type: 'Income' or 'Expense'
        session: Database session
        check_duplicates: Whether to check for duplicates

    Returns:
        tuple: (success_count: int, failure_count: int, errors: list[str])
    """
    success_count = 0
    failure_count = 0
    errors = []

    for txn in transactions:
        success, error = post_transaction_to_ledger(
            txn, category, txn_type, session, check_duplicates
        )

        if success:
            success_count += 1
        else:
            failure_count += 1
            if error:
                errors.append(f"Transaction {txn.id}: {error}")

    return success_count, failure_count, errors


def update_transaction_categorization(
    txn: Transaction,
    category: str,
    txn_type: str,
    is_personal: bool = False,
    reviewed: bool = True
) -> None:
    """
    Update transaction categorization fields

    Args:
        txn: Transaction object to update
        category: Category to assign
        txn_type: 'Income' or 'Expense'
        is_personal: Whether transaction is personal
        reviewed: Whether transaction has been reviewed
    """
    txn.is_personal = is_personal
    txn.guessed_type = txn_type
    txn.guessed_category = category
    txn.reviewed = reviewed
    txn.last_modified_at = datetime.utcnow()
