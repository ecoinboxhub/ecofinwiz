"""
World market indices service — educational market overview data.

Provides a single, compact, cached payload of major African exchange indices,
global indices, cryptocurrency prices and commodity prices. Designed for
low-bandwidth clients: one GET returns everything, and responses are cached
in-memory (TTL) to avoid recomputation and reduce reliance on external APIs.

The data is indicative/educational only and is NOT investment advice.
No external API is required; a provider hook is provided for future live data.
"""

import time
from datetime import datetime, timezone
from typing import Optional

from app.shared.logger import get_logger

logger = get_logger(__name__)

DISCLAIMER = (
    "Market data is indicative and for educational purposes only. It is not "
    "investment advice and may be delayed or incomplete. Past performance does "
    "not guarantee future results. Consult a licensed investment advisor."
)

CACHE_TTL_SECONDS = 900  # 15 minutes

# fmt: off
AFRICA_INDICES = [
    # {symbol, name, country, currency, value, change, change_pct}
    {"symbol": "NGXASI", "name": "NGX All-Share Index", "country": "Nigeria", "currency": "NGN", "value": 152840.35, "change": 875.12, "change_pct": 0.58},
    {"symbol": "GSE", "name": "GSE Composite Index", "country": "Ghana", "currency": "GHS", "value": 4380.12, "change": -18.44, "change_pct": -0.42},
    {"symbol": "NSE20", "name": "NSE 20 Share Index", "country": "Kenya", "currency": "KES", "value": 2140.87, "change": 12.36, "change_pct": 0.58},
    {"symbol": "NSEASI", "name": "NSE All-Share Index", "country": "Kenya", "currency": "KES", "value": 16890.40, "change": 95.20, "change_pct": 0.57},
    {"symbol": "JSE40", "name": "FTSE/JSE Top 40", "country": "South Africa", "currency": "ZAR", "value": 78210.55, "change": -420.33, "change_pct": -0.53},
    {"symbol": "EGX30", "name": "EGX 30 Index", "country": "Egypt", "currency": "EGP", "value": 33240.12, "change": 215.60, "change_pct": 0.65},
    {"symbol": "MASI", "name": "MASI Index", "country": "Morocco", "currency": "MAD", "value": 14280.90, "change": -32.10, "change_pct": -0.22},
    {"symbol": "BRVM", "name": "BRVM Composite", "country": "Ivory Coast", "currency": "XOF", "value": 265.40, "change": 0.85, "change_pct": 0.32},
    {"symbol": "DSE", "name": "DSE All-Share Index", "country": "Tanzania", "currency": "TZS", "value": 2350.75, "change": 8.40, "change_pct": 0.36},
    {"symbol": "USE", "name": "USE All-Share Index", "country": "Uganda", "currency": "UGX", "value": 1040.25, "change": 3.15, "change_pct": 0.30},
    {"symbol": "RSE", "name": "RSE Share Index", "country": "Rwanda", "currency": "RWF", "value": 2480.60, "change": 12.20, "change_pct": 0.49},
    {"symbol": "SEMDEX", "name": "SEMDEX Index", "country": "Mauritius", "currency": "MUR", "value": 2250.85, "change": -5.60, "change_pct": -0.25},
    {"symbol": "BSE", "name": "BSE Domestic Index", "country": "Botswana", "currency": "BWP", "value": 12580.30, "change": 45.20, "change_pct": 0.36},
    {"symbol": "ZSE", "name": "ZSE All-Share Index", "country": "Zimbabwe", "currency": "ZWL", "value": 1840.55, "change": -22.35, "change_pct": -1.20},
    {"symbol": "TUNINDEX", "name": "TUNINDEX", "country": "Tunisia", "currency": "TND", "value": 9850.45, "change": 10.80, "change_pct": 0.11},
    {"symbol": "ALSI", "name": "JSE All-Share Index", "country": "South Africa", "currency": "ZAR", "value": 86120.90, "change": -380.40, "change_pct": -0.44},
]

GLOBAL_INDICES = [
    {"symbol": "SPX", "name": "S&P 500", "country": "United States", "currency": "USD", "value": 6254.30, "change": 18.20, "change_pct": 0.29},
    {"symbol": "IXIC", "name": "NASDAQ Composite", "country": "United States", "currency": "USD", "value": 20850.55, "change": 95.40, "change_pct": 0.46},
    {"symbol": "DJI", "name": "Dow Jones Industrial", "country": "United States", "currency": "USD", "value": 44520.85, "change": -62.10, "change_pct": -0.14},
    {"symbol": "FTSE", "name": "FTSE 100", "country": "United Kingdom", "currency": "GBP", "value": 8920.45, "change": 12.35, "change_pct": 0.14},
    {"symbol": "N225", "name": "Nikkei 225", "country": "Japan", "currency": "JPY", "value": 42250.60, "change": -210.50, "change_pct": -0.50},
    {"symbol": "HSI", "name": "Hang Seng Index", "country": "Hong Kong (China)", "currency": "HKD", "value": 24980.35, "change": 88.20, "change_pct": 0.35},
    {"symbol": "SSE", "name": "Shanghai Composite", "country": "China", "currency": "CNY", "value": 3820.15, "change": -12.40, "change_pct": -0.32},
    {"symbol": "SENSEX", "name": "S&P BSE Sensex", "country": "India", "currency": "INR", "value": 85540.25, "change": 215.60, "change_pct": 0.25},
    {"symbol": "DAX", "name": "DAX 40", "country": "Germany", "currency": "EUR", "value": 22540.80, "change": 45.20, "change_pct": 0.20},
    {"symbol": "CAC", "name": "CAC 40", "country": "France", "currency": "EUR", "value": 7860.55, "change": -15.30, "change_pct": -0.19},
]

