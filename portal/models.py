from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from selenium.webdriver.remote.webelement import WebElement


# ==========================================================
# SUBJECT
# ==========================================================

@dataclass(slots=True)
class Subject:
    """
    Represents a subject in the Adventista portal.
    """

    name: str


# ==========================================================
# RESOURCE
# ==========================================================

@dataclass(slots=True)
class Resource:
    """
    Represents a downloadable resource.
    """

    subject: str
    name: str

    element: Optional[WebElement] = None
    path: Optional[Path] = None

    downloaded: bool = False

    def mark_downloaded(self, path: Path):
        self.path = path
        self.downloaded = True


# ==========================================================
# TASK
# ==========================================================

@dataclass(slots=True)
class Task:
    """
    Represents a subject task/activity.
    """

    subject: str
    content: str


# ==========================================================
# COLLECTION RESULTS
# ==========================================================

@dataclass(slots=True)
class CollectionResult:
    """
    Convenience object returned by the collector.

    Allows a single collection pass to return
    both resources and tasks if desired.
    """

    resources: list[Resource] = field(default_factory=list)
    tasks: list[Task] = field(default_factory=list)