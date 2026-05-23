from fastapi import APIRouter, HTTPException, status

from app.api.deps import CurrentUser, DB
from app.core.security import create_access_token, create_refresh_token, decode_token
from app.schemas.auth import TokenRefresh, TokenResponse, UserLogin, UserRegister, UserResponse
from app.schemas.common import APIResponse
from app.services.auth import authenticate_user, create_user, get_user_by_email, get_user_by_id

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=APIResponse[UserResponse], status_code=status.HTTP_201_CREATED)
async def register(data: UserRegister, db: DB):
    existing = await get_user_by_email(db, data.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Bu e-posta adresi zaten kayıtlı",
        )
    user = await create_user(db, data)
    return {"status": "success", "data": UserResponse.model_validate(user)}


@router.post("/login", response_model=APIResponse[TokenResponse])
async def login(data: UserLogin, db: DB):
    user = await authenticate_user(db, data.email, data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-posta veya şifre hatalı",
        )
    access_token = create_access_token(str(user.id))
    refresh_token = create_refresh_token(str(user.id))
    return {
        "status": "success",
        "data": TokenResponse(access_token=access_token, refresh_token=refresh_token),
    }


@router.post("/refresh", response_model=APIResponse[TokenResponse])
async def refresh(data: TokenRefresh, db: DB):
    payload = decode_token(data.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Geçersiz refresh token",
        )
    import uuid
    user_id = uuid.UUID(payload["sub"])
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Kullanıcı bulunamadı")

    access_token = create_access_token(str(user.id))
    refresh_token = create_refresh_token(str(user.id))
    return {
        "status": "success",
        "data": TokenResponse(access_token=access_token, refresh_token=refresh_token),
    }


@router.post("/logout", response_model=APIResponse[None])
async def logout(current_user: CurrentUser):
    # Stateless JWT: client tarafında token silinir.
    # Gelecekte Redis blacklist eklenebilir.
    return {"status": "success", "data": None, "message": "Çıkış yapıldı"}


@router.get("/me", response_model=APIResponse[UserResponse])
async def me(current_user: CurrentUser):
    return {"status": "success", "data": UserResponse.model_validate(current_user)}
