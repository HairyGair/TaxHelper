# Making Tax Digital (MTD) for Income Tax - Research & Implementation Guide

**Date:** October 12, 2025
**Status:** Research Complete - Not Yet Implemented
**For:** Tax Helper App

---

## Executive Summary

Making Tax Digital (MTD) for Income Tax Self Assessment is HMRC's digital initiative requiring certain taxpayers to keep digital records and submit quarterly updates via API. This document outlines the requirements, timeline, and implementation approach for integrating MTD into Tax Helper.

---

## What is Making Tax Digital (MTD)?

MTD for Income Tax requires eligible taxpayers to:

1. **Maintain digital records** using compatible software or spreadsheets
2. **Submit quarterly updates** of income and expenditure to HMRC
3. **Submit a final declaration** after the end of the tax year
4. **Use HMRC APIs** for all submissions (no manual form filling)

### Who Must Use MTD?

**Phased rollout:**

- **April 2026:** Self-employed individuals and landlords with combined income **over £50,000**
- **April 2027:** Those with income **over £30,000**
- **April 2028:** Those with income **over £20,000**

**Public Beta:** Opened April 2025 for voluntary early adoption

**Exemptions:** Some taxpayers can opt out based on age, disability, or religious beliefs

---

## Why Integrate MTD into Tax Helper?

### Benefits

1. **Future-proof:** MTD becomes mandatory for most self-employed individuals
2. **Convenience:** Submit directly from Tax Helper without using HMRC website
3. **Compliance:** Ensures users meet quarterly obligations automatically
4. **Competitive advantage:** Become an "MTD-compatible software"
5. **User retention:** Users won't need to switch to other software

### Challenges

1. **Complex API integration** (30-40 hours development)
2. **HMRC approval process** (can take weeks/months)
3. **Ongoing maintenance** (API changes, testing)
4. **Fraud prevention requirements** (specific headers needed)
5. **User support burden** (helping users with HMRC authentication)

---

## Technical Requirements

### 1. Minimum Functionality Standards

HMRC requires MTD software to support:

✅ **Digital record keeping** - Track income and expenses digitally
✅ **Quarterly submissions** - Submit updates within 1 month after quarter end
✅ **Tax calculations** - Calculate tax liability
✅ **Accounting adjustments** - Support accruals, prepayments, etc.
✅ **Loss claims** - Handle business losses
✅ **Additional income sources** - Employment, property, dividends
✅ **Final declaration** - End-of-year submission
✅ **HMRC nudges** - Receive and display HMRC prompts

**Tax Helper Status:**
- ✅ Digital record keeping: **Already implemented**
- ✅ Tax calculations: **Already implemented**
- ❌ Quarterly submissions: **Not implemented**
- ❌ API integration: **Not implemented**
- ⚠️ Accounting adjustments: **Partially implemented**

### 2. Authentication & Authorization

**Method:** OAuth 2.0

**Process:**
1. User authorizes Tax Helper to access their HMRC data
2. User redirected to HMRC login page
3. User grants permission
4. HMRC returns authorization code
5. Tax Helper exchanges code for access token
6. Access token used for all API requests

**Implementation needs:**
- OAuth 2.0 client library
- Secure token storage (encrypted)
- Token refresh mechanism
- User authorization flow UI

### 3. Fraud Prevention Headers

**Required headers on ALL API requests:**

- `Gov-Client-Connection-Method` - How user connects (WEB_APP_VIA_SERVER)
- `Gov-Client-Device-ID` - Unique device identifier
- `Gov-Client-User-IDs` - User identifier
- `Gov-Client-Timezone` - User timezone (e.g., UTC+00:00)
- `Gov-Client-Local-IPs` - User's local IP addresses
- `Gov-Client-Screens` - Screen resolution
- `Gov-Client-Window-Size` - Browser window size
- `Gov-Client-Browser-Plugins` - Installed plugins
- `Gov-Client-Browser-JS-User-Agent` - JavaScript user agent
- `Gov-Client-Multi-Factor` - Multi-factor auth details
- `Gov-Client-User-Agent` - User agent string

**Why?** HMRC uses these to detect fraud and ensure software legitimacy.

**Challenge:** Many of these require client-side JavaScript to collect, which is challenging for a Streamlit app.

### 4. Core APIs Needed

#### A. Self Assessment Individual Details API
**Purpose:** Retrieve customer NINO, MTD ID, business details

**Endpoint:** `GET /individuals/details/nino/{nino}`

**Returns:**
```json
{
  "mtdId": "XAIT00000000001",
  "firstName": "John",
  "lastName": "Smith",
  "nino": "AB123456C",
  "dateOfBirth": "1990-01-01"
}
```

