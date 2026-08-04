from __future__ import annotations

from logger import get_logger

from portal.models import Resource


logger = get_logger("ResourcesJob")


class ResourcesJob:
    """
    Checks for new portal resources.

    Flow:

        Collect
          ↓
        Cache check
          ↓
        Download
          ↓
        Discord upload
          ↓
        Cache update
    """

    def __init__(
        self,
        collector,
        downloader,
        discord,
        cache,
    ):

        self.collector = collector

        self.downloader = downloader

        self.discord = discord

        self.cache = cache



    async def run(self):

        logger.info(
            "Running resource check..."
        )


        try:

            resources = (
                self.collector
                    .collect_resources()
            )


            logger.info(
                f"Found {len(resources)} resources."
            )


            for resource in resources:

                await self._process(
                    resource
                )


        except Exception:

            logger.exception(
                "Resource job failed."
            )



    async def _process(
        self,
        resource: Resource,
    ):

        cache_key = self._cache_key(
            resource
        )


        if self.cache.contains(
            cache_key
        ):

            logger.debug(
                f"Already sent: {cache_key}"
            )

            return



        logger.info(
            f"New resource: {cache_key}"
        )


        file_path = (
            self.downloader
            .download(resource)
        )


        if file_path is None:

            logger.warning(
                f"Download failed: {cache_key}"
            )

            return



        await self.discord.upload_resource(

            subject=resource.subject,

            filepath=file_path

        )


        self.cache.add(
            cache_key
        )


        logger.info(
            f"Processed resource: {cache_key}"
        )



    @staticmethod
    def _cache_key(
        resource: Resource,
    ) -> str:

        return (
            f"{resource.subject}:"
            f"{resource.name}"
        )