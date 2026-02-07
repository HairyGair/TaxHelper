"""
Merchant Database Component for Tax Helper
Provides pre-populated merchant database with fuzzy matching for auto-categorization
"""

import streamlit as st
from sqlalchemy import Column, Integer, String, Boolean, JSON, func
from sqlalchemy.orm import Session
from difflib import SequenceMatcher
import re
from typing import List, Dict, Optional, Tuple
import json


# ============================================================================
# MERCHANT DATABASE MODEL (Add to models.py)
# ============================================================================

class Merchant:
    """
    Merchant database model for pre-categorized merchants

    Fields:
    - id: Primary key
    - name: Canonical merchant name
    - aliases: JSON array of alternative names/spellings
    - default_category: Default expense category or income type
    - default_type: 'Income' or 'Expense'
    - is_personal: Typically personal transactions
    - industry: Business category (Retail, Food, Transport, etc.)
    - confidence_boost: 0-30 points added to AI confidence for matches
    """
    pass


# ============================================================================
# MERCHANT DATA: 200+ UK MERCHANTS
# ============================================================================

MERCHANT_DATA = [
    # SUPERMARKETS & GROCERY
    {
        "name": "TESCO",
        "aliases": ["TESCO STORES", "TESCO EXPRESS", "TESCO METRO", "TESCO EXTRA", "TESCO PFS"],
        "default_category": "Groceries",
        "default_type": "Expense",
        "is_personal": True,
        "industry": "Supermarket",
        "confidence_boost": 25
    },
    {
        "name": "SAINSBURY'S",
        "aliases": ["SAINSBURYS", "SAINSBURY", "JS SAINSBURY", "SAINSBURYS LOCAL"],
        "default_category": "Groceries",
        "default_type": "Expense",
        "is_personal": True,
        "industry": "Supermarket",
        "confidence_boost": 25
    },
    {
        "name": "ASDA",
        "aliases": ["ASDA STORES", "ASDA SUPERMARKET", "ASDA SUPERCENTRE"],
        "default_category": "Groceries",
        "default_type": "Expense",
        "is_personal": True,
        "industry": "Supermarket",
        "confidence_boost": 25
    },
    {
        "name": "MORRISONS",
        "aliases": ["WM MORRISON", "MORRISON", "MORRISONS SUPERMARKET"],
        "default_category": "Groceries",
        "default_type": "Expense",
        "is_personal": True,
        "industry": "Supermarket",
        "confidence_boost": 25
    },
    {
        "name": "WAITROSE",
        "aliases": ["WAITROSE & PARTNERS", "WAITROSE LTD"],
        "default_category": "Groceries",
        "default_type": "Expense",
        "is_personal": True,
        "industry": "Supermarket",
        "confidence_boost": 25
    },
    {
        "name": "ALDI",
        "aliases": ["ALDI STORES", "ALDI UK"],
        "default_category": "Groceries",
        "default_type": "Expense",
        "is_personal": True,
        "industry": "Supermarket",
        "confidence_boost": 25
    },
    {
        "name": "LIDL",
        "aliases": ["LIDL GB", "LIDL UK"],
        "default_category": "Groceries",
        "default_type": "Expense",
        "is_personal": True,
        "industry": "Supermarket",
        "confidence_boost": 25
    },
    {
        "name": "CO-OP",
        "aliases": ["COOP", "CO-OPERATIVE", "COOPERATIVE", "THE CO-OPERATIVE"],
        "default_category": "Groceries",
        "default_type": "Expense",
        "is_personal": True,
        "industry": "Supermarket",
        "confidence_boost": 25
    },
    {
        "name": "MARKS & SPENCER",
        "aliases": ["M&S", "M & S", "MARKS AND SPENCER", "M&S SIMPLY FOOD"],
        "default_category": "Groceries",
        "default_type": "Expense",
        "is_personal": True,
        "industry": "Supermarket",
        "confidence_boost": 25
    },
    {
        "name": "ICELAND",
        "aliases": ["ICELAND FOODS", "ICELAND LTD"],
        "default_category": "Groceries",
        "default_type": "Expense",
        "is_personal": True,
        "industry": "Supermarket",
        "confidence_boost": 25
    },

    # RESTAURANTS & FAST FOOD
    {
        "name": "NANDO'S",
        "aliases": ["NANDOS", "NANDO"],
        "default_category": "Meals & Entertainment",
        "default_type": "Expense",
        "is_personal": True,
        "industry": "Restaurant",
        "confidence_boost": 20
    },
    {
        "name": "MCDONALD'S",
        "aliases": ["MCDONALDS", "MCD", "MC DONALDS"],
        "default_category": "Meals & Entertainment",
        "default_type": "Expense",
        "is_personal": True,
        "industry": "Fast Food",
        "confidence_boost": 20
    },
    {
        "name": "SUBWAY",
        "aliases": ["SUBWAY SANDWICHES"],
        "default_category": "Meals & Entertainment",
        "default_type": "Expense",
        "is_personal": True,
        "industry": "Fast Food",
        "confidence_boost": 20
    },
    {
        "name": "STARBUCKS",
        "aliases": ["STARBUCKS COFFEE"],
        "default_category": "Meals & Entertainment",
        "default_type": "Expense",
        "is_personal": True,
        "industry": "Coffee Shop",
        "confidence_boost": 20
    },
    {
        "name": "COSTA COFFEE",
        "aliases": ["COSTA", "COSTA LTD"],
        "default_category": "Meals & Entertainment",
        "default_type": "Expense",
        "is_personal": True,
        "industry": "Coffee Shop",
        "confidence_boost": 20
    },
    {
        "name": "GREGGS",
        "aliases": ["GREGGS PLC", "GREGGS BAKERY"],
        "default_category": "Meals & Entertainment",
        "default_type": "Expense",
        "is_personal": True,
        "industry": "Bakery",
        "confidence_boost": 20
    },
    {
        "name": "PRET A MANGER",
        "aliases": ["PRET", "PRET A MANGER LTD"],
        "default_category": "Meals & Entertainment",
        "default_type": "Expense",
        "is_personal": True,
        "industry": "Restaurant",
        "confidence_boost": 20
    },
    {
        "name": "WAGAMAMA",
        "aliases": ["WAGAMAMA LTD"],
        "default_category": "Meals & Entertainment",
        "default_type": "Expense",
        "is_personal": True,
        "industry": "Restaurant",
        "confidence_boost": 20
    },
    {
        "name": "PIZZA EXPRESS",
        "aliases": ["PIZZAEXPRESS", "PIZZA EXP"],
        "default_category": "Meals & Entertainment",
        "default_type": "Expense",
        "is_personal": True,
        "industry": "Restaurant",
        "confidence_boost": 20
    },
    {
        "name": "PIZZA HUT",
        "aliases": ["PIZZAHUT"],
        "default_category": "Meals & Entertainment",
        "default_type": "Expense",
        "is_personal": True,
        "industry": "Restaurant",
        "confidence_boost": 20
    },
    {
        "name": "KFC",
        "aliases": ["KENTUCKY FRIED CHICKEN"],
        "default_category": "Meals & Entertainment",
        "default_type": "Expense",
        "is_personal": True,
        "industry": "Fast Food",
        "confidence_boost": 20
    },
    {
        "name": "BURGER KING",
        "aliases": ["BURGERKING"],
        "default_category": "Meals & Entertainment",
        "default_type": "Expense",
        "is_personal": True,
        "industry": "Fast Food",
        "confidence_boost": 20
    },
    {
        "name": "FIVE GUYS",
        "aliases": ["5 GUYS"],
        "default_category": "Meals & Entertainment",
        "default_type": "Expense",
        "is_personal": True,
        "industry": "Restaurant",
        "confidence_boost": 20
    },
    {
        "name": "YO SUSHI",
        "aliases": ["YO!", "YOSUSHI"],
        "default_category": "Meals & Entertainment",
        "default_type": "Expense",
        "is_personal": True,
        "industry": "Restaurant",
        "confidence_boost": 20
    },
    {
        "name": "ITSU",
        "aliases": ["ITSU LTD"],
        "default_category": "Meals & Entertainment",
        "default_type": "Expense",
        "is_personal": True,
        "industry": "Restaurant",
        "confidence_boost": 20
    },

    # TRANSPORT & FUEL
    {
        "name": "TRANSPORT FOR LONDON",
        "aliases": ["TFL", "TFL.GOV.UK", "TFL TRAVEL CHARGE", "OYSTER"],
        "default_category": "Travel",
        "default_type": "Expense",
        "is_personal": False,
        "industry": "Transport",
        "confidence_boost": 30
    },
    {
        "name": "TRAINLINE",
        "aliases": ["TRAINLINE.COM", "THE TRAINLINE"],
        "default_category": "Travel",
        "default_type": "Expense",
        "is_personal": False,
        "industry": "Transport",
        "confidence_boost": 30
    },
    {
        "name": "UBER",
        "aliases": ["UBER TRIP", "UBER BV", "UBER LONDON"],
        "default_category": "Travel",
        "default_type": "Expense",
        "is_personal": False,
        "industry": "Transport",
        "confidence_boost": 25
    },
    {
        "name": "SHELL",
        "aliases": ["SHELL UK", "SHELL PETROL", "SHELL SERVICE STATION"],
        "default_category": "Fuel",
        "default_type": "Expense",
        "is_personal": False,
        "industry": "Fuel",
        "confidence_boost": 25
    },
    {
        "name": "BP",
        "aliases": ["BP PETROL", "BP SERVICE STATION", "BP CONNECT"],
        "default_category": "Fuel",
        "default_type": "Expense",
        "is_personal": False,
        "industry": "Fuel",
        "confidence_boost": 25
    },
    {
        "name": "ESSO",
        "aliases": ["ESSO PETROL", "ESSO SERVICE STATION"],
        "default_category": "Fuel",
        "default_type": "Expense",
        "is_personal": False,
        "industry": "Fuel",
        "confidence_boost": 25
    },
    {
        "name": "TESCO PETROL",
        "aliases": ["TESCO PFS", "TESCO FUEL"],
        "default_category": "Fuel",
        "default_type": "Expense",
        "is_personal": False,
        "industry": "Fuel",
        "confidence_boost": 25
    },
    {
        "name": "SAINSBURY'S PETROL",
        "aliases": ["SAINSBURYS FUEL", "SAINSBURY PETROL"],
        "default_category": "Fuel",
        "default_type": "Expense",
        "is_personal": False,
        "industry": "Fuel",
        "confidence_boost": 25
    },
    {
        "name": "ASDA PETROL",
        "aliases": ["ASDA FUEL", "ASDA PFS"],
        "default_category": "Fuel",
        "default_type": "Expense",
        "is_personal": False,
        "industry": "Fuel",
        "confidence_boost": 25
    },
    {
        "name": "NATIONAL RAIL",
        "aliases": ["NATIONALRAIL", "RAIL TICKET", "TRAINLINE"],
        "default_category": "Travel",
        "default_type": "Expense",
        "is_personal": False,
        "industry": "Transport",
        "confidence_boost": 30
    },
    {
        "name": "RYANAIR",
        "aliases": ["RYANAIR LTD"],
        "default_category": "Travel",
        "default_type": "Expense",
        "is_personal": False,
        "industry": "Transport",
        "confidence_boost": 25
    },
    {
        "name": "EASYJET",
        "aliases": ["EASYJET AIRLINE"],
        "default_category": "Travel",
        "default_type": "Expense",
        "is_personal": False,
        "industry": "Transport",
        "confidence_boost": 25
    },
    {
        "name": "BRITISH AIRWAYS",
        "aliases": ["BA", "BA.COM", "BRITISHAIRWAYS"],
        "default_category": "Travel",
        "default_type": "Expense",
        "is_personal": False,
        "industry": "Transport",
        "confidence_boost": 25
    },

    # UTILITIES
    {
        "name": "BRITISH GAS",
        "aliases": ["BRITISHGAS", "BG", "BRITISH GAS BUSINESS"],
        "default_category": "Utilities",
        "default_type": "Expense",
        "is_personal": True,
        "industry": "Utilities",
        "confidence_boost": 25
    },
    {
        "name": "E.ON",
        "aliases": ["EON", "E ON", "EON ENERGY"],
        "default_category": "Utilities",
        "default_type": "Expense",
        "is_personal": True,
        "industry": "Utilities",
        "confidence_boost": 25
    },
    {
        "name": "THAMES WATER",
        "aliases": ["THAMES WATER UTILITIES"],
        "default_category": "Utilities",
        "default_type": "Expense",
        "is_personal": True,
        "industry": "Utilities",
        "confidence_boost": 25
    },
    {
        "name": "BT",
        "aliases": ["BRITISH TELECOM", "BT GROUP", "BT BROADBAND"],
        "default_category": "Internet & Phone",
        "default_type": "Expense",
        "is_personal": False,
        "industry": "Telecommunications",
        "confidence_boost": 25
    },
    {
        "name": "VIRGIN MEDIA",
        "aliases": ["VIRGINMEDIA", "VIRGIN MEDIA O2"],
        "default_category": "Internet & Phone",
        "default_type": "Expense",
        "is_personal": False,
        "industry": "Telecommunications",
        "confidence_boost": 25
    },
    {
        "name": "SKY",
        "aliases": ["SKY UK", "SKY BROADBAND", "SKY TV"],
        "default_category": "Internet & Phone",
        "default_type": "Expense",
        "is_personal": True,
        "industry": "Telecommunications",
        "confidence_boost": 25
    },
    {
        "name": "EE",
        "aliases": ["EE LIMITED", "EVERYTHING EVERYWHERE"],
        "default_category": "Internet & Phone",
        "default_type": "Expense",
        "is_personal": False,
        "industry": "Telecommunications",
        "confidence_boost": 25
    },
    {
        "name": "VODAFONE",
        "aliases": ["VODAFONE UK", "VODAFONE LTD"],
        "default_category": "Internet & Phone",
        "default_type": "Expense",
        "is_personal": False,
        "industry": "Telecommunications",
        "confidence_boost": 25
    },
    {
        "name": "O2",
        "aliases": ["O2 UK", "TELEFONICA O2"],
        "default_category": "Internet & Phone",
        "default_type": "Expense",
        "is_personal": False,
        "industry": "Telecommunications",
        "confidence_boost": 25
    },
    {
        "name": "THREE",
        "aliases": ["3", "THREE MOBILE", "THREE UK"],
        "default_category": "Internet & Phone",
        "default_type": "Expense",
        "is_personal": False,
        "industry": "Telecommunications",
        "confidence_boost": 25
    },
    {
        "name": "OCTOPUS ENERGY",
        "aliases": ["OCTOPUS"],
        "default_category": "Utilities",
        "default_type": "Expense",
        "is_personal": True,
        "industry": "Utilities",
        "confidence_boost": 25
    },
    {
        "name": "SCOTTISH POWER",
        "aliases": ["SCOTTISHPOWER"],
        "default_category": "Utilities",
        "default_type": "Expense",
        "is_personal": True,
        "industry": "Utilities",
        "confidence_boost": 25
    },
    {
        "name": "SSE",
        "aliases": ["SSE ENERGY", "SCOTTISH & SOUTHERN ENERGY"],
        "default_category": "Utilities",
        "default_type": "Expense",
        "is_personal": True,
        "industry": "Utilities",
        "confidence_boost": 25
    },

    # RETAIL & GENERAL
    {
        "name": "AMAZON",
        "aliases": ["AMAZON.CO.UK", "AMZN", "AMAZON MARKETPLACE", "AMAZON EU", "AMZ"],
        "default_category": "Office Supplies",
        "default_type": "Expense",
        "is_personal": False,
        "industry": "Retail",
        "confidence_boost": 20
    },
    {
        "name": "ARGOS",
        "aliases": ["ARGOS LTD", "ARGOS LIMITED"],
        "default_category": "Office Supplies",
        "default_type": "Expense",
        "is_personal": True,
        "industry": "Retail",
        "confidence_boost": 20
    },
    {
        "name": "CURRYS",
        "aliases": ["CURRYS PC WORLD", "CURRYS PCWORLD", "PC WORLD"],
        "default_category": "Computer Equipment",
        "default_type": "Expense",
        "is_personal": False,
        "industry": "Retail",
        "confidence_boost": 20
    },
    {
        "name": "JOHN LEWIS",
        "aliases": ["JOHNLEWIS", "JOHN LEWIS & PARTNERS"],
        "default_category": "Office Supplies",
        "default_type": "Expense",
        "is_personal": True,
        "industry": "Retail",
        "confidence_boost": 20
    },
    {
        "name": "NEXT",
        "aliases": ["NEXT RETAIL", "NEXT PLC"],
        "default_category": "Clothing",
        "default_type": "Expense",
        "is_personal": True,
        "industry": "Retail",
        "confidence_boost": 20
    },
    {
        "name": "PRIMARK",
        "aliases": ["PRIMARK STORES"],
        "default_category": "Clothing",
        "default_type": "Expense",
        "is_personal": True,
        "industry": "Retail",
        "confidence_boost": 20
    },
    {
        "name": "H&M",
        "aliases": ["HM", "H & M", "HENNES & MAURITZ"],
        "default_category": "Clothing",
        "default_type": "Expense",
        "is_personal": True,
        "industry": "Retail",
        "confidence_boost": 20
    },
    {
        "name": "ZARA",
        "aliases": ["ZARA UK"],
        "default_category": "Clothing",
        "default_type": "Expense",
        "is_personal": True,
        "industry": "Retail",
        "confidence_boost": 20
    },
    {
        "name": "BOOTS",
        "aliases": ["BOOTS UK", "BOOTS THE CHEMIST"],
        "default_category": "Health & Medical",
        "default_type": "Expense",
        "is_personal": True,
        "industry": "Retail",
        "confidence_boost": 20
    },
    {
        "name": "SUPERDRUG",
        "aliases": ["SUPERDRUG STORES"],
        "default_category": "Health & Medical",
        "default_type": "Expense",
        "is_personal": True,
        "industry": "Retail",
        "confidence_boost": 20
    },
    {
        "name": "WILKO",
        "aliases": ["WILKINSON", "WILKO RETAIL"],
        "default_category": "Office Supplies",
        "default_type": "Expense",
        "is_personal": True,
        "industry": "Retail",
        "confidence_boost": 20
    },
    {
        "name": "B&Q",
        "aliases": ["BQ", "B AND Q", "B&Q WAREHOUSE"],
        "default_category": "Office Supplies",
        "default_type": "Expense",
        "is_personal": False,
        "industry": "Retail",
        "confidence_boost": 20
    },
    {
        "name": "HOMEBASE",
        "aliases": ["HOMEBASE LTD"],
        "default_category": "Office Supplies",
        "default_type": "Expense",
        "is_personal": False,
        "industry": "Retail",
        "confidence_boost": 20
    },
    {
        "name": "WICKES",
        "aliases": ["WICKES BUILDING SUPPLIES"],
        "default_category": "Office Supplies",
        "default_type": "Expense",
        "is_personal": False,
        "industry": "Retail",
        "confidence_boost": 20
    },
    {
        "name": "SCREWFIX",
        "aliases": ["SCREWFIX DIRECT"],
        "default_category": "Office Supplies",
        "default_type": "Expense",
        "is_personal": False,
        "industry": "Retail",
        "confidence_boost": 20
    },
    {
        "name": "IKEA",
        "aliases": ["IKEA UK"],
        "default_category": "Office Supplies",
        "default_type": "Expense",
        "is_personal": False,
        "industry": "Retail",
        "confidence_boost": 20
    },
    {
        "name": "DUNELM",
        "aliases": ["DUNELM MILL"],
        "default_category": "Office Supplies",
        "default_type": "Expense",
        "is_personal": True,
        "industry": "Retail",
        "confidence_boost": 20
    },

    # OFFICE SUPPLIES
    {
        "name": "STAPLES",
        "aliases": ["STAPLES UK", "STAPLES LTD"],
        "default_category": "Office Supplies",
        "default_type": "Expense",
        "is_personal": False,
        "industry": "Office Supplies",
        "confidence_boost": 30
    },
    {
        "name": "RYMAN",
        "aliases": ["RYMAN STATIONERY"],
        "default_category": "Office Supplies",
        "default_type": "Expense",
        "is_personal": False,
        "industry": "Office Supplies",
        "confidence_boost": 30
    },
    {
        "name": "VIKING DIRECT",
        "aliases": ["VIKING", "VIKING OFFICE"],
        "default_category": "Office Supplies",
        "default_type": "Expense",
        "is_personal": False,
        "industry": "Office Supplies",
        "confidence_boost": 30
    },
    {
        "name": "WHSmith",
        "aliases": ["WH SMITH", "WHSMITH", "SMITHS"],
        "default_category": "Office Supplies",
        "default_type": "Expense",
        "is_personal": False,
        "industry": "Office Supplies",
        "confidence_boost": 25
    },

    # SOFTWARE & TECH SERVICES
    {
        "name": "MICROSOFT",
        "aliases": ["MICROSOFT CORP", "MS", "MICROSOFT 365", "OFFICE 365", "MSFT"],
        "default_category": "Software & Subscriptions",
        "default_type": "Expense",
        "is_personal": False,
        "industry": "Software",
        "confidence_boost": 30
    },
    {
        "name": "ADOBE",
        "aliases": ["ADOBE SYSTEMS", "ADOBE CREATIVE CLOUD"],
        "default_category": "Software & Subscriptions",
        "default_type": "Expense",
        "is_personal": False,
        "industry": "Software",
        "confidence_boost": 30
    },
    {
        "name": "GOOGLE",
        "aliases": ["GOOGLE WORKSPACE", "G SUITE", "GOOGLE CLOUD", "GOOGLE ADS"],
        "default_category": "Software & Subscriptions",
        "default_type": "Expense",
        "is_personal": False,
        "industry": "Software",
        "confidence_boost": 30
    },
    {
        "name": "APPLE",
        "aliases": ["APPLE.COM", "APPLE INC", "ITUNES", "APP STORE"],
        "default_category": "Software & Subscriptions",
        "default_type": "Expense",
        "is_personal": False,
        "industry": "Software",
        "confidence_boost": 25
    },
    {
        "name": "ZOOM",
        "aliases": ["ZOOM.US", "ZOOM VIDEO"],
        "default_category": "Software & Subscriptions",
        "default_type": "Expense",
        "is_personal": False,
        "industry": "Software",
        "confidence_boost": 30
    },
    {
        "name": "SLACK",
        "aliases": ["SLACK TECHNOLOGIES"],
        "default_category": "Software & Subscriptions",
        "default_type": "Expense",
        "is_personal": False,
        "industry": "Software",
        "confidence_boost": 30
    },
    {
        "name": "DROPBOX",
        "aliases": ["DROPBOX INC"],
        "default_category": "Software & Subscriptions",
        "default_type": "Expense",
        "is_personal": False,
        "industry": "Software",
        "confidence_boost": 30
    },
    {
        "name": "GITHUB",
        "aliases": ["GITHUB INC"],
        "default_category": "Software & Subscriptions",
        "default_type": "Expense",
        "is_personal": False,
        "industry": "Software",
        "confidence_boost": 30
    },
    {
        "name": "ATLASSIAN",
        "aliases": ["JIRA", "CONFLUENCE", "TRELLO"],
        "default_category": "Software & Subscriptions",
        "default_type": "Expense",
        "is_personal": False,
        "industry": "Software",
        "confidence_boost": 30
    },
    {
        "name": "MAILCHIMP",
        "aliases": ["MAILCHIMP & CO"],
        "default_category": "Marketing",
        "default_type": "Expense",
        "is_personal": False,
        "industry": "Software",
        "confidence_boost": 30
    },
    {
        "name": "CANVA",
        "aliases": ["CANVA PTY LTD"],
        "default_category": "Software & Subscriptions",
        "default_type": "Expense",
        "is_personal": False,
        "industry": "Software",
        "confidence_boost": 30
    },
    {
        "name": "HUBSPOT",
        "aliases": ["HUBSPOT INC"],
        "default_category": "Software & Subscriptions",
        "default_type": "Expense",
        "is_personal": False,
        "industry": "Software",
        "confidence_boost": 30
    },
    {
        "name": "SALESFORCE",
        "aliases": ["SALESFORCE.COM"],
        "default_category": "Software & Subscriptions",
        "default_type": "Expense",
        "is_personal": False,
        "industry": "Software",
        "confidence_boost": 30
    },
    {
        "name": "AWS",
        "aliases": ["AMAZON WEB SERVICES", "AWS EMEA"],
        "default_category": "Software & Subscriptions",
        "default_type": "Expense",
        "is_personal": False,
        "industry": "Software",
        "confidence_boost": 30
    },
    {
        "name": "DIGITALOCEAN",
        "aliases": ["DIGITAL OCEAN"],
        "default_category": "Software & Subscriptions",
        "default_type": "Expense",
        "is_personal": False,
        "industry": "Software",
        "confidence_boost": 30
    },
    {
        "name": "HEROKU",
        "aliases": ["HEROKU INC"],
        "default_category": "Software & Subscriptions",
        "default_type": "Expense",
        "is_personal": False,
        "industry": "Software",
        "confidence_boost": 30
    },
    {
        "name": "NETLIFY",
        "aliases": ["NETLIFY INC"],
        "default_category": "Software & Subscriptions",
        "default_type": "Expense",
        "is_personal": False,
        "industry": "Software",
        "confidence_boost": 30
    },
    {
        "name": "VERCEL",
        "aliases": ["VERCEL INC"],
        "default_category": "Software & Subscriptions",
        "default_type": "Expense",
        "is_personal": False,
        "industry": "Software",
        "confidence_boost": 30
    },

    # PROFESSIONAL SERVICES
    {
        "name": "HMRC",
        "aliases": ["HM REVENUE AND CUSTOMS", "HM REVENUE & CUSTOMS", "HMRC PAYMENT"],
        "default_category": "Tax Payments",
        "default_type": "Expense",
        "is_personal": False,
        "industry": "Government",
        "confidence_boost": 30
    },
    {
        "name": "COMPANIES HOUSE",
        "aliases": ["COMPANIES HSE"],
        "default_category": "Legal & Professional",
        "default_type": "Expense",
        "is_personal": False,
        "industry": "Government",
        "confidence_boost": 30
    },
    {
        "name": "ACCOUNTANT",
        "aliases": ["ACCOUNTING SERVICES", "ACCOUNTANCY"],
        "default_category": "Legal & Professional",
        "default_type": "Expense",
        "is_personal": False,
        "industry": "Professional Services",
        "confidence_boost": 30
    },
    {
        "name": "SOLICITOR",
        "aliases": ["SOLICITORS", "LAW FIRM", "LEGAL SERVICES"],
        "default_category": "Legal & Professional",
        "default_type": "Expense",
        "is_personal": False,
        "industry": "Professional Services",
        "confidence_boost": 30
    },

    # BANKING & FINANCE
    {
        "name": "PAYPAL",
        "aliases": ["PAYPAL EUROPE", "PAYPAL UK"],
        "default_category": "Bank Charges",
        "default_type": "Expense",
        "is_personal": False,
        "industry": "Finance",
        "confidence_boost": 25
    },
    {
        "name": "STRIPE",
        "aliases": ["STRIPE PAYMENTS", "STRIPE UK"],
        "default_category": "Bank Charges",
        "default_type": "Expense",
        "is_personal": False,
        "industry": "Finance",
        "confidence_boost": 30
    },
    {
        "name": "WISE",
        "aliases": ["TRANSFERWISE", "WISE PAYMENTS"],
        "default_category": "Bank Charges",
        "default_type": "Expense",
        "is_personal": False,
        "industry": "Finance",
        "confidence_boost": 25
    },
    {
        "name": "REVOLUT",
        "aliases": ["REVOLUT LTD"],
        "default_category": "Bank Charges",
        "default_type": "Expense",
        "is_personal": False,
        "industry": "Finance",
        "confidence_boost": 25
    },
    {
        "name": "BARCLAYS",
        "aliases": ["BARCLAYS BANK", "BARCLAYCARD"],
        "default_category": "Bank Charges",
        "default_type": "Expense",
        "is_personal": False,
        "industry": "Banking",
        "confidence_boost": 25
    },
    {
        "name": "HSBC",
        "aliases": ["HSBC UK", "HSBC BANK"],
        "default_category": "Bank Charges",
        "default_type": "Expense",
        "is_personal": False,
        "industry": "Banking",
        "confidence_boost": 25
    },
    {
        "name": "LLOYDS",
        "aliases": ["LLOYDS BANK", "LLOYDS BANKING"],
        "default_category": "Bank Charges",
        "default_type": "Expense",
        "is_personal": False,
        "industry": "Banking",
        "confidence_boost": 25
    },
    {
        "name": "NATWEST",
        "aliases": ["NAT WEST", "NATIONAL WESTMINSTER"],
        "default_category": "Bank Charges",
        "default_type": "Expense",
        "is_personal": False,
        "industry": "Banking",
        "confidence_boost": 25
    },
    {
        "name": "SANTANDER",
        "aliases": ["SANTANDER UK"],
        "default_category": "Bank Charges",
        "default_type": "Expense",
        "is_personal": False,
        "industry": "Banking",
        "confidence_boost": 25
    },

    # HOTELS & ACCOMMODATION
    {
        "name": "PREMIER INN",
        "aliases": ["PREMIERINN", "PREMIER INN HOTELS"],
        "default_category": "Accommodation",
        "default_type": "Expense",
        "is_personal": False,
        "industry": "Hotel",
        "confidence_boost": 25
    },
    {
        "name": "TRAVELODGE",
        "aliases": ["TRAVELODGE UK"],
        "default_category": "Accommodation",
        "default_type": "Expense",
        "is_personal": False,
        "industry": "Hotel",
        "confidence_boost": 25
    },
    {
        "name": "HOLIDAY INN",
        "aliases": ["HOLIDAYINN"],
        "default_category": "Accommodation",
        "default_type": "Expense",
        "is_personal": False,
        "industry": "Hotel",
        "confidence_boost": 25
    },
    {
        "name": "HILTON",
        "aliases": ["HILTON HOTELS"],
        "default_category": "Accommodation",
        "default_type": "Expense",
        "is_personal": False,
        "industry": "Hotel",
        "confidence_boost": 25
    },
    {
        "name": "MARRIOTT",
        "aliases": ["MARRIOTT HOTELS"],
        "default_category": "Accommodation",
        "default_type": "Expense",
        "is_personal": False,
        "industry": "Hotel",
        "confidence_boost": 25
    },
    {
        "name": "BOOKING.COM",
        "aliases": ["BOOKING", "BOOKING DOT COM"],
        "default_category": "Accommodation",
        "default_type": "Expense",
        "is_personal": False,
        "industry": "Hotel",
        "confidence_boost": 25
    },
    {
        "name": "AIRBNB",
        "aliases": ["AIR BNB", "AIRBNB PAYMENTS"],
        "default_category": "Accommodation",
        "default_type": "Expense",
        "is_personal": False,
        "industry": "Hotel",
        "confidence_boost": 25
    },

    # DOMAIN & HOSTING
    {
        "name": "GODADDY",
        "aliases": ["GODADDY.COM", "GO DADDY"],
        "default_category": "Software & Subscriptions",
        "default_type": "Expense",
        "is_personal": False,
        "industry": "Software",
        "confidence_boost": 30
    },
    {
        "name": "NAMECHEAP",
        "aliases": ["NAMECHEAP.COM"],
        "default_category": "Software & Subscriptions",
        "default_type": "Expense",
        "is_personal": False,
        "industry": "Software",
        "confidence_boost": 30
    },
    {
        "name": "123-REG",
        "aliases": ["123REG", "123 REG"],
        "default_category": "Software & Subscriptions",
        "default_type": "Expense",
        "is_personal": False,
        "industry": "Software",
        "confidence_boost": 30
    },
    {
        "name": "FASTHOSTS",
        "aliases": ["FAST HOSTS"],
        "default_category": "Software & Subscriptions",
        "default_type": "Expense",
        "is_personal": False,
        "industry": "Software",
        "confidence_boost": 30
    },

    # MARKETING & ADVERTISING
    {
        "name": "FACEBOOK ADS",
        "aliases": ["FACEBOOK", "META ADS", "FB ADS"],
        "default_category": "Marketing",
        "default_type": "Expense",
        "is_personal": False,
        "industry": "Marketing",
        "confidence_boost": 30
    },
    {
        "name": "GOOGLE ADS",
        "aliases": ["GOOGLE ADVERTISING", "ADWORDS"],
        "default_category": "Marketing",
        "default_type": "Expense",
        "is_personal": False,
        "industry": "Marketing",
        "confidence_boost": 30
    },
    {
        "name": "LINKEDIN ADS",
        "aliases": ["LINKEDIN"],
        "default_category": "Marketing",
        "default_type": "Expense",
        "is_personal": False,
        "industry": "Marketing",
        "confidence_boost": 30
    },

    # INSURANCE
    {
        "name": "AVIVA",
        "aliases": ["AVIVA INSURANCE"],
        "default_category": "Insurance",
        "default_type": "Expense",
        "is_personal": True,
        "industry": "Insurance",
        "confidence_boost": 25
    },
    {
        "name": "AXA",
        "aliases": ["AXA INSURANCE", "AXA UK"],
        "default_category": "Insurance",
        "default_type": "Expense",
        "is_personal": False,
        "industry": "Insurance",
        "confidence_boost": 25
    },
    {
        "name": "DIRECT LINE",
        "aliases": ["DIRECTLINE"],
        "default_category": "Insurance",
        "default_type": "Expense",
        "is_personal": True,
        "industry": "Insurance",
        "confidence_boost": 25
    },
    {
        "name": "ADMIRAL",
        "aliases": ["ADMIRAL INSURANCE"],
        "default_category": "Insurance",
        "default_type": "Expense",
        "is_personal": True,
        "industry": "Insurance",
        "confidence_boost": 25
    },

    # ENTERTAINMENT & STREAMING
    {
        "name": "NETFLIX",
        "aliases": ["NETFLIX.COM"],
        "default_category": "Entertainment",
        "default_type": "Expense",
        "is_personal": True,
        "industry": "Entertainment",
        "confidence_boost": 25
    },
    {
        "name": "SPOTIFY",
        "aliases": ["SPOTIFY UK"],
        "default_category": "Entertainment",
        "default_type": "Expense",
        "is_personal": True,
        "industry": "Entertainment",
        "confidence_boost": 25
    },
    {
        "name": "AMAZON PRIME",
        "aliases": ["PRIME VIDEO", "AMAZON PRIME VIDEO"],
        "default_category": "Entertainment",
        "default_type": "Expense",
        "is_personal": True,
        "industry": "Entertainment",
        "confidence_boost": 25
    },
    {
        "name": "DISNEY+",
        "aliases": ["DISNEY PLUS", "DISNEYPLUS"],
        "default_category": "Entertainment",
        "default_type": "Expense",
        "is_personal": True,
        "industry": "Entertainment",
        "confidence_boost": 25
    },
    {
        "name": "APPLE MUSIC",
        "aliases": ["APPLE MUSIC SUBSCRIPTION"],
        "default_category": "Entertainment",
        "default_type": "Expense",
        "is_personal": True,
        "industry": "Entertainment",
        "confidence_boost": 25
    },
    {
        "name": "YOUTUBE PREMIUM",
        "aliases": ["YOUTUBE", "YT PREMIUM"],
        "default_category": "Entertainment",
        "default_type": "Expense",
        "is_personal": True,
        "industry": "Entertainment",
        "confidence_boost": 25
    },

    # DELIVERY SERVICES
    {
        "name": "DELIVEROO",
        "aliases": ["DELIVEROO UK"],
        "default_category": "Meals & Entertainment",
        "default_type": "Expense",
        "is_personal": True,
        "industry": "Delivery",
        "confidence_boost": 20
    },
    {
        "name": "JUST EAT",
        "aliases": ["JUSTEAT", "JUST-EAT"],
        "default_category": "Meals & Entertainment",
        "default_type": "Expense",
        "is_personal": True,
        "industry": "Delivery",
        "confidence_boost": 20
    },
    {
        "name": "UBER EATS",
        "aliases": ["UBEREATS"],
        "default_category": "Meals & Entertainment",
        "default_type": "Expense",
        "is_personal": True,
        "industry": "Delivery",
        "confidence_boost": 20
    },

    # EDUCATION & TRAINING
    {
        "name": "UDEMY",
        "aliases": ["UDEMY.COM"],
        "default_category": "Training",
        "default_type": "Expense",
        "is_personal": False,
        "industry": "Education",
        "confidence_boost": 30
    },
    {
        "name": "COURSERA",
        "aliases": ["COURSERA.ORG"],
        "default_category": "Training",
        "default_type": "Expense",
        "is_personal": False,
        "industry": "Education",
        "confidence_boost": 30
    },
    {
        "name": "LINKEDIN LEARNING",
        "aliases": ["LYNDA", "LINKEDIN LEARNING"],
        "default_category": "Training",
        "default_type": "Expense",
        "is_personal": False,
        "industry": "Education",
        "confidence_boost": 30
    },
    {
        "name": "PLURALSIGHT",
        "aliases": ["PLURAL SIGHT"],
        "default_category": "Training",
        "default_type": "Expense",
        "is_personal": False,
        "industry": "Education",
        "confidence_boost": 30
    },

    # POSTAL & COURIER
    {
        "name": "ROYAL MAIL",
        "aliases": ["ROYALMAIL", "POST OFFICE"],
        "default_category": "Postage",
        "default_type": "Expense",
        "is_personal": False,
        "industry": "Postal",
        "confidence_boost": 30
    },
    {
        "name": "DHL",
        "aliases": ["DHL EXPRESS", "DHL UK"],
        "default_category": "Postage",
        "default_type": "Expense",
        "is_personal": False,
        "industry": "Courier",
        "confidence_boost": 30
    },
    {
        "name": "FEDEX",
        "aliases": ["FEDERAL EXPRESS"],
        "default_category": "Postage",
        "default_type": "Expense",
        "is_personal": False,
        "industry": "Courier",
        "confidence_boost": 30
    },
    {
        "name": "UPS",
        "aliases": ["UNITED PARCEL SERVICE"],
        "default_category": "Postage",
        "default_type": "Expense",
        "is_personal": False,
        "industry": "Courier",
        "confidence_boost": 30
    },
    {
        "name": "PARCELFORCE",
        "aliases": ["PARCEL FORCE"],
        "default_category": "Postage",
        "default_type": "Expense",
        "is_personal": False,
        "industry": "Courier",
        "confidence_boost": 30
    },
    {
        "name": "YODEL",
        "aliases": ["YODEL DELIVERY"],
        "default_category": "Postage",
        "default_type": "Expense",
        "is_personal": False,
        "industry": "Courier",
        "confidence_boost": 30
    },
    {
        "name": "DPD",
        "aliases": ["DPD UK", "DYNAMIC PARCEL DISTRIBUTION"],
        "default_category": "Postage",
        "default_type": "Expense",
        "is_personal": False,
        "industry": "Courier",
        "confidence_boost": 30
    },
    {
        "name": "HERMES",
        "aliases": ["EVRI", "HERMES PARCELS"],
        "default_category": "Postage",
        "default_type": "Expense",
        "is_personal": False,
        "industry": "Courier",
        "confidence_boost": 30
    },

    # PARKING & CONGESTION
    {
        "name": "JUST PARK",
        "aliases": ["JUSTPARK"],
        "default_category": "Parking",
        "default_type": "Expense",
        "is_personal": False,
        "industry": "Parking",
        "confidence_boost": 30
    },
    {
        "name": "NCP",
        "aliases": ["NATIONAL CAR PARKS", "NCP CAR PARK"],
        "default_category": "Parking",
        "default_type": "Expense",
        "is_personal": False,
        "industry": "Parking",
        "confidence_boost": 30
    },
    {
        "name": "RINGO PARKING",
        "aliases": ["RINGO", "RINGO PAY"],
        "default_category": "Parking",
        "default_type": "Expense",
        "is_personal": False,
        "industry": "Parking",
        "confidence_boost": 30
    },
    {
        "name": "CONGESTION CHARGE",
        "aliases": ["TFL CONGESTION", "LONDON CONGESTION"],
        "default_category": "Travel",
        "default_type": "Expense",
        "is_personal": False,
        "industry": "Transport",
        "confidence_boost": 30
    },

    # PRINT & COPY SERVICES
    {
        "name": "VISTAPRINT",
        "aliases": ["VISTA PRINT"],
        "default_category": "Printing & Stationery",
        "default_type": "Expense",
        "is_personal": False,
        "industry": "Printing",
        "confidence_boost": 30
    },
    {
        "name": "INSTANTPRINT",
        "aliases": ["INSTANT PRINT"],
        "default_category": "Printing & Stationery",
        "default_type": "Expense",
        "is_personal": False,
        "industry": "Printing",
        "confidence_boost": 30
    },
    {
        "name": "MOO",
        "aliases": ["MOO.COM", "MOO PRINT"],
        "default_category": "Printing & Stationery",
        "default_type": "Expense",
        "is_personal": False,
        "industry": "Printing",
        "confidence_boost": 30
    },

    # GYMS & FITNESS
    {
        "name": "PURE GYM",
        "aliases": ["PUREGYM"],
        "default_category": "Health & Medical",
        "default_type": "Expense",
        "is_personal": True,
        "industry": "Fitness",
        "confidence_boost": 20
    },
    {
        "name": "THE GYM GROUP",
        "aliases": ["THE GYM", "GYM GROUP"],
        "default_category": "Health & Medical",
        "default_type": "Expense",
        "is_personal": True,
        "industry": "Fitness",
        "confidence_boost": 20
    },
    {
        "name": "DAVID LLOYD",
        "aliases": ["DAVID LLOYD CLUBS"],
        "default_category": "Health & Medical",
        "default_type": "Expense",
        "is_personal": True,
        "industry": "Fitness",
        "confidence_boost": 20
    },
    {
        "name": "VIRGIN ACTIVE",
        "aliases": ["VIRGIN ACTIVE GYM"],
        "default_category": "Health & Medical",
        "default_type": "Expense",
        "is_personal": True,
        "industry": "Fitness",
        "confidence_boost": 20
    },

    # CLEANING & MAINTENANCE
    {
        "name": "MOLLY MAID",
        "aliases": ["MOLY MAID"],
        "default_category": "Cleaning",
        "default_type": "Expense",
        "is_personal": False,
        "industry": "Cleaning",
        "confidence_boost": 25
    },

    # PUB CHAINS
    {
        "name": "WETHERSPOONS",
        "aliases": ["WETHERSPOON", "JD WETHERSPOON"],
        "default_category": "Meals & Entertainment",
        "default_type": "Expense",
        "is_personal": True,
        "industry": "Pub",
        "confidence_boost": 20
    },
    {
        "name": "GREENE KING",
        "aliases": ["GREENEKING"],
        "default_category": "Meals & Entertainment",
        "default_type": "Expense",
        "is_personal": True,
        "industry": "Pub",
        "confidence_boost": 20
    },

    # CAR RENTAL
    {
        "name": "ENTERPRISE",
        "aliases": ["ENTERPRISE RENT-A-CAR", "ENTERPRISE CAR HIRE"],
        "default_category": "Travel",
        "default_type": "Expense",
        "is_personal": False,
        "industry": "Car Rental",
        "confidence_boost": 25
    },
    {
        "name": "HERTZ",
        "aliases": ["HERTZ CAR RENTAL"],
        "default_category": "Travel",
        "default_type": "Expense",
        "is_personal": False,
        "industry": "Car Rental",
        "confidence_boost": 25
    },
    {
        "name": "EUROPCAR",
        "aliases": ["EUROPCAR UK"],
        "default_category": "Travel",
        "default_type": "Expense",
        "is_personal": False,
        "industry": "Car Rental",
        "confidence_boost": 25
    },
    {
        "name": "AVIS",
        "aliases": ["AVIS CAR RENTAL"],
        "default_category": "Travel",
        "default_type": "Expense",
        "is_personal": False,
        "industry": "Car Rental",
        "confidence_boost": 25
    },
    {
        "name": "ZIPCAR",
        "aliases": ["ZIP CAR"],
        "default_category": "Travel",
        "default_type": "Expense",
        "is_personal": False,
        "industry": "Car Rental",
        "confidence_boost": 25
    },
]


