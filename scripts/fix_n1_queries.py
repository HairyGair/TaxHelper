#!/usr/bin/env python3
"""
Script to fix N+1 query problems in app.py
This script applies all necessary fixes for bulk operations
"""

import re

def fix_app_py():
    """Fix N+1 queries in app.py"""

    with open('/Users/anthony/Tax Helper/app.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # Fix 1: Bulk review - Mark as Reviewed
    old_pattern1 = r'''                if bulk_action == "Mark as Reviewed":
                    for txn_id in selected_ids:
                        txn = session\.query\(Transaction\)\.get\(txn_id\)
                        if txn:
                            txn\.reviewed = True
                    session\.commit\(\)'''

    new_pattern1 = '''                if bulk_action == "Mark as Reviewed":
                    # Bulk update using filter().in_() - avoids N+1 query problem
                    session.query(Transaction).filter(Transaction.id.in_(selected_ids)).update(
                        {Transaction.reviewed: True},
                        synchronize_session=False
                    )
                    session.commit()'''

    content = re.sub(old_pattern1, new_pattern1, content, flags=re.MULTILINE)

    # Fix 2: Bulk delete transactions
    old_pattern2 = r'''                        # Perform delete with progress indicator
                        with st\.spinner\(f"Deleting \{len\(selected_ids\)\} transactions\.\.\."\):
                            for txn_id in selected_ids:
                                txn = session\.query\(Transaction\)\.get\(txn_id\)
                                if txn:
                                    session\.delete\(txn\)
                            session\.commit\(\)'''

    new_pattern2 = '''                        # Perform delete with progress indicator
                        # Bulk delete using filter().in_() - avoids N+1 query problem
                        with st.spinner(f"Deleting {len(selected_ids)} transactions..."):
                            session.query(Transaction).filter(Transaction.id.in_(selected_ids)).delete(
                                synchronize_session=False
                            )
                            session.commit()'''

    content = re.sub(old_pattern2, new_pattern2, content, flags=re.MULTILINE)

    # Fix 3: Bulk update expense category
    old_pattern3 = r'''                        if bulk_action_category and st\.button\("Apply", key="apply_bulk_category"\):
                            count = 0
                            for exp_id in list\(st\.session_state\.bulk_selected_expenses\):
                                exp = session\.query\(Expense\)\.filter\(Expense\.id == exp_id\)\.first\(\)
                                if exp:
                                    exp\.category = bulk_action_category
                                    count \+= 1
                            session\.commit\(\)'''

    new_pattern3 = '''                        if bulk_action_category and st.button("Apply", key="apply_bulk_category"):
                            # Bulk update using filter().in_() - avoids N+1 query problem
                            expense_ids = list(st.session_state.bulk_selected_expenses)
                            count = session.query(Expense).filter(Expense.id.in_(expense_ids)).update(
                                {Expense.category: bulk_action_category},
                                synchronize_session=False
                            )
                            session.commit()'''

    content = re.sub(old_pattern3, new_pattern3, content, flags=re.MULTILINE)

    # Fix 4: Bulk delete expenses
    old_pattern4 = r'''                        if st\.button\(f"🗑️ Delete Selected \(\{len\(st\.session_state\.bulk_selected_expenses\)\}\)", type="secondary"\):
                            count = 0
                            for exp_id in list\(st\.session_state\.bulk_selected_expenses\):
                                exp = session\.query\(Expense\)\.filter\(Expense\.id == exp_id\)\.first\(\)
                                if exp:
                                    session\.delete\(exp\)
                                    count \+= 1
                            session\.commit\(\)'''

    new_pattern4 = '''                        if st.button(f"🗑️ Delete Selected ({len(st.session_state.bulk_selected_expenses)})", type="secondary"):
                            # Bulk delete using filter().in_() - avoids N+1 query problem
                            expense_ids = list(st.session_state.bulk_selected_expenses)
                            count = session.query(Expense).filter(Expense.id.in_(expense_ids)).delete(
                                synchronize_session=False
                            )
                            session.commit()'''

    content = re.sub(old_pattern4, new_pattern4, content, flags=re.MULTILINE)

    # Fix 5: Selected total calculation
    old_pattern5 = r'''                    with col4:
                        selected_total = sum\(
                            session\.query\(Expense\)\.filter\(Expense\.id == exp_id\)\.first\(\)\.amount
                            for exp_id in st\.session_state\.bulk_selected_expenses
                            if session\.query\(Expense\)\.filter\(Expense\.id == exp_id\)\.first\(\)
                        \)'''

    new_pattern5 = '''                    with col4:
                        # Bulk query using filter().in_() and SQL SUM - avoids N+1 query problem
                        from sqlalchemy import func
                        expense_ids = list(st.session_state.bulk_selected_expenses)
                        selected_total = session.query(func.sum(Expense.amount)).filter(
                            Expense.id.in_(expense_ids)
                        ).scalar() or 0.0'''

    content = re.sub(old_pattern5, new_pattern5, content, flags=re.MULTILINE)

    # Write back
    with open('/Users/anthony/Tax Helper/app.py', 'w', encoding='utf-8') as f:
        f.write(content)

    print("✓ Fixed N+1 queries in app.py")

if __name__ == '__main__':
    fix_app_py()
