import os

import pytest


@pytest.fixture(scope="session", autouse=True)
def _disable_sync_scheduler():
    os.environ["DISABLE_SYNC_SCHEDULER"] = "1"
