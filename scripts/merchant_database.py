"""
UK Merchant Categorization Database
Provides intelligent categorization for common UK merchants and transaction types
"""

# Confidence levels
CONFIDENCE_CERTAIN = 100  # 100% certain (government benefits, known personal retailers)
CONFIDENCE_HIGH = 90      # Very likely correct
CONFIDENCE_MEDIUM = 70    # Probably correct
CONFIDENCE_LOW = 50       # Ambiguous, needs review
CONFIDENCE_UNKNOWN = 0    # No information

class MerchantCategory:
    """Merchant categorization with confidence scoring"""
    def __init__(self, name, is_personal, category, confidence, notes=""):
        self.name = name
        self.is_personal = is_personal
        self.category = category  # For business: expense category, For personal: type
        self.confidence = confidence
        self.notes = notes


# ===================================================================
# PERSONAL - GOVERNMENT & BENEFITS (100% Confidence)
# ===================================================================
GOVERNMENT_BENEFITS = {
    'DWP': MerchantCategory('DWP', True, 'Government Benefits', CONFIDENCE_CERTAIN, 'Department for Work & Pensions'),
    'HMRC CHILD BENEFIT': MerchantCategory('HMRC Child Benefit', True, 'Government Benefits', CONFIDENCE_CERTAIN),
    'UNIVERSAL CREDIT': MerchantCategory('Universal Credit', True, 'Government Benefits', CONFIDENCE_CERTAIN),
    'DWP UC': MerchantCategory('Universal Credit', True, 'Government Benefits', CONFIDENCE_CERTAIN),
    'DWP CA': MerchantCategory('Carers Allowance', True, 'Government Benefits', CONFIDENCE_CERTAIN),
    'DWP DLA': MerchantCategory('Disability Living Allowance', True, 'Government Benefits', CONFIDENCE_CERTAIN),
    'DWP PIP': MerchantCategory('Personal Independence Payment', True, 'Government Benefits', CONFIDENCE_CERTAIN),
    'DWP ESA': MerchantCategory('Employment Support Allowance', True, 'Government Benefits', CONFIDENCE_CERTAIN),
    'TAX CREDITS': MerchantCategory('Tax Credits', True, 'Government Benefits', CONFIDENCE_CERTAIN),
}

# ===================================================================
# PERSONAL - SUPERMARKETS & GROCERIES (100% Confidence)
# ===================================================================
SUPERMARKETS = {
    'TESCO': MerchantCategory('Tesco', True, 'Groceries', CONFIDENCE_CERTAIN),
    'SAINSBURY': MerchantCategory('Sainsburys', True, 'Groceries', CONFIDENCE_CERTAIN),
    'ASDA': MerchantCategory('ASDA', True, 'Groceries', CONFIDENCE_CERTAIN),
    'MORRISONS': MerchantCategory('Morrisons', True, 'Groceries', CONFIDENCE_CERTAIN),
    'LIDL': MerchantCategory('Lidl', True, 'Groceries', CONFIDENCE_CERTAIN),
    'ALDI': MerchantCategory('Aldi', True, 'Groceries', CONFIDENCE_CERTAIN),
    'WAITROSE': MerchantCategory('Waitrose', True, 'Groceries', CONFIDENCE_CERTAIN),
    'M&S': MerchantCategory('M&S', True, 'Groceries', CONFIDENCE_CERTAIN),
    'MARKS & SPENCER': MerchantCategory('M&S', True, 'Groceries', CONFIDENCE_CERTAIN),
    'MARKS AND SPENCER': MerchantCategory('M&S', True, 'Groceries', CONFIDENCE_CERTAIN),
    'CO-OP': MerchantCategory('Co-op', True, 'Groceries', CONFIDENCE_CERTAIN),
    'ICELAND': MerchantCategory('Iceland', True, 'Groceries', CONFIDENCE_CERTAIN),
    'FARM FOODS': MerchantCategory('Farm Foods', True, 'Groceries', CONFIDENCE_CERTAIN),
    'HOME BARGAINS': MerchantCategory('Home Bargains', True, 'Groceries', CONFIDENCE_CERTAIN),
    'B&M': MerchantCategory('B&M', True, 'Groceries', CONFIDENCE_CERTAIN),
    'POUNDLAND': MerchantCategory('Poundland', True, 'Groceries', CONFIDENCE_CERTAIN),
    'POUND STRETCHER': MerchantCategory('Poundstretcher', True, 'Groceries', CONFIDENCE_CERTAIN),
}

