"""US trade deficit from the Time-MMD `Economy.csv` (columns Month, Exports, Imports, OT, date, ...).

Source: https://github.com/AdityaLab/Time-MMD (see docs/research/time-mmd-structure.md). The file has no licence,
so it is downloaded by `prototypes/kpi-qa-PROTOTYPE/tools/fetch_data.py` and never committed.
OT is exports minus imports (always negative); the series is the deficit, so a positive value is a deficit.
The file's rows are not in date order; the Series orders them.
"""
import csv
from datetime import date
from pathlib import Path

from ..series import Series


def load_us_trade(path: str | Path) -> Series:
    points: dict[date, float] = {}
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            points[date.fromisoformat(row["date"][:10])] = -float(row["OT"])
    return Series.from_points("US trade deficit", "USD millions", points)
