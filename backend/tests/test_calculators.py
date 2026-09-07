"""Smoke tests for the financial calculators module."""
import pytest
from pytest import approx


@pytest.mark.smoke
class TestCalculatorsList:
    def test_list_calculators(self, client):
        resp = client.get("/api/v1/calculators")
        assert resp.status_code == 200
        keys = {c["key"] for c in resp.json()["calculators"]}
        assert {"mortgage", "investment", "mutual_fund", "bond",
                "treasury_bill", "commercial_paper", "real_estate",
                "compound_interest"} <= keys


@pytest.mark.smoke
class TestMortgageCalculator:
    def test_monthly_payment(self, client):
        resp = client.post("/api/v1/calculators/mortgage", json={
            "principal": 200000, "annual_rate_pct": 5, "term_years": 30,
        })
        assert resp.status_code == 200
        data = resp.json()
        # 200k @ 5% for 30y -> ~1073.64/mo
        assert data["monthly_payment"] == approx(1073.64, abs=0.5)
        assert data["total_payment"] == approx(386511.57, abs=200)
        assert data["total_interest"] == approx(186511.57, abs=200)

    def test_invalid_input(self, client):
        resp = client.post("/api/v1/calculators/mortgage", json={
            "principal": -1, "annual_rate_pct": 5, "term_years": 30,
        })
        assert resp.status_code == 422


@pytest.mark.smoke
class TestInvestmentCalculator:
    def test_roi_and_cagr(self, client):
        resp = client.post("/api/v1/calculators/investment", json={
            "principal": 1000, "annual_rate_pct": 10, "years": 5,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["future_value"] == approx(1610.51, abs=0.01)
        assert data["roi_pct"] == approx(61.05, abs=0.01)
        assert data["cagr_pct"] == approx(10.0, abs=0.01)


@pytest.mark.smoke
class TestMutualFundCalculator:
    def test_lump_plus_sip(self, client):
        resp = client.post("/api/v1/calculators/mutual-fund", json={
            "initial_lump_sum": 10000, "monthly_contribution": 500,
            "annual_rate_pct": 12, "years": 5,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_invested"] == approx(40000, abs=0.01)
        assert data["future_value"] == approx(59001.80, abs=1.0)
        assert data["growth_amount"] == approx(19001.80, abs=1.0)


@pytest.mark.smoke
class TestBondCalculator:
    def test_yields(self, client):
        resp = client.post("/api/v1/calculators/bond", json={
            "face_value": 1000, "coupon_rate_pct": 5, "price": 950,
            "years_to_maturity": 10,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["annual_coupon"] == approx(50, abs=0.01)
        assert data["current_yield_pct"] == approx(5.26, abs=0.01)
        assert data["ytm_approx_pct"] == approx(5.64, abs=0.05)


@pytest.mark.smoke
class TestTreasuryBillCalculator:
    def test_discount_and_effective_yield(self, client):
        resp = client.post("/api/v1/calculators/treasury-bill", json={
            "face_value": 1000, "price": 970, "days": 91,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["profit"] == approx(30, abs=0.01)
        assert data["discount_yield_pct"] == approx(11.87, abs=0.05)
        assert data["effective_yield_pct"] == approx(13.00, abs=0.15)


@pytest.mark.smoke
class TestCommercialPaperCalculator:
    def test_price_and_yields(self, client):
        resp = client.post("/api/v1/calculators/commercial-paper", json={
            "face_value": 1000, "discount_rate_pct": 8, "days": 180,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["price"] == approx(960, abs=0.01)
        assert data["discount_yield_pct"] == approx(8.0, abs=0.01)
        assert data["effective_yield_pct"] == approx(8.63, abs=0.1)
        assert data["profit"] == approx(40, abs=0.01)


@pytest.mark.smoke
class TestRealEstateCalculator:
    def test_yields_and_roi(self, client):
        resp = client.post("/api/v1/calculators/real-estate", json={
            "property_value": 1000000, "annual_rent": 100000,
            "annual_expenses": 20000, "down_payment": 250000,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["gross_rental_yield_pct"] == approx(10.0, abs=0.01)
        assert data["net_rental_yield_pct"] == approx(8.0, abs=0.01)
        assert data["net_annual_income"] == approx(80000, abs=0.01)
        assert data["cash_on_cash_roi_pct"] == approx(32.0, abs=0.01)


@pytest.mark.smoke
class TestCompoundInterestCalculator:
    def test_goal_projection(self, client):
        resp = client.post("/api/v1/calculators/compound-interest", json={
            "principal": 0, "monthly_contribution": 10000,
            "annual_rate_pct": 12, "years": 10,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_contributions"] == approx(1200000, abs=0.01)
        assert data["future_value"] == approx(2300387, abs=1000)
        assert data["total_interest"] == approx(1100387, abs=1000)