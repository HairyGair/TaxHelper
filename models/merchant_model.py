"""
SQLAlchemy Model for Merchant Database
Add this model to your existing models.py file
"""

from sqlalchemy import Column, Integer, String, Boolean, JSON, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class Merchant(Base):
    """
    Merchant database model for pre-categorized merchants

    This model stores common UK merchants with their default categorization
    to enable automatic transaction categorization via fuzzy matching.
    """

    __tablename__ = 'merchants'

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Merchant Information
    name = Column(String(200), nullable=False, unique=True, index=True)
    """Canonical merchant name (uppercase)"""

    aliases = Column(JSON, nullable=True)
    """JSON array of alternative names/spellings for matching"""

    # Default Transaction Settings
    default_category = Column(String(100), nullable=False)
    """Default expense category or income type"""

    default_type = Column(String(20), nullable=False)
    """Transaction type: 'Income' or 'Expense'"""

    is_personal = Column(Boolean, default=False, nullable=False)
    """True if typically personal transactions (not business deductible)"""

    # Classification
    industry = Column(String(100), nullable=True)
    """Business industry category (Retail, Food, Transport, etc.)"""

    confidence_boost = Column(Integer, default=0, nullable=False)
    """0-30 points added to AI confidence when matched (higher = more reliable)"""

    # Metadata
    is_custom = Column(Boolean, default=False, nullable=False)
    """True if user-added merchant (not from pre-populated database)"""

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    """Timestamp when merchant was added"""

    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    """Timestamp when merchant was last updated"""

    # Usage Statistics (optional)
    usage_count = Column(Integer, default=0, nullable=False)
    """Number of times this merchant has been matched to transactions"""

    last_matched_at = Column(DateTime, nullable=True)
    """Timestamp of most recent transaction match"""

    def __repr__(self):
        return f"<Merchant(id={self.id}, name='{self.name}', category='{self.default_category}')>"

    def to_dict(self):
        """Convert merchant to dictionary"""
        import json

        return {
            'id': self.id,
            'name': self.name,
            'aliases': json.loads(self.aliases) if self.aliases else [],
            'default_category': self.default_category,
            'default_type': self.default_type,
            'is_personal': self.is_personal,
            'industry': self.industry,
            'confidence_boost': self.confidence_boost,
            'is_custom': self.is_custom,
            'usage_count': self.usage_count,
            'last_matched_at': self.last_matched_at.isoformat() if self.last_matched_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


# ============================================================================
# DATABASE MIGRATION SQL
# ============================================================================

"""
-- SQL to create merchants table (if not using SQLAlchemy migrations)

CREATE TABLE merchants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(200) NOT NULL UNIQUE,
    aliases TEXT,  -- JSON array
    default_category VARCHAR(100) NOT NULL,
    default_type VARCHAR(20) NOT NULL,
    is_personal BOOLEAN NOT NULL DEFAULT 0,
    industry VARCHAR(100),
    confidence_boost INTEGER NOT NULL DEFAULT 0,
    is_custom BOOLEAN NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    usage_count INTEGER NOT NULL DEFAULT 0,
    last_matched_at TIMESTAMP
);

CREATE INDEX idx_merchants_name ON merchants(name);
CREATE INDEX idx_merchants_industry ON merchants(industry);
CREATE INDEX idx_merchants_category ON merchants(default_category);
"""


# ============================================================================
# USAGE WITH EXISTING DATABASE
# ============================================================================

"""
If you already have a database.py file, add this model to it:

# In your database.py or models.py file:

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from merchant_model import Merchant, Base

# Create engine
engine = create_engine('sqlite:///taxhelper.db')

# Create tables
Base.metadata.create_all(engine)

# Create session
SessionLocal = sessionmaker(bind=engine)
"""