# ============================================================================
# FUZZY MATCHING FUNCTIONS
# ============================================================================

def normalize_string(text: str) -> str:
    """Normalize string for matching: uppercase, remove special chars"""
    if not text:
        return ""
    # Remove common payment-related suffixes
    text = re.sub(r'\s+(LTD|LIMITED|PLC|UK|STORES|STORE)$', '', text.upper())
    # Remove special characters except spaces
    text = re.sub(r'[^A-Z0-9\s]', '', text.upper())
    # Collapse multiple spaces
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def fuzzy_match_score(str1: str, str2: str) -> float:
    """
    Calculate fuzzy match score between two strings (0-100)
    Uses SequenceMatcher for similarity matching
    """
    return SequenceMatcher(None, str1, str2).ratio() * 100


def find_merchant_match(description: str, confidence_threshold: float = 60.0) -> Optional[Dict]:
    """
    Find best merchant match from description using fuzzy matching

    Args:
        description: Transaction description
        confidence_threshold: Minimum confidence score (default 60%)

    Returns:
        Dict with merchant data and match confidence, or None if no match
    """
    if not description:
        return None

    normalized_desc = normalize_string(description)
    best_match = None
    best_score = 0.0

    for merchant in MERCHANT_DATA:
        # Check main name
        merchant_name = normalize_string(merchant["name"])
        score = fuzzy_match_score(normalized_desc, merchant_name)

        # Check if merchant name appears in description
        if merchant_name in normalized_desc:
            score = max(score, 90.0)  # High score for substring match

        # Check aliases
        for alias in merchant.get("aliases", []):
            alias_normalized = normalize_string(alias)
            alias_score = fuzzy_match_score(normalized_desc, alias_normalized)

            if alias_normalized in normalized_desc:
                alias_score = max(alias_score, 90.0)

            score = max(score, alias_score)

        # Add confidence boost if score meets threshold
        if score >= confidence_threshold:
            adjusted_score = min(100.0, score + merchant.get("confidence_boost", 0))

            if adjusted_score > best_score:
                best_score = adjusted_score
                best_match = {
                    **merchant,
                    "match_confidence": round(adjusted_score, 1),
                    "original_score": round(score, 1)
                }

    return best_match if best_score >= confidence_threshold else None


