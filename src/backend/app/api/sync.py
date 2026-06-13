from fastapi import APIRouter, Header, HTTPException

from app.sync.service import run_sync, sync_status

router = APIRouter(prefix="/sync", tags=["sync"])


@router.get("/status")
def get_sync_status():
    return sync_status()


@router.post("/run")
def trigger_sync(x_sync_secret: str | None = Header(default=None, alias="X-Sync-Secret")):
    import os

    secret = os.environ.get("SYNC_SECRET")
    if secret and x_sync_secret != secret:
        raise HTTPException(status_code=403, detail="Invalid sync secret")
    return run_sync()
