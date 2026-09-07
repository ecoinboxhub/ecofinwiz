from pydantic import BaseModel, Field


# ── Mortgage ──
class MortgageInput(BaseModel):
    principal: float = Field(gt=0)
    annual_rate_pct: float = Field(gt=0)
    term_years: int = Field(gt=0, le=60)


class MortgageResult(BaseModel):
    monthly_payment: float
    total_payment: float
    total_interest: float
    monthly_rate_pct: float


# ── Stock / investment return ──
class InvestmentInput(BaseModel):
    principal: float = Field(gt=0)
    annual_rate_pct: float = Field(gt=-100)
    years: int = Field(gt=0, le=100)


class InvestmentResult(BaseModel):
    future_value: float
    roi_pct: float
    cagr_pct: float


# ── Mutual fund / money market (lump sum + SIP) ──
class MutualFundInput(BaseModel):
    initial_lump_sum: float = Field(default=0, ge=0)
    monthly_contribution: float = Field(default=0, ge=0)
    annual_rate_pct: float = Field(gt=0)
    years: int = Field(gt=0, le=100)


class MutualFundResult(BaseModel):
    future_value: float
    total_invested: float
    growth_amount: float
    growth_pct: float


# ── Bond yield ──
class BondInput(BaseModel):
    face_value: float = Field(gt=0)
    coupon_rate_pct: float = Field(gt=0)
    price: float = Field(gt=0)
    years_to_maturity: int = Field(gt=0, le=100)


class BondResult(BaseModel):
    annual_coupon: float
    current_yield_pct: float
    ytm_approx_pct: float


# ── Treasury bill ──
class TreasuryBillInput(BaseModel):
    face_value: float = Field(gt=0)
    price: float = Field(gt=0)
    days: int = Field(ge=1, le=365)


class TreasuryBillResult(BaseModel):
    discount_yield_pct: float
    effective_yield_pct: float
    profit: float


# ── Commercial paper ──
class CommercialPaperInput(BaseModel):
    face_value: float = Field(gt=0)
    discount_rate_pct: float = Field(gt=0)
    days: int = Field(ge=1, le=365)


class CommercialPaperResult(BaseModel):
    price: float
    discount_yield_pct: float
    effective_yield_pct: float
    profit: float


# ── Real estate ──
class RealEstateInput(BaseModel):
    property_value: float = Field(gt=0)
    annual_rent: float = Field(ge=0)
    annual_expenses: float = Field(default=0, ge=0)
    down_payment: float = Field(gt=0)


class RealEstateResult(BaseModel):
    gross_rental_yield_pct: float
    net_rental_yield_pct: float
    net_annual_income: float
    cash_on_cash_roi_pct: float


# ── Compound interest / goal projection ──
class CompoundInterestInput(BaseModel):
    principal: float = Field(default=0, ge=0)
    monthly_contribution: float = Field(default=0, ge=0)
    annual_rate_pct: float = Field(gt=0)
    years: int = Field(gt=0, le=100)


class CompoundInterestResult(BaseModel):
    future_value: float
    total_contributions: float
    total_interest: float