"""'What happened?': the change in value and percent against the previous period."""
from ..answer import Chart, Claim, Draft, Evidence, Figure
from ..measures import MEASURES, change, percent_change
from ..series import Series

PATTERN = r"\bwhat (happened|changed|moved)\b|\bhappen|\blatest\b|\blast month\b|\bhow did\b"
PRIORITY = 100


def answer(series: Series, i: int, question: str) -> Draft | None:
    if i < 1:
        return None  # nothing to compare the first period with

    def shown(measure: str) -> str:
        m = MEASURES[measure]
        return m.render(series, m.compute(series, i))

    cur, prev = series.label(i), series.label(i - 1)
    v, d = shown("level"), shown("direction")
    claims = [Claim("level", i, v), Claim("direction", i, d)]
    path = [f"{cur} = {series.values[i]:,.3f}", f"{prev} = {series.values[i - 1]:,.3f}"]
    if d == "unchanged":
        text = f"{series.name}: {cur} was {v} {series.unit}, unchanged from {prev}."
        path.append("change = 0")
    else:
        c = shown("change")
        claims.append(Claim("change", i, c))
        path.append(f"change = {series.values[i]:,.3f} - {series.values[i - 1]:,.3f} = {change(series, i):+,.3f}")
        if percent_change(series, i) is None:
            text = f"{series.name}: {cur} was {v} {series.unit}, {d} {c} from {prev}. No percent change: {prev} is not above zero."
        else:
            p = shown("percent")
            claims.append(Claim("percent", i, p))
            path.append(f"percent = {change(series, i):+,.3f} / {series.values[i - 1]:,.3f} = {p}")
            text = f"{series.name}: {cur} was {v} {series.unit}, {d} {c} ({p}) from {prev}."
    chart = Chart(tuple(x.isoformat() for x in series.dates), series.values, (i - 1, i))
    evidence = Evidence((Figure(cur, series.values[i]), Figure(prev, series.values[i - 1])), chart)
    return Draft(text, tuple(claims), tuple(path), evidence)
