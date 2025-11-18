"""Risk scoring algorithms and composite score calculation."""

from typing import Any, Dict, List, Optional
import pandas as pd
from datetime import datetime

from config.risk_thresholds import RiskThresholds
from src.data_sources.gdelt import GDELTClient
from src.data_sources.newsapi import NewsAPIClient
from src.data_sources.worldbank import WorldBankClient
from src.data_sources.acled import ACLEDClient
from src.utils.logger import get_logger
from src.utils.transformers import country_to_iso

logger = get_logger(__name__)


class RiskScorer:
    """Calculate composite geopolitical risk scores."""

    def __init__(self):
        """Initialize risk scorer with data source clients."""
        self.gdelt = GDELTClient()
        self.newsapi = NewsAPIClient()
        self.worldbank = WorldBankClient()
        self.acled = ACLEDClient()
        self.weights = RiskThresholds.FACTOR_WEIGHTS

    def calculate_composite_score(
        self,
        country: str,
        include_news: bool = True,
    ) -> Dict[str, Any]:
        """
        Calculate composite risk score for a country.

        Args:
            country: Country name
            include_news: Whether to include news sentiment analysis

        Returns:
            Dictionary with composite score and breakdown
        """
        iso_code = country_to_iso(country)

        # Get individual factor scores
        political_score = self._calculate_political_score(iso_code)
        economic_score = self._calculate_economic_score(iso_code)
        security_score = self._calculate_security_score(country)
        trade_score = self._calculate_trade_score(country)

        # Apply weights
        composite = (
            political_score * self.weights["political"]
            + economic_score * self.weights["economic"]
            + security_score * self.weights["security"]
            + trade_score * self.weights["trade"]
        )

        # Get risk level
        risk_level = RiskThresholds.get_risk_level(composite)

        return {
            "country": country,
            "iso_code": iso_code,
            "composite_score": round(composite, 1),
            "risk_level": risk_level,
            "factors": {
                "political": round(political_score, 1),
                "economic": round(economic_score, 1),
                "security": round(security_score, 1),
                "trade": round(trade_score, 1),
            },
            "weights": self.weights,
            "timestamp": datetime.utcnow().isoformat(),
        }

    def _calculate_political_score(self, iso_code: str) -> float:
        """Calculate political stability risk score."""
        try:
            score = self.worldbank.calculate_governance_risk_score(iso_code)
            return score
        except Exception as e:
            logger.error(f"Error calculating political score for {iso_code}: {e}")
            return 50.0

    def _calculate_economic_score(self, iso_code: str) -> float:
        """Calculate economic risk score."""
        try:
            # Use regulatory quality and government effectiveness as proxy
            indicators = self.worldbank.get_governance_indicators(iso_code)

            if indicators and indicators.get("indicators"):
                gov_eff = indicators["indicators"].get("Government Effectiveness", {})
                reg_qual = indicators["indicators"].get("Regulatory Quality", {})

                values = []
                if gov_eff.get("value"):
                    values.append(gov_eff["value"])
                if reg_qual.get("value"):
                    values.append(reg_qual["value"])

                if values:
                    avg = sum(values) / len(values)
                    # Convert from [-2.5, 2.5] to [0, 100] risk
                    return ((2.5 - avg) / 5) * 100

            return 50.0
        except Exception as e:
            logger.error(f"Error calculating economic score for {iso_code}: {e}")
            return 50.0

    def _calculate_security_score(self, country: str) -> float:
        """Calculate security/conflict risk score."""
        try:
            return self.acled.calculate_conflict_risk_score(country)
        except Exception as e:
            logger.error(f"Error calculating security score for {country}: {e}")
            return 30.0

    def _calculate_trade_score(self, country: str) -> float:
        """Calculate trade relations risk score."""
        try:
            # Use news sentiment around trade topics as proxy
            sentiment = self.gdelt.get_sentiment_analysis(country, "trade")

            if sentiment and sentiment.get("total_articles", 0) > 0:
                ratio = sentiment.get("sentiment_ratio", 1.0)
                # Lower ratio = more negative sentiment = higher risk
                return min(100, max(0, (1 / max(ratio, 0.1)) * 20))

            return 40.0
        except Exception as e:
            logger.error(f"Error calculating trade score for {country}: {e}")
            return 40.0

    def get_batch_scores(
        self,
        countries: List[str],
    ) -> pd.DataFrame:
        """
        Calculate risk scores for multiple countries.

        Args:
            countries: List of country names

        Returns:
            DataFrame with all scores
        """
        results = []

        for country in countries:
            try:
                score_data = self.calculate_composite_score(country)
                results.append({
                    "country": score_data["country"],
                    "iso_code": score_data["iso_code"],
                    "composite_score": score_data["composite_score"],
                    "risk_level": score_data["risk_level"],
                    "political": score_data["factors"]["political"],
                    "economic": score_data["factors"]["economic"],
                    "security": score_data["factors"]["security"],
                    "trade": score_data["factors"]["trade"],
                })
            except Exception as e:
                logger.error(f"Error scoring {country}: {e}")
                continue

        return pd.DataFrame(results)

    def get_risk_changes(
        self,
        country: str,
        current_score: float,
        historical_scores: List[float],
    ) -> Dict[str, Any]:
        """
        Analyze risk score changes over time.

        Args:
            country: Country name
            current_score: Current risk score
            historical_scores: List of historical scores (oldest first)

        Returns:
            Change analysis dictionary
        """
        if not historical_scores:
            return {
                "country": country,
                "current": current_score,
                "change_7d": 0,
                "change_30d": 0,
                "trend": "stable",
            }

        # Calculate changes
        change_7d = current_score - historical_scores[-1] if len(historical_scores) >= 1 else 0
        change_30d = current_score - historical_scores[0] if len(historical_scores) >= 4 else 0

        # Determine trend
        if change_30d > 5:
            trend = "increasing"
        elif change_30d < -5:
            trend = "decreasing"
        else:
            trend = "stable"

        return {
            "country": country,
            "current": current_score,
            "change_7d": round(change_7d, 1),
            "change_30d": round(change_30d, 1),
            "trend": trend,
        }

    def generate_alerts(
        self,
        scores_df: pd.DataFrame,
        threshold: int = None,
    ) -> List[Dict[str, Any]]:
        """
        Generate alerts for high-risk countries.

        Args:
            scores_df: DataFrame with risk scores
            threshold: Score threshold for alerts

        Returns:
            List of alert dictionaries
        """
        threshold = threshold or RiskThresholds.ALERT_THRESHOLD_ABSOLUTE
        alerts = []

        for _, row in scores_df.iterrows():
            if row["composite_score"] >= threshold:
                alerts.append({
                    "country": row["country"],
                    "score": row["composite_score"],
                    "risk_level": row["risk_level"],
                    "primary_factor": self._get_primary_factor(row),
                    "timestamp": datetime.utcnow().isoformat(),
                })

        # Sort by score descending
        alerts.sort(key=lambda x: x["score"], reverse=True)

        return alerts

    def _get_primary_factor(self, row: pd.Series) -> str:
        """Get the primary risk factor for a country."""
        factors = {
            "political": row.get("political", 0),
            "economic": row.get("economic", 0),
            "security": row.get("security", 0),
            "trade": row.get("trade", 0),
        }
        return max(factors, key=factors.get)


def get_default_countries() -> List[str]:
    """Get default list of countries to monitor."""
    return [
        "United States",
        "China",
        "Russia",
        "India",
        "Brazil",
        "United Kingdom",
        "Germany",
        "France",
        "Japan",
        "South Korea",
        "Iran",
        "Saudi Arabia",
        "Turkey",
        "Israel",
        "Ukraine",
        "Taiwan",
        "Pakistan",
        "Nigeria",
        "South Africa",
        "Mexico",
        "Indonesia",
        "Egypt",
        "Thailand",
        "Vietnam",
        "Poland",
    ]
