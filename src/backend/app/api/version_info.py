from fastapi import APIRouter

from app.services import get_version_info

router = APIRouter(prefix="/version", tags=["version"])


@router.get("")
def api_version():
    """API and active model version metadata."""
    return get_version_info()
