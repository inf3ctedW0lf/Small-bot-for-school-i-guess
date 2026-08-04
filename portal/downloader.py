from __future__ import annotations

import time
import shutil
from pathlib import Path

from logger import get_logger
import config

from .models import Resource
from . import selectors


logger = get_logger("Downloader")


class PortalDownloader:
    """
    Handles downloading portal resources.

    Responsible for:
        - clicking download buttons
        - waiting for files
        - organizing downloads

    Does NOT:
        - collect resources
        - send Discord messages
    """

    def __init__(
        self,
        session,
    ):

        self.session = session

        self.download_dir = Path(
            config.DOWNLOAD_DIR
        )

        self.download_dir.mkdir(
            parents=True,
            exist_ok=True
        )


    # ======================================================
    # Public API
    # ======================================================

    def download(
        self,
        resource: Resource,
    ) -> Path | None:

        logger.info(
            f"Downloading {resource.name}"
        )


        before = self._current_files()


        self._click_download(
            resource
        )


        downloaded = (
            self.session.wait_for_download(
                before
            )
        )


        if downloaded is None:

            logger.warning(
                f"Download failed: {resource.name}"
            )

            return None


        final = self._rename(
            downloaded,
            resource
        )


        resource.mark_downloaded(
            final
        )


        logger.info(
            f"Downloaded: {final.name}"
        )


        return final



    # ======================================================
    # Download interaction
    # ======================================================

    def _click_download(
        self,
        resource: Resource,
    ):

        if resource.element is None:

            raise ValueError(
                "Resource has no Selenium element"
            )


        button = resource.element.find_element(
            "xpath",
            selectors.DOWNLOAD_BUTTON
        )


        self.session.execute_script(
            """
            arguments[0].click();
            """,
            button
        )


    # ======================================================
    # File handling
    # ======================================================

    def _current_files(
        self,
    ) -> set[str]:

        return {
            file.name
            for file in self.download_dir.iterdir()
            if file.is_file()
        }


    def _rename(
        self,
        file: Path,
        resource: Resource,
    ) -> Path:


        safe_subject = (
            resource.subject
            .replace("/", "-")
        )

        safe_name = (
            resource.name
            .replace("/", "-")
        )


        filename = (
            f"{safe_subject} - "
            f"{safe_name}"
        )


        if not filename.endswith(".pdf"):

            filename += ".pdf"


        destination = (
            self.download_dir /
            filename
        )


        shutil.move(
            str(file),
            str(destination)
        )


        return destination