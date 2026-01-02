#!/usr/bin/env python3
"""
CLI entry point to run the Markets Lab pipeline.
"""

import sys
import os
import json
import argparse
from datetime import datetime
import pandas as pd

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from src.markets.connectors import MockConnector
from src.markets.models import MovingAverageForecaster, LogisticCalibrator
from src.markets.pipeline import MarketPipeline
from src.markets.eval import BacktestHarness
from src.utils.logger import get_logger

logger = get_logger("markets_cli")


def save_artifacts(config, results):
    """Save run results to artifacts directory."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    artifact_dir = f"artifacts/runs/{timestamp}"
    os.makedirs(artifact_dir, exist_ok=True)

    # Save Config
    with open(f"{artifact_dir}/config.json", "w") as f:
        json.dump(config, f, indent=2)

    # Save Results Summary
    summary = []
    for res in results:
        summary.append(
            {
                "model": res.model_name,
                "metrics": res.metrics,
                "predictions_count": len(res.predictions),
            }
        )

    with open(f"{artifact_dir}/results.json", "w") as f:
        json.dump(summary, f, indent=2)

    # Save Predictions
    all_preds = []
    for res in results:
        for p in res.predictions:
            all_preds.append(
                {
                    "model": p.model_name,
                    "timestamp": p.timestamp.isoformat(),
                    "predicted": p.predicted_value,
                    "confidence": p.confidence,
                }
            )

    if all_preds:
        df = pd.DataFrame(all_preds)
        df.to_csv(f"{artifact_dir}/sample_predictions.csv", index=False)

    logger.info(f"Artifacts saved to {artifact_dir}")
    return artifact_dir


def main():
    parser = argparse.ArgumentParser(description="Run Markets Lab Pipeline")
    parser.add_argument("--symbol", type=str, default="GPT5")
    parser.add_argument("--days", type=int, default=30)
    parser.add_argument(
        "--provider",
        type=str,
        default="mock",
        choices=["mock", "polymarket"],
        help="Market data provider",
    )
    args = parser.parse_args()

    logger.info("Starting Markets Lab Pipeline...")

    # Configure Pipeline
    if args.provider == "polymarket":
        from src.markets.connectors import PolymarketConnector
        from config.settings import Settings

        config = {
            "POLYMARKET_API_URL": Settings.POLYMARKET_API_URL,
            "POLYMARKET_GAMMA_URL": Settings.POLYMARKET_GAMMA_URL,
            "POLYMARKET_API_KEY": Settings.POLYMARKET_API_KEY,
        }
        connector = PolymarketConnector(config=config)
    else:
        connector = MockConnector()

    models = [MovingAverageForecaster(window=7), LogisticCalibrator(temperature=1.2)]
    backtester = BacktestHarness()

    pipeline = MarketPipeline(connector, models, backtester)

    # Fetch Data
    logger.info(f"Fetching data for {args.symbol}...")
    data_map = pipeline.fetch_data([args.symbol])

    # Run Backtest
    logger.info("Running backtest...")
    end_date = datetime.now()
    start_date = end_date - pd.Timedelta(days=args.days)

    results = pipeline.run_backtest(data_map, start_date, end_date)

    # Save Artifacts
    config = {
        "symbol": args.symbol,
        "days": args.days,
        "models": [m.name for m in models],
    }

    artifact_path = save_artifacts(config, results)
    logger.info("Pipeline completed successfully.")


if __name__ == "__main__":
    main()
