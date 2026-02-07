"""
Confidence Tooltips Component
Beautiful, informative tooltips explaining AI confidence scores

Features:
- Visual breakdown of confidence factors
- Hover tooltips with detailed explanations
- Progress bars showing contribution of each factor
- Color-coded visual feedback
- Help modal explaining the scoring system
- Integration with merchant database and pattern learning

Usage:
    from components.confidence_tooltips import (
        render_confidence_tooltip,
        calculate_confidence_breakdown,
        render_help_modal
    )

    # In your transaction display:
    breakdown = calculate_confidence_breakdown(transaction, session)
    render_confidence_tooltip(transaction.confidence_score, breakdown)
"""

import streamlit as st
from typing import Dict, Optional
import re


def calculate_confidence_breakdown(transaction, session) -> Dict:
    """
    Calculate detailed confidence score breakdown for a transaction

    Args:
        transaction: Transaction object from database
        session: SQLAlchemy session

    Returns:
        Dictionary containing:
        - merchant_match: Dict with score and explanation
        - rule_match: Dict with score and explanation
        - pattern_learning: Dict with score and explanation
        - amount_consistency: Dict with score and explanation
        - total_score: Overall confidence score
        - explanation: Human-readable summary
    """
    from models import Rule

    breakdown = {
        'merchant_match': {'score': 0, 'explanation': 'No merchant match found', 'max': 40},
        'rule_match': {'score': 0, 'explanation': 'No rule match found', 'max': 30},
        'pattern_learning': {'score': 0, 'explanation': 'No similar transactions found', 'max': 20},
        'amount_consistency': {'score': 0, 'explanation': 'No amount data available', 'max': 10},
        'total_score': 0,
        'explanation': ''
    }

    # 1. MERCHANT MATCH (0-40 points)
    merchant_score = calculate_merchant_match_score(transaction)
    breakdown['merchant_match']['score'] = merchant_score['score']
    breakdown['merchant_match']['explanation'] = merchant_score['explanation']
    breakdown['merchant_match']['merchant_name'] = merchant_score.get('merchant_name', '')

    # 2. RULE MATCH (0-30 points)
    rule_score = calculate_rule_match_score(transaction, session)
    breakdown['rule_match']['score'] = rule_score['score']
    breakdown['rule_match']['explanation'] = rule_score['explanation']
    breakdown['rule_match']['rule_text'] = rule_score.get('rule_text', '')

    # 3. PATTERN LEARNING (0-20 points)
    pattern_score = calculate_pattern_learning_score(transaction, session)
    breakdown['pattern_learning']['score'] = pattern_score['score']
    breakdown['pattern_learning']['explanation'] = pattern_score['explanation']
    breakdown['pattern_learning']['similar_count'] = pattern_score.get('similar_count', 0)

    # 4. AMOUNT CONSISTENCY (0-10 points)
    amount_score = calculate_amount_consistency_score(transaction, session)
    breakdown['amount_consistency']['score'] = amount_score['score']
    breakdown['amount_consistency']['explanation'] = amount_score['explanation']

    # Calculate total
    total = (
        breakdown['merchant_match']['score'] +
        breakdown['rule_match']['score'] +
        breakdown['pattern_learning']['score'] +
        breakdown['amount_consistency']['score']
    )
    breakdown['total_score'] = min(total, 100)

    # Generate explanation
    breakdown['explanation'] = generate_confidence_explanation(breakdown['total_score'])

    return breakdown


