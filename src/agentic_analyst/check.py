"""The Check: recompute every Claim from the data by code. Failed Claims are corrected in the text and flagged."""
from __future__ import annotations

from .answer import CheckedClaim, Claim, Draft
from .measures import MEASURES
from .series import Series


def check_claim(series: Series, claim: Claim) -> CheckedClaim:
    m = MEASURES[claim.measure]
    recomputed = m.render(series, m.compute(series, claim.period))
    return CheckedClaim(claim, passed=recomputed == claim.shown, recomputed=recomputed)


def check_draft(series: Series, draft: Draft) -> tuple[str, tuple[CheckedClaim, ...]]:
    """Return the text to show and the checked Claims. Never returns an unchecked Claim."""
    checked = tuple(check_claim(series, c) for c in draft.claims)
    text = draft.text
    failed = [c for c in checked if not c.passed]
    for c in failed:
        text = text.replace(c.claim.shown, c.recomputed)
    if failed:
        fixes = "; ".join(f"{c.claim.measure}: {c.claim.shown} -> {c.recomputed}" for c in failed)
        text += f" Check: {len(failed)} claim(s) failed and were corrected ({fixes})."
    return text, checked
