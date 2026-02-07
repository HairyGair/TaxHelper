"""
UK Transaction Pattern Recognition Engine
Detects patterns in bank transactions to improve auto-categorization accuracy
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
from enum import Enum
from collections import defaultdict
import re
import hashlib


# ===================================================================
# ENUMS AND CONSTANTS
# ===================================================================

class PatternType(Enum):
    """Types of transaction patterns that can be detected"""
    RECURRING_PAYMENT = "recurring_payment"
    GOVERNMENT_BENEFIT = "government_benefit"
    INTERNAL_TRANSFER = "internal_transfer"
    ROUND_UP = "round_up"
    RECURRING_SMALL_AMOUNT = "recurring_small_amount"
    LARGE_PURCHASE = "large_purchase"
    NO_PATTERN = "no_pattern"


# ===================================================================
# DATA CLASSES
# ===================================================================

@dataclass
class PatternMatch:
    """Represents a single pattern detection result for a transaction"""
    pattern_type: PatternType
    confidence: int  # 0-100
    metadata: Dict[str, any]
    transaction_id: int
    notes: str = ""


@dataclass
class PatternGroup:
    """Groups related transactions that share a pattern"""
    group_id: str
    pattern_type: PatternType
    transaction_ids: List[int]
    description_normalized: str
    frequency_days: Optional[int] = None
    average_amount: Optional[float] = None
    variance_percent: Optional[float] = None
    first_occurrence: Optional[datetime] = None
    last_occurrence: Optional[datetime] = None
    occurrences: int = 0


@dataclass
class AnalysisResult:
    """Complete analysis result for a single transaction"""
    transaction_id: int
    pattern_matches: List[PatternMatch]
    primary_pattern: Optional[PatternMatch] = None
    pattern_confidence: int = 0
    suggested_type: Optional[str] = None
    suggested_category: Optional[str] = None
    is_personal: Optional[bool] = None
    requires_review: bool = False
    notes: List[str] = field(default_factory=list)


# ===================================================================
# UTILITY FUNCTIONS
# ===================================================================

def normalize_description(description: str) -> str:
    """
    Normalize transaction descriptions for pattern matching

    Removes:
    - Dates (various formats)
    - Transaction IDs and reference numbers
    - Multiple spaces
    - Special characters

    Example:
        "TESCO STORE 12345 REF:ABC123 04/01/25" -> "TESCO STORE"
    """
    if not description:
        return ""

    text = description.upper().strip()

    # Remove common reference patterns
    text = re.sub(r'\bREF:?\s*[A-Z0-9]+', '', text)
    text = re.sub(r'\b[A-Z]{2}\d{6}[A-Z]?\b', '', text)  # DWP reference codes
    text = re.sub(r'\b\d{4,}\b', '', text)  # Long numbers (transaction IDs)

    # Remove dates
    text = re.sub(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b', '', text)
    text = re.sub(r'\b\d{1,2}-[A-Z]{3}-\d{2,4}\b', '', text)

    # Remove card numbers
    text = re.sub(r'\*+\d{4}', '', text)

    # Clean up spaces and punctuation
    text = re.sub(r'[^A-Z0-9\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text)

    return text.strip()


def calculate_interval_consistency(dates: List[datetime]) -> Tuple[int, float]:
    """
    Calculate average interval and variance for recurring transactions

    Returns:
        (average_days, variance_percentage)
    """
    if len(dates) < 2:
        return 0, 0.0

    sorted_dates = sorted(dates)
    intervals = []

    for i in range(1, len(sorted_dates)):
        interval = (sorted_dates[i] - sorted_dates[i-1]).days
        intervals.append(interval)

    if not intervals:
        return 0, 0.0

    avg_interval = sum(intervals) / len(intervals)

    # Calculate variance as percentage
    if avg_interval > 0:
        variance = sum(abs(interval - avg_interval) for interval in intervals) / len(intervals)
        variance_percent = (variance / avg_interval) * 100
    else:
        variance_percent = 0.0

    return int(avg_interval), variance_percent


def calculate_amount_consistency(amounts: List[float]) -> Tuple[float, float]:
    """
    Calculate average and variance for recurring amounts

    Returns:
        (average_amount, variance_percentage)
    """
    if not amounts:
        return 0.0, 0.0

    avg_amount = sum(amounts) / len(amounts)

    if avg_amount > 0:
        variance = sum(abs(amount - avg_amount) for amount in amounts) / len(amounts)
        variance_percent = (variance / avg_amount) * 100
    else:
        variance_percent = 0.0

    return avg_amount, variance_percent


def generate_group_id(pattern_type: PatternType, description: str) -> str:
    """Generate unique ID for a pattern group"""
    key = f"{pattern_type.value}:{description}"
    return hashlib.md5(key.encode()).hexdigest()[:12]


# ===================================================================
# BASE PATTERN DETECTOR
# ===================================================================

class BasePatternDetector(ABC):
    """Abstract base class for all pattern detectors"""

    @property
    @abstractmethod
    def pattern_type(self) -> PatternType:
        """Return the pattern type this detector identifies"""
        pass

    @property
    def min_confidence_threshold(self) -> int:
        """Minimum confidence to report a match (default: 50)"""
        return 50

    @abstractmethod
    def detect_patterns(
        self,
        transactions: List,
        existing_groups: Optional[List[PatternGroup]] = None
    ) -> List[PatternGroup]:
        """
        Analyze transactions to identify pattern groups

        Args:
            transactions: List of Transaction model instances
            existing_groups: Previously identified groups (for incremental updates)

        Returns:
            List of PatternGroup objects
        """
        pass

    @abstractmethod
    def match_transaction(
        self,
        transaction,
        pattern_groups: List[PatternGroup]
    ) -> Optional[PatternMatch]:
        """
        Match a single transaction against known pattern groups

        Args:
            transaction: Transaction model instance
            pattern_groups: Known patterns to match against

        Returns:
            PatternMatch if found, None otherwise
        """
        pass


# ===================================================================
# RECURRING PAYMENT DETECTOR
# ===================================================================

class RecurringPaymentDetector(BasePatternDetector):
    """
    Detects regular monthly/weekly payments (bills, subscriptions, salaries)

    Algorithm:
    - Groups transactions by normalized description
    - Checks for regular intervals (7, 14, 28-31, 91 days)
    - Validates amount consistency (within 5% variance)
    - Requires minimum 3 occurrences
    """

    # Configuration
    FREQUENCY_TOLERANCE_DAYS = 3
    AMOUNT_VARIANCE_PERCENT = 5.0
    MIN_OCCURRENCES = 3
    EXPECTED_FREQUENCIES = [7, 14, 28, 29, 30, 31, 91]  # Weekly, fortnightly, monthly, quarterly

    @property
    def pattern_type(self) -> PatternType:
        return PatternType.RECURRING_PAYMENT

    def detect_patterns(self, transactions: List, existing_groups=None) -> List[PatternGroup]:
        """Detect recurring payment patterns"""
        if len(transactions) < self.MIN_OCCURRENCES:
            return []

        # Group by normalized description
        groups_by_desc = defaultdict(list)

        for txn in transactions:
            normalized = normalize_description(txn.description)
            if normalized:
                groups_by_desc[normalized].append(txn)

        pattern_groups = []

        for normalized_desc, txn_list in groups_by_desc.items():
            if len(txn_list) < self.MIN_OCCURRENCES:
                continue

            # Sort by date
            txn_list.sort(key=lambda t: t.date)

            # Check for consistent amounts
            amounts = [t.paid_out if t.paid_out > 0 else t.paid_in for t in txn_list]
            avg_amount, variance_percent = calculate_amount_consistency(amounts)

            if variance_percent > self.AMOUNT_VARIANCE_PERCENT:
                continue  # Too much variation in amounts

            # Check for regular intervals
            dates = [t.date for t in txn_list]
            avg_interval, interval_variance = calculate_interval_consistency(dates)

            # Check if interval matches expected frequencies
            is_regular = False
            for expected_freq in self.EXPECTED_FREQUENCIES:
                if abs(avg_interval - expected_freq) <= self.FREQUENCY_TOLERANCE_DAYS:
                    is_regular = True
                    break

            if not is_regular:
                continue

            # Create pattern group
            group_id = generate_group_id(self.pattern_type, normalized_desc)

            pattern_groups.append(PatternGroup(
                group_id=group_id,
                pattern_type=self.pattern_type,
                transaction_ids=[t.id for t in txn_list],
                description_normalized=normalized_desc,
                frequency_days=avg_interval,
                average_amount=avg_amount,
                variance_percent=variance_percent,
                first_occurrence=txn_list[0].date,
                last_occurrence=txn_list[-1].date,
                occurrences=len(txn_list)
            ))

        return pattern_groups

    def match_transaction(self, transaction, pattern_groups: List[PatternGroup]) -> Optional[PatternMatch]:
        """Match transaction to recurring payment groups"""
        normalized = normalize_description(transaction.description)

        for group in pattern_groups:
            if group.pattern_type != self.pattern_type:
                continue

            if group.description_normalized == normalized:
                # Calculate confidence based on group strength
                confidence = 70  # Base confidence

                # Boost for long-running patterns
                if group.occurrences >= 12:
                    confidence += 15
                elif group.occurrences >= 6:
                    confidence += 10
                elif group.occurrences >= 4:
                    confidence += 5

                # Boost for low variance
                if group.variance_percent < 2.0:
                    confidence += 10
                elif group.variance_percent < 5.0:
                    confidence += 5

                confidence = min(confidence, 95)  # Cap at 95

                return PatternMatch(
                    pattern_type=self.pattern_type,
                    confidence=confidence,
                    metadata={
                        'group_id': group.group_id,
                        'frequency_days': group.frequency_days,
                        'average_amount': group.average_amount,
                        'occurrences': group.occurrences,
                        'variance_percent': group.variance_percent
                    },
                    transaction_id=transaction.id,
                    notes=f"Recurring payment: {group.occurrences}x occurrences, every ~{group.frequency_days} days"
                )

        return None


# ===================================================================
# GOVERNMENT BENEFIT DETECTOR
# ===================================================================

class GovernmentBenefitDetector(BasePatternDetector):
    """
    Detects UK government benefit payments (Universal Credit, PIP, ESA, etc.)

    Keywords:
    - DWP (Department for Work and Pensions)
    - HMRC benefit keywords
    - Specific benefit codes: UC, PIP, ESA, JSA, etc.
    """

    BENEFIT_KEYWORDS = {
        'universal_credit': ['DWP UC', 'UNIVERSAL CREDIT', 'DWP UNIVERSAL'],
        'pip': ['DWP PIP', 'PERSONAL INDEPENDENCE'],
        'esa': ['DWP ESA', 'EMPLOYMENT SUPPORT'],
        'carers_allowance': ['DWP CA', 'CARERS ALLOWANCE', 'CARER ALLOWANCE'],
        'dla': ['DWP DLA', 'DISABILITY LIVING'],
        'jsa': ['DWP JSA', 'JOBSEEKER'],
        'pension_credit': ['DWP PC', 'PENSION CREDIT'],
        'child_benefit': ['CHILD BENEFIT', 'CHB', 'HMRC CHILD'],
        'tax_credit': ['TAX CREDIT', 'HMRC TAX CREDIT'],
        'state_pension': ['STATE PENSION', 'PENSION SERVICE'],
    }

    @property
    def pattern_type(self) -> PatternType:
        return PatternType.GOVERNMENT_BENEFIT

    def detect_patterns(self, transactions: List, existing_groups=None) -> List[PatternGroup]:
        """Detect government benefit patterns"""
        benefit_groups = defaultdict(list)

        for txn in transactions:
            if txn.paid_in <= 0:  # Benefits are always paid in
                continue

            desc_upper = txn.description.upper()

            for benefit_type, keywords in self.BENEFIT_KEYWORDS.items():
                for keyword in keywords:
                    if keyword in desc_upper:
                        benefit_groups[benefit_type].append(txn)
                        break

        pattern_groups = []

        for benefit_type, txn_list in benefit_groups.items():
            if not txn_list:
                continue

            txn_list.sort(key=lambda t: t.date)

            group_id = generate_group_id(self.pattern_type, benefit_type)

            dates = [t.date for t in txn_list]
            amounts = [t.paid_in for t in txn_list]

            avg_interval, interval_variance = calculate_interval_consistency(dates)
            avg_amount, amount_variance = calculate_amount_consistency(amounts)

            pattern_groups.append(PatternGroup(
                group_id=group_id,
                pattern_type=self.pattern_type,
                transaction_ids=[t.id for t in txn_list],
                description_normalized=benefit_type,
                frequency_days=avg_interval,
                average_amount=avg_amount,
                variance_percent=amount_variance,
                first_occurrence=txn_list[0].date,
                last_occurrence=txn_list[-1].date,
                occurrences=len(txn_list)
            ))

        return pattern_groups

    def match_transaction(self, transaction, pattern_groups: List[PatternGroup]) -> Optional[PatternMatch]:
        """Match transaction to government benefit patterns"""
        if transaction.paid_in <= 0:
            return None

        desc_upper = transaction.description.upper()

        for benefit_type, keywords in self.BENEFIT_KEYWORDS.items():
            for keyword in keywords:
                if keyword in desc_upper:
                    # High confidence for government benefits
                    confidence = 95

                    return PatternMatch(
                        pattern_type=self.pattern_type,
                        confidence=confidence,
                        metadata={
                            'benefit_type': benefit_type,
                            'keyword_matched': keyword
                        },
                        transaction_id=transaction.id,
                        notes=f"UK Government Benefit: {benefit_type.replace('_', ' ').title()}"
                    )

        return None


# ===================================================================
# INTERNAL TRANSFER DETECTOR
# ===================================================================

class InternalTransferDetector(BasePatternDetector):
    """
    Detects transfers between accounts belonging to same person

    Patterns:
    - Keywords: TRANSFER, TO/FROM, SAVINGS, CURRENT
    - Matching amounts on same day
    """

    TRANSFER_KEYWORDS = [
        'TRANSFER', 'TO SAVINGS', 'FROM SAVINGS', 'INTERNAL',
        'BETWEEN ACCOUNTS', 'TO CURRENT', 'FROM CURRENT'
    ]

    @property
    def pattern_type(self) -> PatternType:
        return PatternType.INTERNAL_TRANSFER

    def detect_patterns(self, transactions: List, existing_groups=None) -> List[PatternGroup]:
        """Detect internal transfer patterns"""
        # Group potential transfers by date and amount
        transfers_by_date = defaultdict(list)

        for txn in transactions:
            desc_upper = txn.description.upper()

            # Check for transfer keywords
            has_keyword = any(keyword in desc_upper for keyword in self.TRANSFER_KEYWORDS)

            if has_keyword:
                date_key = txn.date.strftime('%Y-%m-%d')
                transfers_by_date[date_key].append(txn)

        # Note: Full matching pairs logic would be more complex
        # For now, just identify transactions with transfer keywords

        return []  # Pairs would be complex to track

    def match_transaction(self, transaction, pattern_groups: List[PatternGroup]) -> Optional[PatternMatch]:
        """Match transaction to internal transfer pattern"""
        desc_upper = transaction.description.upper()

        # Check for transfer keywords
        matched_keyword = None
        for keyword in self.TRANSFER_KEYWORDS:
            if keyword in desc_upper:
                matched_keyword = keyword
                break

        if matched_keyword:
            return PatternMatch(
                pattern_type=self.pattern_type,
                confidence=90,
                metadata={'keyword': matched_keyword},
                transaction_id=transaction.id,
                notes="Internal transfer between own accounts"
            )

        return None


# ===================================================================
# ROUND-UP DETECTOR
# ===================================================================

class RoundUpDetector(BasePatternDetector):
    """
    Detects savings round-up transactions (e.g., Monzo, Starling features)

    Characteristics:
    - Very small amounts (typically < £1)
    - Descriptions mentioning "round up", "spare change"
    - Frequent occurrences
    """

    MAX_ROUND_UP_AMOUNT = 1.0
    ROUND_UP_KEYWORDS = ['ROUND UP', 'SPARE CHANGE', 'ROUNDUP', 'SAVE THE CHANGE', 'ROUND-UP']

    @property
    def pattern_type(self) -> PatternType:
        return PatternType.ROUND_UP

    def detect_patterns(self, transactions: List, existing_groups=None) -> List[PatternGroup]:
        """Detect round-up savings patterns"""
        roundup_txns = []

        for txn in transactions:
            desc_upper = txn.description.upper()
            amount = txn.paid_out if txn.paid_out > 0 else 0

            has_keyword = any(keyword in desc_upper for keyword in self.ROUND_UP_KEYWORDS)

            if has_keyword or (amount > 0 and amount <= self.MAX_ROUND_UP_AMOUNT and 'SAVE' in desc_upper):
                roundup_txns.append(txn)

        if len(roundup_txns) >= 3:
            group_id = generate_group_id(self.pattern_type, "roundup_savings")

            return [PatternGroup(
                group_id=group_id,
                pattern_type=self.pattern_type,
                transaction_ids=[t.id for t in roundup_txns],
                description_normalized="ROUND UP SAVINGS",
                occurrences=len(roundup_txns)
            )]

        return []

    def match_transaction(self, transaction, pattern_groups: List[PatternGroup]) -> Optional[PatternMatch]:
        """Match transaction to round-up pattern"""
        desc_upper = transaction.description.upper()
        amount = transaction.paid_out if transaction.paid_out > 0 else 0

        has_keyword = any(keyword in desc_upper for keyword in self.ROUND_UP_KEYWORDS)

        if has_keyword or (amount > 0 and amount <= self.MAX_ROUND_UP_AMOUNT and 'SAVE' in desc_upper):
            return PatternMatch(
                pattern_type=self.pattern_type,
                confidence=100,
                metadata={'amount': amount},
                transaction_id=transaction.id,
                notes="Automatic savings round-up"
            )

        return None


# ===================================================================
# RECURRING SMALL AMOUNT DETECTOR
# ===================================================================

class RecurringSmallAmountDetector(BasePatternDetector):
    """
    Detects frequent small personal expenses (coffee, lunch, etc.)

    Characteristics:
    - Small amounts (< £15)
    - High frequency (multiple per week)
    - Same merchant
    """

    SMALL_AMOUNT_THRESHOLD = 15.0
    MIN_FREQUENCY_PER_MONTH = 4

    @property
    def pattern_type(self) -> PatternType:
        return PatternType.RECURRING_SMALL_AMOUNT

    def detect_patterns(self, transactions: List, existing_groups=None) -> List[PatternGroup]:
        """Detect recurring small purchase patterns"""
        small_txns_by_merchant = defaultdict(list)

        for txn in transactions:
            amount = txn.paid_out if txn.paid_out > 0 else 0

            if 0 < amount <= self.SMALL_AMOUNT_THRESHOLD:
                normalized = normalize_description(txn.description)
                if normalized:
                    small_txns_by_merchant[normalized].append(txn)

        pattern_groups = []

        for normalized_desc, txn_list in small_txns_by_merchant.items():
            if len(txn_list) < self.MIN_FREQUENCY_PER_MONTH:
                continue

            txn_list.sort(key=lambda t: t.date)

            group_id = generate_group_id(self.pattern_type, normalized_desc)

            pattern_groups.append(PatternGroup(
                group_id=group_id,
                pattern_type=self.pattern_type,
                transaction_ids=[t.id for t in txn_list],
                description_normalized=normalized_desc,
                occurrences=len(txn_list),
                first_occurrence=txn_list[0].date,
                last_occurrence=txn_list[-1].date
            ))

        return pattern_groups

    def match_transaction(self, transaction, pattern_groups: List[PatternGroup]) -> Optional[PatternMatch]:
        """Match transaction to recurring small amount pattern"""
        amount = transaction.paid_out if transaction.paid_out > 0 else 0

        if amount <= 0 or amount > self.SMALL_AMOUNT_THRESHOLD:
            return None

        normalized = normalize_description(transaction.description)

        for group in pattern_groups:
            if group.pattern_type != self.pattern_type:
                continue

            if group.description_normalized == normalized and group.occurrences >= self.MIN_FREQUENCY_PER_MONTH:
                confidence = 75

                if group.occurrences >= 10:
                    confidence = 85

                return PatternMatch(
                    pattern_type=self.pattern_type,
                    confidence=confidence,
                    metadata={
                        'group_id': group.group_id,
                        'occurrences': group.occurrences
                    },
                    transaction_id=transaction.id,
                    notes=f"Recurring small purchase: {group.occurrences}x occurrences"
                )

        return None


# ===================================================================
# LARGE PURCHASE DETECTOR
# ===================================================================

class LargePurchaseDetector(BasePatternDetector):
    """
    Flags unusually large one-time purchases for manual review

    Algorithm:
    - Calculate user's median transaction amount
    - Flag transactions > 5x median or > £1000
    """

    LARGE_AMOUNT_THRESHOLD = 1000.0
    MEDIAN_MULTIPLIER = 5.0

    @property
    def pattern_type(self) -> PatternType:
        return PatternType.LARGE_PURCHASE

    def detect_patterns(self, transactions: List, existing_groups=None) -> List[PatternGroup]:
        """Calculate median for large purchase detection"""
        # Don't create groups, just calculate thresholds
        return []

    def match_transaction(self, transaction, pattern_groups: List[PatternGroup]) -> Optional[PatternMatch]:
        """Flag large purchases"""
        amount = max(transaction.paid_out, transaction.paid_in)

        if amount >= self.LARGE_AMOUNT_THRESHOLD:
            return PatternMatch(
                pattern_type=self.pattern_type,
                confidence=60,
                metadata={'amount': amount},
                transaction_id=transaction.id,
                notes=f"Large transaction: £{amount:.2f} - recommend manual review"
            )

        return None


# ===================================================================
# PATTERN ANALYZER - MAIN ORCHESTRATOR
# ===================================================================

class PatternAnalyzer:
    """
    Main orchestrator for transaction pattern analysis
    Coordinates multiple pattern detectors and combines results
    """

    def __init__(self, session, enable_caching: bool = True):
        """
        Args:
            session: SQLAlchemy session for database access
            enable_caching: Cache pattern groups for performance
        """
        self.session = session
        self.enable_caching = enable_caching
        self._pattern_cache: Dict[PatternType, List[PatternGroup]] = {}

        # Initialize pattern detectors in priority order
        self.detectors: List[BasePatternDetector] = [
            GovernmentBenefitDetector(),     # Highest priority - always personal
            InternalTransferDetector(),       # High priority - should be ignored
            RoundUpDetector(),                # High priority - always personal
            RecurringPaymentDetector(),       # Medium priority
            RecurringSmallAmountDetector(),   # Lower priority
            LargePurchaseDetector(),          # Lowest priority - just flags
        ]

    def analyze_all_transactions(self, transactions: List) -> Dict[int, AnalysisResult]:
        """
        Analyze all transactions to detect patterns

        Args:
            transactions: List of Transaction model instances

        Returns:
            Dict mapping transaction_id -> AnalysisResult
        """
        if not transactions:
            return {}

        # Run detectors to build pattern groups
        all_pattern_groups = []

        for detector in self.detectors:
            try:
                groups = detector.detect_patterns(transactions)
                all_pattern_groups.extend(groups)
            except Exception as e:
                print(f"Warning: {detector.__class__.__name__} failed: {str(e)}")

        # Cache groups
        if self.enable_caching:
            for group in all_pattern_groups:
                if group.pattern_type not in self._pattern_cache:
                    self._pattern_cache[group.pattern_type] = []
                self._pattern_cache[group.pattern_type].append(group)

        # Match each transaction against groups
        results = {}

        for transaction in transactions:
            matches = self._match_transaction_to_patterns(transaction, all_pattern_groups)
            results[transaction.id] = self._create_analysis_result(transaction, matches)

        return results

    def _match_transaction_to_patterns(
        self,
        transaction,
        pattern_groups: List[PatternGroup]
    ) -> List[PatternMatch]:
        """Match a transaction against all pattern groups"""
        matches = []

        for detector in self.detectors:
            try:
                match = detector.match_transaction(transaction, pattern_groups)
                if match and match.confidence >= detector.min_confidence_threshold:
                    matches.append(match)
            except Exception as e:
                print(f"Warning: {detector.__class__.__name__} matching failed: {str(e)}")

        return matches

    def _create_analysis_result(
        self,
        transaction,
        matches: List[PatternMatch]
    ) -> AnalysisResult:
        """Create analysis result from pattern matches"""
        if not matches:
            return AnalysisResult(
                transaction_id=transaction.id,
                pattern_matches=[],
                pattern_confidence=0,
                notes=["No pattern detected"]
            )

        # Sort by confidence
        matches.sort(key=lambda m: m.confidence, reverse=True)
        primary_match = matches[0]

        # Determine suggested categorization based on pattern
        suggested_type = None
        suggested_category = None
        is_personal = None
        requires_review = False

        if primary_match.pattern_type == PatternType.GOVERNMENT_BENEFIT:
            suggested_type = "Income"
            suggested_category = "Government Benefits"
            is_personal = True
        elif primary_match.pattern_type == PatternType.RECURRING_PAYMENT:
            suggested_type = "Expense" if transaction.paid_out > 0 else "Income"
            suggested_category = "Recurring Payment"
            is_personal = True  # Most bills are personal
        elif primary_match.pattern_type == PatternType.INTERNAL_TRANSFER:
            suggested_type = "Ignore"
            is_personal = True
        elif primary_match.pattern_type == PatternType.ROUND_UP:
            suggested_type = "Ignore"
            is_personal = True
        elif primary_match.pattern_type == PatternType.RECURRING_SMALL_AMOUNT:
            suggested_type = "Expense"
            suggested_category = "Personal Spending"
            is_personal = True
        elif primary_match.pattern_type == PatternType.LARGE_PURCHASE:
            requires_review = True

        return AnalysisResult(
            transaction_id=transaction.id,
            pattern_matches=matches,
            primary_pattern=primary_match,
            pattern_confidence=primary_match.confidence,
            suggested_type=suggested_type,
            suggested_category=suggested_category,
            is_personal=is_personal,
            requires_review=requires_review,
            notes=[m.notes for m in matches if m.notes]
        )


# ===================================================================
# PUBLIC API FUNCTIONS
# ===================================================================

def analyze_transactions(session, transactions: List) -> Dict[int, AnalysisResult]:
    """
    Main entry point for pattern analysis

    Args:
        session: SQLAlchemy session
        transactions: List of Transaction model instances

    Returns:
        Dictionary mapping transaction_id to AnalysisResult
    """
    analyzer = PatternAnalyzer(session)
    return analyzer.analyze_all_transactions(transactions)


def merge_confidence_scores(
    pattern_confidence: int,
    merchant_confidence: int,
    pattern_type: Optional[PatternType] = None,
    pattern_personal: Optional[bool] = None,
    merchant_personal: Optional[bool] = None
) -> Tuple[int, bool]:
    """
    Combine pattern and merchant confidence scores

    Args:
        pattern_confidence: Confidence from pattern analysis (0-100)
        merchant_confidence: Confidence from merchant lookup (0-100)
        pattern_type: Type of pattern detected
        pattern_personal: Is personal according to pattern
        merchant_personal: Is personal according to merchant

    Returns:
        (combined_confidence, is_personal)
    """
    # High-confidence patterns take precedence
    if pattern_type in [PatternType.GOVERNMENT_BENEFIT, PatternType.INTERNAL_TRANSFER, PatternType.ROUND_UP]:
        if pattern_confidence >= 90:
            return pattern_confidence, pattern_personal if pattern_personal is not None else True

    # Check if both sources agree on personal/business
    both_agree = (pattern_personal is not None and
                  merchant_personal is not None and
                  pattern_personal == merchant_personal)

    # Both sources agree and are strong
    if both_agree and pattern_confidence > 70 and merchant_confidence > 70:
        combined = min(95, max(pattern_confidence, merchant_confidence) + 5)
        return combined, pattern_personal

    # One source is very strong
    if pattern_confidence > 80:
        return pattern_confidence, pattern_personal if pattern_personal is not None else True

    if merchant_confidence > 80:
        return merchant_confidence, merchant_personal if merchant_personal is not None else True

    # Both moderate: weighted average
    if pattern_confidence > 50 and merchant_confidence > 50:
        combined = int((pattern_confidence + merchant_confidence) / 2 * 1.1)
        combined = min(combined, 95)

        # Prefer pattern for personal flag if available
        is_personal = pattern_personal if pattern_personal is not None else merchant_personal
        return combined, is_personal

    # Default: take maximum
    max_conf = max(pattern_confidence, merchant_confidence)
    is_personal = pattern_personal if pattern_confidence >= merchant_confidence else merchant_personal

    return max_conf, is_personal if is_personal is not None else True