def calculate_merchant_match_score(transaction) -> Dict:
    """
    Calculate merchant database match score (0-40 points)

    Returns:
        Dict with score and explanation
    """
    try:
        from scripts.merchant_database import match_merchant

        merchant_match = match_merchant(transaction.description)

        if merchant_match:
            # Map confidence levels to scores
            confidence_map = {
                100: 40,  # CONFIDENCE_CERTAIN
                90: 35,   # CONFIDENCE_HIGH
                70: 28,   # CONFIDENCE_MEDIUM
                50: 20,   # CONFIDENCE_LOW
            }

            merchant_confidence = merchant_match.get('confidence', 0)
            score = confidence_map.get(merchant_confidence, int(merchant_confidence * 0.4))

            merchant_name = merchant_match.get('merchant_name', 'Unknown')
            category = merchant_match.get('category', 'Unknown')

            return {
                'score': score,
                'explanation': f"Matched merchant '{merchant_name}' in database",
                'merchant_name': merchant_name,
                'category': category
            }
    except (ImportError, AttributeError):
        pass

    return {
        'score': 0,
        'explanation': 'No merchant match found',
        'merchant_name': ''
    }


def calculate_rule_match_score(transaction, session) -> Dict:
    """
    Calculate rule match score (0-30 points)

    Returns:
        Dict with score and explanation
    """
    from models import Rule

    # Find matching rule
    rules = session.query(Rule).filter(Rule.enabled == True).order_by(Rule.priority).all()

    for rule in rules:
        desc = transaction.description.upper()
        match_text = rule.text_to_match.upper()

        matched = False
        if rule.match_mode == 'Contains' and match_text in desc:
            matched = True
        elif rule.match_mode == 'Equals' and match_text == desc:
            matched = True
        elif rule.match_mode == 'Regex':
            try:
                if re.search(rule.text_to_match, transaction.description, re.IGNORECASE):
                    matched = True
            except re.error:
                continue

        if matched:
            # Score based on rule specificity and priority
            # Higher priority (lower number) = higher score
            base_score = 30
            priority_factor = max(0, (100 - rule.priority) / 100)
            score = int(base_score * priority_factor)
            score = max(15, min(score, 30))  # Clamp between 15-30

            category = rule.expense_category or rule.income_type or rule.map_to

            return {
                'score': score,
                'explanation': f"Rule '{rule.text_to_match}' → {category}",
                'rule_text': rule.text_to_match,
                'category': category
            }

    return {
        'score': 0,
        'explanation': 'No matching rule found',
        'rule_text': ''
    }


def calculate_pattern_learning_score(transaction, session) -> Dict:
    """
    Calculate pattern learning score (0-20 points)

    Returns:
        Dict with score and explanation
    """
    from models import Transaction

    # Extract merchant name
    desc = transaction.description
    cleaned = re.sub(r'\d{4}\s*\w{3}\d{2}', '', desc)  # Remove dates
    cleaned = re.sub(r'\d{2}/\d{2}/\d{2,4}', '', cleaned)
    cleaned = re.sub(r',.*', '', cleaned).strip()
    merchant_key = cleaned[:30] if len(cleaned) >= 10 else cleaned

    if not merchant_key or len(merchant_key) < 3:
        return {
            'score': 0,
            'explanation': 'Merchant name too short to analyze',
            'similar_count': 0
        }

    # Find similar reviewed transactions
    similar = session.query(Transaction).filter(
        Transaction.description.like(f'%{merchant_key}%'),
        Transaction.reviewed == True,
        Transaction.id != transaction.id
    ).limit(50).all()

    if not similar:
        return {
            'score': 0,
            'explanation': 'No similar transactions found',
            'similar_count': 0
        }

    # Score based on number of similar transactions and consistency
    count = len(similar)

    # Check consistency (same category)
    if transaction.guessed_category:
        consistent = sum(
            1 for t in similar
            if t.guessed_category == transaction.guessed_category
        )
        consistency_ratio = consistent / count if count > 0 else 0
    else:
        consistency_ratio = 0.5

    # Calculate score
    # More similar transactions = higher score
    # Higher consistency = higher score
    count_score = min(count * 2, 15)  # Max 15 points for quantity
    consistency_score = int(consistency_ratio * 5)  # Max 5 points for consistency
    score = count_score + consistency_score

    if count >= 15:
        explanation = f"Very similar to {count} previous transactions"
    elif count >= 5:
        explanation = f"Similar to {count} previous transactions"
    else:
        explanation = f"Found {count} similar transaction(s)"

    return {
        'score': min(score, 20),
        'explanation': explanation,
        'similar_count': count,
        'consistency_ratio': consistency_ratio
    }


