"""Finding the period a Question is about."""
from __future__ import annotations

import re
from dataclasses import dataclass

from .series import MONTH_NAMES

_ABBREVIATIONS = {"jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6, "jul": 7,
                  "aug": 8, "sep": 9, "sept": 9, "oct": 10, "nov": 11, "dec": 12}
_NAMES = {name.lower(): n for n, name in enumerate(MONTH_NAMES, 1)} | _ABBREVIATIONS
_MONTH_YEAR = re.compile(r"\b(" + "|".join(sorted(_NAMES, key=len, reverse=True)) + r")\.?,?\s+((?:19|20)\d\d)\b")
_ISO = re.compile(r"\b((?:19|20)\d\d)-(0[1-9]|1[0-2])\b")
_BARE_YEAR = re.compile(r"\b(?:19|20)\d\d\b")
_BARE_MONTH = re.compile(r"\b(" + "|".join(n for n in _NAMES if len(n) > 3 and n != "may") + r")\b")


@dataclass(frozen=True)
class NamedPeriod:
    year: int
    month: int


def find_period(question: str) -> NamedPeriod | None | str:
    """A NamedPeriod, None when no period is named (meaning the latest), or "incomplete" when a year or
    month is named without the other, which cannot be pinned to one month."""
    q = question.lower()
    if m := _MONTH_YEAR.search(q):
        return NamedPeriod(int(m.group(2)), _NAMES[m.group(1)])
    if m := _ISO.search(q):
        return NamedPeriod(int(m.group(1)), int(m.group(2)))
    if _BARE_YEAR.search(q) or _BARE_MONTH.search(q):
        return "incomplete"
    return None
