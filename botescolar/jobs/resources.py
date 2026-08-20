from __future__ import annotations

from logger import get_logger
from portal.models import Resource


logger = get_logger("ResourcesJob")


class ResourcesJob:
    """
    Checks for new portal resources.

    Flow:

        Collect + download (sync, while browser is on that subject)
          ↓
        Discord upload (async, after browser has moved on)
          ↓
        Cache update
    """

    def __init__(self, collector, downloader, discord, cache):
        self.collector = collector
        self.downloader = downloader
        self.discord = discord
        self.cache = cache

    async def run(self):
        logger.info("Running resource check...")

        to_upload: list[tuple[Resource, object]] = []

        try:
            count = self.collector.collect_resources(
                lambda resource: self._collect(resource, to_upload)
            )
            logger.info(f"Found {count} resources.")

        except Exception:
            logger.exception("Resource job failed.")
            return

        for resource, file_path in to_upload:
            await self._upload(resource, file_path)

    def _collect(self, resource: Resource, to_upload: list):
        """
        Called SYNCHRONOUSLY by the collector, while resource.element
        is still valid (browser hasn't navigated away yet).
        """
        cache_key = self._cache_key(resource)

        if self.cache.contains(cache_key):
            logger.debug(f"Already sent: {cache_key}")
            return

        logger.info(f"New resource: {cache_key}")

        file_path = self.downloader.download(resource)

        if file_path is None:
            logger.warning(f"Download failed: {cache_key}")
            return

        to_upload.append((resource, file_path))

    async def _upload(self, resource: Resource, file_path):
        cache_key = self._cache_key(resource)

        await self.discord.upload_resource(
            subject=resource.subject,
            filepath=file_path,
        )

        self.cache.add(cache_key)

        logger.info(f"Processed resource: {cache_key}")

    @staticmethod
    def _cache_key(resource: Resource) -> str:
        return f"{resource.subject}:{resource.name}"
