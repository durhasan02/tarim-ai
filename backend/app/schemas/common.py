from typing import Any, Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    status: str = "success"
    data: T | None = None
    message: str | None = None


class PaginatedResponse(BaseModel, Generic[T]):
    status: str = "success"
    data: list[T]
    message: str | None = None
    pagination: dict[str, Any]


def paginated(data: list, page: int, per_page: int, total: int) -> dict:
    return {
        "status": "success",
        "data": data,
        "message": None,
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
        },
    }
