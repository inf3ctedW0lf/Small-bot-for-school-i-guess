from __future__ import annotations

from datetime import datetime
from pathlib import Path


class DailyCache:
    """
    Daily cache that stores already-processed items.

    File format:

    --- DD/MM/YYYY ---
    item1
    item2
    item3
    """

    def __init__(self, filepath: str | Path):
        self.filepath = Path(filepath)
        self.today = self._today()
        self.items: set[str] = set()

        self.filepath.parent.mkdir(parents=True, exist_ok=True)

        self._load()

    # =====================================================
    # Internal
    # =====================================================

    @staticmethod
    def _today() -> str:
        return datetime.now().strftime("%d/%m/%Y")

    def _header(self) -> str:
        return f"--- {self.today} ---"

    # =====================================================
    # Loading
    # =====================================================

    def _load(self):

        self.today = self._today()

        if not self.filepath.exists():
            self.filepath.write_text(
                self._header() + "\n",
                encoding="utf-8"
            )
            self.items.clear()
            return

        lines = self.filepath.read_text(
            encoding="utf-8"
        ).splitlines()

        if self._header() not in lines:
            self.filepath.write_text(
                self._header() + "\n",
                encoding="utf-8"
            )
            self.items.clear()
            return

        start = lines.index(self._header()) + 1

        self.items = {
            line.strip()
            for line in lines[start:]
            if line.strip() and not line.startswith("---")
        }

    # =====================================================
    # Public API
    # =====================================================

    def refresh(self):
        """
        Reloads only if the day changed.
        """

        if self._today() != self.today:
            self._load()

    def contains(self, key: str) -> bool:
        self.refresh()
        return key in self.items

    def add(self, key: str):

        self.refresh()

        if key in self.items:
            return

        self.items.add(key)

        with self.filepath.open(
            "a",
            encoding="utf-8"
        ) as file:
            file.write(key + "\n")

    def remove(self, key: str):

        self.refresh()

        if key not in self.items:
            return

        self.items.remove(key)

        self.save()

    def clear(self):
        """
        Clears today's cache.
        """

        self.items.clear()

        self.filepath.write_text(
            self._header() + "\n",
            encoding="utf-8"
        )

    def save(self):
        """
        Rewrites the cache file.
        """

        with self.filepath.open(
            "w",
            encoding="utf-8"
        ) as file:

            file.write(self._header() + "\n")

            for item in sorted(self.items):
                file.write(item + "\n")

    # =====================================================
    # Convenience
    # =====================================================

    def __contains__(self, item: str):
        return self.contains(item)

    def __len__(self):
        return len(self.items)

    def __iter__(self):
        return iter(self.items)

    def __repr__(self):
        return (
            f"<DailyCache "
            f"items={len(self.items)} "
            f"date='{self.today}'>"
        )