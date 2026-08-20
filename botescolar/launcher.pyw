from __future__ import annotations

import asyncio

import config

import time

from cache import DailyCache

from discord_service import DiscordService


from jobs.resources import ResourcesJob
from jobs.tasks import TasksJob

from logger import (
    get_logger,
    startup,
    shutdown,
)

from portal import (
    PortalCollector,
    PortalDownloader,
    PortalSession,
)

from portal.portal_token import PortalToken


logger = get_logger("Launcher")


async def main():

    startup(logger)

    # ======================================================
    # Portal Token
    # ======================================================

    logger.info("Obtaining portal token...")

    token = PortalToken().get()

    if not token:

        logger.error(
            "Failed to obtain portal token."
        )

        return

    logger.info("Portal token acquired.")

    # ======================================================
    # Portal
    # ======================================================

    portal = PortalSession()

    portal.start()

    portal.preload_token(token)
    portal.open(config.PORTAL_URL)

    # Give Angular's route guard time to redirect if the token is dead —
    # checking current_url immediately after open() races the redirect.
    redirected_to_login = False
    deadline = time.time() + 8

    while time.time() < deadline:
        if "login." in portal.driver.current_url:
            redirected_to_login = True
            break
        time.sleep(0.5)

    if redirected_to_login:
        logger.warning("Saved token was invalid. Recapturing...")
        PortalToken().clear()
        token = PortalToken().get()

        if not token:
            logger.error("Failed to obtain portal token.")
            return

        portal.preload_token(token)
        portal.open(config.PORTAL_URL)

    collector = PortalCollector(portal)

    downloader = PortalDownloader(portal)

    # ======================================================
    # Discord
    # ======================================================

    discord = DiscordService()

    await discord.start()

    await discord.wait_until_ready()

    logger.info("Discord connected.")

    # ======================================================
    # Cache
    # ======================================================

    resource_cache = DailyCache(
        config.RESOURCES_CACHE
    )

    task_cache = DailyCache(
        config.TASKS_CACHE
    )

    # ======================================================
    # Jobs
    # ======================================================

    resources = ResourcesJob(
        collector,
        downloader,
        discord,
        resource_cache,
    )

    tasks = TasksJob(
        collector,
        discord,
        task_cache,
    )

    logger.info("Launcher ready.")

    # ======================================================
    # Main Loop
    # ======================================================

    try:

        while True:

            logger.info(
                "Starting scheduled check..."
            )

            try:

                await resources.run()

            except Exception:

                logger.exception(
                    "Resources job crashed."
                )

            try:

                await tasks.run()

            except Exception:

                logger.exception(
                    "Tasks job crashed."
                )

            logger.info(
                f"Sleeping for {config.CHECK_INTERVAL}s..."
            )

            await asyncio.sleep(
                config.CHECK_INTERVAL
            )

    finally:

        logger.info(
            "Stopping services..."
        )

        await discord.stop()

        portal.stop()

        shutdown(logger)


if __name__ == "__main__":

    try:

        asyncio.run(main())

    except KeyboardInterrupt:

        print("\nInterrupted by user.")