"""Smoke tests for the world market indices module."""
import pytest


@pytest.mark.smoke
class TestMarketsOverview:
    def test_overview_shape(self, client):
        resp = client.get("/api/v1/markets/overview")
        assert resp.status_code == 200
        data = resp.json()
        assert "as_of" in data
        assert "disclaimer" in data
        assert "regions" in data
        assert "crypto" in data
        assert "commodities" in data

    def test_africa_region_includes_core_exchanges(self, client):
        resp = client.get("/api/v1/markets/overview")
        data = resp.json()
        regions = {r["region"]: r for r in data["regions"]}
        assert "africa" in regions
        symbols = {i["symbol"] for i in regions["africa"]["indices"]}
        assert {"NGXASI", "GSE", "NSE20", "JSE40", "EGX30"} <= symbols

    def test_global_region_includes_us_uk_japan_china(self, client):
        resp = client.get("/api/v1/markets/overview")
        data = resp.json()
        regions = {r["region"]: r for r in data["regions"]}
        assert "global" in regions
        countries = {i["country"] for i in regions["global"]["indices"]}
        assert {"United States", "United Kingdom", "Japan", "China"} <= countries

    def test_crypto_and_commodities_present(self, client):
        resp = client.get("/api/v1/markets/overview")
        data = resp.json()
        assert "BTC" in {c["symbol"] for c in data["crypto"]}
        assert "ETH" in {c["symbol"] for c in data["crypto"]}
        commodity_symbols = {c["symbol"] for c in data["commodities"]}
        assert {"XAU", "BRENT", "WTI"} <= commodity_symbols

    def test_disclaimer_present(self, client):
        resp = client.get("/api/v1/markets/overview")
        data = resp.json()
        assert "not investment advice" in data["disclaimer"].lower()

    def test_cached_serves_same_as_of(self, client):
        first = client.get("/api/v1/markets/overview").json()
        second = client.get("/api/v1/markets/overview").json()
        assert first["as_of"] == second["as_of"]


@pytest.mark.smoke
class TestMarketsFiltering:
    def test_indices_africa(self, client):
        resp = client.get("/api/v1/markets/indices", params={"region": "africa"})
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["regions"]) == 1
        assert data["regions"][0]["region"] == "africa"

    def test_indices_global(self, client):
        resp = client.get("/api/v1/markets/indices", params={"region": "global"})
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["regions"]) == 1
        assert data["regions"][0]["region"] == "global"

    def test_indices_no_region_returns_all(self, client):
        resp = client.get("/api/v1/markets/indices")
        assert resp.status_code == 200
        assert len(resp.json()["regions"]) == 2

    def test_indices_invalid_region_returns_empty(self, client):
        resp = client.get("/api/v1/markets/indices", params={"region": "mars"})
        assert resp.status_code == 200
        assert resp.json()["regions"] == []


@pytest.mark.smoke
class TestMarketsCryptoAndCommodities:
    def test_crypto_endpoint(self, client):
        resp = client.get("/api/v1/markets/crypto")
        assert resp.status_code == 200
        assert len(resp.json()["crypto"]) > 0

    def test_commodities_endpoint(self, client):
        resp = client.get("/api/v1/markets/commodities")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["commodities"]) > 0
        assert all("unit" in c for c in data["commodities"])