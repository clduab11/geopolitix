"""
Tests for Basic Features.
"""

import pytest
import pandas as pd
from src.markets.features.basic import BasicFeatureExtractor
from src.markets.types import MarketData


def test_feature_generation():
    # consistent data
    df = pd.DataFrame(
        {
            "timestamp": pd.date_range("2023-01-01", periods=10),
            "price": [1.0, 1.1, 1.05, 1.2, 1.15, 1.3, 1.25, 1.4, 1.35, 1.5],
            "volume": [100] * 10,
        }
    )

    md = MarketData("test", "SYM", "test", df, {})

    extractor = BasicFeatureExtractor(windows=[2])
    res_df = extractor.fit_transform(md)

    assert "rolling_mean_2" in res_df.columns
    assert "return" in res_df.columns

    # Check manual calcs
    # return for row 1 = (1.1 - 1.0)/1.0 = 0.1
    assert res_df.iloc[1]["return"] == pytest.approx(0.1)

    # mean_2 for row 1 = (1.0 + 1.1) / 2 = 1.05
    assert res_df.iloc[1]["rolling_mean_2"] == pytest.approx(1.05)
