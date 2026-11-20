"""The 'Ask a Question' seam: a series and a Question in, a checked Answer out."""
from __future__ import annotations

from typing import Callable

from .answer import Answer, Draft
from .check import check_draft
from .period import NamedPeriod, find_period
from .routing import route
from .series import Series

# A language layer may rewrite the code-computed Draft (ADR 0001: the model phrases). Whatever it returns is Checked.
Drafter = Callable[[Draft], Draft]


def ask(series: Series, question: str, drafter: Drafter | None = None) -> Answer:
    named = find_period(question)
    if named == "incomplete":
        return Answer(question, "declined", "Name the month, for example 'March 2024', so that I know which period you mean.")
    if isinstance(named, NamedPeriod):
        i = series.index_of(named.year, named.month)
        if i is None:
            return Answer(question, "out_of_coverage", f"No data for that period. The series covers {series.coverage()}.")
    else:
        i = len(series) - 1

    answer_type = route(question)
    draft = answer_type.answer(series, i, question) if answer_type else None
    if draft is None:
        return Answer(question, "declined", _cannot_answer(series, i, answer_type))
    if drafter is not None:
        draft = drafter(draft)
    text, claims = check_draft(series, draft)
    return Answer(question, "answered", text, claims, draft.calculation_path, draft.evidence)


def _cannot_answer(series: Series, i: int, answer_type) -> str:
    if answer_type is not None and i < 1:
        return f"{series.label(i)} is the first period in the data, so there is no earlier period to compare it with."
    return "I cannot answer that kind of Question yet. Try 'What happened in March 2024?' or 'What happened in the latest period?'."
