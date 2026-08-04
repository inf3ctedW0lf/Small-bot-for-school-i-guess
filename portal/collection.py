from __future__ import annotations

from typing import Iterator

import config

from logger import get_logger

from .models import (
    Subject,
    Resource,
    Task,
)

from . import selectors


logger = get_logger("Collector")


class PortalCollector:
    """
    Handles extracting information from the portal.

    Does not:
        - control Chrome
        - download files
        - send Discord messages

    It only collects data.
    """

    def __init__(self, session):

        self.session = session

        self.current_subject: str | None = None


    # ======================================================
    # Navigation
    # ======================================================

    def open_dashboard(self):

        logger.info(
            "Opening dashboard..."
        )

        self.session.open(
            config.PORTAL_URL
        )

        self.session.focus()


    def open_today(self):
        """
        Opens today's subject list.
        """

        logger.info(
            "Opening today's classes..."
        )


        # Check if modal is already available

        try:

            self.session.wait(
                selectors.SUBJECT_MODAL,
                timeout=5
            )

            logger.info(
                "Today's module already open."
            )

            return


        except     Exception:

            pass



        logger.info(
            "Clicking today's module..."
        )


        self.session.click(
            selectors.DAY_BLOCK,
            timeout=60
        )


        self.session.wait(
            selectors.SUBJECT_MODAL,
            timeout=90
        )


        logger.info(
            "Today's module opened."
        )


    # ======================================================
    # Subjects
    # ======================================================

    # ======================================================
# Subjects
# ======================================================

    def get_subjects(
        self,
    ) -> list[Subject]:

        """
        Finds available subjects.
        """

        logger.info(
            "Collecting subjects..."
        )


        modal = self.session.wait(
            selectors.SUBJECT_MODAL
        )


        links = self.session.find_all(
            selectors.SUBJECT_LINKS,
            parent=modal
        )


        subjects = []


        for link in links:

            name = " ".join(
                link.text.split()
            )


            if not name:
                continue


            subjects.append(
                Subject(
                    name=name
                )
            )


        logger.info(
            f"Found {len(subjects)} subjects."
        )


        return subjects



    def open_subject(
        self,
        subject: Subject
    ):

        logger.info(
            f"Opening {subject.name}"
        )


        xpath = (
            "//app-day-subject-summary"
            f"//span[normalize-space()='{subject.name}']"
            "/ancestor::app-day-subject-summary"
            "//div[contains(@class,'cursor-pointer')]"
        )


        self.session.click(
            xpath,
            timeout=60
        )


        self.current_subject = subject.name

    # ======================================================
    # Cards
    # ======================================================

    from selenium.webdriver.common.by import By

    def get_cards(self):
        """
        Returns content cards from current subject.
        """

        # Wait until at least one exists.
        self.session.wait(selectors.CONTENT_CARD)

        # Return ALL of them.
        return self.session.driver.find_elements(
        self.By.XPATH,
        selectors.CONTENT_CARD
        )


    # ======================================================
    # Resources
    # ======================================================

    def collect_resources(
        self,
    ) -> list[Resource]:

        logger.info(
            "Collecting resources..."
        )


        resources = []


        subjects = self.get_subjects()


        for subject in subjects:

            self.open_subject(
                subject
            )


            cards = self.get_cards()


            for card in cards:


                resource = Resource(

                    subject=subject.name,

                    name=card.text.strip(),

                    element=card

                )


                resources.append(
                    resource
                )


        logger.info(
            f"Collected {len(resources)} resources."
        )


        return resources


    # ======================================================
    # Tasks
    # ======================================================

    def collect_tasks(
        self,
    ) -> list[Task]:

        logger.info(
            "Collecting tasks..."
        )


        tasks = []


        subjects = self.get_subjects()


        for subject in subjects:

            self.open_subject(
                subject
            )


            cards = self.get_cards()


            for card in cards:

                text = (
                    card.text
                    .strip()
                )


                if not text:
                    continue


                tasks.append(

                    Task(

                        subject=subject.name,

                        content=text

                    )

                )


        logger.info(
            f"Collected {len(tasks)} tasks."
        )


        return tasks