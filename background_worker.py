import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from services.sync_changes_services import SyncService

logger = logging.getLogger(__name__)


class SyncWorker:
    def __init__(self, interval: int = 5):
        self.interval = interval
        self._running = False
        self._task: asyncio.Task | None = None
        self._lock = asyncio.Lock()
        self.sync_service = SyncService()

    async def start(self):
        if self._running:
            return

        self._running = True
        self._task = asyncio.create_task(self._run())
        logger.info("SyncWorker started")

    async def stop(self):
        self._running = False
        if self._task:
            await self._task
        logger.info("SyncWorker stopped")

    async def _run(self):
        while self._running:
            try:
                await self._tick()
            except Exception as e:
                logger.exception(f"Worker error: {e}")
            await asyncio.sleep(self.interval)

    async def _tick(self):
        if self._lock.locked():
            logger.warning("Previous sync still running, skipping this cycle")
            return

        async with self._lock:
            await self._do_sync()

    async def _do_sync(self):
        from models.local.changes_model import Changes

        user_ids = await Changes.filter(used=False).distinct().values_list("user_id", flat=True)
        for user_id in user_ids:
            try:
                cloud_user_id = user_id  # adjust if needed
                stats = await self.sync_service.sync(user_id, cloud_user_id)
                logger.info(
                    f"[SYNC] user={user_id} success={stats['success']} failed={stats['failed']}")
            except Exception as e:
                logger.error(f"[SYNC ERROR] user={user_id}: {e}")
