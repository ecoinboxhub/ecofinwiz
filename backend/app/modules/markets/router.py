from fastapi import APIRouter, Depends, Query

from app.modules.auth.dependencies import get_current_user
from app.models import User
from app.modules.markets import service

router = APIRouter(prefix="/markets", tags=["Markets"])


@router.get("/overview")
async def markets_overview(
    current_user: User = Depends(get_current_user),
):
    return await service.get_market_data_service().get_overview()


@router.get("/indices")
async def markets_indices(
    region: str = Query(default=None, description="africa | global"),
    current_user: User = Depends(get_current_user),
):
    return await service.get_market_data_service().get_indices(region=region)


@router.get("/crypto")
async def markets_crypto(
    current_user: User = Depends(get_current_user),
):
    return await service.get_market_data_service().get_crypto()


@router.get("/commodities")
async def markets_commodities(
    current_user: User = Depends(get_current_user),
):
    return await service.get_market_data_service().get_commodities()