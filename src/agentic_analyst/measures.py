"""Measures: what code can compute about a series at period `i`, and how each is written down.

Both the answer types (to draft Claims) and the Check (to recompute them) go through this table, so a
number is written exactly one way. A new answer type registers its own measures with `register_measure`.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from .series import Series


@dataclass(frozen=True)
class Measure:
    compute: Callable[[Series, int], Any]
    render: Callable[[Series, Any], str]


MEASURES: dict[str, Measure] = {}


def register_measure(name: str, compute: Callable[[Series, int], Any], render: Callable[[Series, Any], str]) -> None:
    MEASURES[name] = Measure(compute, render)


def format_value(x: float) -> str:
    return f"{x:,.0f}" if abs(x) >= 100 else f"{x:,.2f}"


def change(s: Series, i: int) -> float:
    return s.values[i] - s.values[i - 1]


def percent_change(s: Series, i: int) -> float | None:
    """None when the previous value is not positive, where a percent change has no clear meaning."""
    return change(s, i) / s.values[i - 1] if s.values[i - 1] > 0 else None


def direction(s: Series, i: int) -> str:
    c = change(s, i)
    return "up" if c > 0 else "down" if c < 0 else "unchanged"


register_measure("level", lambda s, i: s.values[i], lambda s, x: format_value(x))
register_measure("change", change, lambda s, x: format_value(abs(x)))  # sign is carried by "direction"
register_measure("percent", percent_change, lambda s, x: f"{x * 100:+.1f}%")
register_measure("direction", direction, lambda s, x: x)
