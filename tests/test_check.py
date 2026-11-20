"""A language layer may rewrite the draft; whatever it says is Checked before the Partner sees it."""
import dataclasses

from agentic_analyst import ask
from agentic_analyst.answer import Claim


def wrong_change(draft):
    """A stand-in language layer that gets the change wrong (says 999 where the data says 450)."""
    claims = tuple(dataclasses.replace(c, shown="999") if c.measure == "change" else c for c in draft.claims)
    return dataclasses.replace(draft, text=draft.text.replace("450", "999"), claims=claims)


def flipped_direction(draft):
    claims = tuple(dataclasses.replace(c, shown="down") if c.measure == "direction" else c for c in draft.claims)
    return dataclasses.replace(draft, text=draft.text.replace(" up ", " down "), claims=claims)


def test_failed_claim_is_corrected_and_flagged(trade):
    answer = ask(trade, "What happened in September 2023?", drafter=wrong_change)

    failed = [c for c in answer.claims if not c.passed]
    assert [(c.claim.measure, c.claim.shown, c.recomputed) for c in failed] == [("change", "999", "450")]
    assert "999" not in answer.text.split("Check:")[0]
    assert "up 450" in answer.text
    assert "failed" in answer.text and "corrected" in answer.text
    assert not answer.all_claims_passed


def test_flipped_direction_is_caught(trade):
    answer = ask(trade, "What happened in September 2023?", drafter=flipped_direction)

    failed = [c for c in answer.claims if not c.passed]
    assert [c.claim.measure for c in failed] == ["direction"]
    assert "up 450" in answer.text


def test_claim_about_the_wrong_period_is_caught(trade):
    def wrong_period(draft):
        # claims that August's level was 1,350 (that is September's)
        return dataclasses.replace(draft, claims=draft.claims + (Claim("level", 7, "1,350"),))

    answer = ask(trade, "What happened in September 2023?", drafter=wrong_period)

    failed = [c for c in answer.claims if not c.passed]
    assert [(c.claim.period, c.recomputed) for c in failed] == [(7, "900")]


def test_honest_language_layer_is_left_alone(trade):
    answer = ask(trade, "What happened in September 2023?", drafter=lambda d: d)

    assert answer.all_claims_passed
    assert "Check:" not in answer.text
