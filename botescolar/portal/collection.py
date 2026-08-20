from __future__ import annotations

import time
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

    # ======================================================
    # Subjects (persistent filter panel — no dashboard round-trip)
    # ======================================================

    def get_subject_count(self) -> int:
        # find_all() does a plain find_elements with no wait, unlike
        # find()/click() which go through wait_present/wait_clickable,
        # so we wait for at least one link before counting. NOTE: this
        # panel lives inside app-layout-module, which only mounts once
        # we're on a subject's own page — it does NOT exist on the root
        # dashboard (that's app-layout-dashboard, a different component).
        # Call this only after entering a subject via open_subject(),
        # never right after open_dashboard().
        self.session.wait(selectors.SUBJECT_FILTER_LINKS, timeout=30)
        links = self.session.find_all(selectors.SUBJECT_FILTER_LINKS)
        return len(links)

    def open_subject_by_index(self, index: int) -> str:
        """
        Clicks the subject at position `index` (1-based) in the
        persistent subject filter panel. This panel stays mounted
        across subject navigations, so this works whether we're
        currently on the dashboard OR on another subject's page —
        no need to navigate back to the portal in between.
        """
        xpath = f"{selectors.SUBJECT_FILTER_LINKS}[{index}]"

        element = self.session.find(xpath)
        name = " ".join(element.text.split()) if element else ""
        if not name:
            name = f"Subject {index}"

        logger.info(f"Opening {name}")

        self.session.click(xpath, timeout=30)
        self.current_subject = name

        return name


    def enter_subjects_view(self) -> int:
        """
        Gets from the root dashboard (app-layout-dashboard) into a
        subject's own page (app-layout-module) — the persistent filter
        panel used by get_subject_count()/open_subject_by_index() only
        exists in the latter, so this MUST run first, via the old
        modal flow, before any index-based navigation is possible.

        Opens today's module and clicks the first subject listed
        there. Returns the total subject count (0 if there are no
        subjects today), read from the panel once we've actually
        landed on it — the modal and the panel are different
        components, so we don't assume their orderings match.
        """
        self.open_today()
        subjects = self.get_subjects()

        if not subjects:
            return 0

        self.open_subject(subjects[0])

        return self.get_subject_count()

    def open_dashboard(self):

        logger.info(
            "Opening dashboard..."
        )

        self.session.open(
            config.PORTAL_URL
        )

        self.session.focus()


    def open_today(self):
        logger.info("Opening today's classes...")

        # Make sure we're actually on the dashboard first
        if "/eclass/" in self.session.driver.current_url:
            self.session.open(config.PORTAL_URL)

        try:
            self.session.wait(selectors.SUBJECT_MODAL, timeout=5)
            logger.info("Today's module already open.")
            return
        except Exception:
            pass

        logger.info("Clicking today's module...")
        self.session.click(selectors.DAY_BLOCK, timeout=60)
        self.session.wait(selectors.SUBJECT_MODAL, timeout=90)
        logger.info("Today's module opened.")


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

    def get_cards(self, previous_text: str | None = None):
        """
        Returns the app-card elements for the current subject
        (one per class entry that day), plus the joined text seen.

        Waits for the content to actually change from the previous
        subject's content, not just for two reads in a row to match
        (which could otherwise accept stale leftover content from
        the subject we just navigated away from).

        Requires several consecutive matching reads, not just two,
        before trusting a snapshot — two reads 0.5s apart can both
        land on an incomplete/placeholder render if Angular hasn't
        actually started re-rendering yet by the time we sample.
        The very first subject has no previous_text to guard against
        this (nothing to compare against), so it gets a longer
        required settle window than subsequent subjects do.
        """
        self.session.wait(selectors.CONTENT_CARD, timeout=60)

        required_stable_reads = 3 if previous_text is not None else 6

        deadline = time.time() + 15
        last_snapshot = None
        stable_reads = 0

        while time.time() < deadline:
            cards = self.session.find_all(selectors.CONTENT_CARD)
            snapshot = [c.text.strip() for c in cards]
            joined = "\n".join(snapshot)

            if snapshot and joined != previous_text and snapshot == last_snapshot:
                stable_reads += 1
                if stable_reads >= required_stable_reads:
                    return cards, joined
            else:
                stable_reads = 0

            last_snapshot = snapshot
            time.sleep(0.5)

        cards = self.session.find_all(selectors.CONTENT_CARD)
        return cards, "\n".join(c.text.strip() for c in cards)


    # ======================================================
    # Resources
    # ======================================================

    def collect_resources(self, on_resource) -> int:
        """
        Visits each subject via the persistent filter panel and calls
        on_resource(resource) immediately for each resource attachment
        found, while still on that subject's page (so the element
        stays valid for downloading). Never returns to the dashboard
        between subjects — clicks the next subject directly from the
        current one.
        """
        logger.info("Collecting resources...")
        count = 0
        previous_text = None

        self.open_dashboard()
        total = self.enter_subjects_view()
        logger.info(f"Found {total} subjects.")

        for i in range(1, total + 1):
            name = self.current_subject if i == 1 else self.open_subject_by_index(i)

            cards, previous_text = self.get_cards(previous_text)
            logger.info(f"{name}: {len(cards)} card(s) found.")

            for card in cards:
                items = self.session.find_all(
                    selectors.RESOURCE_ITEMS,
                    parent=card,
                )

                for item in items:
                    text = item.text.strip()
                    if not text or "Nenhum dado encontrado" in text:
                        continue

                    resource = Resource(subject=name, name=text, element=item)
                    on_resource(resource)   # process while the element is still valid
                    count += 1

        logger.info(f"Collected {count} resources.")
        return count


    # ======================================================
    # Tasks
    # ======================================================

    def collect_tasks(self) -> list[Task]:
        logger.info("Collecting tasks...")
        tasks = []
        previous_text = None

        self.open_dashboard()
        total = self.enter_subjects_view()
        logger.info(f"Found {total} subjects.")

        for i in range(1, total + 1):
            name = self.current_subject if i == 1 else self.open_subject_by_index(i)

            cards, previous_text = self.get_cards(previous_text)
            logger.info(f"{name}: {len(cards)} card(s) found.")

            for card in cards:
                text = card.text.strip()

                if not text:
                    continue

                # Aula and Atividade can each independently show this
                # "no data" placeholder — drop just those lines so real
                # content in either half still comes through.
                cleaned = "\n".join(
                    line for line in text.splitlines()
                    if "Nenhum dado encontrado" not in line
                ).strip()

                if not cleaned:
                    continue

                tasks.append(Task(subject=name, content=cleaned))

        logger.info(f"Collected {len(tasks)} tasks.")
        return tasks