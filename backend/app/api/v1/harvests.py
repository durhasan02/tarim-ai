from fastapi import APIRouter, status

from app.api.deps import CurrentUser, DB
from app.schemas.common import APIResponse, paginated
from app.schemas.harvest import HarvestCreate, HarvestResponse, SaleCreate, SaleResponse
from app.services import harvest as harvest_service

router = APIRouter(tags=["harvests"])


@router.get("/harvests", response_model=dict)
async def list_harvests(current_user: CurrentUser, db: DB):
    harvests = await harvest_service.get_user_harvests(db, current_user.id)
    data = [HarvestResponse.model_validate(h).model_dump() for h in harvests]
    return paginated(data, page=1, per_page=len(data), total=len(data))


@router.post("/harvests", status_code=status.HTTP_201_CREATED, response_model=APIResponse[HarvestResponse])
async def create_harvest(data: HarvestCreate, current_user: CurrentUser, db: DB):
    harvest = await harvest_service.create_harvest(db, current_user.id, data)
    return {"status": "success", "data": HarvestResponse.model_validate(harvest)}


@router.post("/sales", status_code=status.HTTP_201_CREATED, response_model=APIResponse[SaleResponse])
async def create_sale(data: SaleCreate, current_user: CurrentUser, db: DB):
    sale = await harvest_service.create_sale(db, current_user.id, data)
    return {"status": "success", "data": SaleResponse.model_validate(sale)}


@router.get("/sales/summary", response_model=APIResponse[dict])
async def sales_summary(current_user: CurrentUser, db: DB):
    summary = await harvest_service.get_sales_summary(db, current_user.id)
    return {"status": "success", "data": summary}
