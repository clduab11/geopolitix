"""Tests for Financial Modeling Prep API client."""

from unittest.mock import MagicMock, patch
import pytest

from src.data_sources.fmp_api import FMPClient


class TestFMPClient:
    """Test cases for FMPClient."""

    def test_init(self):
        """Test client initialization."""
        with patch.object(FMPClient, "__init__", lambda self: None):
            client = FMPClient()
            client.api_key = "test_key"
            client.base_url = "https://financialmodelingprep.com/api/v3"

            assert client._is_available()

    def test_init_without_api_key(self):
        """Test initialization without API key."""
        with patch.object(FMPClient, "__init__", lambda self: None):
            client = FMPClient()
            client.api_key = ""

            assert not client._is_available()

    def test_get_params_adds_api_key(self):
        """Test that API key is added to parameters."""
        with patch.object(FMPClient, "__init__", lambda self: None):
            client = FMPClient()
            client.api_key = "test_key"

            params = client._get_params(limit=10)

            assert params["apikey"] == "test_key"
            assert params["limit"] == 10

    @patch("requests.Session.get")
    def test_get_stock_quote_success(self, mock_get):
        """Test successful stock quote retrieval."""
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {
                "symbol": "AAPL",
                "name": "Apple Inc.",
                "price": 150.50,
                "change": 2.50,
                "changesPercentage": 1.69,
                "dayLow": 148.00,
                "dayHigh": 151.00,
                "yearLow": 124.00,
                "yearHigh": 178.00,
                "marketCap": 2500000000000,
                "pe": 28.5,
                "eps": 5.28,
                "volume": 50000000,
                "avgVolume": 45000000,
                "open": 149.00,
                "previousClose": 148.00,
                "exchange": "NASDAQ",
            }
        ]
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        with patch.object(FMPClient, "__init__", lambda self: None):
            client = FMPClient()
            client.api_key = "test_key"
            client.base_url = "https://api.example.com"
            client.session = MagicMock()
            client.session.get = mock_get

            result = client.get_stock_quote("AAPL")

            assert result["ticker"] == "AAPL"
            assert result["name"] == "Apple Inc."
            assert result["price"] == 150.50
            assert result["change"] == 2.50
            assert result["market_cap"] == 2500000000000

    def test_get_stock_quote_not_available(self):
        """Test stock quote returns empty when not available."""
        with patch.object(FMPClient, "__init__", lambda self: None):
            client = FMPClient()
            client.api_key = ""

            result = client._empty_quote("AAPL")

            assert result["ticker"] == "AAPL"
            assert result["price"] == 0
            assert "error" in result

    @patch("requests.Session.get")
    def test_get_company_profile_success(self, mock_get):
        """Test successful company profile retrieval."""
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {
                "symbol": "AAPL",
                "companyName": "Apple Inc.",
                "description": "Technology company",
                "ceo": "Tim Cook",
                "sector": "Technology",
                "industry": "Consumer Electronics",
                "country": "US",
                "exchangeShortName": "NASDAQ",
                "website": "https://www.apple.com",
                "fullTimeEmployees": 164000,
                "mktCap": 2500000000000,
                "beta": 1.2,
                "lastDiv": 0.24,
                "ipoDate": "1980-12-12",
                "image": "https://example.com/logo.png",
            }
        ]
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        with patch.object(FMPClient, "__init__", lambda self: None):
            client = FMPClient()
            client.api_key = "test_key"
            client.base_url = "https://api.example.com"
            client.session = MagicMock()
            client.session.get = mock_get

            result = client.get_company_profile("AAPL")

            assert result["ticker"] == "AAPL"
            assert result["name"] == "Apple Inc."
            assert result["sector"] == "Technology"
            assert result["ceo"] == "Tim Cook"

    @patch("requests.Session.get")
    def test_get_historical_prices_success(self, mock_get):
        """Test successful historical prices retrieval."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "symbol": "AAPL",
            "historical": [
                {
                    "date": "2024-01-15",
                    "open": 149.00,
                    "high": 151.00,
                    "low": 148.00,
                    "close": 150.50,
                    "volume": 50000000,
                },
                {
                    "date": "2024-01-14",
                    "open": 148.00,
                    "high": 150.00,
                    "low": 147.00,
                    "close": 149.00,
                    "volume": 45000000,
                },
            ]
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        with patch.object(FMPClient, "__init__", lambda self: None):
            client = FMPClient()
            client.api_key = "test_key"
            client.base_url = "https://api.example.com"
            client.session = MagicMock()
            client.session.get = mock_get

            result = client.get_historical_prices("AAPL", period="1M")

            assert result["ticker"] == "AAPL"
            assert result["period"] == "1M"
            assert len(result["historical"]) == 2

    @patch("requests.Session.get")
    def test_get_income_statement_success(self, mock_get):
        """Test successful income statement retrieval."""
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {
                "date": "2023-12-31",
                "revenue": 100000000000,
                "costOfRevenue": 60000000000,
                "grossProfit": 40000000000,
                "operatingIncome": 25000000000,
                "netIncome": 20000000000,
                "eps": 5.00,
                "epsdiluted": 4.95,
                "ebitda": 30000000000,
                "grossProfitRatio": 0.40,
                "operatingIncomeRatio": 0.25,
                "netIncomeRatio": 0.20,
            }
        ]
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        with patch.object(FMPClient, "__init__", lambda self: None):
            client = FMPClient()
            client.api_key = "test_key"
            client.base_url = "https://api.example.com"
            client.session = MagicMock()
            client.session.get = mock_get

            result = client.get_income_statement("AAPL", period="annual")

            assert result["ticker"] == "AAPL"
            assert result["period"] == "annual"
            assert len(result["statements"]) == 1
            assert result["statements"][0]["revenue"] == 100000000000

    @patch("requests.Session.get")
    def test_get_balance_sheet_success(self, mock_get):
        """Test successful balance sheet retrieval."""
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {
                "date": "2023-12-31",
                "totalAssets": 350000000000,
                "totalLiabilities": 290000000000,
                "totalStockholdersEquity": 60000000000,
                "cashAndCashEquivalents": 25000000000,
                "totalDebt": 110000000000,
                "netDebt": 85000000000,
                "inventory": 5000000000,
                "netReceivables": 20000000000,
                "accountPayables": 50000000000,
            }
        ]
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        with patch.object(FMPClient, "__init__", lambda self: None):
            client = FMPClient()
            client.api_key = "test_key"
            client.base_url = "https://api.example.com"
            client.session = MagicMock()
            client.session.get = mock_get

            result = client.get_balance_sheet("AAPL", period="annual")

            assert result["ticker"] == "AAPL"
            assert len(result["statements"]) == 1
            assert result["statements"][0]["total_assets"] == 350000000000

    @patch("requests.Session.get")
    def test_get_cash_flow_success(self, mock_get):
        """Test successful cash flow statement retrieval."""
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {
                "date": "2023-12-31",
                "operatingCashFlow": 30000000000,
                "netCashUsedForInvestingActivites": -15000000000,
                "netCashUsedProvidedByFinancingActivities": -10000000000,
                "freeCashFlow": 25000000000,
                "capitalExpenditure": -5000000000,
                "dividendsPaid": -3000000000,
                "commonStockRepurchased": -70000000000,
            }
        ]
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        with patch.object(FMPClient, "__init__", lambda self: None):
            client = FMPClient()
            client.api_key = "test_key"
            client.base_url = "https://api.example.com"
            client.session = MagicMock()
            client.session.get = mock_get

            result = client.get_cash_flow("AAPL", period="annual")

            assert result["ticker"] == "AAPL"
            assert len(result["statements"]) == 1
            assert result["statements"][0]["free_cash_flow"] == 25000000000

    @patch("requests.Session.get")
    def test_get_key_metrics_success(self, mock_get):
        """Test successful key metrics retrieval."""
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {
                "peRatioTTM": 28.5,
                "pegRatioTTM": 2.5,
                "priceToBookRatioTTM": 45.0,
                "priceToSalesRatioTTM": 8.0,
                "enterpriseValueOverEBITDATTM": 22.0,
                "roeTTM": 0.50,
                "roaTTM": 0.20,
                "dividendYieldTTM": 0.005,
                "debtToEquityTTM": 1.8,
                "currentRatioTTM": 1.0,
                "quickRatioTTM": 0.9,
                "revenuePerShareTTM": 25.0,
                "netIncomePerShareTTM": 5.0,
                "freeCashFlowPerShareTTM": 4.5,
            }
        ]
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        with patch.object(FMPClient, "__init__", lambda self: None):
            client = FMPClient()
            client.api_key = "test_key"
            client.base_url = "https://api.example.com"
            client.session = MagicMock()
            client.session.get = mock_get

            result = client.get_key_metrics("AAPL")

            assert result["ticker"] == "AAPL"
            assert result["metrics"]["pe_ratio"] == 28.5
            assert result["metrics"]["roe"] == 0.50

    @patch("requests.Session.get")
    def test_search_ticker_success(self, mock_get):
        """Test successful ticker search."""
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {
                "symbol": "AAPL",
                "name": "Apple Inc.",
                "stockExchange": "NASDAQ",
                "exchangeShortName": "NASDAQ",
            },
            {
                "symbol": "AAPD",
                "name": "Direxion Daily AAPL Bear 1X Shares",
                "stockExchange": "NASDAQ",
                "exchangeShortName": "NASDAQ",
            },
        ]
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        with patch.object(FMPClient, "__init__", lambda self: None):
            client = FMPClient()
            client.api_key = "test_key"
            client.base_url = "https://api.example.com"
            client.session = MagicMock()
            client.session.get = mock_get

            result = client.search_ticker("Apple")

            assert len(result) == 2
            assert result[0]["ticker"] == "AAPL"
            assert result[0]["name"] == "Apple Inc."

    def test_search_ticker_empty_query(self):
        """Test ticker search with empty query."""
        with patch.object(FMPClient, "__init__", lambda self: None):
            client = FMPClient()
            client.api_key = "test_key"

            result = client.search_ticker("")

            assert result == []

    @patch("requests.Session.get")
    def test_get_sector_performance_success(self, mock_get):
        """Test successful sector performance retrieval."""
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {"sector": "Technology", "changesPercentage": "2.5%"},
            {"sector": "Healthcare", "changesPercentage": "-0.5%"},
            {"sector": "Financial", "changesPercentage": "1.2%"},
        ]
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        with patch.object(FMPClient, "__init__", lambda self: None):
            client = FMPClient()
            client.api_key = "test_key"
            client.base_url = "https://api.example.com"
            client.session = MagicMock()
            client.session.get = mock_get

            result = client.get_sector_performance()

            assert len(result) == 3
            assert result[0]["sector"] == "Technology"
            assert result[0]["change_percent"] == 2.5

    def test_empty_quote_structure(self):
        """Test empty quote structure."""
        with patch.object(FMPClient, "__init__", lambda self: None):
            client = FMPClient()
            client.api_key = ""

            result = client._empty_quote("TEST")

            assert result["ticker"] == "TEST"
            assert result["price"] == 0
            assert "error" in result
            assert "timestamp" in result

    def test_empty_profile_structure(self):
        """Test empty profile structure."""
        with patch.object(FMPClient, "__init__", lambda self: None):
            client = FMPClient()
            client.api_key = ""

            result = client._empty_profile("TEST")

            assert result["ticker"] == "TEST"
            assert result["name"] == ""
            assert "error" in result
            assert "timestamp" in result