CRYPTO_TICKERS = [
    {"symbol": "BTC", "name": "Bitcoin", "value": 104500.20, "change": 1420.50, "change_pct": 1.38},
    {"symbol": "ETH", "name": "Ethereum", "value": 3980.75, "change": 52.30, "change_pct": 1.33},
    {"symbol": "SOL", "name": "Solana", "value": 228.40, "change": 4.10, "change_pct": 1.83},
    {"symbol": "BNB", "name": "BNB", "value": 742.15, "change": 6.80, "change_pct": 0.92},
    {"symbol": "XRP", "name": "XRP", "value": 2.86, "change": 0.04, "change_pct": 1.42},
    {"symbol": "DOGE", "name": "Dogecoin", "value": 0.42, "change": 0.01, "change_pct": 2.44},
    {"symbol": "ADA", "name": "Cardano", "value": 1.18, "change": 0.02, "change_pct": 1.72},
]

COMMODITIES = [
    {"symbol": "XAU", "name": "Gold", "unit": "USD/troy oz", "value": 3385.40, "change": 12.60, "change_pct": 0.37},
    {"symbol": "XAG", "name": "Silver", "unit": "USD/troy oz", "value": 41.85, "change": 0.35, "change_pct": 0.84},
    {"symbol": "BRENT", "name": "Brent Crude Oil", "unit": "USD/bbl", "value": 82.40, "change": -0.60, "change_pct": -0.72},
    {"symbol": "WTI", "name": "WTI Crude Oil", "unit": "USD/bbl", "value": 78.65, "change": -0.45, "change_pct": -0.57},
    {"symbol": "NG", "name": "Natural Gas", "unit": "USD/MMBtu", "value": 3.42, "change": 0.08, "change_pct": 2.40},
    {"symbol": "COPPER", "name": "Copper", "unit": "USD/lb", "value": 4.85, "change": 0.04, "change_pct": 0.83},
    {"symbol": "COCOA", "name": "Cocoa", "unit": "USD/tonne", "value": 10480.00, "change": 220.00, "change_pct": 2.14},
]
# fmt: on


class MarketDataService:
    """Provides cached market overview data with an optional live provider hook."""

    def __init__(self):
        self._cache: dict[str, tuple[float, dict]] = {}
        self.provider: Optional[object] = None

    def _get_cached(self, key: str) -> Optional[dict]:
        entry = self._cache.get(key)
        if not entry:
            return None
        cached_at, payload = entry
        if time.time() - cached_at > CACHE_TTL_SECONDS:
            self._cache.pop(key, None)
            return None
        return payload

    def _set_cached(self, key: str, payload: dict):
        self._cache[key] = (time.time(), payload)

    async def _fetch_from_provider(self) -> Optional[dict]:
        """Optional live data provider. Returns None when not configured."""
        if not self.provider:
            return None
        try:
            return await self.provider.fetch_markets()
        except Exception as e:  # noqa: BLE001
            logger.warning("Market data provider failed: %s", e)
            return None

    def _static_overview(self) -> dict:
        return {
            "regions": [
                {"region": "africa", "name": "African Exchanges", "indices": AFRICA_INDICES},
                {"region": "global", "name": "Global Markets", "indices": GLOBAL_INDICES},
            ],
            "crypto": CRYPTO_TICKERS,
            "commodities": COMMODITIES,
        }

    async def get_overview(self, force_refresh: bool = False) -> dict:
        key = "markets:overview"
        if not force_refresh:
            cached = self._get_cached(key)
            if cached:
                return cached

        provider_payload = await self._fetch_from_provider()
        payload = provider_payload if provider_payload else self._static_overview()
        result = {
            "as_of": datetime.now(timezone.utc).isoformat(),
            "disclaimer": DISCLAIMER,
            **payload,
        }
        self._set_cached(key, result)
        return result

    async def get_indices(self, region: Optional[str] = None) -> dict:
        overview = await self.get_overview()
        regions = overview["regions"]
        if region:
            regions = [r for r in regions if r["region"] == region]
        return {
            "as_of": overview["as_of"],
            "disclaimer": overview["disclaimer"],
            "regions": regions,
        }

    async def get_crypto(self) -> dict:
        overview = await self.get_overview()
        return {
            "as_of": overview["as_of"],
            "disclaimer": overview["disclaimer"],
            "crypto": overview["crypto"],
        }

    async def get_commodities(self) -> dict:
        overview = await self.get_overview()
        return {
            "as_of": overview["as_of"],
            "disclaimer": overview["disclaimer"],
            "commodities": overview["commodities"],
        }


_market_data_service: Optional[MarketDataService] = None


def get_market_data_service() -> MarketDataService:
    global _market_data_service
    if _market_data_service is None:
        _market_data_service = MarketDataService()
    return _market_data_service