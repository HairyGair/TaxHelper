"""
SQLAlchemy models for UK Self Assessment Tax Helper
Manages transactions, income, expenses, mileage, donations, rules, and settings
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, Date, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from enum import Enum
import os

Base = declarative_base()


class TransactionType(Enum):
    """Transaction type enum for categorization"""
    INCOME = "income"
    EXPENSE = "expense"
    TRANSFER = "transfer"
    IGNORE = "ignore"


class Transaction(Base):
    """
    Transaction inbox - imported from bank statements
    Transactions are reviewed and then posted to appropriate ledgers
    """
    __tablename__ = 'transactions'
    __table_args__ = (
        # Performance indexes for common queries
        {'extend_existing': True},
    )

    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False, index=True)  # Indexed for date filtering
    type = Column(String(50))  # POS, DD, CR, etc.
    description = Column(String(500), nullable=False)
    paid_out = Column(Float, default=0.0)
    paid_in = Column(Float, default=0.0)
    balance = Column(Float)
    guessed_type = Column(String(50))  # Income/Expense/Ignore
    guessed_category = Column(String(100))  # Specific category
    is_personal = Column(Boolean, default=False, index=True)  # Indexed for personal/business filtering
    reviewed = Column(Boolean, default=False, index=True)  # Indexed for reviewed/unreviewed filtering
    notes = Column(Text)

    # Smart categorization fields
    confidence_score = Column(Integer, default=0)  # Combined confidence (0-100)
    merchant_confidence = Column(Integer, default=0)  # Merchant database confidence
    pattern_confidence = Column(Integer, default=0)  # Pattern analysis confidence
    pattern_type = Column(String(50), nullable=True)  # Primary pattern detected
    pattern_group_id = Column(String(100), nullable=True)  # For linking recurring transactions
    pattern_metadata = Column(JSON, nullable=True)  # Store pattern-specific data
    requires_review = Column(Boolean, default=False)  # Flag for manual review

    import_date = Column(Date, default=datetime.now)
    account_name = Column(String(100), default='Main Account', index=True)  # Indexed for account filtering


class Income(Base):
    """
    Income ledger - all business income
    Tracks different income types for HMRC reporting
    """
    __tablename__ = 'income'

    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False, index=True)  # Indexed for date filtering
    source = Column(String(200), nullable=False)
    description = Column(String(500))
    amount_gross = Column(Float, nullable=False)
    tax_deducted = Column(Float, default=0.0)
    income_type = Column(String(50), nullable=False, index=True)  # Indexed for type filtering
    notes = Column(Text)
    created_date = Column(Date, default=datetime.now)


class Expense(Base):
    """
    Expense ledger - allowable business expenses
    Categories aligned with HMRC SA103S form
    """
    __tablename__ = 'expenses'

    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False, index=True)  # Indexed for date filtering
    supplier = Column(String(200), nullable=False)
    description = Column(String(500))
    category = Column(String(100), nullable=False, index=True)  # Indexed for category filtering
    amount = Column(Float, nullable=False)
    receipt_link = Column(String(500))
    notes = Column(Text)
    created_date = Column(Date, default=datetime.now)


class Mileage(Base):
    """
    Mileage log for business travel
    HMRC allows 45p/mile for first 10,000 miles, then 25p/mile
    """
    __tablename__ = 'mileage'

    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False, index=True)  # Indexed for date filtering
    purpose = Column(String(500), nullable=False)
    from_location = Column(String(200))
    to_location = Column(String(200))
    miles = Column(Float, nullable=False)
    rate_per_mile = Column(Float, default=0.45)
    allowable_amount = Column(Float, nullable=False)
    notes = Column(Text)
    created_date = Column(Date, default=datetime.now)


class Donation(Base):
    """
    Gift Aid donations
    HMRC grosses up automatically, we just report what was paid
    """
    __tablename__ = 'donations'

    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False, index=True)  # Indexed for date filtering
    charity = Column(String(200), nullable=False)
    amount_paid = Column(Float, nullable=False)
    gift_aid = Column(Boolean, default=True)
    notes = Column(Text)
    created_date = Column(Date, default=datetime.now)


class Rule(Base):
    """
    Categorization rules for automatic transaction classification
    Applied during CSV import to guess transaction types
    """
    __tablename__ = 'rules'

    id = Column(Integer, primary_key=True)
    match_mode = Column(String(20), nullable=False)  # Contains/Equals/Regex
    text_to_match = Column(String(200), nullable=False)
    map_to = Column(String(50), nullable=False)  # Income/Expense/Ignore
    income_type = Column(String(50))  # If map_to=Income
    expense_category = Column(String(100))  # If map_to=Expense
    is_personal = Column(Boolean, default=False)  # True = personal, False = business
    priority = Column(Integer, default=100)  # Lower = higher priority
    enabled = Column(Boolean, default=True)
    notes = Column(Text)


class Setting(Base):
    """
    Key-value store for application settings
    Stores tax year, accounting basis, column mappings, etc.
    """
    __tablename__ = 'settings'

    key = Column(String(100), primary_key=True)
    value = Column(Text)
    description = Column(Text)


class AuditLog(Base):
    """
    Audit trail for tracking all changes to records
    Enables undo functionality and change history
    """
    __tablename__ = 'audit_log'

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, nullable=False, index=True)  # Indexed for timestamp filtering
    action_type = Column(String(20), nullable=False)  # CREATE, UPDATE, DELETE, BULK_UPDATE
    record_type = Column(String(50), nullable=False, index=True)  # Indexed for record type filtering
    record_id = Column(Integer, nullable=False, index=True)  # Indexed for record lookup
    old_values = Column(Text)  # JSON string of old field values
    new_values = Column(Text)  # JSON string of new field values
    changes_summary = Column(Text, nullable=False)  # Human-readable description


class Merchant(Base):
    """
    Merchant database for auto-categorization
    Pre-populated with 200+ UK merchants and their default categories
    """
    __tablename__ = 'merchants'

    id = Column(Integer, primary_key=True)
    name = Column(String(200), unique=True, nullable=False, index=True)  # Indexed for name lookups
    aliases = Column(Text)  # JSON array of alternative names/spellings
    default_category = Column(String(100))  # Default expense category or income type
    default_type = Column(String(20))  # Income or Expense
    is_personal = Column(Boolean, default=False)  # Typically personal transaction
    industry = Column(String(100))  # Retail, Food, Transport, Software, etc.
    confidence_boost = Column(Integer, default=20)  # 0-30 points added to confidence score
    usage_count = Column(Integer, default=0)  # Track how often matched
    created_date = Column(DateTime, default=datetime.now)
    last_used_date = Column(DateTime)


def init_db(db_path='tax_helper.db'):
    """
    Initialize database and create all tables with optimized SQLite settings
    Returns engine and session factory
    """
    # Configure SQLite with performance optimizations
    engine = create_engine(
        f'sqlite:///{db_path}',
        connect_args={
            'check_same_thread': False,  # Allow multi-threaded access
        },
        pool_pre_ping=True,  # Verify connections before use
        pool_recycle=3600,  # Recycle connections after 1 hour
    )

    # Apply SQLite-specific PRAGMA statements for performance
    from sqlalchemy import event

    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        # Enable WAL mode for better concurrency (readers don't block writers)
        cursor.execute("PRAGMA journal_mode=WAL")
        # Increase cache size to 64MB (default is 2MB)
        cursor.execute("PRAGMA cache_size=-64000")
        # Store temp tables in memory for better performance
        cursor.execute("PRAGMA temp_store=MEMORY")
        # Synchronous=NORMAL is safe with WAL and faster than FULL
        cursor.execute("PRAGMA synchronous=NORMAL")
        # Enable foreign key constraints
        cursor.execute("PRAGMA foreign_keys=ON")
        # Set busy timeout to 5 seconds for better concurrency
        cursor.execute("PRAGMA busy_timeout=5000")
        cursor.close()

    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return engine, Session


def seed_default_data(session):
    """
    Seed default settings and rules on first run
    """
    # Check if already seeded
    existing_settings = session.query(Setting).first()
    if existing_settings:
        return

    # Default settings
    default_settings = [
        Setting(key='tax_year', value='2024/25', description='Current tax year (6 April - 5 April)'),
        Setting(key='accounting_basis', value='Cash', description='Cash or Accruals'),
        Setting(key='currency', value='GBP', description='Currency code'),
        Setting(key='timezone', value='Europe/London', description='Timezone for date processing'),
        Setting(key='mileage_rate_standard', value='0.45', description='First 10,000 miles rate'),
        Setting(key='mileage_rate_reduced', value='0.25', description='After 10,000 miles rate'),
        Setting(key='mileage_threshold', value='10000', description='Miles threshold for rate change'),
        Setting(key='date_format', value='DD/MM/YYYY', description='Preferred date format'),
        Setting(key='column_date', value='Date', description='CSV column for date'),
        Setting(key='column_type', value='Type', description='CSV column for transaction type'),
        Setting(key='column_description', value='Description', description='CSV column for description'),
        Setting(key='column_paid_out', value='', description='CSV column for debits (leave empty if using single Value column)'),
        Setting(key='column_paid_in', value='', description='CSV column for credits (leave empty if using single Value column)'),
        Setting(key='column_value', value='Value', description='CSV column for single value (negative=debit, positive=credit)'),
        Setting(key='column_balance', value='Balance', description='CSV column for balance'),
    ]

    # Default categorization rules
    default_rules = [
        # Income rules (Business)
        Rule(match_mode='Contains', text_to_match='CLIENT', map_to='Income',
             income_type='Self-employment', is_personal=False, priority=10,
             notes='Customer payments'),
        Rule(match_mode='Contains', text_to_match='PAYMENT RECEIVED', map_to='Income',
             income_type='Self-employment', is_personal=False, priority=10,
             notes='Generic payment received'),
        Rule(match_mode='Contains', text_to_match='INTEREST', map_to='Income',
             income_type='Interest', is_personal=False, priority=5,
             notes='Bank interest'),
        Rule(match_mode='Contains', text_to_match='DIVIDEND', map_to='Income',
             income_type='Dividends', is_personal=False, priority=5,
             notes='Dividend payments'),
        Rule(match_mode='Contains', text_to_match='SALARY', map_to='Income',
             income_type='Employment', is_personal=False, priority=5,
             notes='Employment income'),

        # Expense rules - Office costs (Business)
        Rule(match_mode='Contains', text_to_match='SAINSBURY', map_to='Expense',
             expense_category='Office costs', is_personal=False, priority=20,
             notes='Office supplies from supermarket'),
        Rule(match_mode='Contains', text_to_match='STAPLES', map_to='Expense',
             expense_category='Office costs', is_personal=False, priority=20,
             notes='Office supplies'),
        Rule(match_mode='Contains', text_to_match='AMAZON', map_to='Expense',
             expense_category='Office costs', is_personal=False, priority=30,
             notes='Amazon purchases - may need review'),

        # Expense rules - Travel (Business)
        Rule(match_mode='Contains', text_to_match='UBER', map_to='Expense',
             expense_category='Travel', is_personal=False, priority=15,
             notes='Taxi/Uber travel'),
        Rule(match_mode='Contains', text_to_match='TRAINLINE', map_to='Expense',
             expense_category='Travel', is_personal=False, priority=15,
             notes='Train travel'),
        Rule(match_mode='Contains', text_to_match='TFL', map_to='Expense',
             expense_category='Travel', is_personal=False, priority=15,
             notes='Transport for London'),

        # Expense rules - Professional fees (Business)
        Rule(match_mode='Contains', text_to_match='ACCOUNTANT', map_to='Expense',
             expense_category='Accountancy', is_personal=False, priority=10,
             notes='Accountancy fees'),
        Rule(match_mode='Contains', text_to_match='HMRC', map_to='Expense',
             expense_category='Other business expenses', is_personal=False, priority=10,
             notes='HMRC payments'),

        # Expense rules - Phone & Internet (Business)
        Rule(match_mode='Contains', text_to_match='EE', map_to='Expense',
             expense_category='Phone', is_personal=False, priority=20,
             notes='Mobile phone'),
        Rule(match_mode='Contains', text_to_match='VODAFONE', map_to='Expense',
             expense_category='Phone', is_personal=False, priority=20,
             notes='Mobile phone'),
        Rule(match_mode='Contains', text_to_match='BT', map_to='Expense',
             expense_category='Phone', is_personal=False, priority=20,
             notes='Phone/Internet'),

        # Personal expenses - Entertainment
        Rule(match_mode='Contains', text_to_match='NETFLIX', map_to='Ignore',
             is_personal=True, priority=10, notes='Personal entertainment'),
        Rule(match_mode='Contains', text_to_match='SPOTIFY', map_to='Ignore',
             is_personal=True, priority=10, notes='Personal entertainment'),
        Rule(match_mode='Contains', text_to_match='TESCO', map_to='Ignore',
             is_personal=True, priority=25, notes='Personal shopping - may need review'),
        Rule(match_mode='Contains', text_to_match='ASDA', map_to='Ignore',
             is_personal=True, priority=25, notes='Personal shopping'),
        Rule(match_mode='Contains', text_to_match='MORRISONS', map_to='Ignore',
             is_personal=True, priority=25, notes='Personal shopping'),

        # Personal expenses - Housing
        Rule(match_mode='Contains', text_to_match='MORTGAGE', map_to='Ignore',
             is_personal=True, priority=5, notes='Personal mortgage'),
        Rule(match_mode='Contains', text_to_match='COUNCIL TAX', map_to='Ignore',
             is_personal=True, priority=5, notes='Personal council tax'),
        Rule(match_mode='Contains', text_to_match='RENT', map_to='Ignore',
             is_personal=True, priority=5, notes='Personal rent'),

        # Personal expenses - Utilities
        Rule(match_mode='Contains', text_to_match='BRITISH GAS', map_to='Ignore',
             is_personal=True, priority=15, notes='Personal gas bill'),
        Rule(match_mode='Contains', text_to_match='WATER', map_to='Ignore',
             is_personal=True, priority=15, notes='Personal water bill'),

        # Personal expenses - Restaurants/Takeaway
        Rule(match_mode='Contains', text_to_match='MCDONALD', map_to='Ignore',
             is_personal=True, priority=20, notes='Personal food'),
        Rule(match_mode='Contains', text_to_match='COSTA', map_to='Ignore',
             is_personal=True, priority=20, notes='Personal food/drink'),
        Rule(match_mode='Contains', text_to_match='GREGGS', map_to='Ignore',
             is_personal=True, priority=20, notes='Personal food'),

        # Personal expenses - Lottery/Gambling
        Rule(match_mode='Contains', text_to_match='LOTTERY', map_to='Ignore',
             is_personal=True, priority=10, notes='Personal lottery'),
        Rule(match_mode='Contains', text_to_match='ROUND UP', map_to='Ignore',
             is_personal=True, priority=10, notes='Personal savings round-up'),
    ]

    session.add_all(default_settings)
    session.add_all(default_rules)
    session.commit()


# Expense categories aligned with HMRC SA103S
EXPENSE_CATEGORIES = [
    # HMRC SA103 Box 17-32 Categories (in order)
    'Stock/Materials',  # Box 17 - Cost of goods bought for resale
    'Advertising',  # Box 18 - Advertising/marketing costs
    'Office costs',  # Box 20 - Stationery, phone, postage, software
    'Travel',  # Box 21 - Business travel (NOT commuting)
    'Professional fees',  # Box 22 - Accountant, solicitor, etc.
    'Accountancy',  # Box 22 - Accountancy fees
    'Bank charges',  # Box 23 - Business bank charges only
    'Insurance',  # Box 24 - Business insurance
    'Phone',  # Box 25 - Business phone/internet proportion
    'Interest',  # Box 26 - Business loan interest
    'Rent/Rates',  # Box 27 - Premises rent, rates, power
    'Capital Allowances',  # Box 29 - Equipment (use instead of depreciation)
    'Legal fees',  # Box 22 - Business-related legal costs
    'Utilities',  # Box 27 - Gas, electric, water (business premises)
    'Subscriptions',  # Box 32 - Professional subscriptions
    'Staff costs',  # Box 19 - Wages, salaries, other staff costs
    'Training',  # Box 32 - Business-related training
    'Other business expenses',  # Box 32 - Must be wholly & exclusively for business
]

# Income types for HMRC reporting
INCOME_TYPES = [
    'Employment',
    'Self-employment',
    'Interest',
    'Dividends',
    'Property',
    'Other',
]

# Match modes for rules
MATCH_MODES = ['Contains', 'Equals', 'Regex']
