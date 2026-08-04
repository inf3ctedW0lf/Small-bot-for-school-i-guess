from __future__ import annotations

import asyncio
from datetime import datetime
from pathlib import Path
from typing import Optional

import discord

import config
from logger import get_logger

logger = get_logger("Discord")


class DiscordService:
    """
    Handles every interaction with Discord.

    Responsibilities:
        - Connect to Discord
        - Cache channels
        - Cache forum threads
        - Upload resources
        - Post tasks
        - Send notifications

    Other modules should NEVER interact with discord.py directly.
    """

    def __init__(self):

        intents = discord.Intents.default()
        intents.guilds = True
        intents.messages = True

        self.client = discord.Client(intents=intents)

        self.ready_event = asyncio.Event()

        self.files_channel = None
        self.forum_channel = None

        self.thread_cache: dict[str, discord.Thread] = {}

        self._register_events()

    # ============================================================
    # Discord Events
    # ============================================================

    def _register_events(self):

        @self.client.event
        async def on_ready():

            logger.info(
                f"Connected as {self.client.user}"
            )

            await self._cache_channels()

            await self._cache_threads()

            self.ready_event.set()

    # ============================================================
    # Startup / Shutdown
    # ============================================================

    async def start(self):

        logger.info("Connecting to Discord...")

        asyncio.create_task(
            self.client.start(config.DISCORD_TOKEN)
        )

    async def stop(self):

        logger.info("Disconnecting from Discord...")

        await self.client.close()

    async def wait_until_ready(self):

        await self.ready_event.wait()

    # ============================================================
    # Channel Cache
    # ============================================================

    async def _cache_channels(self):

        logger.info("Caching Discord channels...")

        self.files_channel = await self.client.fetch_channel(
            config.FILES_CHANNEL_ID
        )

        self.forum_channel = await self.client.fetch_channel(
            config.FORUM_CHANNEL_ID
        )

    # ============================================================
    # Thread Cache
    # ============================================================

    async def _cache_threads(self):

        logger.info("Caching forum threads...")

        self.thread_cache.clear()

        # Active threads
        for thread in self.forum_channel.threads:
            self.thread_cache[
                thread.name.lower()
            ] = thread

        # Archived threads
        async for thread in self.forum_channel.archived_threads(limit=None):

            self.thread_cache[
                thread.name.lower()
            ] = thread

        logger.info(
            f"Cached {len(self.thread_cache)} threads."
        )

    # ============================================================
    # Helpers
    # ============================================================

    def _find_thread(
        self,
        subject: str
    ) -> Optional[discord.Thread]:

        subject = subject.lower()

        for name, thread in self.thread_cache.items():

            if subject in name:
                return thread

        return None

    @staticmethod
    def _today():

        return datetime.now().strftime("%d/%m/%Y")

    # ============================================================
    # Resource Uploads
    # ============================================================

    async def upload_resource(

        self,

        subject: str,

        filepath: str | Path,

        mention: int | None = config.DEFAULT_MENTION

    ):

        filepath = Path(filepath)

        if not filepath.exists():

            logger.warning(
                f"File not found: {filepath}"
            )

            return

        size = filepath.stat().st_size

        if size > config.MAX_DISCORD_FILE_SIZE:

            await self.files_channel.send(

                content=(
                    f"📚 **{subject}** — {self._today()}\n\n"
                    f"⚠ File **{filepath.name}** exceeds "
                    "Discord's upload limit."
                )

            )

            return

        message = f"📚 **{subject}** — {self._today()}"

        if mention is not None:
            message += f" <@{mention}>"

        await self.files_channel.send(

            content=message,

            file=discord.File(filepath)

        )

        logger.info(
            f"Uploaded '{filepath.name}'"
        )

    # ============================================================
    # Tasks
    # ============================================================

    async def post_task(

        self,

        subject: str,

        content: str,

        ping_everyone: bool = True

    ):

        thread = self._find_thread(subject)

        if thread is None:

            logger.warning(
                f"No thread found for '{subject}'"
            )

            return

        message = f"📅 {self._today()}\n"

        if ping_everyone:
            message += "@everyone\n\n"

        message += content

        await thread.send(message)

        logger.info(
            f"Posted task to '{thread.name}'"
        )

    # ============================================================
    # Notifications
    # ============================================================

    async def notify(

        self,

        message: str

    ):

        channel = await self.client.fetch_channel(
            config.NOTIFY_CHANNEL_ID
        )

        await channel.send(message)

    # ============================================================
    # Utilities
    # ============================================================

    async def refresh_threads(self):

        """
        Refreshes the thread cache.

        Useful if new forum threads are created while
        the bot is running.
        """

        logger.info(
            "Refreshing thread cache..."
        )

        await self._cache_threads()

    def is_ready(self):

        return self.ready_event.is_set()