"""
Smart Learning Component
Enhanced machine learning for transaction categorization

Features:
- Detects similar transactions after user corrections
- Suggests bulk application of categorization
- Creates rules automatically
- Improves accuracy over time
- Visual, engaging prompts

Usage:
    from components.smart_learning import detect_and_prompt_similar, render_enhanced_modal

    # After user categorizes a transaction:
    detect_and_prompt_similar(session, corrected_transaction)
"""

import streamlit as st
import re
from collections import defaultdict


def detect_similar_transactions(session, reference_txn, unreviewed_only=True):
    """
    Find transactions similar to the reference transaction

    Args:
        session: SQLAlchemy session
        reference_txn: Transaction object to match against
        unreviewed_only: Only return unreviewed transactions

    Returns:
        List of similar Transaction objects
    """
    from models import Transaction

    # Extract merchant name (clean)
    desc = reference_txn.description
    cleaned = re.sub(r'\d{4}\s*\w{3}\d{2}', '', desc)  # Remove dates
    cleaned = re.sub(r'\d{2}/\d{2}/\d{2,4}', '', cleaned)
    cleaned = re.sub(r',.*', '', cleaned).strip()
    merchant_key = cleaned[:30] if len(cleaned) >= 10 else cleaned

    # Build query
    query = session.query(Transaction).filter(
        Transaction.description.like(f'%{merchant_key}%'),
        Transaction.id != reference_txn.id
    )

    if unreviewed_only:
        query = query.filter(Transaction.reviewed == False)

    similar_txns = query.all()

    # Filter by amount similarity (within 20% range) for better accuracy
    amount = reference_txn.paid_in if reference_txn.paid_in > 0 else reference_txn.paid_out
    if amount > 0:
        similar_txns = [
            t for t in similar_txns
            if abs(((t.paid_in or t.paid_out) - amount) / amount) < 0.2
        ]

    return similar_txns