def calculate_amount_consistency_score(transaction, session) -> Dict:
    """
    Calculate amount consistency score (0-10 points)

    Returns:
        Dict with score and explanation
    """
    from models import Transaction

    # Extract merchant name
    desc = transaction.description
    cleaned = re.sub(r'\d{4}\s*\w{3}\d{2}', '', desc)
    cleaned = re.sub(r'\d{2}/\d{2}/\d{2,4}', '', cleaned)
    cleaned = re.sub(r',.*', '', cleaned).strip()
    merchant_key = cleaned[:30] if len(cleaned) >= 10 else cleaned

    if not merchant_key or len(merchant_key) < 3:
        return {
            'score': 0,
            'explanation': 'Cannot analyze amount consistency',
        }

    # Get transaction amount
    amount = transaction.paid_in if transaction.paid_in > 0 else transaction.paid_out

    if amount == 0:
        return {
            'score': 0,
            'explanation': 'No amount data available',
        }

    # Find similar transactions
    similar = session.query(Transaction).filter(
        Transaction.description.like(f'%{merchant_key}%'),
        Transaction.id != transaction.id
    ).limit(20).all()

    if not similar:
        return {
            'score': 5,  # Default middle score if no history
            'explanation': 'No historical amounts to compare',
        }

    # Calculate amount variance
    amounts = []
    for t in similar:
        t_amount = t.paid_in if t.paid_in > 0 else t.paid_out
        if t_amount > 0:
            amounts.append(t_amount)

    if not amounts:
        return {
            'score': 5,
            'explanation': 'No historical amounts to compare',
        }

    # Check if amount is within typical range
    avg_amount = sum(amounts) / len(amounts)
    variance = abs((amount - avg_amount) / avg_amount) if avg_amount > 0 else 1

    # Score based on consistency
    if variance < 0.1:  # Within 10%
        score = 10
        explanation = f"Amount typical for this merchant (±10%)"
    elif variance < 0.25:  # Within 25%
        score = 7
        explanation = f"Amount within normal range for this merchant"
    elif variance < 0.5:  # Within 50%
        score = 4
        explanation = f"Amount slightly unusual for this merchant"
    else:
        score = 2
        explanation = f"Amount differs significantly from typical"

    return {
        'score': score,
        'explanation': explanation,
        'variance': variance
    }


def generate_confidence_explanation(score: int) -> str:
    """
    Generate human-readable explanation for confidence score

    Args:
        score: Confidence score (0-100)

    Returns:
        Human-readable explanation string
    """
    if score >= 70:
        return "We're very confident this categorization is correct"
    elif score >= 40:
        return "This looks likely based on patterns and rules"
    elif score >= 10:
        return "This is our best guess - please review carefully"
    else:
        return "No strong matches found - manual review required"


def get_confidence_level(score: int) -> Dict:
    """
    Get confidence level information

    Args:
        score: Confidence score (0-100)

    Returns:
        Dict with level, color, emoji, and description
    """
    if score >= 70:
        return {
            'level': 'High',
            'color': '#28a745',
            'emoji': '🟢',
            'description': "We're very confident this is correct"
        }
    elif score >= 40:
        return {
            'level': 'Medium',
            'color': '#ffc107',
            'emoji': '🟡',
            'description': "This looks likely based on patterns"
        }
    elif score >= 10:
        return {
            'level': 'Low',
            'color': '#ff9800',
            'emoji': '🟠',
            'description': "This is just our best guess"
        }
    else:
        return {
            'level': 'None',
            'color': '#dc3545',
            'emoji': '🔴',
            'description': "No matches found - please review carefully"
        }


