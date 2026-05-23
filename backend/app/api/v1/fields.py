import uuid

from fastapi import APIRouter, HTTPException, status

from app.api.deps import CurrentUser, DB
from app.schemas.common import APIResponse, paginated
from app.schemas.field import FieldCreate, FieldResponse, FieldStats, FieldUpdate
from app.services import field as field_service

router = APIRouter(prefix="/fields", tags=["fields"])


@router.get("", response_model=dict)
async def list_fields(current_user: CurrentUser, db: DB):
    fields = await field_service.get_user_fields(db, current_user.id)
    return paginated(fields, page=1, per_page=len(fields), total=len(fields))


@router.post("", status_code=status.HTTP_201_CREATED, response_model=APIResponse[FieldResponse])
async def create_field(data: FieldCreate, current_user: CurrentUser, db: DB):
    field = await field_service.create_field(db, current_user.id, data)
    return {"status": "success", "data": field}


@router.get("/{field_id}", response_model=APIResponse[FieldResponse])
async def get_field(field_id: uuid.UUID, current_user: CurrentUser, db: DB):
    field = await field_service.get_field(db, field_id, current_user.id)
    if not field:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tarla bulunamadı")
    return {"status": "success", "data": field}


@router.put("/{field_id}", response_model=APIResponse[FieldResponse])
async def update_field(field_id: uuid.UUID, data: FieldUpdate, current_user: CurrentUser, db: DB):
    field = await field_service.update_field(db, field_id, current_user.id, data)
    if not field:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tarla bulunamadı")
    return {"status": "success", "data": field}


@router.delete("/{field_id}", response_model=APIResponse[None])
async def delete_field(field_id: uuid.UUID, current_user: CurrentUser, db: DB):
    deleted = await field_service.delete_field(db, field_id, current_user.id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tarla bulunamadı")
    return {"status": "success", "data": None, "message": "Tarla silindi"}


@router.get("/{field_id}/stats", response_model=APIResponse[FieldStats])
async def field_stats(field_id: uuid.UUID, current_user: CurrentUser, db: DB):
    stats = await field_service.get_field_stats(db, field_id, current_user.id)
    if not stats:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tarla bulunamadı")
    return {"status": "success", "data": stats}
