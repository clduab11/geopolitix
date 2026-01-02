"""
Backtesting engine.
"""

import pandas as pd
import numpy as np
from typing import List, Dict
from datetime import datetime

from ..types import MarketData, BacktestResult, Prediction
from ..models.baselines import BaseForecaster


class BacktestHarness:
    """
    Runs a walk-forward backtest.
    """

    def run(
        self,
        data: MarketData,
        models: List[BaseForecaster],
        start_date: datetime,
        end_date: datetime,
    ) -> BacktestResult:
        """
        Simulate the past.
        For each day in [start_date, end_date]:
           1. Mask data to only show history up to t-1
           2. Ask models to predict t
           3. Compare prediction to actual t
        """
        df = data.data.sort_values("timestamp")

        # Filter strictly within range
        mask = (df["timestamp"] >= start_date) & (df["timestamp"] <= end_date)
        test_period = df[mask]

        all_predictions = []
        metrics = {}

        # Simple walk-forward
        # This is computationally expensive for large data, but fine for prototype
        total_brier = 0.0
        total_log_loss = 0.0
        count = 0

        # We need at least one model, assume the first one for the main result container
        # Ideally we'd return a result per model, but sticking to simplifications
        primary_model = models[0]

        for idx, row in test_period.iterrows():
            current_time = row["timestamp"]
            actual_price = row["price"]

            # Create a view of data UP TO just before this timestamp
            history_mask = df["timestamp"] < current_time
            history_df = df[history_mask]

            # Create a localized MarketData slice
            history_data = MarketData(
                market_id=data.market_id,
                symbol=data.symbol,
                source=data.source,
                data=history_df,
                metadata=data.metadata,
            )

            # Predict
            # For this harness, we'll just track the primary model's performance
            pred = primary_model.train_predict(history_data)

            # Evaluate
            diff = pred.predicted_value - actual_price
            brier = diff**2

            # Log Loss: - (y log(p) + (1-y) log(1-p))
            # Treat price as probability if it's 0-1, or just binary outcome?
            # Markets are usually probabilities of binary events.
            # If price is 0.7, it means 70% chance.
            # But we don't have the "resolution" event here, just price stream.
            # For price stream forecasting, RMSE (Brier) is appropriate.
            # Log Loss is undefined unless we know the binary outcome.
            # We will use the Brier score as the main metric for price-tracking.

            total_brier += brier
            count += 1

            all_predictions.append(pred)

        metrics = {
            "brier_score": total_brier / count if count > 0 else 0.0,
            "count": count,
        }

        return BacktestResult(
            model_name=primary_model.name,
            start_date=start_date,
            end_date=end_date,
            metrics=metrics,
            predictions=all_predictions,
            config={"mode": "walk-forward"},
        )
