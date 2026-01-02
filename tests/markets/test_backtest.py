"""
Tests for Backtest Harness.
"""

import pytest
import pandas as pd
from datetime import datetime, timedelta
from src.markets.eval.backtest import BacktestHarness
from src.markets.models.baselines import MovingAverageForecaster
from src.markets.types import MarketData


def test_backtest_execution():
    dates = pd.date_range(datetime.now() - timedelta(days=10), periods=10)
    df = pd.DataFrame({"timestamp": dates, "price": [0.5] * 10, "volume": [100] * 10})

    md = MarketData("test", "SYM", "test", df, {})

    harness = BacktestHarness()
    model = MovingAverageForecaster(window=2)

    start = dates[5]
    end = dates[9]

    res = harness.run(md, [model], start, end)

    assert res.model_name == model.name
    # Since prices are constant 0.5, predictions should be perfect after warm-up
    # MA(2) of [0.5, 0.5] is 0.5. Actual is 0.5. Error 0.
    assert res.metrics["brier_score"] == pytest.approx(0.0)
    assert len(res.predictions) > 0