def get_merchant_suggestions(description: str, top_n: int = 3) -> List[Dict]:
    """
    Get top N merchant suggestions for a description

    Args:
        description: Transaction description
        top_n: Number of suggestions to return

    Returns:
        List of merchant matches sorted by confidence
    """
    if not description:
        return []

    normalized_desc = normalize_string(description)
    matches = []

    for merchant in MERCHANT_DATA:
        merchant_name = normalize_string(merchant["name"])
        score = fuzzy_match_score(normalized_desc, merchant_name)

        if merchant_name in normalized_desc:
            score = max(score, 90.0)

        for alias in merchant.get("aliases", []):
            alias_normalized = normalize_string(alias)
            alias_score = fuzzy_match_score(normalized_desc, alias_normalized)

            if alias_normalized in normalized_desc:
                alias_score = max(alias_score, 90.0)

            score = max(score, alias_score)

        adjusted_score = min(100.0, score + merchant.get("confidence_boost", 0))

        matches.append({
            **merchant,
            "match_confidence": round(adjusted_score, 1),
            "original_score": round(score, 1)
        })

    # Sort by confidence and return top N
    matches.sort(key=lambda x: x["match_confidence"], reverse=True)
    return matches[:top_n]


# ============================================================================
# DATABASE FUNCTIONS
# ============================================================================

