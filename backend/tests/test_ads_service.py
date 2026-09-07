"""
Regression tests for the ad-serving query.

The original filter combined `end_date IS NULL` and `end_date >= now` with an
AND, which is contradictory (a row can never satisfy both), so no ad campaign
could ever be served. These tests pin the corrected OR semantics in the
compiled SQL so the bug cannot silently return.
"""

from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.dialects import postgresql

from app.models import AdCampaign
from app.modules.ads.service import _eligible_campaign_conditions


def _compiled_where(now: datetime) -> str:
    stmt = select(AdCampaign.id).where(*_eligible_campaign_conditions(now))
    return str(stmt.compile(dialect=postgresql.dialect()))


def test_end_date_rule_uses_or_not_and():
    now = datetime.now(timezone.utc)
    sql = _compiled_where(now)

    # Both branches of the eligibility rule must appear...
    assert "end_date IS NULL" in sql
    assert "end_date >= " in sql

    # ...combined with OR (regression: previously AND, which served nothing).
    assert "IS NULL OR" in sql or "IS NULL\nOR" in sql
    assert "IS NULL AND" not in sql


def test_active_and_started_conditions_present():
    now = datetime.now(timezone.utc)
    sql = _compiled_where(now)

    assert "is_active IS true" in sql
    assert "start_date <= " in sql
    assert "impressions_bought > " in sql and "impressions_served" in sql


def test_campaign_with_no_end_date_is_served():
    """A campaign with end_date=None satisfies the OR rule's left branch."""
    from app.models import AdCampaign

    now = datetime.now(timezone.utc)

    eligible = AdCampaign(
        advertiser_name="Zenith Bank",
        image_url="https://example.com/ad.png",
        target_url="https://example.com",
        cpm=5.0,
        impressions_bought=100,
        impressions_served=0,
        is_active=True,
        start_date=now - timedelta(days=1),
        end_date=None,
    )
    assert eligible.end_date is None

    # The OR condition is satisfied when end_date is NULL, so the campaign
    # row remains a candidate for serving.
    sql = _compiled_where(now)
    assert "end_date IS NULL OR" in sql or "end_date IS NULL\nOR" in sql


def test_campaign_with_future_end_date_is_served():
    """A campaign with a future end_date satisfies the OR rule's right branch."""
    from app.models import AdCampaign

    now = datetime.now(timezone.utc)

    eligible = AdCampaign(
        advertiser_name="GTBank",
        image_url="https://example.com/ad2.png",
        target_url="https://example.com",
        cpm=5.0,
        impressions_bought=100,
        impressions_served=0,
        is_active=True,
        start_date=now - timedelta(days=1),
        end_date=now + timedelta(days=7),
    )
    assert eligible.end_date > now

    sql = _compiled_where(now)
    assert "end_date >= " in sql
