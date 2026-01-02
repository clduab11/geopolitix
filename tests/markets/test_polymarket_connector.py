"""
Tests for Polymarket Connector.
"""

import pytest
import responses
from datetime import datetime
from src.markets.connectors.polymarket import PolymarketConnector


@pytest.fixture
def connector():
    return PolymarketConnector()


@responses.activate
def test_fetch_history_success(connector):
    token_id = "test_token"
    url = "https://clob.polymarket.com/prices-history"

    mock_response = {
        "history": [
            {"t": 1672531200, "p": 0.45},  # 2023-01-01
            {"t": 1672617600, "p": 0.48},  # 2023-01-02
        ]
    }

    responses.add(responses.GET, url, json=mock_response, status=200)

    data = connector.fetch_history(token_id)

    assert data.symbol == token_id
    assert len(data.data) == 2
    assert "timestamp" in data.data.columns
    assert "price" in data.data.columns
    assert data.data.iloc[0]["price"] == 0.45


@responses.activate
def test_fetch_history_retry(connector):
    url = "https://clob.polymarket.com/prices-history"

    # 429 then 200
    responses.add(responses.GET, url, status=429)
    responses.add(
        responses.GET, url, json={"history": [{"t": 1, "p": 0.1}]}, status=200
    )

    data = connector.fetch_history("token_retry")
    assert len(data.data) == 1


def test_list_markets_gamma_api(connector):
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.GET,
            "https://gamma-api.polymarket.com/markets",
            json=[{"id": "m1", "question": "Q1"}],
            status=200,
        )

        markets = connector.list_markets()
        assert len(markets) == 1
        assert markets[0]["id"] == "m1"