# ===================================================================
# PERSONAL - FAST FOOD & RESTAURANTS (100% Confidence)
# ===================================================================
FAST_FOOD = {
    'MCDONALDS': MerchantCategory('McDonalds', True, 'Food & Drink', CONFIDENCE_CERTAIN),
    'GREGGS': MerchantCategory('Greggs', True, 'Food & Drink', CONFIDENCE_CERTAIN),
    'COSTA': MerchantCategory('Costa Coffee', True, 'Food & Drink', CONFIDENCE_CERTAIN),
    'STARBUCKS': MerchantCategory('Starbucks', True, 'Food & Drink', CONFIDENCE_CERTAIN),
    'SUBWAY': MerchantCategory('Subway', True, 'Food & Drink', CONFIDENCE_CERTAIN),
    'KFC': MerchantCategory('KFC', True, 'Food & Drink', CONFIDENCE_CERTAIN),
    'BURGER KING': MerchantCategory('Burger King', True, 'Food & Drink', CONFIDENCE_CERTAIN),
    'NANDOS': MerchantCategory('Nandos', True, 'Food & Drink', CONFIDENCE_CERTAIN),
    'PIZZA HUT': MerchantCategory('Pizza Hut', True, 'Food & Drink', CONFIDENCE_CERTAIN),
    'DOMINOS': MerchantCategory('Dominos', True, 'Food & Drink', CONFIDENCE_CERTAIN),
    'PAPA JOHNS': MerchantCategory('Papa Johns', True, 'Food & Drink', CONFIDENCE_CERTAIN),
    'PRET A MANGER': MerchantCategory('Pret', True, 'Food & Drink', CONFIDENCE_CERTAIN),
    'WAGAMAMA': MerchantCategory('Wagamama', True, 'Food & Drink', CONFIDENCE_HIGH),
    'NOODLE BAR': MerchantCategory('Noodle Bar', True, 'Food & Drink', CONFIDENCE_HIGH),
    'FISH AND CHIPS': MerchantCategory('Fish & Chips', True, 'Food & Drink', CONFIDENCE_CERTAIN),
    'CHINESE': MerchantCategory('Takeaway', True, 'Food & Drink', CONFIDENCE_HIGH),
    'INDIAN': MerchantCategory('Takeaway', True, 'Food & Drink', CONFIDENCE_HIGH),
}

