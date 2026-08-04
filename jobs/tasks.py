from __future__ import annotations

from logger import get_logger
from portal.models import Task

logger = get_logger("TasksJob")


class TasksJob:

    def __init__(
        self,
        collector,
        discord,
        cache,
    ):

        self.collector = collector
        self.discord = discord
        self.cache = cache

    async def run(self):

        logger.info("Running task check...")

        try:

            tasks = self.collector.collect_tasks()

            logger.info(
                f"Found {len(tasks)} tasks."
            )

            for task in tasks:

                await self._process(task)

        except Exception:

            logger.exception(
                "Task job failed."
            )

    async def _process(
        self,
        task: Task,
    ):

        cache_key = self._cache_key(task)

        if self.cache.contains(cache_key):

            logger.debug(
                f"Already sent: {cache_key}"
            )

            return

        logger.info(
            f"New task: {cache_key}"
        )

        await self.discord.post_task(
            subject=task.subject,
            content=task.content,
        )

        self.cache.add(cache_key)

        logger.info(
            f"Processed task: {cache_key}"
        )

    @staticmethod
    def _cache_key(
        task: Task,
    ) -> str:

        return (
            f"{task.subject}:"
            f"{task.content}"
        )