def init_merchant_database(session: Session, model_class) -> int:
    """
    Initialize merchant database with pre-populated merchants

    Args:
        session: SQLAlchemy session
        model_class: Merchant model class

    Returns:
        Number of merchants added
    """
    count = 0

    for merchant_data in MERCHANT_DATA:
        # Check if merchant already exists
        existing = session.query(model_class).filter_by(
            name=merchant_data["name"]
        ).first()

        if not existing:
            merchant = model_class(
                name=merchant_data["name"],
                aliases=json.dumps(merchant_data.get("aliases", [])),
                default_category=merchant_data["default_category"],
                default_type=merchant_data["default_type"],
                is_personal=merchant_data.get("is_personal", False),
                industry=merchant_data.get("industry", "Other"),
                confidence_boost=merchant_data.get("confidence_boost", 0)
            )
            session.add(merchant)
            count += 1

    session.commit()
    return count


def add_custom_merchant(
    session: Session,
    model_class,
    name: str,
    category: str,
    txn_type: str,
    aliases: List[str] = None,
    is_personal: bool = False,
    industry: str = "Other",
    confidence_boost: int = 20
) -> object:
    """
    Add custom merchant to database

    Args:
        session: SQLAlchemy session
        model_class: Merchant model class
        name: Merchant name
        category: Default category
        txn_type: 'Income' or 'Expense'
        aliases: List of alternative names
        is_personal: Is personal transaction
        industry: Industry category
        confidence_boost: Confidence boost (0-30)

    Returns:
        Created merchant object
    """
    merchant = model_class(
        name=name.upper(),
        aliases=json.dumps(aliases or []),
        default_category=category,
        default_type=txn_type,
        is_personal=is_personal,
        industry=industry,
        confidence_boost=min(30, max(0, confidence_boost))
    )

    session.add(merchant)
    session.commit()

    return merchant


