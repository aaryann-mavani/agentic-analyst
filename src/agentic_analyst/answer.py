"""The shapes that make up an Answer."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Claim:
    """One statement the data can confirm or refute: `measure` at period index `period`, written as `shown`."""
    measure: str
    period: int
    shown: str


@dataclass(frozen=True)
class CheckedClaim:
    claim: Claim
    passed: bool
    recomputed: str  # what code computes from the data; equals claim.shown when passed


@dataclass(frozen=True)
class Figure:
    label: str
    value: float


@dataclass(frozen=True)
class Chart:
    """The series with the relevant periods highlighted (indices into dates/values)."""
    dates: tuple[str, ...]
    values: tuple[float, ...]
    highlight: tuple[int, ...]


@dataclass(frozen=True)
class Evidence:
    figures: tuple[Figure, ...]
    chart: Chart


@dataclass(frozen=True)
class Draft:
    """What an answer type (or a language layer) proposes, before the Check."""
    text: str
    claims: tuple[Claim, ...]
    calculation_path: tuple[str, ...]
    evidence: Evidence | None = None


@dataclass(frozen=True)
class Answer:
    question: str
    # "answered", "out_of_coverage" (period not in the data), "declined" (the data cannot answer it)
    status: str
    text: str
    claims: tuple[CheckedClaim, ...] = ()
    calculation_path: tuple[str, ...] = ()
    evidence: Evidence | None = None

    @property
    def all_claims_passed(self) -> bool:
        return all(c.passed for c in self.claims)
