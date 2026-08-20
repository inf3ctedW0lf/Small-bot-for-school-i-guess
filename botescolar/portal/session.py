from __future__ import annotations

from pathlib import Path
from typing import Optional

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.remote.webelement import WebElement

import config
from logger import get_logger
import json

from . import utils

logger = get_logger("PortalSession")


class PortalSession:
    """
    Owns the Selenium browser session.

    Responsibilities
    ----------------
    • Create Chrome
    • Restart Chrome
    • Shutdown Chrome
    • Navigate
    • Safe browser interaction
    • Driver recovery

    It intentionally knows NOTHING about:
        - Subjects
        - Resources
        - Tasks
        - Discord
    """

    def __init__(self):

        self.driver: Optional[webdriver.Chrome] = None

        self.current_url: str = config.PORTAL_URL

        self.started = False

    def set_token(self, token: str):

        self.ensure_alive()

        logger.info("Injecting portal token...")

        self.execute_script(
            """
            localStorage.setItem(
                'portal-token',
                arguments[0]
            );
            """,
            token
        )

        logger.info("Token injected. Refreshing...")

        self.refresh()

    def preload_token(self, token: str):
        """
        Seeds localStorage with the token BEFORE the page's own
        JS runs, avoiding the route-guard redirect race.
        Must be called before self.open(...).
        """
        self.ensure_alive()

        script = (
            "window.localStorage.setItem"
            f"('portal-token', {json.dumps(token)});"
        )

        self.driver.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument",
            {"source": script}
        )

        logger.info("Token preload script registered.")

    # =====================================================
    # Lifecycle
    # =====================================================

    def start(self):

        if self.started:
            return

        logger.info("Starting Chrome...")

        self.driver = self._create_driver()

        self.started = True

    def stop(self):

        if self.driver:

            logger.info("Closing Chrome...")

            try:
                self.driver.quit()

            except Exception:
                pass

        self.driver = None
        self.started = False

    def restart(self):

        logger.warning("Restarting Chrome...")

        self.stop()

        self.start()

        self.open(self.current_url)

    # =====================================================
    # Driver
    # =====================================================

    def _create_driver(self) -> webdriver.Chrome:

        options = Options()

        # Prevent Chrome background throttling
        options.add_argument(
            "--disable-background-timer-throttling"
        )

        options.add_argument("--start-maximized")

        options.add_argument(
            "--disable-backgrounding-occluded-windows"
        )

        options.add_argument(
            "--disable-renderer-backgrounding"
        )

        options.add_argument(
            "--disable-features=CalculateNativeWinOcclusion"
        )

        options.add_argument(
            f"--user-agent={config.CHROME_USER_AGENT}"
        )

        options.add_experimental_option(
            "prefs",
            config.CHROME_PREFS,
        )

        options.add_argument(
            f"--window-size={config.CHROME_WINDOW_SIZE[0]},"
            f"{config.CHROME_WINDOW_SIZE[1]}"
        )

        options.add_argument("--new-window")

        options.add_argument(
            "--disable-extensions"
        )

        options.add_argument(
            "--no-first-run"
        )

        options.add_argument(
            "--no-default-browser-check"
        )
        service = Service()
        driver = webdriver.Chrome(
            service=service,
            options=options,
        )

        driver.set_page_load_timeout(60)

        return driver

    # =====================================================
    # Recovery
    # =====================================================

    def ensure_alive(self):

        if self.driver is None:

            self.start()
            return

        if not utils.driver_alive(self.driver):

            logger.warning("Driver died.")

            self.restart()

    # =====================================================
    # Navigation
    # =====================================================

    def open(self, url: str):

        self.ensure_alive()

        self.current_url = url

        logger.info(f"Opening {url}")

        self.driver.get(url)

    def refresh(self):

        self.ensure_alive()

        self.driver.refresh()

    def back(self):

        self.ensure_alive()

        self.driver.back()

    # =====================================================
    # Browser wrappers
    # =====================================================

    

    def wait(self, xpath: str, timeout: int = 30):

        self.ensure_alive()

        return utils.wait_present(
            self.driver,
            xpath,
            timeout,
        )
    
    

    def click(self, xpath: str, timeout: int = 30):

        self.ensure_alive()

        return utils.wait_and_click(
            self.driver,
            xpath,
            timeout,
        )

    def find(self, xpath: str):

        self.ensure_alive()

        return utils.safe_find(
            self.driver,
            xpath,
        )
    
    def find_all(
        self,
        xpath: str,
        parent: WebElement | None = None,
    ):

        self.ensure_alive()

        if parent:
            return parent.find_elements(
                "xpath",
                xpath
            )

        return self.driver.find_elements(
            "xpath",
            xpath
        )

    def execute_script(self, script: str, *args):

        self.ensure_alive()

        return self.driver.execute_script(
            script,
            *args,
        )

    def focus(self):

        self.ensure_alive()

        utils.inject_focus(self.driver)

    # =====================================================
    # Downloads
    # =====================================================

    def wait_for_download(
        self,
        previous_files: set[str],
        timeout: int = 60,
    ):

        return utils.wait_for_download(
            Path(config.DOWNLOAD_DIR),
            previous_files,
            timeout,
        )   

    # =====================================================
    # Context Manager
    # =====================================================

    def __enter__(self):

        self.start()

        return self

    def __exit__(self, exc_type, exc, tb):

        self.stop()

    
    def validate_token(self):

        return self.execute_script(
            """
            return localStorage.getItem(
                'portal-token'
            ) !== null;
            """
    )