# ===================================================================
# PERSONAL - BILLS & UTILITIES (100% Confidence)
# ===================================================================
BILLS_UTILITIES = {
    'COUNCIL TAX': MerchantCategory('Council Tax', True, 'Bills', CONFIDENCE_CERTAIN),
    'MORTGAGE': MerchantCategory('Mortgage', True, 'Bills', CONFIDENCE_CERTAIN),
    'RENT': MerchantCategory('Rent', True, 'Bills', CONFIDENCE_CERTAIN),
    'LLOYDS BANK MTG': MerchantCategory('Mortgage', True, 'Bills', CONFIDENCE_CERTAIN),
    'NATWEST LOAN': MerchantCategory('Loan', True, 'Bills', CONFIDENCE_CERTAIN),
    'CAPITAL ONE': MerchantCategory('Credit Card', True, 'Bills', CONFIDENCE_CERTAIN),
    'BARCLAYCARD': MerchantCategory('Credit Card', True, 'Bills', CONFIDENCE_CERTAIN),
    'MBNA': MerchantCategory('Credit Card', True, 'Bills', CONFIDENCE_CERTAIN),
    'SKY': MerchantCategory('TV/Broadband', True, 'Bills', CONFIDENCE_CERTAIN),
    'VIRGIN MEDIA': MerchantCategory('TV/Broadband', True, 'Bills', CONFIDENCE_CERTAIN),
    'BT': MerchantCategory('Phone/Broadband', True, 'Bills', CONFIDENCE_HIGH),
    'TALKTALK': MerchantCategory('Broadband', True, 'Bills', CONFIDENCE_CERTAIN),
    'EE LIMITED': MerchantCategory('Mobile Phone', True, 'Bills', CONFIDENCE_HIGH, 'Could be business if business phone'),
    'O2': MerchantCategory('Mobile Phone', True, 'Bills', CONFIDENCE_HIGH, 'Could be business if business phone'),
    'VODAFONE': MerchantCategory('Mobile Phone', True, 'Bills', CONFIDENCE_HIGH, 'Could be business if business phone'),
    'THREE': MerchantCategory('Mobile Phone', True, 'Bills', CONFIDENCE_HIGH, 'Could be business if business phone'),
    'BRITISH GAS': MerchantCategory('Gas/Electric', True, 'Bills', CONFIDENCE_CERTAIN),
    'E.ON': MerchantCategory('Gas/Electric', True, 'Bills', CONFIDENCE_CERTAIN),
    'SCOTTISH POWER': MerchantCategory('Gas/Electric', True, 'Bills', CONFIDENCE_CERTAIN),
    'OVO ENERGY': MerchantCategory('Gas/Electric', True, 'Bills', CONFIDENCE_CERTAIN),
    'WATER': MerchantCategory('Water', True, 'Bills', CONFIDENCE_CERTAIN),
    'THAMES WATER': MerchantCategory('Water', True, 'Bills', CONFIDENCE_CERTAIN),
    'SEVERN TRENT': MerchantCategory('Water', True, 'Bills', CONFIDENCE_CERTAIN),
    'ANGLIAN WATER': MerchantCategory('Water', True, 'Bills', CONFIDENCE_CERTAIN),
}

# ===================================================================
# PERSONAL - RETAIL & SHOPPING (90-100% Confidence)
# ===================================================================
RETAIL_SHOPPING = {
    'PRIMARK': MerchantCategory('Primark', True, 'Clothing', CONFIDENCE_CERTAIN),
    'NEXT': MerchantCategory('Next', True, 'Clothing', CONFIDENCE_HIGH),
    'NEXT RETAIL': MerchantCategory('Next', True, 'Clothing', CONFIDENCE_HIGH),
    'H&M': MerchantCategory('H&M', True, 'Clothing', CONFIDENCE_CERTAIN),
    'ZARA': MerchantCategory('Zara', True, 'Clothing', CONFIDENCE_CERTAIN),
    'MATALAN': MerchantCategory('Matalan', True, 'Clothing/Homeware', CONFIDENCE_CERTAIN),
    'TK MAXX': MerchantCategory('TK Maxx', True, 'Clothing/Homeware', CONFIDENCE_CERTAIN),
    'NEW LOOK': MerchantCategory('New Look', True, 'Clothing', CONFIDENCE_CERTAIN),
    'NEWLOOK': MerchantCategory('New Look', True, 'Clothing', CONFIDENCE_CERTAIN),
    'RIVER ISLAND': MerchantCategory('River Island', True, 'Clothing', CONFIDENCE_CERTAIN),
    'TOPSHOP': MerchantCategory('Topshop', True, 'Clothing', CONFIDENCE_CERTAIN),
    'BOOTS': MerchantCategory('Boots', True, 'Pharmacy/Health', CONFIDENCE_CERTAIN),
    'SUPERDRUG': MerchantCategory('Superdrug', True, 'Pharmacy/Health', CONFIDENCE_CERTAIN),
    'ARGOS': MerchantCategory('Argos', True, 'General Retail', CONFIDENCE_HIGH),
    'IKEA': MerchantCategory('IKEA', True, 'Furniture/Homeware', CONFIDENCE_HIGH, 'Could be business if office furniture'),
    'IKEA LTD': MerchantCategory('IKEA', True, 'Furniture/Homeware', CONFIDENCE_HIGH, 'Could be business if office furniture'),
    'DUNELM': MerchantCategory('Dunelm', True, 'Homeware', CONFIDENCE_CERTAIN),
    'WILKO': MerchantCategory('Wilko', True, 'Homeware', CONFIDENCE_CERTAIN),
    'VERY': MerchantCategory('Very', True, 'Online Retail', CONFIDENCE_CERTAIN),
    'SPORTS DIRECT': MerchantCategory('Sports Direct', True, 'Sports/Leisure', CONFIDENCE_CERTAIN),
    'JD SPORTS': MerchantCategory('JD Sports', True, 'Sports/Leisure', CONFIDENCE_CERTAIN),
    'HMV': MerchantCategory('HMV', True, 'Entertainment', CONFIDENCE_CERTAIN),
    'HMV RETAIL': MerchantCategory('HMV', True, 'Entertainment', CONFIDENCE_CERTAIN),
    'GAME': MerchantCategory('Game', True, 'Entertainment', CONFIDENCE_CERTAIN),
    'CEX': MerchantCategory('CEX', True, 'Entertainment', CONFIDENCE_CERTAIN),
    'WATERSTONES': MerchantCategory('Waterstones', True, 'Books', CONFIDENCE_CERTAIN),
    'WHSmith': MerchantCategory('WHSmith', True, 'Books/Stationery', CONFIDENCE_HIGH, 'Could be business if office supplies'),
    'PETS AT HOME': MerchantCategory('Pets at Home', True, 'Pets', CONFIDENCE_CERTAIN),
    'HARRODS': MerchantCategory('Harrods', True, 'Retail', CONFIDENCE_CERTAIN),
    'HARRODS BEAUTY': MerchantCategory('Harrods Beauty', True, 'Beauty', CONFIDENCE_CERTAIN),
    'FENWICK': MerchantCategory('Fenwick', True, 'Department Store', CONFIDENCE_CERTAIN),
}

