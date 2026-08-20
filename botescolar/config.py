# config.py

from pathlib import Path
import os

# ==========================================================
# PROJECT PATHS
# ==========================================================

ROOT_DIR = Path(__file__).resolve().parent

DATA_DIR = ROOT_DIR / "data"
LOG_DIR = ROOT_DIR / "logs"
DOWNLOAD_DIR = ROOT_DIR / "downloads"

DATA_DIR.mkdir(exist_ok=True)
LOG_DIR.mkdir(exist_ok=True)
DOWNLOAD_DIR.mkdir(exist_ok=True)

# ==========================================================
# DISCORD
# ==========================================================

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "MTQ3ODQ5MjU4ODU3MDA1MDY2Mg.G8gg1T.-BChyBqF-WyMdQ1PjSHHG7VcYrE_bRwzZOGXgY")

FILES_CHANNEL_ID = 1481373708957516037
FORUM_CHANNEL_ID = 1478491666292805835
NOTIFY_CHANNEL_ID = 1514356306641813664

MAX_DISCORD_FILE_SIZE = 25 * 1024 * 1024

# ==========================================================
# PORTAL
# ==========================================================

PORTAL_URL = "https://portal.educacaoadventista.org.br/"

TOKEN_STORAGE_KEY = "portal-token"

TOKEN_KEY = "portal-token"

# ==========================================================
# BOT
# ==========================================================

CHECK_INTERVAL = 180  # 3 minutes; raise/lower as you like

SKIP_WEEKENDS = True

# ==========================================================
# SENT CACHE
# ==========================================================

RESOURCES_CACHE = DATA_DIR / "sent_files.txt"
TASKS_CACHE = DATA_DIR / "sent_tasks.txt"

# ==========================================================
# LOGGING
# ==========================================================

MAIN_LOG = LOG_DIR / "bot.log"

RESOURCE_LOG = LOG_DIR / "resources.log"

TASK_LOG = LOG_DIR / "tasks.log"

# ==========================================================
# CHROME
# ==========================================================

CHROME_WINDOW_SIZE = (1920, 1080)

CHROME_USER_AGENT = (
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)

CHROME_ARGUMENTS = [
    "--headless=new",
    "--disable-gpu",
    "--disable-dev-shm-usage",
    "--no-sandbox",
    "--disable-background-timer-throttling",
    "--disable-backgrounding-occluded-windows",
    "--disable-renderer-backgrounding",
    "--disable-features=TranslateUI",
    "--disable-ipc-flooding-protection",
]

CHROME_PREFS = {
    "download.default_directory": str(DOWNLOAD_DIR),
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "plugins.always_open_pdf_externally": True,
    "download.open_pdf_in_system_reader": False,
    "safebrowsing.enabled": True,
}

# ==========================================================
# MENTIONS
# ==========================================================

DEFAULT_MENTION = 646712305786159125

EVERYONE = "@everyone"

# ==========================================================
# DEBUG
# ==========================================================

DEBUG = True

VERBOSE = True