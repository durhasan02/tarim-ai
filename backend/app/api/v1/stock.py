import uuid

from fastapi import APIRouter, HTTPException, status

from app.api.deps import CurrentUser, DB
from app.schemas.common import APIResponse, paginated
from app.schemas.stock import StockItemCreate, StockItemResponse, StockItemUpdate, StockMoveCreate
from app.services import stock as stock_service

router = APIRouter(prefix="/stock", tags=["stock"])


@router.get("", response_model=dict)
async def list_stock(current_user: CurrentUser, db: DB):
    items = await stock_service.get_user_stock(db, current_user.id)
    return paginated(items, page=1, per_page=len(items), total=len(items))


@router.post("", status_code=status.HTTP_201_CREATED, response_model=APIResponse[StockItemResponse])
async def create_stock(data: StockItemCreate, current_user: CurrentUser, db: DB):
    item = await stock_service.create_stock_item(db, current_user.id, data)
    return {"status": "success", "data": item}


@router.put("/{item_id}", response_model=APIResponse[StockItemResponse])
async def update_stock(item_id: uuid.UUID, data: StockItemUpdate, current_user: CurrentUser, db: DB):
    item = await stock_service.update_stock_item(db, item_id, current_user.id, data)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stok kalemi bulunamadı")
    return {"status": "success", "data": item}


@router.post("/{item_id}/move", response_model=APIResponse[StockItemResponse])
async def move_stock(item_id: uuid.UUID, data: StockMoveCreate, current_user: CurrentUser, db: DB):
    item = await stock_service.move_stock(db, item_id, current_user.id, data)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stok kalemi bulunamadı")
    return {"status": "success", "data": item}


@router.get("/alerts", response_model=dict)
async def stock_alerts(current_user: CurrentUser, db: DB):
    items = await stock_service.get_critical_stock(db, current_user.id)
    return paginated(items, page=1, per_page=len(items), total=len(items))
