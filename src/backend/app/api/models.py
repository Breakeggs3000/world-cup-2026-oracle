from fastapi import APIRouter

from app.services import list_available_models

router = APIRouter(prefix="/api/models", tags=["models"])


@router.get("")
def models_registry():
    """List registered model artifacts and the active model id."""
    return list_available_models()
