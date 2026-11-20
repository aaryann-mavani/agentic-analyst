"""The standardized series: one value per month, with a name and a unit label.

Every source is turned into this shape by a loader in `sources/`; the engine only ever sees a Series.
Strict validation of the data (gaps, duplicates, components that do not add up) belongs to the loaders
(issue #13); this module only orders the periods.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date

MONTH_NAMES = ["January", "February", "March", "April", "May", "June", "July",
               "August", "September", "October", "November", "December"]


@dataclass(frozen=True)
class Series:
    name: str
    unit: str  # a label only, never converted
    dates: tuple[date, ...]  # first day of each month, ascending
    values: tuple[float, ...]

    @classmethod
    def from_points(cls, name: str, unit: str, points: dict[date, float]) -> "Series":
        ordered = sorted(points)
        return cls(name, unit, tuple(ordered), tuple(points[d] for d in ordered))

    def __len__(self) -> int:
        return len(self.values)

    def label(self, i: int) -> str:
        d = self.dates[i]
        return f"{MONTH_NAMES[d.month - 1]} {d.year}"

    def index_of(self, year: int, month: int) -> int | None:
        for i, d in enumerate(self.dates):
            if (d.year, d.month) == (year, month):
                return i
        return None

    def coverage(self) -> str:
        return f"{self.label(0)} to {self.label(len(self) - 1)}"
