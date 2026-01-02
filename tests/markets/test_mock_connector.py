"""
Tests for Mock Connector.
"""

import pytest
import pandas as pd
from src.markets.connectors.mock import MockConnector


from datetime import datetime


def test_mock_determinism():
    fixed_end = datetime(2023, 1, 1)
    c1 = MockConnector(seed=42)
    d1 = c1.fetch_history("TEST", end_date=fixed_end)

    c2 = MockConnector(seed=42)
    d2 = c2.fetch_history("TEST", end_date=fixed_end)

    pd.testing.assert_frame_equal(d1.data, d2.data)


def test_mock_randomness():
    fixed_end = datetime(2023, 1, 1)
    c1 = MockConnector(seed=42)
    d1 = c1.fetch_history("TEST", end_date=fixed_end)

    c2 = MockConnector(seed=99)
    d2 = c2.fetch_history("TEST", end_date=fixed_end)

    # Assert not equal
    with pytest.raises(AssertionError):
        pd.testing.assert_frame_equal(d1.data, d2.data)