def render_confidence_tooltip(confidence_score: int, breakdown: Dict, show_badge: bool = True):
    """
    Render confidence tooltip with detailed breakdown

    Args:
        confidence_score: Overall confidence score (0-100)
        breakdown: Detailed breakdown from calculate_confidence_breakdown()
        show_badge: Whether to show the confidence badge
    """
    if confidence_score is None or confidence_score == 0:
        return

    level_info = get_confidence_level(confidence_score)

    # Generate unique key for this tooltip
    tooltip_id = f"conf_{id(breakdown)}"

    # Inject CSS for tooltip styling
    st.markdown("""
    <style>
    .confidence-tooltip-container {
        display: inline-block;
        position: relative;
    }

    .confidence-badge {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: 600;
        color: white;
        cursor: help;
        transition: all 0.2s ease;
    }

    .confidence-badge:hover {
        transform: scale(1.05);
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    }

    .confidence-info-icon {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 18px;
        height: 18px;
        border-radius: 50%;
        background: rgba(255,255,255,0.3);
        font-size: 12px;
        margin-left: 2px;
        cursor: help;
    }

    .confidence-breakdown-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 12px;
        margin: 10px 0;
        box-shadow: 0 4px 20px rgba(0,0,0,0.15);
    }

    .breakdown-header {
        font-size: 16px;
        font-weight: 600;
        margin-bottom: 15px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .breakdown-factor {
        background: rgba(255,255,255,0.1);
        padding: 12px;
        border-radius: 8px;
        margin-bottom: 10px;
        transition: all 0.2s ease;
    }

    .breakdown-factor:hover {
        background: rgba(255,255,255,0.15);
        transform: translateX(2px);
    }

    .factor-label {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 6px;
        font-size: 13px;
    }

    .factor-score {
        font-weight: 700;
        font-size: 14px;
    }

    .progress-bar-container {
        width: 100%;
        height: 8px;
        background: rgba(255,255,255,0.2);
        border-radius: 4px;
        overflow: hidden;
        margin-bottom: 4px;
    }

    .progress-bar-fill {
        height: 100%;
        background: linear-gradient(90deg, #4CAF50 0%, #8BC34A 100%);
        border-radius: 4px;
        transition: width 0.5s ease;
    }

    .progress-bar-fill.empty {
        background: rgba(255,255,255,0.1);
    }

    .factor-explanation {
        font-size: 11px;
        opacity: 0.9;
        margin-top: 4px;
    }

    .total-score {
        background: rgba(255,255,255,0.2);
        padding: 15px;
        border-radius: 8px;
        margin-top: 15px;
        text-align: center;
        font-size: 18px;
        font-weight: 700;
    }

    .total-score-label {
        font-size: 12px;
        opacity: 0.8;
        margin-bottom: 5px;
    }

    .confidence-explanation {
        background: rgba(255,255,255,0.1);
        padding: 10px;
        border-radius: 6px;
        margin-top: 10px;
        font-size: 12px;
        text-align: center;
        font-style: italic;
    }
    </style>
    """, unsafe_allow_html=True)

    # Render badge if requested
    if show_badge:
        st.markdown(f"""
        <div class="confidence-tooltip-container">
            <span class="confidence-badge" style="background-color: {level_info['color']};">
                <span>{level_info['emoji']}</span>
                <span>{level_info['level']}</span>
                <span>{confidence_score}%</span>
                <span class="confidence-info-icon" title="Click to see breakdown">ⓘ</span>
            </span>
        </div>
        """, unsafe_allow_html=True)


