import asyncio

import config

from portal import (
    PortalSession,
    PortalCollector,
    PortalDownloader,
)

from portal.portal_token import PortalToken

from jobs.resources import ResourcesJob

from discord_service import DiscordService

from cache import DailyCache


async def main():

    # ==========================
    # Get token
    # ==========================

    token_provider = PortalToken()

    token_provider = PortalToken()

    token = token_provider.get()

    if not token:
        print("No token received.")
        return


    # ==========================
    # Portal
    # ==========================

    portal = PortalSession()

    portal.start()

    portal.open(
        config.PORTAL_URL
    )


    portal.set_token(
        token
    )


    # ==========================
    # Services
    # ==========================

    collector = PortalCollector(
        portal
    )


    downloader = PortalDownloader(
        portal
    )


    discord = DiscordService()


    resource_cache = DailyCache(
        "data/resources_cache.txt"
    )


    # ==========================
    # Job
    # ==========================

    job = ResourcesJob(
        collector=collector,
        downloader=downloader,
        discord=discord,
        cache=resource_cache,
    )


    try:

        await job.run()


    finally:

        portal.stop()



if __name__ == "__main__":

    try:

        asyncio.run(main())


    except Exception as e:

        print("\nERROR:")
        print(e)


    finally:

        input(
            "\nPress ENTER to close..."
        )