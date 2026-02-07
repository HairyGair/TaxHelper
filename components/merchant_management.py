"""
Merchant Management UI Component
Comprehensive interface for adding, editing, and managing custom merchants

Features:
- Add new custom merchants
- View and search existing merchants
- Edit merchant details
- Delete merchants with confirmation
- Import/export merchants via CSV
- Merchant statistics and usage tracking
- Duplicate detection and merge tools
"""

import streamlit as st
import pandas as pd
import json
import io
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_, func, and_

from models import Merchant, Transaction, EXPENSE_CATEGORIES, INCOME_TYPES
from components.export_manager import render_export_panel


# ============================================================================
# VALIDATION FUNCTIONS
# ============================================================================

def validate_merchant_data(
    name: str,
    category: str,
    txn_type: str,
    confidence_boost: int = 20
) -> Tuple[bool, str]:
    """
    Validate merchant data before saving

    Args:
        name: Merchant name
        category: Default category
        txn_type: Transaction type (Income/Expense)
        confidence_boost: Confidence boost value

    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check name not empty
    if not name or not name.strip():
        return False, "Merchant name cannot be empty"

    # Check name length
    if len(name.strip()) < 2:
        return False, "Merchant name must be at least 2 characters"

    # Check category not empty
    if not category or not category.strip():
        return False, "Category cannot be empty"

    # Check type is valid
    if txn_type not in ["Income", "Expense"]:
        return False, "Type must be either 'Income' or 'Expense'"

    # Validate category based on type
    if txn_type == "Expense":
        # Allow custom categories, but warn if not in standard list
        pass  # We'll allow any category for flexibility
    elif txn_type == "Income":
        # Allow custom categories for income too
        pass

    # Check confidence boost range
    if not (0 <= confidence_boost <= 30):
        return False, "Confidence boost must be between 0 and 30"

    return True, ""


def check_duplicate_merchant(session: Session, name: str, exclude_id: int = None) -> Optional[Merchant]:
    """
    Check if merchant with same name already exists

    Args:
        session: Database session
        name: Merchant name to check
        exclude_id: Merchant ID to exclude (for updates)

    Returns:
        Existing merchant if found, None otherwise
    """
    normalized_name = name.strip().upper()

    query = session.query(Merchant).filter(
        func.upper(Merchant.name) == normalized_name
    )

    if exclude_id:
        query = query.filter(Merchant.id != exclude_id)

    return query.first()


def find_similar_merchants(session: Session, name: str, threshold: float = 0.7) -> List[Merchant]:
    """
    Find merchants with similar names (potential duplicates)

    Args:
        session: Database session
        name: Merchant name to compare
        threshold: Similarity threshold (0-1)

    Returns:
        List of similar merchants
    """
    from difflib import SequenceMatcher

    normalized_name = name.strip().upper()
    all_merchants = session.query(Merchant).all()
    similar = []

    for merchant in all_merchants:
        merchant_name = merchant.name.upper()
        similarity = SequenceMatcher(None, normalized_name, merchant_name).ratio()

        if similarity >= threshold and merchant_name != normalized_name:
            similar.append(merchant)

    return similar


# ============================================================================
# DATABASE OPERATIONS
# ============================================================================

def add_custom_merchant(
    session: Session,
    name: str,
    aliases: List[str],
    default_category: str,
    default_type: str,
    is_personal: bool,
    industry: str,
    confidence_boost: int
) -> Merchant:
    """
    Add custom merchant to database

    Args:
        session: Database session
        name: Merchant name
        aliases: List of alternative names
        default_category: Default category
        default_type: Income or Expense
        is_personal: Is typically personal
        industry: Industry category
        confidence_boost: Confidence boost (0-30)

    Returns:
        Created Merchant object
    """
    # Normalize name
    normalized_name = name.strip().upper()

    # Clean and normalize aliases
    clean_aliases = [alias.strip().upper() for alias in aliases if alias.strip()]

    merchant = Merchant(
        name=normalized_name,
        aliases=json.dumps(clean_aliases) if clean_aliases else None,
        default_category=default_category,
        default_type=default_type,
        is_personal=is_personal,
        industry=industry,
        confidence_boost=min(30, max(0, confidence_boost)),
        usage_count=0,
        created_date=datetime.now()
    )

    session.add(merchant)
    session.commit()

    return merchant


def update_merchant(
    session: Session,
    merchant_id: int,
    name: str = None,
    aliases: List[str] = None,
    default_category: str = None,
    default_type: str = None,
    is_personal: bool = None,
    industry: str = None,
    confidence_boost: int = None
) -> Merchant:
    """
    Update existing merchant

    Args:
        session: Database session
        merchant_id: Merchant ID to update
        name: New name (optional)
        aliases: New aliases (optional)
        default_category: New category (optional)
        default_type: New type (optional)
        is_personal: New personal flag (optional)
        industry: New industry (optional)
        confidence_boost: New confidence boost (optional)

    Returns:
        Updated Merchant object
    """
    merchant = session.query(Merchant).get(merchant_id)

    if not merchant:
        raise ValueError(f"Merchant with ID {merchant_id} not found")

    # Update fields if provided
    if name is not None:
        merchant.name = name.strip().upper()

    if aliases is not None:
        clean_aliases = [alias.strip().upper() for alias in aliases if alias.strip()]
        merchant.aliases = json.dumps(clean_aliases) if clean_aliases else None

    if default_category is not None:
        merchant.default_category = default_category

    if default_type is not None:
        merchant.default_type = default_type

    if is_personal is not None:
        merchant.is_personal = is_personal

    if industry is not None:
        merchant.industry = industry

    if confidence_boost is not None:
        merchant.confidence_boost = min(30, max(0, confidence_boost))

    session.commit()

    return merchant


def delete_merchant(session: Session, merchant_id: int) -> bool:
    """
    Delete merchant from database

    Args:
        session: Database session
        merchant_id: Merchant ID to delete

    Returns:
        True if deleted successfully
    """
    merchant = session.query(Merchant).get(merchant_id)

    if not merchant:
        return False

    session.delete(merchant)
    session.commit()

    return True


def search_merchants(
    session: Session,
    query: str = None,
    filter_type: str = "All",
    filter_personal: str = "All",
    filter_industry: str = "All",
    page: int = 1,
    page_size: int = 20
) -> Tuple[List[Merchant], int]:
    """
    Search and filter merchants with pagination

    Args:
        session: Database session
        query: Search query (searches name and aliases)
        filter_type: Filter by type (All/Income/Expense)
        filter_personal: Filter by personal flag (All/Personal/Business)
        filter_industry: Filter by industry
        page: Page number (1-indexed)
        page_size: Results per page

    Returns:
        Tuple of (merchants list, total count)
    """
    # Build query
    db_query = session.query(Merchant)

    # Apply search filter
    if query and query.strip():
        search_term = f"%{query.strip().upper()}%"
        db_query = db_query.filter(
            or_(
                Merchant.name.ilike(search_term),
                Merchant.aliases.ilike(search_term)
            )
        )

    # Apply type filter
    if filter_type != "All":
        db_query = db_query.filter(Merchant.default_type == filter_type)

    # Apply personal filter
    if filter_personal == "Personal":
        db_query = db_query.filter(Merchant.is_personal == True)
    elif filter_personal == "Business":
        db_query = db_query.filter(Merchant.is_personal == False)

    # Apply industry filter
    if filter_industry != "All":
        db_query = db_query.filter(Merchant.industry == filter_industry)

    # Get total count
    total_count = db_query.count()

    # Apply pagination
    offset = (page - 1) * page_size
    merchants = db_query.order_by(Merchant.name).offset(offset).limit(page_size).all()

    return merchants, total_count


def get_merchant_usage_count(session: Session, merchant_id: int) -> int:
    """
    Get actual usage count by checking transaction descriptions

    Args:
        session: Database session
        merchant_id: Merchant ID

    Returns:
        Number of times merchant appears in transactions
    """
    merchant = session.query(Merchant).get(merchant_id)

    if not merchant:
        return 0

    # Check merchant name in transaction descriptions
    count = 0
    search_terms = [merchant.name]

    # Add aliases
    if merchant.aliases:
        try:
            aliases = json.loads(merchant.aliases)
            search_terms.extend(aliases)
        except:
            pass

    # Search transactions
    for term in search_terms:
        count += session.query(Transaction).filter(
            Transaction.description.ilike(f"%{term}%")
        ).count()

    # Update usage count in merchant record
    if count != merchant.usage_count:
        merchant.usage_count = count
        session.commit()

    return count


# ============================================================================
# IMPORT/EXPORT FUNCTIONS
# ============================================================================

def export_merchants_to_csv(session: Session) -> str:
    """
    Export all merchants to CSV format

    Args:
        session: Database session

    Returns:
        CSV string
    """
    merchants = session.query(Merchant).order_by(Merchant.name).all()

    # Build CSV data
    rows = []
    for merchant in merchants:
        # Parse aliases
        aliases_str = ""
        if merchant.aliases:
            try:
                aliases = json.loads(merchant.aliases)
                aliases_str = ",".join(aliases)
            except:
                pass

        rows.append({
            "name": merchant.name,
            "aliases": aliases_str,
            "default_category": merchant.default_category,
            "default_type": merchant.default_type,
            "is_personal": "TRUE" if merchant.is_personal else "FALSE",
            "industry": merchant.industry or "",
            "confidence_boost": merchant.confidence_boost
        })

    # Convert to DataFrame and CSV
    df = pd.DataFrame(rows)
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)

    return csv_buffer.getvalue()


def import_merchants_from_csv(session: Session, csv_content: str, skip_duplicates: bool = True) -> Dict:
    """
    Import merchants from CSV content

    Args:
        session: Database session
        csv_content: CSV file content
        skip_duplicates: Skip merchants with duplicate names

    Returns:
        Dict with import statistics
    """
    # Parse CSV
    csv_buffer = io.StringIO(csv_content)
    df = pd.read_csv(csv_buffer)

    stats = {
        "total": len(df),
        "added": 0,
        "skipped": 0,
        "errors": []
    }

    for idx, row in df.iterrows():
        try:
            # Extract data
            name = str(row.get("name", "")).strip()
            aliases_str = str(row.get("aliases", ""))
            category = str(row.get("default_category", ""))
            txn_type = str(row.get("default_type", "Expense"))
            is_personal = str(row.get("is_personal", "FALSE")).upper() == "TRUE"
            industry = str(row.get("industry", "Other"))
            confidence_boost = int(row.get("confidence_boost", 20))

            # Validate
            is_valid, error_msg = validate_merchant_data(name, category, txn_type, confidence_boost)
            if not is_valid:
                stats["errors"].append(f"Row {idx + 2}: {error_msg}")
                stats["skipped"] += 1
                continue

            # Check for duplicates
            existing = check_duplicate_merchant(session, name)
            if existing and skip_duplicates:
                stats["skipped"] += 1
                continue

            # Parse aliases
            aliases = []
            if aliases_str and aliases_str != "nan":
                aliases = [a.strip() for a in aliases_str.split(",") if a.strip()]

            # Add merchant
            add_custom_merchant(
                session=session,
                name=name,
                aliases=aliases,
                default_category=category,
                default_type=txn_type,
                is_personal=is_personal,
                industry=industry,
                confidence_boost=confidence_boost
            )

            stats["added"] += 1

        except Exception as e:
            stats["errors"].append(f"Row {idx + 2}: {str(e)}")
            stats["skipped"] += 1

    return stats


# ============================================================================
# MERCHANT STATISTICS
# ============================================================================

def get_merchant_statistics(session: Session) -> Dict:
    """
    Get comprehensive merchant statistics

    Args:
        session: Database session

    Returns:
        Dictionary of statistics
    """
    all_merchants = session.query(Merchant).all()

    # Basic counts
    total = len(all_merchants)
    system_count = sum(1 for m in all_merchants if m.created_date and m.created_date < datetime(2024, 1, 1))
    custom_count = total - system_count

    # By type
    income_count = sum(1 for m in all_merchants if m.default_type == "Income")
    expense_count = sum(1 for m in all_merchants if m.default_type == "Expense")

    # By personal flag
    personal_count = sum(1 for m in all_merchants if m.is_personal)
    business_count = total - personal_count

    # By industry
    by_industry = {}
    for merchant in all_merchants:
        industry = merchant.industry or "Other"
        by_industry[industry] = by_industry.get(industry, 0) + 1

    # Most used (top 10)
    most_used = sorted(
        [m for m in all_merchants if m.usage_count > 0],
        key=lambda x: x.usage_count,
        reverse=True
    )[:10]

    # Recently added (top 5)
    recently_added = sorted(
        [m for m in all_merchants if m.created_date],
        key=lambda x: x.created_date,
        reverse=True
    )[:5]

    return {
        "total": total,
        "system": system_count,
        "custom": custom_count,
        "income": income_count,
        "expense": expense_count,
        "personal": personal_count,
        "business": business_count,
        "by_industry": by_industry,
        "most_used": most_used,
        "recently_added": recently_added
    }


# ============================================================================
# UI COMPONENTS
# ============================================================================

def render_add_merchant_form(session: Session) -> Optional[Merchant]:
    """
    Render form to add new merchant

    Args:
        session: Database session

    Returns:
        Created merchant if successful, None otherwise
    """
    st.subheader("Add Custom Merchant")

    with st.form("add_merchant_form"):
        # Merchant Name
        name = st.text_input(
            "Merchant Name*",
            placeholder="Joe's Coffee Shop",
            help="Enter the canonical name for this merchant (will be normalized to uppercase)"
        )

        # Aliases
        aliases_input = st.text_input(
            "Aliases (comma-separated variations)",
            placeholder="JOES COFFEE, JOE'S, JOES",
            help="Alternative names or spellings that should match to this merchant"
        )

        # Type selection
        col1, col2 = st.columns(2)

        with col1:
            default_type = st.radio(
                "Default Type*",
                ["Expense", "Income"],
                horizontal=True,
                help="Is this typically an income or expense?"
            )

        with col2:
            is_personal = st.checkbox(
                "Usually Personal?",
                help="Check if this is typically a personal (non-business) transaction"
            )

        # Category selection based on type
        if default_type == "Expense":
            categories = [""] + EXPENSE_CATEGORIES
            default_category = st.selectbox(
                "Default Category*",
                categories,
                help="Select the default expense category for this merchant"
            )
        else:
            categories = [""] + INCOME_TYPES
            default_category = st.selectbox(
                "Default Category*",
                categories,
                help="Select the default income type for this merchant"
            )

        # Industry
        industries = [
            "Other", "Supermarket", "Restaurant", "Fast Food", "Coffee Shop",
            "Transport", "Fuel", "Utilities", "Telecommunications",
            "Office Supplies", "Software", "Professional Services",
            "Banking", "Hotel", "Retail", "Marketing", "Insurance",
            "Entertainment", "Education", "Postal", "Courier",
            "Parking", "Printing", "Fitness", "Cleaning"
        ]

        industry = st.selectbox(
            "Industry",
            industries,
            help="Business category for this merchant"
        )

        # Confidence boost
        confidence_boost = st.slider(
            "Confidence Boost",
            min_value=0,
            max_value=30,
            value=20,
            help="Points added to confidence score when matched (0-30). Higher = more reliable match."
        )

        # Submit button
        submitted = st.form_submit_button("Add Merchant", type="primary")

        if submitted:
            # Validate
            is_valid, error_msg = validate_merchant_data(
                name, default_category, default_type, confidence_boost
            )

            if not is_valid:
                st.error(error_msg)
                return None

            # Check for duplicates
            existing = check_duplicate_merchant(session, name)
            if existing:
                st.error(f"Merchant '{existing.name}' already exists!")
                return None

            # Check for similar merchants
            similar = find_similar_merchants(session, name, threshold=0.8)
            if similar:
                st.warning("Similar merchants found:")
                for sim in similar:
                    st.write(f"- {sim.name} ({sim.default_category})")
                st.info("You can still add this merchant, or edit an existing one.")

            # Parse aliases
            aliases = []
            if aliases_input:
                aliases = [a.strip() for a in aliases_input.split(",") if a.strip()]

            # Add merchant
            try:
                merchant = add_custom_merchant(
                    session=session,
                    name=name,
                    aliases=aliases,
                    default_category=default_category,
                    default_type=default_type,
                    is_personal=is_personal,
                    industry=industry,
                    confidence_boost=confidence_boost
                )

                st.success(f"Successfully added merchant: {merchant.name}")
                st.balloons()
                return merchant

            except Exception as e:
                st.error(f"Error adding merchant: {str(e)}")
                return None

    return None


def render_merchant_list(
    session: Session,
    query: str = None,
    filter_type: str = "All",
    filter_personal: str = "All",
    filter_industry: str = "All",
    page: int = 1,
    page_size: int = 20
) -> None:
    """
    Render paginated merchant list with search and filters

    Args:
        session: Database session
        query: Search query
        filter_type: Type filter
        filter_personal: Personal filter
        filter_industry: Industry filter
        page: Current page
        page_size: Items per page
    """
    # Get merchants
    merchants, total_count = search_merchants(
        session, query, filter_type, filter_personal, filter_industry, page, page_size
    )

    total_pages = (total_count + page_size - 1) // page_size

    # Header
    st.subheader(f"Your Merchants (Showing {len(merchants)} of {total_count})")

    # No results
    if total_count == 0:
        st.info("No merchants found matching your criteria.")
        return

    # Display merchants
    for merchant in merchants:
        with st.container():
            st.markdown("---")

            # Header row
            col1, col2, col3 = st.columns([3, 2, 2])

            with col1:
                # Badge for system vs custom
                badge = "System" if merchant.created_date and merchant.created_date < datetime(2024, 1, 1) else "Custom"
                badge_color = "blue" if badge == "System" else "green"

                st.markdown(f"### {merchant.name} :{badge_color}[{badge}]")

            with col2:
                st.write(f"**{merchant.default_category}**")

            with col3:
                type_emoji = "💰" if merchant.default_type == "Income" else "💳"
                personal_emoji = "👤" if merchant.is_personal else "💼"
                st.write(f"{type_emoji} {merchant.default_type} {personal_emoji}")

            # Details row
            col1, col2 = st.columns([3, 2])

            with col1:
                # Aliases
                if merchant.aliases:
                    try:
                        aliases = json.loads(merchant.aliases)
                        if aliases:
                            st.caption(f"Aliases: {', '.join(aliases)}")
                    except:
                        pass

                # Industry
                st.caption(f"Industry: {merchant.industry or 'Other'} | Confidence Boost: +{merchant.confidence_boost}")

            with col2:
                # Usage count
                usage = merchant.usage_count or 0
                st.caption(f"Used {usage} times")

            # Action buttons
            col1, col2, col3 = st.columns([1, 1, 3])

            with col1:
                if st.button("Edit", key=f"edit_{merchant.id}"):
                    st.session_state.edit_merchant_id = merchant.id
                    st.rerun()

            with col2:
                if st.button("Delete", key=f"delete_{merchant.id}"):
                    st.session_state.delete_merchant_id = merchant.id
                    st.rerun()

    # Pagination
    if total_pages > 1:
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])

        with col1:
            if page > 1:
                if st.button("← Previous"):
                    st.session_state.merchant_page = page - 1
                    st.rerun()

        with col2:
            st.write(f"Page {page} of {total_pages}")

        with col3:
            if page < total_pages:
                if st.button("Next →"):
                    st.session_state.merchant_page = page + 1
                    st.rerun()


def render_edit_merchant_modal(session: Session, merchant_id: int) -> bool:
    """
    Render modal to edit existing merchant

    Args:
        session: Database session
        merchant_id: Merchant ID to edit

    Returns:
        True if merchant was updated
    """
    merchant = session.query(Merchant).get(merchant_id)

    if not merchant:
        st.error("Merchant not found")
        return False

    st.subheader(f"Edit Merchant: {merchant.name}")

    with st.form("edit_merchant_form"):
        # Merchant Name
        name = st.text_input(
            "Merchant Name*",
            value=merchant.name,
            help="Canonical name for this merchant"
        )

        # Aliases
        current_aliases = []
        if merchant.aliases:
            try:
                current_aliases = json.loads(merchant.aliases)
            except:
                pass

        aliases_input = st.text_input(
            "Aliases (comma-separated)",
            value=", ".join(current_aliases),
            help="Alternative names or spellings"
        )

        # Type and personal flag
        col1, col2 = st.columns(2)

        with col1:
            default_type = st.radio(
                "Default Type*",
                ["Expense", "Income"],
                index=0 if merchant.default_type == "Expense" else 1,
                horizontal=True
            )

        with col2:
            is_personal = st.checkbox(
                "Usually Personal?",
                value=merchant.is_personal
            )

        # Category
        if default_type == "Expense":
            categories = EXPENSE_CATEGORIES
            try:
                default_idx = categories.index(merchant.default_category)
            except ValueError:
                default_idx = 0

            default_category = st.selectbox(
                "Default Category*",
                categories,
                index=default_idx
            )
        else:
            categories = INCOME_TYPES
            try:
                default_idx = categories.index(merchant.default_category)
            except ValueError:
                default_idx = 0

            default_category = st.selectbox(
                "Default Category*",
                categories,
                index=default_idx
            )

        # Industry
        industries = [
            "Other", "Supermarket", "Restaurant", "Fast Food", "Coffee Shop",
            "Transport", "Fuel", "Utilities", "Telecommunications",
            "Office Supplies", "Software", "Professional Services",
            "Banking", "Hotel", "Retail", "Marketing", "Insurance",
            "Entertainment", "Education", "Postal", "Courier",
            "Parking", "Printing", "Fitness", "Cleaning"
        ]

        try:
            industry_idx = industries.index(merchant.industry) if merchant.industry else 0
        except ValueError:
            industry_idx = 0

        industry = st.selectbox(
            "Industry",
            industries,
            index=industry_idx
        )

        # Confidence boost
        confidence_boost = st.slider(
            "Confidence Boost",
            min_value=0,
            max_value=30,
            value=merchant.confidence_boost
        )

        # Submit buttons
        col1, col2 = st.columns(2)

        with col1:
            submitted = st.form_submit_button("Save Changes", type="primary")

        with col2:
            cancelled = st.form_submit_button("Cancel")

        if cancelled:
            if 'edit_merchant_id' in st.session_state:
                del st.session_state.edit_merchant_id
            st.rerun()
            return False

        if submitted:
            # Validate
            is_valid, error_msg = validate_merchant_data(
                name, default_category, default_type, confidence_boost
            )

            if not is_valid:
                st.error(error_msg)
                return False

            # Check for duplicate names (excluding current merchant)
            existing = check_duplicate_merchant(session, name, exclude_id=merchant_id)
            if existing:
                st.error(f"Merchant '{existing.name}' already exists!")
                return False

            # Parse aliases
            aliases = []
            if aliases_input:
                aliases = [a.strip() for a in aliases_input.split(",") if a.strip()]

            # Update merchant
            try:
                update_merchant(
                    session=session,
                    merchant_id=merchant_id,
                    name=name,
                    aliases=aliases,
                    default_category=default_category,
                    default_type=default_type,
                    is_personal=is_personal,
                    industry=industry,
                    confidence_boost=confidence_boost
                )

                st.success("Merchant updated successfully!")

                # Clear edit state
                if 'edit_merchant_id' in st.session_state:
                    del st.session_state.edit_merchant_id

                st.rerun()
                return True

            except Exception as e:
                st.error(f"Error updating merchant: {str(e)}")
                return False

    return False


def render_delete_confirmation(session: Session, merchant_id: int) -> bool:
    """
    Render delete confirmation dialog

    Args:
        session: Database session
        merchant_id: Merchant ID to delete

    Returns:
        True if merchant was deleted
    """
    merchant = session.query(Merchant).get(merchant_id)

    if not merchant:
        st.error("Merchant not found")
        return False

    # Get usage count
    usage_count = get_merchant_usage_count(session, merchant_id)

    st.warning("Delete Merchant?")
    st.write(f"Are you sure you want to delete **{merchant.name}**?")

    if usage_count > 0:
        st.info(f"This merchant has been used {usage_count} times. "
                "Transactions will NOT be affected, but future transactions "
                "won't auto-match to this merchant.")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Cancel", key="cancel_delete"):
            if 'delete_merchant_id' in st.session_state:
                del st.session_state.delete_merchant_id
            st.rerun()
            return False

    with col2:
        if st.button("Yes, Delete", type="primary", key="confirm_delete"):
            try:
                delete_merchant(session, merchant_id)
                st.success(f"Merchant '{merchant.name}' deleted successfully")

                # Clear delete state
                if 'delete_merchant_id' in st.session_state:
                    del st.session_state.delete_merchant_id

                st.rerun()
                return True

            except Exception as e:
                st.error(f"Error deleting merchant: {str(e)}")
                return False

    return False


def render_merchant_stats(session: Session) -> None:
    """
    Render merchant statistics dashboard

    Args:
        session: Database session
    """
    stats = get_merchant_statistics(session)

    st.subheader("Merchant Statistics")

    # Top-level metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Merchants", stats["total"])

    with col2:
        st.metric("System", stats["system"])

    with col3:
        st.metric("Custom", stats["custom"])

    with col4:
        st.metric("Business Default", stats["business"])

    st.markdown("---")

    # Type breakdown
    col1, col2 = st.columns(2)

    with col1:
        st.write("**By Transaction Type:**")
        st.write(f"- Income: {stats['income']}")
        st.write(f"- Expense: {stats['expense']}")

        st.write("")
        st.write("**Personal vs Business:**")
        st.write(f"- Personal: {stats['personal']}")
        st.write(f"- Business: {stats['business']}")

    with col2:
        st.write("**Top Industries:**")
        top_industries = sorted(
            stats["by_industry"].items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]

        for industry, count in top_industries:
            st.write(f"- {industry}: {count}")

    # Most used merchants
    if stats["most_used"]:
        st.markdown("---")
        st.write("**Most Used Merchants:**")

        for i, merchant in enumerate(stats["most_used"], 1):
            st.write(f"{i}. {merchant.name} - {merchant.usage_count} matches")

    # Recently added
    if stats["recently_added"]:
        st.markdown("---")
        st.write("**Recently Added:**")

        for merchant in stats["recently_added"]:
            days_ago = (datetime.now() - merchant.created_date).days
            time_str = f"{days_ago} days ago" if days_ago > 0 else "today"
            st.write(f"- {merchant.name} ({time_str})")


def render_import_export_ui(session: Session) -> None:
    """
    Render import/export interface

    Args:
        session: Database session
    """
    st.subheader("Import/Export Merchants")

    # Export section
    st.write("**Export Merchants**")
    st.write("Download all merchants as a CSV file for backup or sharing.")

    if st.button("Export to CSV"):
        try:
            # Get all merchants
            merchants = session.query(Merchant).order_by(Merchant.name).all()

            # Build data for export
            rows = []
            for merchant in merchants:
                # Parse aliases
                aliases_str = ""
                if merchant.aliases:
                    try:
                        aliases = json.loads(merchant.aliases)
                        aliases_str = ",".join(aliases)
                    except:
                        aliases_str = merchant.aliases

                # Parse keywords
                keywords_str = ""
                if merchant.keywords:
                    try:
                        keywords = json.loads(merchant.keywords)
                        keywords_str = ",".join(keywords)
                    except:
                        keywords_str = merchant.keywords

                rows.append({
                    'Name': merchant.name,
                    'Type': merchant.merchant_type,
                    'Default Category': merchant.default_category or '',
                    'Default Description': merchant.default_description or '',
                    'VAT Number': merchant.vat_number or '',
                    'Website': merchant.website or '',
                    'Aliases': aliases_str,
                    'Keywords': keywords_str,
                    'Auto Categorize': merchant.auto_categorize,
                    'Created': merchant.created_at.strftime('%Y-%m-%d %H:%M:%S') if merchant.created_at else '',
                    'Updated': merchant.updated_at.strftime('%Y-%m-%d %H:%M:%S') if merchant.updated_at else ''
                })

            merchants_df = pd.DataFrame(rows)

            # Show Aurora-themed export panel
            with st.expander("Export Merchants Database", expanded=True):
                render_export_panel(
                    session=session,
                    data=merchants_df,
                    title="Merchants Database Export",
                    filename_prefix=f"merchants_{datetime.now().strftime('%Y%m%d')}",
                    metadata={
                        'Total Merchants': str(len(merchants)),
                        'Expense Merchants': str(len([m for m in merchants if m.merchant_type == 'expense'])),
                        'Income Merchants': str(len([m for m in merchants if m.merchant_type == 'income'])),
                        'Auto-Categorize Enabled': str(len([m for m in merchants if m.auto_categorize]))
                    },
                    show_formats=['csv', 'excel', 'json'],
                    use_aurora_theme=True
                )

        except Exception as e:
            st.error(f"Error exporting merchants: {str(e)}")

    st.markdown("---")

    # Import section
    st.write("**Import Merchants**")
    st.write("Upload a CSV file to import merchants. Expected format:")
    st.code(
        "name,aliases,default_category,default_type,is_personal,industry,confidence_boost\n"
        "\"JOE'S COFFEE\",\"JOES COFFEE,JOE'S\",\"Office costs\",\"Expense\",FALSE,\"Restaurant\",20",
        language="csv"
    )

    uploaded_file = st.file_uploader(
        "Choose CSV file",
        type=["csv"],
        help="Upload a CSV file with merchant data"
    )

    skip_duplicates = st.checkbox(
        "Skip duplicate merchants",
        value=True,
        help="Skip merchants with names that already exist"
    )

    if uploaded_file is not None:
        if st.button("Import from CSV", type="primary"):
            try:
                # Read file content
                csv_content = uploaded_file.getvalue().decode("utf-8")

                # Import
                stats = import_merchants_from_csv(session, csv_content, skip_duplicates)

                # Show results
                st.success(f"Import complete!")
                st.write(f"- Total rows: {stats['total']}")
                st.write(f"- Added: {stats['added']}")
                st.write(f"- Skipped: {stats['skipped']}")

                if stats['errors']:
                    st.warning("Errors encountered:")
                    for error in stats['errors'][:10]:  # Show first 10 errors
                        st.write(f"- {error}")

                if stats['added'] > 0:
                    st.rerun()

            except Exception as e:
                st.error(f"Error importing merchants: {str(e)}")


def render_merchant_management_page(session: Session) -> None:
    """
    Main merchant management page

    Args:
        session: Database session
    """
    st.title("Merchant Management")

    # Initialize session state
    if 'merchant_page' not in st.session_state:
        st.session_state.merchant_page = 1

    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "Browse Merchants",
        "Add Merchant",
        "Statistics",
        "Import/Export"
    ])

    # Tab 1: Browse and manage merchants
    with tab1:
        # Check if editing or deleting
        if 'edit_merchant_id' in st.session_state:
            render_edit_merchant_modal(session, st.session_state.edit_merchant_id)
        elif 'delete_merchant_id' in st.session_state:
            render_delete_confirmation(session, st.session_state.delete_merchant_id)
        else:
            # Search and filters
            col1, col2 = st.columns([2, 1])

            with col1:
                search_query = st.text_input(
                    "Search merchants",
                    placeholder="Enter merchant name...",
                    key="merchant_search"
                )

            with col2:
                st.write("")  # Spacing
                st.write("")  # Spacing
                if st.button("Clear Filters"):
                    st.session_state.merchant_page = 1
                    st.rerun()

            # Filters
            col1, col2, col3 = st.columns(3)

            with col1:
                filter_type = st.selectbox(
                    "Type",
                    ["All", "Income", "Expense"],
                    key="filter_type"
                )

            with col2:
                filter_personal = st.selectbox(
                    "Personal/Business",
                    ["All", "Personal", "Business"],
                    key="filter_personal"
                )

            with col3:
                # Get unique industries
                all_merchants = session.query(Merchant).all()
                industries = sorted(set(m.industry for m in all_merchants if m.industry))

                filter_industry = st.selectbox(
                    "Industry",
                    ["All"] + industries,
                    key="filter_industry"
                )

            st.markdown("---")

            # Render merchant list
            render_merchant_list(
                session=session,
                query=search_query,
                filter_type=filter_type,
                filter_personal=filter_personal,
                filter_industry=filter_industry,
                page=st.session_state.merchant_page,
                page_size=20
            )

    # Tab 2: Add new merchant
    with tab2:
        render_add_merchant_form(session)

    # Tab 3: Statistics
    with tab3:
        render_merchant_stats(session)

    # Tab 4: Import/Export
    with tab4:
        render_import_export_ui(session)


# ============================================================================
# QUICK ACCESS FUNCTIONS (for use in other parts of app)
# ============================================================================

def quick_add_merchant_button(session: Session, suggested_name: str = None) -> None:
    """
    Render a quick "Add Merchant" button with optional pre-filled name

    Args:
        session: Database session
        suggested_name: Pre-fill merchant name
    """
    if st.button("+ Add Custom Merchant"):
        st.session_state.show_quick_add_merchant = True
        if suggested_name:
            st.session_state.quick_merchant_name = suggested_name
        st.rerun()


def render_quick_add_merchant_modal(session: Session) -> Optional[Merchant]:
    """
    Render simplified add merchant modal for quick access

    Args:
        session: Database session

    Returns:
        Created merchant if successful
    """
    suggested_name = st.session_state.get('quick_merchant_name', '')

    st.subheader("Quick Add Merchant")

    with st.form("quick_add_merchant"):
        name = st.text_input("Merchant Name*", value=suggested_name)

        col1, col2 = st.columns(2)
        with col1:
            default_type = st.radio("Type*", ["Expense", "Income"], horizontal=True)
        with col2:
            is_personal = st.checkbox("Personal?")

        if default_type == "Expense":
            category = st.selectbox("Category*", EXPENSE_CATEGORIES)
        else:
            category = st.selectbox("Category*", INCOME_TYPES)

        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("Add", type="primary")
        with col2:
            cancelled = st.form_submit_button("Cancel")

        if cancelled:
            st.session_state.show_quick_add_merchant = False
            if 'quick_merchant_name' in st.session_state:
                del st.session_state.quick_merchant_name
            st.rerun()
            return None

        if submitted:
            is_valid, error_msg = validate_merchant_data(name, category, default_type, 20)

            if not is_valid:
                st.error(error_msg)
                return None

            try:
                merchant = add_custom_merchant(
                    session=session,
                    name=name,
                    aliases=[],
                    default_category=category,
                    default_type=default_type,
                    is_personal=is_personal,
                    industry="Other",
                    confidence_boost=20
                )

                st.success(f"Added: {merchant.name}")
                st.session_state.show_quick_add_merchant = False
                if 'quick_merchant_name' in st.session_state:
                    del st.session_state.quick_merchant_name
                st.rerun()
                return merchant

            except Exception as e:
                st.error(f"Error: {str(e)}")
                return None

    return None
