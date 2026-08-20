from __future__ import annotations

import time
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from logger import get_logger

import config


logger = get_logger("PortalToken")


class PortalToken:


    def __init__(self):

        self.file = Path(
            "data/portal_token.txt"
        )

        self.file.parent.mkdir(
            exist_ok=True
        )


    # =========================
    # Public
    # =========================

    def get(self):

        token = self.load()

        if token:

            logger.info(
                "Using saved portal token."
            )

            return token


        logger.info(
            "No saved token. Starting capture."
        )


        token = self.capture()


        if token:

            self.save(
                token
            )


        return token



    # =========================
    # Storage
    # =========================

    def load(self):

        if not self.file.exists():
            return None


        token = self.file.read_text(
            encoding="utf-8"
        ).strip()


        if not token:
            return None


        return token



    def save(
        self,
        token
    ):

        self.file.write_text(
            token,
            encoding="utf-8"
        )

        logger.info(
            "Token saved."
        )

        # portal_token.py, in the Storage section

    def clear(self):
        if self.file.exists():
            self.file.unlink()
        logger.info("Saved token cleared.")



        # =========================
        # Browser capture
        # =========================

    def capture(self):

        options = Options()

        options.add_argument(
            "--start-maximized"
        )


        driver = webdriver.Chrome(
            options=options
        )


        try:

            driver.get(
                config.PORTAL_URL
            )


            print(
                "\nLogin to the portal."
            )

            print(
                "Waiting for token..."
            )


            timeout = 120

            start = time.time()


            while time.time() - start < timeout:


                token = driver.execute_script(
                    """
                    return localStorage.getItem(
                        'portal-token'
                    );
                    """
                )


                if token:

                    logger.info(
                        "Token captured."
                    )

                    return token



                time.sleep(2)


            logger.error(
                "Token capture timeout."
            )

            return None


        finally:

            driver.quit()