def render_confidence_breakdown_card(breakdown: Dict):
    """
    Render detailed confidence breakdown as an expandable card

    Args:
        breakdown: Detailed breakdown from calculate_confidence_breakdown()
    """
    st.markdown("""
    <div class="confidence-breakdown-card">
        <div class="breakdown-header">
            📊 Confidence Score Breakdown
        </div>
    """, unsafe_allow_html=True)

    # Render each factor
    factors = [
        ('Merchant Match', 'merchant_match', '🏪'),
        ('Rule Match', 'rule_match', '📋'),
        ('Pattern Learning', 'pattern_learning', '🧠'),
        ('Amount Consistency', 'amount_consistency', '💰'),
    ]

    for label, key, emoji in factors:
        factor = breakdown[key]
        score = factor['score']
        max_score = factor['max']
        explanation = factor['explanation']

        # Calculate percentage for progress bar
        percentage = (score / max_score * 100) if max_score > 0 else 0
        bar_class = '' if score > 0 else 'empty'

        st.markdown(f"""
        <div class="breakdown-factor">
            <div class="factor-label">
                <span>{emoji} {label}</span>
                <span class="factor-score">+{score}/{max_score}</span>
            </div>
            <div class="progress-bar-container">
                <div class="progress-bar-fill {bar_class}" style="width: {percentage}%;"></div>
            </div>
            <div class="factor-explanation">{explanation}</div>
        </div>
        """, unsafe_allow_html=True)

    # Total score
    st.markdown(f"""
        <div class="total-score">
            <div class="total-score-label">TOTAL CONFIDENCE</div>
            <div>{breakdown['total_score']}%</div>
        </div>
        <div class="confidence-explanation">
            💡 {breakdown['explanation']}
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_inline_confidence_indicator(confidence_score: int, compact: bool = False):
    """
    Render a compact inline confidence indicator

    Args:
        confidence_score: Confidence score (0-100)
        compact: If True, show only emoji and score
    """
    if confidence_score is None or confidence_score == 0:
        return

    level_info = get_confidence_level(confidence_score)

    if compact:
        st.markdown(f"""
        <span style="background-color: {level_info['color']}; color: white;
                     padding: 2px 6px; border-radius: 10px; font-size: 10px;
                     font-weight: 600; margin-left: 4px;">
            {level_info['emoji']} {confidence_score}%
        </span>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <span style="background-color: {level_info['color']}; color: white;
                     padding: 3px 10px; border-radius: 12px; font-size: 11px;
                     font-weight: 600; margin-left: 5px; display: inline-flex;
                     align-items: center; gap: 4px;">
            <span>{level_info['emoji']}</span>
            <span>{level_info['level']}</span>
            <span>{confidence_score}%</span>
        </span>
        """, unsafe_allow_html=True)


def render_confidence_with_breakdown(transaction, session, key_prefix: str = ""):
    """
    Render confidence badge with expandable breakdown

    Args:
        transaction: Transaction object
        session: SQLAlchemy session
        key_prefix: Unique prefix for widget keys
    """
    if not transaction.confidence_score:
        return

    # Calculate breakdown
    breakdown = calculate_confidence_breakdown(transaction, session)
    level_info = get_confidence_level(transaction.confidence_score)

    # Create columns for badge and expander
    col1, col2 = st.columns([1, 4])

    with col1:
        st.markdown(f"""
        <span style="background-color: {level_info['color']}; color: white;
                     padding: 4px 10px; border-radius: 12px; font-size: 11px;
                     font-weight: 600; display: inline-flex; align-items: center;
                     gap: 4px; white-space: nowrap;">
            <span>{level_info['emoji']}</span>
            <span>{level_info['level']}</span>
            <span>{transaction.confidence_score}%</span>
        </span>
        """, unsafe_allow_html=True)

    with col2:
        with st.expander("ⓘ See breakdown", expanded=False):
            render_confidence_breakdown_card(breakdown)


def render_help_modal():
    """
    Render help modal explaining the confidence scoring system
    """
    st.markdown("""
    <style>
    .help-modal {
        background: linear-gradient(135deg, #6e8efb 0%, #a777e3 100%);
        color: white;
        padding: 30px;
        border-radius: 15px;
        margin: 20px 0;
        box-shadow: 0 10px 40px rgba(0,0,0,0.2);
    }

    .help-section {
        background: rgba(255,255,255,0.1);
        padding: 15px;
        border-radius: 10px;
        margin: 15px 0;
    }

    .help-section h4 {
        margin-top: 0;
        color: #FFD700;
    }

    .help-factor {
        background: rgba(255,255,255,0.05);
        padding: 10px;
        border-radius: 6px;
        margin: 8px 0;
    }

    .help-example {
        background: rgba(255,255,255,0.08);
        padding: 12px;
        border-radius: 8px;
        margin: 10px 0;
        font-style: italic;
        font-size: 13px;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="help-modal">
        <h2 style="margin-top: 0;">🎯 How Confidence Scoring Works</h2>

        <p style="font-size: 16px; opacity: 0.95;">
            Our AI system assigns a confidence score (0-100%) to each transaction categorization
            based on four key factors. Here's how it works:
        </p>

        <div class="help-section">
            <h4>🏪 Merchant Match (0-40 points)</h4>
            <p>We compare the transaction description against our database of 500+ UK merchants.</p>
            <div class="help-factor">
                <strong>40 points:</strong> Exact match with 100% certainty (e.g., TESCO, NETFLIX)
            </div>
            <div class="help-factor">
                <strong>35 points:</strong> High confidence match (e.g., known business supplier)
            </div>
            <div class="help-factor">
                <strong>28 points:</strong> Medium confidence match (e.g., could be business or personal)
            </div>
            <div class="help-factor">
                <strong>20 points:</strong> Low confidence match (ambiguous merchant)
            </div>
            <div class="help-example">
                💡 Example: "TESCO STORES 2341" → Matches TESCO in database (+35 points)
            </div>
        </div>

        <div class="help-section">
            <h4>📋 Rule Match (0-30 points)</h4>
            <p>We check if any of your custom categorization rules apply to this transaction.</p>
            <div class="help-factor">
                <strong>30 points:</strong> High priority rule match (priority 1-20)
            </div>
            <div class="help-factor">
                <strong>25 points:</strong> Medium priority rule match (priority 21-50)
            </div>
            <div class="help-factor">
                <strong>15 points:</strong> Low priority rule match (priority 51-100)
            </div>
            <div class="help-example">
                💡 Example: "AMAZON MKTP" → Matches rule "AMAZON → Office costs" (+25 points)
            </div>
        </div>

        <div class="help-section">
            <h4>🧠 Pattern Learning (0-20 points)</h4>
            <p>We analyze similar transactions you've categorized before to learn patterns.</p>
            <div class="help-factor">
                <strong>20 points:</strong> 15+ similar transactions with consistent categorization
            </div>
            <div class="help-factor">
                <strong>15 points:</strong> 10-14 similar transactions
            </div>
            <div class="help-factor">
                <strong>10 points:</strong> 5-9 similar transactions
            </div>
            <div class="help-factor">
                <strong>5 points:</strong> 1-4 similar transactions
            </div>
            <div class="help-example">
                💡 Example: You've categorized 12 previous "UBER" transactions as Travel → +15 points
            </div>
        </div>

        <div class="help-section">
            <h4>💰 Amount Consistency (0-10 points)</h4>
            <p>We check if the transaction amount is typical for this merchant.</p>
            <div class="help-factor">
                <strong>10 points:</strong> Amount within 10% of historical average
            </div>
            <div class="help-factor">
                <strong>7 points:</strong> Amount within 25% of historical average
            </div>
            <div class="help-factor">
                <strong>4 points:</strong> Amount within 50% of historical average
            </div>
            <div class="help-factor">
                <strong>2 points:</strong> Amount significantly different from typical
            </div>
            <div class="help-example">
                💡 Example: NETFLIX £10.99 (typical) → +10 points vs NETFLIX £99.99 (unusual) → +2 points
            </div>
        </div>

        <div class="help-section">
            <h4>📊 Confidence Levels</h4>
            <div class="help-factor">
                <strong style="color: #90EE90;">🟢 High (70-100%):</strong> We're very confident this is correct
            </div>
            <div class="help-factor">
                <strong style="color: #FFD700;">🟡 Medium (40-69%):</strong> This looks likely based on patterns
            </div>
            <div class="help-factor">
                <strong style="color: #FFA500;">🟠 Low (10-39%):</strong> This is just our best guess
            </div>
            <div class="help-factor">
                <strong style="color: #FF6B6B;">🔴 None (0-9%):</strong> No matches found - please review carefully
            </div>
        </div>

        <div style="background: rgba(255,255,255,0.15); padding: 15px; border-radius: 10px;
                    margin-top: 20px; text-align: center;">
            <strong>💡 Pro Tip:</strong> The more transactions you review and categorize, the smarter
            the system becomes at learning your preferences and patterns!
        </div>
    </div>
    """, unsafe_allow_html=True)


def get_confidence_explanation(score: int) -> str:
    """
    Get human-readable confidence explanation

    Args:
        score: Confidence score (0-100)

    Returns:
        Explanation string
    """
    return generate_confidence_explanation(score)


def render_bulk_confidence_stats(transactions, session):
    """
    Render confidence statistics for bulk operations

    Args:
        transactions: List of Transaction objects
        session: SQLAlchemy session
    """
    if not transactions:
        return

    # Calculate average confidence
    scores = [t.confidence_score for t in transactions if t.confidence_score]

    if not scores:
        st.info("No confidence scores available for selected transactions")
        return

    avg_score = sum(scores) / len(scores)
    level_info = get_confidence_level(int(avg_score))

    # Count by level
    high_count = sum(1 for s in scores if s >= 70)
    medium_count = sum(1 for s in scores if 40 <= s < 70)
    low_count = sum(1 for s in scores if s < 40)

    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white; padding: 20px; border-radius: 12px; margin: 10px 0;">
        <h4 style="margin-top: 0;">📊 Bulk Confidence Statistics</h4>
        <div style="display: flex; justify-content: space-around; margin: 15px 0;">
            <div style="text-align: center;">
                <div style="font-size: 28px; font-weight: bold;">{int(avg_score)}%</div>
                <div style="font-size: 12px; opacity: 0.9;">Average Confidence</div>
            </div>
            <div style="text-align: center;">
                <div style="font-size: 28px; font-weight: bold; color: #90EE90;">🟢 {high_count}</div>
                <div style="font-size: 12px; opacity: 0.9;">High Confidence</div>
            </div>
            <div style="text-align: center;">
                <div style="font-size: 28px; font-weight: bold; color: #FFD700;">🟡 {medium_count}</div>
                <div style="font-size: 12px; opacity: 0.9;">Medium Confidence</div>
            </div>
            <div style="text-align: center;">
                <div style="font-size: 28px; font-weight: bold; color: #FF6B6B;">🔴 {low_count}</div>
                <div style="font-size: 12px; opacity: 0.9;">Low Confidence</div>
            </div>
        </div>
        <div style="background: rgba(255,255,255,0.15); padding: 10px; border-radius: 8px;
                    text-align: center; margin-top: 15px;">
            💡 {level_info['description']}
        </div>
    </div>
    """, unsafe_allow_html=True)


# Quick access functions for common use cases

def quick_render_badge(score: int):
    """Quick render confidence badge only"""
    render_inline_confidence_indicator(score, compact=False)


def quick_render_compact(score: int):
    """Quick render compact confidence indicator"""
    render_inline_confidence_indicator(score, compact=True)


def quick_render_full(transaction, session):
    """Quick render full confidence with breakdown"""
    render_confidence_with_breakdown(transaction, session)
