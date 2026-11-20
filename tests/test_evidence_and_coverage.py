from agentic_analyst import ask


def test_calculation_path_lets_the_partner_retrace_the_numbers(trade):
    answer = ask(trade, "What happened in September 2023?")

    path = "\n".join(answer.calculation_path)
    assert "September 2023 = 1,350.000" in path
    assert "August 2023 = 900.000" in path
    assert "change = 1,350.000 - 900.000 = +450.000" in path
    assert "percent = +450.000 / 900.000 = +50.0%" in path


def test_evidence_has_the_figures_and_a_chart_with_the_period_highlighted(trade):
    answer = ask(trade, "What happened in September 2023?")

    figures = {f.label: f.value for f in answer.evidence.figures}
    assert figures == {"September 2023": 1350.0, "August 2023": 900.0}
    chart = answer.evidence.chart
    assert len(chart.values) == 12 and chart.dates[0] == "2023-01-01" and chart.dates[-1] == "2023-12-01"
    assert [chart.dates[i] for i in chart.highlight] == ["2023-08-01", "2023-09-01"]


def test_period_before_the_data_states_the_coverage(trade):
    answer = ask(trade, "What happened in March 2019?")

    assert answer.status == "out_of_coverage"
    assert "January 2023 to December 2023" in answer.text
    assert answer.claims == () and answer.evidence is None


def test_period_after_the_data_states_the_coverage(trade):
    answer = ask(trade, "What happened in 2024-03?")

    assert answer.status == "out_of_coverage"
    assert "January 2023 to December 2023" in answer.text


def test_first_period_has_nothing_to_compare_with(trade):
    answer = ask(trade, "What happened in January 2023?")

    assert answer.status == "declined"
    assert "first period" in answer.text


def test_year_without_month_asks_for_a_month_instead_of_guessing(trade):
    answer = ask(trade, "What happened in 2023?")

    assert answer.status == "declined"
    assert "month" in answer.text


def test_a_kind_of_question_not_supported_yet_is_declined_not_misanswered(trade):
    answer = ask(trade, "Why did it change in September 2023?")

    assert answer.status == "declined"
    assert answer.claims == ()
