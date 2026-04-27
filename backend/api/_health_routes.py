from fastapi import APIRouter


router = APIRouter(tags=["health"])


@router.get("/", summary="Health check")
def get_root() -> dict[str, str]:
    return {"status": "ok"}