# ===================================================================
# PERSONAL - ENTERTAINMENT & LEISURE (100% Confidence)
# ===================================================================
ENTERTAINMENT = {
    'NETFLIX': MerchantCategory('Netflix', True, 'Entertainment', CONFIDENCE_CERTAIN),
    'AMAZON PRIME': MerchantCategory('Amazon Prime', True, 'Entertainment', CONFIDENCE_CERTAIN),
    'SPOTIFY': MerchantCategory('Spotify', True, 'Entertainment', CONFIDENCE_CERTAIN),
    'APPLE MUSIC': MerchantCategory('Apple Music', True, 'Entertainment', CONFIDENCE_CERTAIN),
    'DISNEY+': MerchantCategory('Disney+', True, 'Entertainment', CONFIDENCE_CERTAIN),
    'NOW TV': MerchantCategory('Now TV', True, 'Entertainment', CONFIDENCE_CERTAIN),
    'CINEMA': MerchantCategory('Cinema', True, 'Entertainment', CONFIDENCE_CERTAIN),
    'CINEWORLD': MerchantCategory('Cinema', True, 'Entertainment', CONFIDENCE_CERTAIN),
    'ODEON': MerchantCategory('Cinema', True, 'Entertainment', CONFIDENCE_CERTAIN),
    'VUE': MerchantCategory('Cinema', True, 'Entertainment', CONFIDENCE_CERTAIN),
    'EVERYONE ACTIVE': MerchantCategory('Gym', True, 'Entertainment', CONFIDENCE_CERTAIN),
    'PURE GYM': MerchantCategory('Gym', True, 'Entertainment', CONFIDENCE_CERTAIN),
    'DAVID LLOYD': MerchantCategory('Gym', True, 'Entertainment', CONFIDENCE_CERTAIN),
    'NUFFIELD': MerchantCategory('Gym', True, 'Entertainment', CONFIDENCE_CERTAIN),
    'LOTTERY': MerchantCategory('Lottery', True, 'Entertainment', CONFIDENCE_CERTAIN),
    'POSTCODE LOTTERY': MerchantCategory('Lottery', True, 'Entertainment', CONFIDENCE_CERTAIN),
}

# ===================================================================
# PERSONAL - SPECIAL PATTERNS (100% Confidence)
# ===================================================================
SPECIAL_PATTERNS = {
    'ROUND UP': MerchantCategory('Savings Round-Up', True, 'Savings', CONFIDENCE_CERTAIN, 'Bank savings round-up feature'),
}

