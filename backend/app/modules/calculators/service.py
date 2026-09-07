"""
Financial calculators — pure math, no database dependencies.

All functions return plain dicts matching the response schemas in
app.modules.calculators.schemas.
"""

from math import pow


def _round2(value: float) -> float:
    return round(value, 2)


def calculate_mortgage(principal: float, annual_rate_pct: float, term_years: int) -> dict:
    """Monthly payment via the standard amortisation formula."""
    monthly_rate = annual_rate_pct / 100 / 12
    n = term_years * 12
    if monthly_rate == 0:
        monthly_payment = principal / n
    else:
        factor = pow(1 + monthly_rate, n)
        monthly_payment = principal * monthly_rate * factor / (factor - 1)
    total_payment = monthly_payment * n
    return {
        "monthly_payment": _round2(monthly_payment),
        "total_payment": _round2(total_payment),
        "total_interest": _round2(total_payment - principal),
        "monthly_rate_pct": _round2(annual_rate_pct / 12),
    }


def calculate_investment(principal: float, annual_rate_pct: float, years: int) -> dict:
    """Future value, ROI and CAGR for a lump-sum investment."""
    rate = annual_rate_pct / 100
    future_value = principal * pow(1 + rate, years)
    roi = (future_value - principal) / principal * 100 if principal else 0
    cagr = (pow(future_value / principal, 1 / years) - 1) * 100 if principal else 0
    return {
        "future_value": _round2(future_value),
        "roi_pct": _round2(roi),
        "cagr_pct": _round2(cagr),
    }


def calculate_mutual_fund(initial_lump_sum: float, monthly_contribution: float,
                          annual_rate_pct: float, years: int) -> dict:
    """Lump sum + recurring (SIP-style) contributions, compounded monthly."""
    monthly_rate = annual_rate_pct / 100 / 12
    n = years * 12
    if monthly_rate == 0:
        future_value = initial_lump_sum + monthly_contribution * n
    else:
        lump_growth = initial_lump_sum * pow(1 + monthly_rate, n)
        sip_growth = monthly_contribution * ((pow(1 + monthly_rate, n) - 1) / monthly_rate)
        future_value = lump_growth + sip_growth
    total_invested = initial_lump_sum + monthly_contribution * n
    growth = future_value - total_invested
    growth_pct = growth / total_invested * 100 if total_invested else 0
    return {
        "future_value": _round2(future_value),
        "total_invested": _round2(total_invested),
        "growth_amount": _round2(growth),
        "growth_pct": _round2(growth_pct),
    }


def calculate_bond(face_value: float, coupon_rate_pct: float, price: float,
                   years_to_maturity: int) -> dict:
    """Current yield + approximate yield-to-maturity for a coupon bond."""
    annual_coupon = face_value * coupon_rate_pct / 100
    current_yield = annual_coupon / price * 100 if price else 0
    avg_price = (face_value + price) / 2
    ytm = (annual_coupon + (face_value - price) / years_to_maturity) / avg_price * 100 if avg_price else 0
    return {
        "annual_coupon": _round2(annual_coupon),
        "current_yield_pct": _round2(current_yield),
        "ytm_approx_pct": _round2(ytm),
    }


def calculate_treasury_bill(face_value: float, price: float, days: int) -> dict:
    """Discount yield and effective (annualised) yield for a T-bill."""
    profit = face_value - price
    discount_yield = profit / face_value * (360 / days) * 100 if days else 0
    effective_yield = (pow(face_value / price, 365 / days) - 1) * 100 if price and days else 0
    return {
        "discount_yield_pct": _round2(discount_yield),
        "effective_yield_pct": _round2(effective_yield),
        "profit": _round2(profit),
    }


def calculate_commercial_paper(face_value: float, discount_rate_pct: float, days: int) -> dict:
    """Proceeds (price), discount yield and effective yield for commercial paper."""
    price = face_value * (1 - discount_rate_pct / 100 * days / 360)
    profit = face_value - price
    effective_yield = (pow(face_value / price, 365 / days) - 1) * 100 if price and days else 0
    return {
        "price": _round2(price),
        "discount_yield_pct": _round2(discount_rate_pct),
        "effective_yield_pct": _round2(effective_yield),
        "profit": _round2(profit),
    }


def calculate_real_estate(property_value: float, annual_rent: float,
                          annual_expenses: float, down_payment: float) -> dict:
    """Gross/net rental yield and cash-on-cash return for a property."""
    gross_yield = annual_rent / property_value * 100 if property_value else 0
    net_income = annual_rent - annual_expenses
    net_yield = net_income / property_value * 100 if property_value else 0
    cash_on_cash = net_income / down_payment * 100 if down_payment else 0
    return {
        "gross_rental_yield_pct": _round2(gross_yield),
        "net_rental_yield_pct": _round2(net_yield),
        "net_annual_income": _round2(net_income),
        "cash_on_cash_roi_pct": _round2(cash_on_cash),
    }


def calculate_compound_interest(principal: float, monthly_contribution: float,
                                annual_rate_pct: float, years: int) -> dict:
    """Goal projection: how a monthly saving grows over time."""
    monthly_rate = annual_rate_pct / 100 / 12
    n = years * 12
    if monthly_rate == 0:
        future_value = principal + monthly_contribution * n
    else:
        principal_growth = principal * pow(1 + monthly_rate, n)
        sip_growth = monthly_contribution * ((pow(1 + monthly_rate, n) - 1) / monthly_rate)
        future_value = principal_growth + sip_growth
    total_contributions = principal + monthly_contribution * n
    return {
        "future_value": _round2(future_value),
        "total_contributions": _round2(total_contributions),
        "total_interest": _round2(future_value - total_contributions),
    }