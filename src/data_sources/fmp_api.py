"""Financial Modeling Prep API client for stock data and financial statements."""

from datetime import datetime, UTC
from typing import Any, Dict, List, Optional

from config.settings import Settings
from src.data_sources.base import BaseAPIClient
from src.utils.cache import cache_response
from src.utils.logger import get_logger

logger = get_logger(__name__)


class FMPClient(BaseAPIClient):
    """Client for Financial Modeling Prep API."""

    def __init__(self):
        """Initialize FMP client."""
        super().__init__(
            base_url=Settings.FMP_BASE_URL,
            api_key=Settings.FMP_API_KEY,
        )

    def _get_params(self, **kwargs: Any) -> Dict[str, Any]:
        """Add API key to parameters."""
        params = {"apikey": self.api_key}
        params.update(kwargs)
        return params

    def _is_available(self) -> bool:
        """Check if the client is available."""
        return bool(self.api_key)

    @cache_response(ttl_minutes=5)
    def get_stock_quote(self, ticker: str) -> Dict[str, Any]:
        """
        Get real-time stock quote.

        Args:
            ticker: Stock ticker symbol (e.g., 'AAPL')

        Returns:
            Stock quote data including price, change, volume
        """
        if not self._is_available():
            return self._empty_quote(ticker)

        response = self.get(f"quote/{ticker.upper()}", params=self._get_params())

        if response and isinstance(response, list) and len(response) > 0:
            data = response[0]
            return {
                "ticker": ticker.upper(),
                "name": data.get("name", ""),
                "price": data.get("price", 0),
                "change": data.get("change", 0),
                "change_percent": data.get("changesPercentage", 0),
                "day_low": data.get("dayLow", 0),
                "day_high": data.get("dayHigh", 0),
                "year_low": data.get("yearLow", 0),
                "year_high": data.get("yearHigh", 0),
                "market_cap": data.get("marketCap", 0),
                "pe_ratio": data.get("pe", 0),
                "eps": data.get("eps", 0),
                "volume": data.get("volume", 0),
                "avg_volume": data.get("avgVolume", 0),
                "open": data.get("open", 0),
                "previous_close": data.get("previousClose", 0),
                "exchange": data.get("exchange", ""),
                "timestamp": datetime.now(UTC).isoformat(),
            }

        return self._empty_quote(ticker)

    @cache_response(ttl_minutes=5)
    def get_stock_quotes(self, tickers: List[str]) -> List[Dict[str, Any]]:
        """
        Get real-time quotes for multiple stocks.

        Args:
            tickers: List of stock ticker symbols

        Returns:
            List of stock quote data
        """
        if not self._is_available() or not tickers:
            return []

        ticker_str = ",".join([t.upper() for t in tickers])
        response = self.get(f"quote/{ticker_str}", params=self._get_params())

        if response and isinstance(response, list):
            return [
                {
                    "ticker": d.get("symbol", ""),
                    "name": d.get("name", ""),
                    "price": d.get("price", 0),
                    "change": d.get("change", 0),
                    "change_percent": d.get("changesPercentage", 0),
                    "market_cap": d.get("marketCap", 0),
                    "pe_ratio": d.get("pe", 0),
                    "volume": d.get("volume", 0),
                }
                for d in response
            ]

        return []

    @cache_response(ttl_minutes=10)
    def get_company_profile(self, ticker: str) -> Dict[str, Any]:
        """
        Get company profile and key information.

        Args:
            ticker: Stock ticker symbol

        Returns:
            Company profile data
        """
        if not self._is_available():
            return self._empty_profile(ticker)

        response = self.get(f"profile/{ticker.upper()}", params=self._get_params())

        if response and isinstance(response, list) and len(response) > 0:
            data = response[0]
            return {
                "ticker": ticker.upper(),
                "name": data.get("companyName", ""),
                "description": data.get("description", ""),
                "ceo": data.get("ceo", ""),
                "sector": data.get("sector", ""),
                "industry": data.get("industry", ""),
                "country": data.get("country", ""),
                "exchange": data.get("exchangeShortName", ""),
                "website": data.get("website", ""),
                "employees": data.get("fullTimeEmployees", 0),
                "market_cap": data.get("mktCap", 0),
                "beta": data.get("beta", 0),
                "dividend_yield": data.get("lastDiv", 0),
                "ipo_date": data.get("ipoDate", ""),
                "logo": data.get("image", ""),
                "timestamp": datetime.now(UTC).isoformat(),
            }

        return self._empty_profile(ticker)

    @cache_response(ttl_minutes=15)
    def get_historical_prices(
        self,
        ticker: str,
        period: str = "1M",
    ) -> Dict[str, Any]:
        """
        Get historical stock prices.

        Args:
            ticker: Stock ticker symbol
            period: Time period ('1D', '5D', '1M', '3M', '6M', '1Y', '5Y')

        Returns:
            Historical price data with OHLCV
        """
        if not self._is_available():
            return {"ticker": ticker, "historical": [], "period": period}

        # Map period to number of days
        period_map = {
            "1D": 1,
            "5D": 5,
            "1M": 30,
            "3M": 90,
            "6M": 180,
            "1Y": 365,
            "5Y": 1825,
        }

        days = period_map.get(period, 30)
        endpoint = f"historical-price-full/{ticker.upper()}"

        params = self._get_params()
        if days <= 5:
            # Use intraday for short periods
            endpoint = f"historical-chart/1hour/{ticker.upper()}"
        else:
            params["serietype"] = "line"

        response = self.get(endpoint, params=params)

        if response:
            # Handle different response formats
            if isinstance(response, dict) and "historical" in response:
                historical = response["historical"][:days]
            elif isinstance(response, list):
                historical = response[:days * 8]  # 8 hours per day for intraday
            else:
                historical = []

            return {
                "ticker": ticker.upper(),
                "period": period,
                "historical": [
                    {
                        "date": h.get("date", ""),
                        "open": h.get("open", 0),
                        "high": h.get("high", 0),
                        "low": h.get("low", 0),
                        "close": h.get("close", 0),
                        "volume": h.get("volume", 0),
                    }
                    for h in historical
                ],
                "timestamp": datetime.now(UTC).isoformat(),
            }

        return {"ticker": ticker, "historical": [], "period": period}

    @cache_response(ttl_minutes=30)
    def get_income_statement(
        self,
        ticker: str,
        period: str = "annual",
        limit: int = 5,
    ) -> Dict[str, Any]:
        """
        Get income statement data.

        Args:
            ticker: Stock ticker symbol
            period: 'annual' or 'quarter'
            limit: Number of periods to return

        Returns:
            Income statement data
        """
        if not self._is_available():
            return {"ticker": ticker, "statements": [], "period": period}

        endpoint = f"income-statement/{ticker.upper()}"
        params = self._get_params(period=period, limit=limit)

        response = self.get(endpoint, params=params)

        if response and isinstance(response, list):
            return {
                "ticker": ticker.upper(),
                "period": period,
                "statements": [
                    {
                        "date": s.get("date", ""),
                        "revenue": s.get("revenue", 0),
                        "cost_of_revenue": s.get("costOfRevenue", 0),
                        "gross_profit": s.get("grossProfit", 0),
                        "operating_income": s.get("operatingIncome", 0),
                        "net_income": s.get("netIncome", 0),
                        "eps": s.get("eps", 0),
                        "eps_diluted": s.get("epsdiluted", 0),
                        "ebitda": s.get("ebitda", 0),
                        "gross_margin": s.get("grossProfitRatio", 0),
                        "operating_margin": s.get("operatingIncomeRatio", 0),
                        "net_margin": s.get("netIncomeRatio", 0),
                    }
                    for s in response
                ],
                "timestamp": datetime.now(UTC).isoformat(),
            }

        return {"ticker": ticker, "statements": [], "period": period}

    @cache_response(ttl_minutes=30)
    def get_balance_sheet(
        self,
        ticker: str,
        period: str = "annual",
        limit: int = 5,
    ) -> Dict[str, Any]:
        """
        Get balance sheet data.

        Args:
            ticker: Stock ticker symbol
            period: 'annual' or 'quarter'
            limit: Number of periods to return

        Returns:
            Balance sheet data
        """
        if not self._is_available():
            return {"ticker": ticker, "statements": [], "period": period}

        endpoint = f"balance-sheet-statement/{ticker.upper()}"
        params = self._get_params(period=period, limit=limit)

        response = self.get(endpoint, params=params)

        if response and isinstance(response, list):
            return {
                "ticker": ticker.upper(),
                "period": period,
                "statements": [
                    {
                        "date": s.get("date", ""),
                        "total_assets": s.get("totalAssets", 0),
                        "total_liabilities": s.get("totalLiabilities", 0),
                        "total_equity": s.get("totalStockholdersEquity", 0),
                        "cash": s.get("cashAndCashEquivalents", 0),
                        "total_debt": s.get("totalDebt", 0),
                        "net_debt": s.get("netDebt", 0),
                        "inventory": s.get("inventory", 0),
                        "receivables": s.get("netReceivables", 0),
                        "payables": s.get("accountPayables", 0),
                    }
                    for s in response
                ],
                "timestamp": datetime.now(UTC).isoformat(),
            }

        return {"ticker": ticker, "statements": [], "period": period}

    @cache_response(ttl_minutes=30)
    def get_cash_flow(
        self,
        ticker: str,
        period: str = "annual",
        limit: int = 5,
    ) -> Dict[str, Any]:
        """
        Get cash flow statement data.

        Args:
            ticker: Stock ticker symbol
            period: 'annual' or 'quarter'
            limit: Number of periods to return

        Returns:
            Cash flow statement data
        """
        if not self._is_available():
            return {"ticker": ticker, "statements": [], "period": period}

        endpoint = f"cash-flow-statement/{ticker.upper()}"
        params = self._get_params(period=period, limit=limit)

        response = self.get(endpoint, params=params)

        if response and isinstance(response, list):
            return {
                "ticker": ticker.upper(),
                "period": period,
                "statements": [
                    {
                        "date": s.get("date", ""),
                        "operating_cash_flow": s.get("operatingCashFlow", 0),
                        "investing_cash_flow": s.get("netCashUsedForInvestingActivites", 0),
                        "financing_cash_flow": s.get("netCashUsedProvidedByFinancingActivities", 0),
                        "free_cash_flow": s.get("freeCashFlow", 0),
                        "capex": s.get("capitalExpenditure", 0),
                        "dividends_paid": s.get("dividendsPaid", 0),
                        "stock_repurchased": s.get("commonStockRepurchased", 0),
                    }
                    for s in response
                ],
                "timestamp": datetime.now(UTC).isoformat(),
            }

        return {"ticker": ticker, "statements": [], "period": period}

    @cache_response(ttl_minutes=15)
    def get_key_metrics(self, ticker: str) -> Dict[str, Any]:
        """
        Get key financial metrics and ratios.

        Args:
            ticker: Stock ticker symbol

        Returns:
            Key metrics including P/E, P/B, ROE, etc.
        """
        if not self._is_available():
            return {"ticker": ticker, "metrics": {}}

        response = self.get(
            f"key-metrics-ttm/{ticker.upper()}",
            params=self._get_params(),
        )

        if response and isinstance(response, list) and len(response) > 0:
            data = response[0]
            return {
                "ticker": ticker.upper(),
                "metrics": {
                    "pe_ratio": data.get("peRatioTTM", 0),
                    "peg_ratio": data.get("pegRatioTTM", 0),
                    "price_to_book": data.get("priceToBookRatioTTM", 0),
                    "price_to_sales": data.get("priceToSalesRatioTTM", 0),
                    "ev_to_ebitda": data.get("enterpriseValueOverEBITDATTM", 0),
                    "roe": data.get("roeTTM", 0),
                    "roa": data.get("roaTTM", 0),
                    "dividend_yield": data.get("dividendYieldTTM", 0),
                    "debt_to_equity": data.get("debtToEquityTTM", 0),
                    "current_ratio": data.get("currentRatioTTM", 0),
                    "quick_ratio": data.get("quickRatioTTM", 0),
                    "revenue_per_share": data.get("revenuePerShareTTM", 0),
                    "earnings_per_share": data.get("netIncomePerShareTTM", 0),
                    "free_cash_flow_per_share": data.get("freeCashFlowPerShareTTM", 0),
                },
                "timestamp": datetime.now(UTC).isoformat(),
            }

        return {"ticker": ticker, "metrics": {}}

    @cache_response(ttl_minutes=10)
    def get_peer_comparison(self, ticker: str) -> Dict[str, Any]:
        """
        Get stock peers for comparison.

        Args:
            ticker: Stock ticker symbol

        Returns:
            List of peer companies with basic metrics
        """
        if not self._is_available():
            return {"ticker": ticker, "peers": []}

        response = self.get(
            f"stock_peers",
            params=self._get_params(symbol=ticker.upper()),
        )

        if response and isinstance(response, list) and len(response) > 0:
            peers = response[0].get("peersList", [])

            # Get quotes for peers
            if peers:
                peer_quotes = self.get_stock_quotes(peers[:10])
                return {
                    "ticker": ticker.upper(),
                    "peers": peer_quotes,
                    "timestamp": datetime.now(UTC).isoformat(),
                }

        return {"ticker": ticker, "peers": []}

    @cache_response(ttl_minutes=5)
    def search_ticker(self, query: str, limit: int = 10) -> List[Dict[str, str]]:
        """
        Search for stock ticker by company name or ticker.

        Args:
            query: Search query (company name or ticker)
            limit: Maximum number of results

        Returns:
            List of matching companies with ticker and name
        """
        if not self._is_available() or not query:
            return []

        response = self.get(
            "search",
            params=self._get_params(query=query, limit=limit),
        )

        if response and isinstance(response, list):
            return [
                {
                    "ticker": r.get("symbol", ""),
                    "name": r.get("name", ""),
                    "exchange": r.get("stockExchange", ""),
                    "type": r.get("exchangeShortName", ""),
                }
                for r in response
            ]

        return []

    @cache_response(ttl_minutes=60)
    def get_sector_performance(self) -> List[Dict[str, Any]]:
        """
        Get sector performance data.

        Returns:
            List of sectors with performance metrics
        """
        if not self._is_available():
            return []

        response = self.get("sector-performance", params=self._get_params())

        if response and isinstance(response, list):
            return [
                {
                    "sector": r.get("sector", ""),
                    "change_percent": float(r.get("changesPercentage", "0").strip("%")),
                }
                for r in response
            ]

        return []

    @cache_response(ttl_minutes=15)
    def get_earnings_calendar(
        self,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get upcoming earnings calendar.

        Args:
            from_date: Start date (YYYY-MM-DD)
            to_date: End date (YYYY-MM-DD)

        Returns:
            List of upcoming earnings events
        """
        if not self._is_available():
            return []

        params = self._get_params()
        if from_date:
            params["from"] = from_date
        if to_date:
            params["to"] = to_date

        response = self.get("earning_calendar", params=params)

        if response and isinstance(response, list):
            return [
                {
                    "ticker": r.get("symbol", ""),
                    "date": r.get("date", ""),
                    "eps_estimate": r.get("epsEstimated"),
                    "eps_actual": r.get("eps"),
                    "revenue_estimate": r.get("revenueEstimated"),
                    "revenue_actual": r.get("revenue"),
                    "time": r.get("time", ""),
                }
                for r in response[:50]  # Limit results
            ]

        return []

    @cache_response(ttl_minutes=30)
    def get_geographic_revenue(self, ticker: str) -> Dict[str, Any]:
        """
        Get geographic revenue breakdown for company exposure analysis.

        Args:
            ticker: Stock ticker symbol

        Returns:
            Geographic revenue data by region
        """
        if not self._is_available():
            return {"ticker": ticker, "segments": []}

        response = self.get(
            f"revenue-geographic-segmentation",
            params=self._get_params(symbol=ticker.upper()),
        )

        if response and isinstance(response, list):
            segments = []
            for item in response:
                if isinstance(item, dict):
                    for date, data in item.items():
                        if isinstance(data, dict):
                            for region, value in data.items():
                                segments.append({
                                    "region": region,
                                    "revenue": value,
                                    "date": date,
                                })
            return {
                "ticker": ticker.upper(),
                "segments": segments,
                "timestamp": datetime.now(UTC).isoformat(),
            }

        return {"ticker": ticker, "segments": []}

    def _empty_quote(self, ticker: str) -> Dict[str, Any]:
        """Return empty quote structure."""
        return {
            "ticker": ticker.upper(),
            "name": "",
            "price": 0,
            "change": 0,
            "change_percent": 0,
            "market_cap": 0,
            "pe_ratio": 0,
            "volume": 0,
            "error": "Data not available",
            "timestamp": datetime.now(UTC).isoformat(),
        }

    def _empty_profile(self, ticker: str) -> Dict[str, Any]:
        """Return empty profile structure."""
        return {
            "ticker": ticker.upper(),
            "name": "",
            "description": "",
            "sector": "",
            "industry": "",
            "country": "",
            "error": "Profile not available",
            "timestamp": datetime.now(UTC).isoformat(),
        }
