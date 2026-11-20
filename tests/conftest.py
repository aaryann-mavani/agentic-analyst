from pathlib import Path

import pytest

from agentic_analyst import load_us_trade

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def trade():
    """US trade deficit, Jan-Dec 2023, built so every answer is known by construction.

    Deficit (USD millions) by month: 1000, 1100, 990, 990, 1200, 900, 900, 900, 1350, 1000, 500, 750.
    The CSV rows are shuffled on purpose: the loader must order them.
    """
    return load_us_trade(FIXTURES / "us_trade_2023.csv")