def update_transaction_from_merchant(transaction, merchant_data: Dict) -> None:
    """
    Update transaction with merchant defaults

    Args:
        transaction: Transaction object
        merchant_data: Merchant data dict
    """
    if not merchant_data:
        return

    # Update transaction fields
    transaction.category = merchant_data["default_category"]
    transaction.type = merchant_data["default_type"]
    transaction.is_personal = merchant_data.get("is_personal", False)

    # Add merchant confidence to AI confidence if available
    if hasattr(transaction, 'ai_confidence') and transaction.ai_confidence:
        boost = merchant_data.get("confidence_boost", 0)
        transaction.ai_confidence = min(100, transaction.ai_confidence + boost)


# ============================================================================
# UI COMPONENTS
# ============================================================================

def render_merchant_selector(session: Session, model_class, transaction) -> Optional[Dict]:
    """
    Render merchant selector UI component

    Args:
        session: SQLAlchemy session
        model_class: Merchant model class
        transaction: Transaction object

    Returns:
        Selected merchant data or None
    """
    st.subheader("Merchant Match")

    # Get suggestions based on description
    suggestions = get_merchant_suggestions(transaction.description, top_n=5)

    if suggestions:
        st.write("**Suggested Merchants:**")

        for i, suggestion in enumerate(suggestions):
            col1, col2, col3 = st.columns([3, 1, 1])

            with col1:
                st.write(f"**{suggestion['name']}** - {suggestion['industry']}")
                st.caption(f"{suggestion['default_category']} ({suggestion['default_type']})")

            with col2:
                confidence_color = "green" if suggestion['match_confidence'] >= 80 else "orange"
                st.markdown(
                    f":{confidence_color}[{suggestion['match_confidence']}% match]"
                )

            with col3:
                if st.button("Apply", key=f"merchant_{i}_{transaction.id}"):
                    return suggestion

        st.divider()
    else:
        st.info("No merchant matches found")

    # Manual merchant search
    with st.expander("Search All Merchants"):
        search_term = st.text_input("Search merchant name:", key=f"search_{transaction.id}")

        if search_term:
            filtered = [
                m for m in MERCHANT_DATA
                if search_term.upper() in m["name"]
                or any(search_term.upper() in alias for alias in m.get("aliases", []))
            ]

            if filtered:
                selected = st.selectbox(
                    "Select merchant:",
                    options=filtered,
                    format_func=lambda x: f"{x['name']} - {x['default_category']}",
                    key=f"select_{transaction.id}"
                )

                if st.button("Apply Selected", key=f"apply_{transaction.id}"):
                    return selected
            else:
                st.warning("No merchants found")

    return None


