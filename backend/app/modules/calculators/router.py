from fastapi import APIRouter, Depends

from app.modules.auth.dependencies import get_current_user
from app.models import User
from app.modules.calculators.schemas import (
    MortgageInput, MortgageResult,
    InvestmentInput, InvestmentResult,
    MutualFundInput, MutualFundResult,
    BondInput, BondResult,
    TreasuryBillInput, TreasuryBillResult,
    CommercialPaperInput, CommercialPaperResult,
    RealEstateInput, RealEstateResult,
    CompoundInterestInput, CompoundInterestResult,
)
from app.modules.calculators import service

router = APIRouter(prefix="/calculators", tags=["Calculators"])


@router.get("")
async def list_calculators(current_user: User = Depends(get_current_user)):
    return {
        "calculators": [
            {"key": "mortgage", "name": "Mortgage"},
            {"key": "investment", "name": "Stock / Investment Return"},
            {"key": "mutual_fund", "name": "Mutual Fund / Money Market"},
            {"key": "bond", "name": "Bond Yield"},
            {"key": "treasury_bill", "name": "Treasury Bill"},
            {"key": "commercial_paper", "name": "Commercial Paper"},
            {"key": "real_estate", "name": "Real Estate"},
            {"key": "compound_interest", "name": "Compound Interest / Goal Projection"},
        ]
    }


@router.post("/mortgage", response_model=MortgageResult)
async def mortgage(body: MortgageInput, current_user: User = Depends(get_current_user)):
    return service.calculate_mortgage(body.principal, body.annual_rate_pct, body.term_years)


@router.post("/investment", response_model=InvestmentResult)
async def investment(body: InvestmentInput, current_user: User = Depends(get_current_user)):
    return service.calculate_investment(body.principal, body.annual_rate_pct, body.years)


@router.post("/mutual-fund", response_model=MutualFundResult)
async def mutual_fund(body: MutualFundInput, current_user: User = Depends(get_current_user)):
    return service.calculate_mutual_fund(
        body.initial_lump_sum, body.monthly_contribution, body.annual_rate_pct, body.years
    )


@router.post("/bond", response_model=BondResult)
async def bond(body: BondInput, current_user: User = Depends(get_current_user)):
    return service.calculate_bond(body.face_value, body.coupon_rate_pct, body.price, body.years_to_maturity)


@router.post("/treasury-bill", response_model=TreasuryBillResult)
async def treasury_bill(body: TreasuryBillInput, current_user: User = Depends(get_current_user)):
    return service.calculate_treasury_bill(body.face_value, body.price, body.days)


@router.post("/commercial-paper", response_model=CommercialPaperResult)
async def commercial_paper(body: CommercialPaperInput, current_user: User = Depends(get_current_user)):
    return service.calculate_commercial_paper(body.face_value, body.discount_rate_pct, body.days)


@router.post("/real-estate", response_model=RealEstateResult)
async def real_estate(body: RealEstateInput, current_user: User = Depends(get_current_user)):
    return service.calculate_real_estate(
        body.property_value, body.annual_rent, body.annual_expenses, body.down_payment
    )


@router.post("/compound-interest", response_model=CompoundInterestResult)
async def compound_interest(body: CompoundInterestInput, current_user: User = Depends(get_current_user)):
    return service.calculate_compound_interest(
        body.principal, body.monthly_contribution, body.annual_rate_pct, body.years
    )