# ===================================================================
# BUSINESS - PROFESSIONAL SERVICES (90-100% Confidence)
# ===================================================================
PROFESSIONAL_SERVICES = {
    'ACCOUNTANT': MerchantCategory('Accountant', False, 'Accountancy', CONFIDENCE_CERTAIN),
    'HMRC': MerchantCategory('HMRC', False, 'Tax Payments', CONFIDENCE_HIGH, 'Tax/VAT payments'),
    'COMPANIES HOUSE': MerchantCategory('Companies House', False, 'Professional fees', CONFIDENCE_CERTAIN),
    'SOLICITOR': MerchantCategory('Solicitor', False, 'Legal fees', CONFIDENCE_HIGH),
    'LEGAL': MerchantCategory('Legal', False, 'Legal fees', CONFIDENCE_HIGH),
}

# ===================================================================
# BUSINESS - SELF EMPLOYMENT INCOME (100% Confidence)
# ===================================================================
SELF_EMPLOYMENT_INCOME = {
    'THE ROAD CENTRE': MerchantCategory('The Road Centre', False, 'Self-employment', CONFIDENCE_CERTAIN, 'Self-employment income'),
    'ROAD CENTRE': MerchantCategory('The Road Centre', False, 'Self-employment', CONFIDENCE_CERTAIN, 'Self-employment income'),
}

# ===================================================================
# BUSINESS - OFFICE SUPPLIES (80-90% Confidence)
# ===================================================================
OFFICE_SUPPLIES = {
    'STAPLES': MerchantCategory('Staples', False, 'Office costs', CONFIDENCE_HIGH),
    'OFFICE DEPOT': MerchantCategory('Office Depot', False, 'Office costs', CONFIDENCE_HIGH),
    'VIKING': MerchantCategory('Viking', False, 'Office costs', CONFIDENCE_HIGH),
    'RYMAN': MerchantCategory('Ryman', False, 'Office costs', CONFIDENCE_HIGH),
}

# ===================================================================
# AMBIGUOUS - NEEDS REVIEW (50% Confidence)
# ===================================================================
AMBIGUOUS_MERCHANTS = {
    'PAYPAL': MerchantCategory('PayPal', True, 'Unknown', CONFIDENCE_LOW, 'Could be business or personal'),
    'AMAZON': MerchantCategory('Amazon', True, 'Shopping', CONFIDENCE_LOW, 'Could be business or personal'),
    'EBAY': MerchantCategory('eBay', True, 'Shopping', CONFIDENCE_LOW, 'Could be business or personal'),
}

# ===================================================================
# COMBINED DATABASE
# ===================================================================
ALL_MERCHANTS = {}
ALL_MERCHANTS.update(GOVERNMENT_BENEFITS)
ALL_MERCHANTS.update(SUPERMARKETS)
ALL_MERCHANTS.update(FAST_FOOD)
ALL_MERCHANTS.update(BILLS_UTILITIES)
ALL_MERCHANTS.update(RETAIL_SHOPPING)
ALL_MERCHANTS.update(ENTERTAINMENT)
ALL_MERCHANTS.update(SPECIAL_PATTERNS)
ALL_MERCHANTS.update(PROFESSIONAL_SERVICES)
ALL_MERCHANTS.update(SELF_EMPLOYMENT_INCOME)
ALL_MERCHANTS.update(OFFICE_SUPPLIES)
ALL_MERCHANTS.update(AMBIGUOUS_MERCHANTS)


def lookup_merchant(description: str):
    """
    Look up a merchant in the database
    Returns: MerchantCategory or None
    """
    desc_upper = description.upper()

    # Check for exact or partial matches
    for keyword, merchant_cat in ALL_MERCHANTS.items():
        if keyword.upper() in desc_upper:
            return merchant_cat

    return None


def get_categorization_confidence(description: str):
    """
    Get categorization confidence for a transaction
    Returns: (is_personal, category, confidence, merchant_name)
    """
    merchant = lookup_merchant(description)

    if merchant:
        return (merchant.is_personal, merchant.category, merchant.confidence, merchant.name)

    # Unknown merchant
    return (True, 'Unknown', CONFIDENCE_UNKNOWN, 'Unknown')  # Default to personal with 0 confidence
