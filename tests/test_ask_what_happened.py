"""Tests at the 'Ask a Question' seam: a series and a Question in, an Answer out."""
from datetime import date

from agentic_analyst import Series, ask


def test_latest_period_reports_change_and_percent(trade):
    answer = ask(trade, "What happened in the latest period?")

    assert answer.status == "answered"
    assert "December 2023" in answer.text
    assert "up 250" in answer.text
    assert "+50.0%" in answer.text


def test_named_period_reports_change_and_percent(trade):
    answer = ask(trade, "What happened in March 2023?")

    assert answer.status == "answered"
    assert "March 2023" in answer.text
    assert "down 110" in answer.text
    assert "-10.0%" in answer.text


def test_period_can_be_written_as_abbreviation_or_iso_month(trade):
    assert "down 300" in ask(trade, "What happened in Jun 2023?").text
    assert "down 500" in ask(trade, "what happened in 2023-11").text


def test_unchanged_period_says_so(trade):
    answer = ask(trade, "What happened in April 2023?")

    assert "unchanged from March 2023" in answer.text


def test_zero_previous_value_gives_change_without_percent():
    s = Series.from_points("KPI", "units", {date(2024, 1, 1): 0.0, date(2024, 2, 1): 5.0})

    answer = ask(s, "What happened in the latest period?")

    assert "up 5.00" in answer.text
    assert "%" not in answer.text
    assert answer.all_claims_passed


def test_every_claim_in_a_computed_answer_is_checked_and_passes(trade):
    answer = ask(trade, "What happened in September 2023?")

    shown = {c.claim.measure: c.claim.shown for c in answer.claims}
    assert shown == {"level": "1,350", "direction": "up", "change": "450", "percent": "+50.0%"}
    assert answer.all_claims_passed