#### B. Business Details API
**Purpose:** Get user's business details (trading name, address, etc.)

**Endpoint:** `GET /individuals/business/details/{nino}`

**Returns:** Business type, accounting period, trading name

#### C. Self Employment Business API
**Purpose:** Submit quarterly updates of income and expenses

**Endpoint:** `POST /individuals/business/self-employment/{nino}/{businessId}/period`

**Request Body:**
```json
{
  "periodFromDate": "2024-04-06",
  "periodToDate": "2024-07-05",
  "income": {
    "turnover": 10000.00,
    "other": 500.00
  },
  "expenses": {
    "costOfGoodsBought": 2000.00,
    "cisPaymentsToSubcontractors": 0.00,
    "staffCosts": 0.00,
    "travelCosts": 300.00,
    "premisesRunningCosts": 500.00,
    "maintenanceCosts": 0.00,
    "adminCosts": 200.00,
    "advertisingCosts": 100.00,
    "interest": 0.00,
    "financialCharges": 50.00,
    "badDebt": 0.00,
    "professionalFees": 800.00,
    "depreciation": 0.00,
    "other": 150.00
  }
}
```

**Maps to:** Tax Helper's Expense categories

#### D. Self Assessment Tax Calculation API
**Purpose:** Trigger and retrieve tax calculations

**Endpoints:**
- `POST /individuals/calculations/{nino}/self-assessment/{taxYear}` - Trigger calculation
- `GET /individuals/calculations/{nino}/self-assessment/{taxYear}/{calculationId}` - Get result

**Returns:** Full tax calculation including Income Tax, NI, allowances

#### E. Obligations API
**Purpose:** Get submission deadlines and status

**Endpoint:** `GET /obligations/details/{nino}/income-and-expenditure`

**Returns:** List of quarterly deadlines and whether met

#### F. Final Declaration API
**Purpose:** Submit final end-of-period statement

**Endpoint:** `POST /individuals/business/{nino}/end-of-period-statement/from/{from}/to/{to}`

**Purpose:** Crystallize the tax return

### 5. Development Process

**Phase 1: Sandbox Testing**
1. Register as a developer on HMRC Developer Hub
2. Create test application
3. Get sandbox credentials
4. Test all API endpoints with fake data

**Phase 2: Production Application**
1. Submit production application to HMRC
2. Provide evidence of sandbox testing
3. Demonstrate minimum functionality
4. Agree to Terms of Use
5. Wait for approval (can take weeks)

**Phase 3: Go Live**
1. Implement OAuth flow
2. Add fraud prevention headers
3. Build quarterly submission UI
4. Test with beta users
5. Launch to all users

---

## Implementation Roadmap

### Short Term (Optional - for early adopters)

**Goal:** Allow voluntary MTD users to submit from Tax Helper

**Tasks:**
1. Add OAuth 2.0 authentication (~8 hours)
2. Implement fraud prevention headers (~4 hours)
3. Create quarterly submission page (~8 hours)
4. Build tax calculation retrieval (~4 hours)
5. Test in HMRC sandbox (~8 hours)
6. Submit for HMRC approval (~admin time)

**Total effort:** ~32 hours + approval wait time

**Value:** Low (voluntary adoption is minimal in 2025)

### Medium Term (Before April 2026)

**Goal:** Be ready for mandatory MTD rollout

**Tasks:**
- Complete all Short Term tasks
- Add obligations tracking (~4 hours)
- Build final declaration UI (~6 hours)
- Add quarterly reminders (~2 hours)
- User documentation and help (~4 hours)
- Beta testing with real users (~ongoing)

**Total effort:** ~48 hours

**Value:** High (essential for users with income >£50k)

### Long Term (2027-2028)

**Goal:** Full MTD compliance for all income levels

**Tasks:**
- Support additional income sources (property, etc.) (~10 hours)
- Advanced accounting adjustments (~8 hours)
- Agent support (if needed) (~15 hours)
- Continuous API maintenance (~ongoing)

---

## Data Mapping: Tax Helper → MTD API

Our data already maps closely to MTD requirements:

| Tax Helper Field | MTD API Field | Notes |
|------------------|---------------|-------|
| Self-employment income | `income.turnover` | Direct mapping |
| Expense: Stock/Materials | `expenses.costOfGoodsBought` | Direct mapping |
| Expense: Staff costs | `expenses.staffCosts` | Direct mapping |
| Expense: Travel | `expenses.travelCosts` | Direct mapping |
| Expense: Rent/Rates | `expenses.premisesRunningCosts` | Direct mapping |
| Expense: Office costs | `expenses.adminCosts` | Direct mapping |
| Expense: Advertising | `expenses.advertisingCosts` | Direct mapping |
| Expense: Interest | `expenses.interest` | Direct mapping |
| Expense: Bank charges | `expenses.financialCharges` | Direct mapping |
| Expense: Professional fees | `expenses.professionalFees` | Direct mapping |
| Expense: Accountancy | `expenses.professionalFees` | Combined with above |
| Expense: Other | `expenses.other` | Direct mapping |
| Mileage allowance | Not in periodic update | Submit separately |

