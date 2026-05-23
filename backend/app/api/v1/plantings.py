import uuid

from fastapi import APIRouter, HTTPException, Query, status

from app.api.deps import CurrentUser, DB
from app.schemas.common import APIResponse, paginated
from app.schemas.irrigation import IrrigationCreate, IrrigationResponse
from app.schemas.planting import PlantingCreate, PlantingResponse, PlantingUpdate
from app.services import planting as planting_service

router = APIRouter(prefix="/plantings", tags=["plantings"])


@router.get("", response_model=dict)
async def list_plantings(
    current_user: CurrentUser,
    db: DB,
    field_id: uuid.UUID | None = Query(None),
):
    plantings = await planting_service.get_user_plantings(db, current_user.id, field_id)
    data = [PlantingResponse.model_validate(p).model_dump() for p in plantings]
    return paginated(data, page=1, per_page=len(data), total=len(data))


@router.post("", status_code=status.HTTP_201_CREATED, response_model=APIResponse[PlantingResponse])
async def create_planting(data: PlantingCreate, current_user: CurrentUser, db: DB):
    planting = await planting_service.create_planting(db, current_user.id, data)
    return {"status": "success", "data": PlantingResponse.model_validate(planting)}


@router.get("/{planting_id}", response_model=APIResponse[PlantingResponse])
async def get_planting(planting_id: uuid.UUID, current_user: CurrentUser, db: DB):
    planting = await planting_service.get_planting(db, planting_id, current_user.id)
    if not planting:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ekim bulunamadı")
    return {"status": "success", "data": PlantingResponse.model_validate(planting)}


@router.put("/{planting_id}", response_model=APIResponse[PlantingResponse])
async def update_planting(
    planting_id: uuid.UUID, data: PlantingUpdate, current_user: CurrentUser, db: DB
):
    planting = await planting_service.update_planting(db, planting_id, current_user.id, data)
    if not planting:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ekim bulunamadı")
    return {"status": "success", "data": PlantingResponse.model_validate(planting)}


@router.get("/{planting_id}/irrigation", response_model=dict)
async def get_irrigation(planting_id: uuid.UUID, current_user: CurrentUser, db: DB):
    # Önce planting'in kullanıcıya ait olduğunu doğrula
    planting = await planting_service.get_planting(db, planting_id, current_user.id)
    if not planting:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ekim bulunamadı")
    logs = await planting_service.get_irrigation_logs(db, planting_id)
    data = [IrrigationResponse.model_validate(log).model_dump() for log in logs]
    return paginated(data, page=1, per_page=len(data), total=len(data))


@router.post("/{planting_id}/irrigation", status_code=status.HTTP_201_CREATED, response_model=APIResponse[IrrigationResponse])
async def add_irrigation(
    planting_id: uuid.UUID, data: IrrigationCreate, current_user: CurrentUser, db: DB
):
    planting = await planting_service.get_planting(db, planting_id, current_user.id)
    if not planting:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ekim bulunamadı")
    log = await planting_service.add_irrigation_log(db, planting_id, data)
    return {"status": "success", "data": IrrigationResponse.model_validate(log)}
