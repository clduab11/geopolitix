"""
Benchmark script for RiskScorer.
Simulates API latency to measure the impact of parallelization.
"""

import time
import logging
from unittest.mock import MagicMock, patch
from src.risk_engine.scoring import RiskScorer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("benchmark")


def mock_with_delay(return_value, delay=0.2):
    """Return a function that sleeps then returns a value."""

    def _mock(*args, **kwargs):
        time.sleep(delay)
        return return_value

    return _mock


def run_benchmark(num_countries=10):
    """Run the benchmark."""
    logger.info(f"Starting benchmark with {num_countries} countries...")

    # Mock data sources to avoid real API calls but simulate latency
    with (
        patch("src.risk_engine.scoring.GDELTClient") as MockGDELT,
        patch("src.risk_engine.scoring.NewsAPIClient") as MockNewsAPI,
        patch("src.risk_engine.scoring.WorldBankClient") as MockWorldBank,
        patch("src.risk_engine.scoring.ACLEDClient") as MockACLED,
    ):
        # Setup mocks with simulated network delay
        # Total delay per country approx:
        # Political (WorldBank) + Economic (WorldBank) + Security (ACLED) + Trade (GDELT)
        # = 0.1s + 0.1s + 0.1s + 0.1s = 0.4s per country sequential

        # WorldBank: political and economic
        wb_instance = MockWorldBank.return_value
        wb_instance.calculate_governance_risk_score.side_effect = mock_with_delay(
            60.0, 0.1
        )
        wb_instance.get_governance_indicators.side_effect = mock_with_delay(
            {
                "indicators": {
                    "Government Effectiveness": {"value": 0.5},
                    "Regulatory Quality": {"value": 0.5},
                }
            },
            0.1,
        )

        # ACLED: security
        acled_instance = MockACLED.return_value
        acled_instance.calculate_conflict_risk_score.side_effect = mock_with_delay(
            40.0, 0.1
        )

        # GDELT: trade (sentiment)
        gdelt_instance = MockGDELT.return_value
        gdelt_instance.get_sentiment_analysis.side_effect = mock_with_delay(
            {"total_articles": 10, "sentiment_ratio": 1.5}, 0.1
        )

        # Initialize scorer (uses mocked clients)
        scorer = RiskScorer()

        # Mock countries list
        countries = [f"Country_{i}" for i in range(num_countries)]

        start_time = time.time()
        results = scorer.get_batch_scores(countries)
        end_time = time.time()

        duration = end_time - start_time
        logger.info(f"Processed {len(results)} countries in {duration:.4f} seconds.")
        logger.info(f"Average time per country: {duration / len(results):.4f} seconds.")

        return duration


if __name__ == "__main__":
    run_benchmark(10)