**Missing fields:**
- CIS payments to subcontractors (not applicable for most users)
- Maintenance costs (could add as category)
- Bad debt (could add as category)
- Depreciation (use Capital Allowances instead)

**Action:** Our expense categories align well. Minor additions needed.

---

## Cost-Benefit Analysis

### Costs

**Development:**
- Initial implementation: ~40-50 hours
- Testing and debugging: ~10-15 hours
- HMRC approval process: ~20 hours (admin, documentation)
- **Total:** ~70-85 hours

**Ongoing:**
- API maintenance: ~5 hours/year
- User support: ~2 hours/month
- Compliance updates: ~10 hours/year

**Financial:**
- Developer time: £70-85 hours × £50/hour = **£3,500-4,250**
- HMRC approval: Free
- API usage: Free

### Benefits

**User Value:**
- Avoid switching to other software (retention)
- One-click quarterly submissions (convenience)
- Automatic deadline tracking (compliance)
- Integrated tax calculations (accuracy)

**Business Value:**
- Competitive advantage (MTD-ready software)
- Marketing opportunity ("HMRC-approved")
- Increased user engagement (quarterly touchpoints)
- Future-proof the application

**Monetization:**
- Could charge premium for MTD features
- Potential subscription model (£10/month for MTD users)
- 100 users × £10/month × 12 months = £12,000/year

**ROI:** Could pay for itself within 4-5 months if monetized

---

## Alternative: Don't Implement MTD

### Option 1: Partner with MTD Software

**Approach:** Export data in format compatible with existing MTD software (e.g., QuickBooks, FreeAgent)

**Pros:**
- No development needed
- No HMRC approval needed
- Users can choose their preferred MTD tool

**Cons:**
- Users need two tools (Tax Helper + MTD software)
- Potential for data inconsistencies
- Users may abandon Tax Helper entirely

### Option 2: Wait and See

**Approach:** Wait until 2026 and reassess

**Pros:**
- Save development time now
- See which users actually need it
- APIs may improve by then

**Cons:**
- Users with income >£50k may leave sooner
- Playing catch-up in competitive market
- Rush implementation under pressure

### Option 3: Basic Export Only

**Approach:** Provide CSV/JSON export that users manually upload to HMRC

**Pros:**
- Minimal development (2-3 hours)
- Still provides value
- Low risk

**Cons:**
- Not "true" MTD integration
- Users still need to visit HMRC site
- Defeats purpose of digital convenience

---

## Recommendation

**For Tax Helper (Personal Use):**

**Recommendation:** **Wait until 2026**

**Reasoning:**
1. Current income likely below £50k threshold
2. Can file via HMRC website for now
3. Save 70+ hours of development
4. APIs will be more mature by 2026
5. Can reassess based on actual need

**Alternative if income exceeds £50k:**

Implement basic MTD support:
1. OAuth authentication
2. Quarterly submission (income + expenses only)
3. Skip advanced features initially
4. Estimated effort: ~25-30 hours

**For Commercial Distribution (e.g., to Jemma or others):**

**Recommendation:** **Implement in 2025**

**Reasoning:**
1. Competitive requirement for self-employed users
2. Marketing advantage ("MTD-ready")
3. Users expect modern software to support MTD
4. April 2026 deadline approaching fast
5. Can potentially monetize as premium feature

**Suggested Pricing:**
- Basic Tax Helper: Free
- MTD Integration: £10/month or £100/year
- Covers development and ongoing maintenance

---

## Technical Architecture (If Implementing)

### Components Needed

1. **OAuth Module** (`mtd_auth.py`)
   - Handle HMRC authorization flow
   - Secure token storage (encrypted in database)
   - Token refresh mechanism

2. **API Client** (`mtd_api.py`)
   - Wrapper for all HMRC API endpoints
   - Fraud prevention header injection
   - Error handling and retry logic

3. **Quarterly Submission Page** (in `app.py`)
   - UI to review and submit quarterly data
   - Show obligations and deadlines
   - Confirmation screens

4. **Obligations Tracker** (Dashboard widget)
   - Display upcoming deadlines
   - Show submission status
   - Send reminders