def render_enhanced_modal(similar_info):
    """
    Render enhanced smart learning modal with better UI

    Args:
        similar_info: Dictionary with similar transaction information
    """
    if 'similar_found' not in st.session_state:
        return

    similar_info = st.session_state['similar_found']

    # Enhanced modal with gradient background
    st.markdown("""
    <style>
    .smart-learning-modal {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 25px;
        border-radius: 15px;
        margin-bottom: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    }
    .smart-stat {
        background: rgba(255,255,255,0.2);
        padding: 10px;
        border-radius: 8px;
        margin: 5px 0;
    }
    </style>
    """, unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="smart-learning-modal">', unsafe_allow_html=True)

        # Title with animation
        st.markdown("### 🎯 Smart Learning Active!")

        # Info box
        st.markdown(f"""
        <div style="background: rgba(255,255,255,0.15); padding: 15px; border-radius: 10px; margin: 15px 0;">
            <div style="font-size: 18px; font-weight: bold; margin-bottom: 10px;">
                Found <span style="color: #ffd700;">{similar_info['count']} similar transactions</span>
            </div>
            <div style="font-size: 14px; opacity: 0.9;">
                Merchant: <strong>"{similar_info['merchant']}"</strong>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # What you just did
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            <div class="smart-stat">
                <div style="font-size: 12px; opacity: 0.8;">Type</div>
                <div style="font-size: 16px; font-weight: bold;">{similar_info['txn_type']}</div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class="smart-stat">
                <div style="font-size: 12px; opacity: 0.8;">Category</div>
                <div style="font-size: 16px; font-weight: bold;">{similar_info['category'] or 'None'}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("**Would you like to apply this to all similar transactions?**")

        # Show preview
        with st.expander("📋 Preview Similar Transactions", expanded=False):
            session = st.session_state.db_session
            from models import Transaction
            preview_txns = session.query(Transaction).filter(
                Transaction.id.in_(similar_info['txn_ids'][:10])
            ).all()

            for idx, txn in enumerate(preview_txns, 1):
                amount = txn.paid_in if txn.paid_in > 0 else txn.paid_out
                st.markdown(
                    f"**{idx}.** {txn.date.strftime('%d/%m/%Y')} - "
                    f"£{amount:,.2f} - {txn.description[:50]}"
                )

            if similar_info['count'] > 10:
                st.caption(f"...and {similar_info['count'] - 10} more")

        st.markdown('</div>', unsafe_allow_html=True)

        # Action buttons - larger and more prominent
        col1, col2, col3 = st.columns([3, 3, 2])

        with col1:
            if st.button(
                f"✅ Yes, Apply to All {similar_info['count']}",
                type="primary",
                use_container_width=True,
                key="smart_learn_apply"
            ):
                apply_smart_learning(session, similar_info)
                del st.session_state['similar_found']
                st.success(f"✓ Applied to {similar_info['count']} transactions!")
                st.balloons()
                st.rerun()

        with col2:
            if st.button(
                "🔍 Review Each One",
                use_container_width=True,
                key="smart_learn_review"
            ):
                del st.session_state['similar_found']
                st.rerun()

        with col3:
            if st.button(
                "⏭️ Skip",
                use_container_width=True,
                key="smart_learn_skip"
            ):
                del st.session_state['similar_found']
                st.rerun()

        # Don't ask again option
        st.checkbox(
            "🔕 Don't ask me about similar transactions again",
            key="smart_learn_disable",
            help="You can re-enable this in Settings later"
        )

        if st.session_state.get('smart_learn_disable', False):
            st.session_state.learn_from_correction = False
            st.warning("Smart Learning disabled. You can re-enable it in Settings.")


def apply_smart_learning(session, similar_info):
    """
    Apply learned categorization to all similar transactions

    Args:
        session: SQLAlchemy session
        similar_info: Dictionary with categorization information
    """
    from models import Transaction, Income, Expense

    applied_count = 0

    for txn_id in similar_info['txn_ids']:
        txn = session.query(Transaction).get(txn_id)
        if txn and not txn.reviewed:
            # Update transaction
            txn.is_personal = similar_info['is_personal']
            txn.guessed_type = similar_info['txn_type']
            txn.guessed_category = similar_info['category']
            txn.reviewed = True
            txn.confidence_score = 90  # High confidence from user learning

            # Auto-post to ledgers
            if not similar_info['is_personal'] and similar_info['txn_type'] in ['Income', 'Expense']:
                post_to_ledger(session, txn, similar_info['txn_type'], similar_info['category'])

            applied_count += 1

    session.commit()

    # Create a rule for future imports (optional)
    if st.session_state.get('auto_create_rules', True) and applied_count > 5:
        create_rule_from_learning(session, similar_info)

    return applied_count


def post_to_ledger(session, transaction, txn_type, category):
    """
    Post transaction to appropriate ledger

    Args:
        session: SQLAlchemy session
        transaction: Transaction object
        txn_type: "Income" or "Expense"
        category: Category for the ledger entry
    """
    from models import Income, Expense

    if txn_type == 'Income' and transaction.paid_in > 0:
        # Check for duplicates
        existing = session.query(Income).filter(
            Income.date == transaction.date,
            Income.source == transaction.description,
            Income.amount_gross == transaction.paid_in
        ).first()

        if not existing:
            income_record = Income(
                date=transaction.date,
                source=transaction.description,
                description=transaction.notes or '',
                amount_gross=transaction.paid_in,
                tax_deducted=0.0,
                income_type=category or 'Other'
            )
            session.add(income_record)

    elif txn_type == 'Expense' and transaction.paid_out > 0:
        # Check for duplicates
        existing = session.query(Expense).filter(
            Expense.date == transaction.date,
            Expense.supplier == transaction.description,
            Expense.amount == transaction.paid_out
        ).first()

        if not existing:
            expense_record = Expense(
                date=transaction.date,
                supplier=transaction.description,
                description=transaction.notes or '',
                category=category or 'Other business expenses',
                amount=transaction.paid_out,
                receipt_link=''
            )
            session.add(expense_record)


def create_rule_from_learning(session, similar_info):
    """
    Automatically create a Rule for future imports

    Args:
        session: SQLAlchemy session
        similar_info: Dictionary with categorization information
    """
    from models import Rule
    from datetime import datetime

    # Extract merchant key
    merchant_key = similar_info['merchant'].split()[0] if similar_info['merchant'] else None

    if not merchant_key or len(merchant_key) < 3:
        return  # Too short to be useful

    # Check if rule already exists
    existing = session.query(Rule).filter(
        Rule.text_to_match.ilike(f'%{merchant_key}%'),
        Rule.match_mode == 'Contains'
    ).first()

    if not existing:
        new_rule = Rule(
            match_mode='Contains',
            text_to_match=merchant_key,
            map_to=similar_info['txn_type'],
            income_type=similar_info['category'] if similar_info['txn_type'] == 'Income' else None,
            expense_category=similar_info['category'] if similar_info['txn_type'] == 'Expense' else None,
            is_personal=similar_info['is_personal'],
            priority=50,
            enabled=True,
            notes=f"Auto-created from Smart Learning on {datetime.now().strftime('%Y-%m-%d')}"
        )
        session.add(new_rule)
        session.commit()
        st.toast(f"✓ Created automatic rule for '{merchant_key}'", icon="📝")


def detect_and_prompt_similar(session, corrected_txn):
    """
    Main function: Detect similar transactions and prompt user

    Args:
        session: SQLAlchemy session
        corrected_txn: Transaction that was just corrected by user
    """
    # Check if learning is enabled
    if not st.session_state.get('learn_from_correction', True):
        return

    # Detect similar transactions
    similar_txns = detect_similar_transactions(session, corrected_txn)

    # Only prompt if we found 3+ similar transactions
    threshold = st.session_state.get('learning_threshold', 3)
    if len(similar_txns) >= threshold:
        # Store in session state
        st.session_state['similar_found'] = {
            'merchant': corrected_txn.description[:50],
            'count': len(similar_txns),
            'txn_ids': [t.id for t in similar_txns],
            'is_personal': corrected_txn.is_personal,
            'txn_type': corrected_txn.guessed_type,
            'category': corrected_txn.guessed_category
        }


# Settings for smart learning
def get_learning_enabled():
    """Check if smart learning is enabled"""
    return st.session_state.get('learn_from_correction', True)


def set_learning_enabled(enabled):
    """Enable or disable smart learning"""
    st.session_state.learn_from_correction = enabled


def get_learning_threshold():
    """Get minimum similar transactions threshold"""
    return st.session_state.get('learning_threshold', 3)


def set_learning_threshold(threshold):
    """Set minimum similar transactions threshold"""
    st.session_state.learning_threshold = threshold