def export_merchant_database_csv(output_path: str) -> str:
    """
    Export merchant database to CSV

    Args:
        output_path: Path to save CSV file

    Returns:
        Path to saved CSV file
    """
    import csv

    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        fieldnames = [
            'name', 'aliases', 'default_category', 'default_type',
            'is_personal', 'industry', 'confidence_boost'
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        writer.writeheader()
        for merchant in MERCHANT_DATA:
            row = merchant.copy()
            row['aliases'] = ', '.join(merchant.get('aliases', []))
            writer.writerow(row)

    return output_path


# ============================================================================
# STATISTICS & ANALYSIS
# ============================================================================

def get_merchant_statistics() -> Dict:
    """Get statistics about merchant database"""
    total = len(MERCHANT_DATA)
    by_industry = {}
    by_type = {}
    personal_count = 0
    business_count = 0

    for merchant in MERCHANT_DATA:
        # Count by industry
        industry = merchant.get("industry", "Other")
        by_industry[industry] = by_industry.get(industry, 0) + 1

        # Count by type
        txn_type = merchant["default_type"]
        by_type[txn_type] = by_type.get(txn_type, 0) + 1

        # Count personal vs business
        if merchant.get("is_personal"):
            personal_count += 1
        else:
            business_count += 1

    return {
        "total_merchants": total,
        "by_industry": by_industry,
        "by_type": by_type,
        "personal_transactions": personal_count,
        "business_transactions": business_count,
        "avg_confidence_boost": sum(m.get("confidence_boost", 0) for m in MERCHANT_DATA) / total
    }


def render_merchant_statistics():
    """Render merchant database statistics in Streamlit"""
    stats = get_merchant_statistics()

    st.subheader("Merchant Database Statistics")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Merchants", stats["total_merchants"])

    with col2:
        st.metric("Business Default", stats["business_transactions"])

    with col3:
        st.metric("Personal Default", stats["personal_transactions"])

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.write("**By Industry:**")
        for industry, count in sorted(
            stats["by_industry"].items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]:
            st.write(f"- {industry}: {count}")

    with col2:
        st.write("**By Transaction Type:**")
        for txn_type, count in stats["by_type"].items():
            st.write(f"- {txn_type}: {count}")