5. **Database Changes** (new table: `mtd_submissions`)
   ```sql
   CREATE TABLE mtd_submissions (
       id INTEGER PRIMARY KEY,
       submission_date DATE,
       period_from DATE,
       period_to DATE,
       submission_id VARCHAR(50),
       status VARCHAR(20),
       response_json TEXT
   );
   ```

6. **Settings** (new fields)
   - MTD enabled (boolean)
   - NINO (encrypted)
   - MTD ID
   - OAuth tokens (encrypted)
   - Last sync date

### Example Code Structure

```python
# mtd_auth.py
import requests
from cryptography.fernet import Fernet

class MTDAuth:
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.auth_url = "https://api.service.hmrc.gov.uk/oauth/authorize"
        self.token_url = "https://api.service.hmrc.gov.uk/oauth/token"

    def get_authorization_url(self, redirect_uri, state):
        """Generate URL for user to authorize"""
        params = {
            'client_id': self.client_id,
            'response_type': 'code',
            'scope': 'read:self-assessment write:self-assessment',
            'redirect_uri': redirect_uri,
            'state': state
        }
        return f"{self.auth_url}?{urlencode(params)}"

    def exchange_code_for_token(self, code, redirect_uri):
        """Exchange authorization code for access token"""
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': redirect_uri
        }
        response = requests.post(self.token_url, data=data)
        return response.json()

    def refresh_token(self, refresh_token):
        """Refresh expired access token"""
        # Implementation here
        pass

# mtd_api.py
class MTDAPI:
    def __init__(self, access_token):
        self.access_token = access_token
        self.base_url = "https://api.service.hmrc.gov.uk"

    def submit_quarterly_update(self, nino, business_id, period_data):
        """Submit quarterly income/expense update"""
        url = f"{self.base_url}/individuals/business/self-employment/{nino}/{business_id}/period"
        headers = self._get_headers()
        response = requests.post(url, json=period_data, headers=headers)
        return response.json()

    def get_obligations(self, nino):
        """Get submission obligations and deadlines"""
        url = f"{self.base_url}/obligations/details/{nino}/income-and-expenditure"
        headers = self._get_headers()
        response = requests.get(url, headers=headers)
        return response.json()

    def _get_headers(self):
        """Build headers including fraud prevention"""
        return {
            'Authorization': f'Bearer {self.access_token}',
            'Accept': 'application/vnd.hmrc.1.0+json',
            'Gov-Client-Connection-Method': 'WEB_APP_VIA_SERVER',
            # ... all other fraud prevention headers
        }
```

---

## Resources & Links

### Official HMRC Resources

- **Developer Hub:** https://developer.service.hmrc.gov.uk/
- **MTD Service Guide:** https://developer.service.hmrc.gov.uk/guides/income-tax-mtd-end-to-end-service-guide/
- **API Documentation:** https://developer.service.hmrc.gov.uk/api-documentation/docs/api
- **Sandbox Testing:** https://developer.service.hmrc.gov.uk/api-test-user
- **Production Checklist:** https://developer.service.hmrc.gov.uk/guides/income-tax-mtd-end-to-end-service-guide/documentation/production-approvals-checklist.html

### Government Guidance

- **Who needs to use MTD:** https://www.gov.uk/guidance/check-if-youre-eligible-for-making-tax-digital-for-income-tax
- **How to use MTD:** https://www.gov.uk/guidance/use-making-tax-digital-for-income-tax
- **Software providers:** https://www.gov.uk/guidance/find-software-thats-compatible-with-making-tax-digital-for-income-tax

### Technical References

- **OAuth 2.0 Spec:** https://oauth.net/2/
- **API Changelog:** https://github.com/hmrc/income-tax-mtd-changelog
- **Python OAuth Library:** https://pypi.org/project/requests-oauthlib/

---

## Summary

**Making Tax Digital is coming**, and Tax Helper is well-positioned to integrate with it. Our data model already aligns with HMRC's requirements.

**Decision Point:**

- **If for personal use only:** Wait until 2026, assess then
- **If distributing to others:** Start implementation in Q1 2025 to be ready for April 2026 deadline

**Next Steps (If Proceeding):**

1. Register on HMRC Developer Hub
2. Create test application and get sandbox credentials
3. Build OAuth authentication module
4. Implement quarterly submission API calls
5. Test thoroughly in sandbox
6. Apply for production approval
7. Launch to users with documentation

**Estimated Timeline:**
- Development: 6-8 weeks part-time
- HMRC approval: 2-4 weeks
- Beta testing: 4 weeks
- **Total:** 3-4 months to production-ready

---

**Version:** 1.0.0
**Research Date:** October 12, 2025
**Next Review:** January 2026
**Status:** Decision pending
