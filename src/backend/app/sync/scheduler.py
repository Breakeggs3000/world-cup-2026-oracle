"""Background sync scheduler."""

from __future__ import annotations

import logging
import os

from app.sync.service import run_sync

logger = logging.getLogger("uvicorn.error")
_scheduler = None


def start_sync_scheduler() -> None:
    global _scheduler
    if os.environ.get("DISABLE_SYNC_SCHEDULER", "0") in ("1", "true", "yes"):
        logger.info("Sync scheduler disabled.")
        return
    if _scheduler is not None:
        return
    try:
        from apscheduler.schedulers.background import BackgroundScheduler
    except ImportError:
        logger.warning("APScheduler not installed; periodic sync disabled.")
        return

    minutes = int(os.environ.get("SYNC_INTERVAL_MINUTES", "10"))
    _scheduler = BackgroundScheduler()
    _scheduler.add_job(run_sync, "interval", minutes=minutes, id="fixture_sync", replace_existing=True)
    _scheduler.start()
    logger.info("Fixture sync scheduler started (every %s min).", minutes)


def stop_sync_scheduler() -> None:
    global _scheduler
    if _scheduler is not None:
        _scheduler.shutdown(wait=False)
        _scheduler = None
