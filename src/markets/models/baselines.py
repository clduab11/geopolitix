"""
Baseline forecasting models.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
from datetime import datetime
import numpy as np

from ..types import MarketData, Prediction


class BaseForecaster(ABC):
    """Abstract base class for forecasters."""

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def train_predict(self, data: MarketData) -> Prediction:
        """
        Train on history (if needed) and predict the NEXT step.
        For a specialized lab, we might split train/predict, but for baselines
        doing it in one go is often easier for rolling backtests.
        """
        pass


class MovingAverageForecaster(BaseForecaster):
    """Predicts next value based on simple moving average."""

    def __init__(self, window: int = 7):
        super().__init__(f"MA({window})")
        self.window = window

    def train_predict(self, data: MarketData) -> Prediction:
        df = data.data
        if len(df) < self.window:
            pred_val = df["price"].mean() if not df.empty else 0.5
        else:
            pred_val = df["price"].iloc[-self.window :].mean()

        return Prediction(
            market_id=data.market_id,
            timestamp=datetime.now(),
            model_name=self.name,
            predicted_value=float(pred_val),
            confidence=0.5,  # Dummy confidence
            horizon="1d",
            metadata={"window": self.window},
        )


class LogisticCalibrator(BaseForecaster):
    """
    Toy example of a 'calibrated' model.
    In reality, this would learn a scaling factor.
    Here we just apply a sigmoid transform to 'smooth' extreme probabilities
    towards 0.5, mimicking a conservative prior.
    """

    def __init__(self, temperature: float = 1.0):
        super().__init__("LogisticCalibrator")
        self.temperature = temperature

    def train_predict(self, data: MarketData) -> Prediction:
        # Just take the last price as the base 'logit'
        if data.data.empty:
            last_price = 0.5
        else:
            last_price = data.data["price"].iloc[-1]

        # Logit transform
        # p = 1 / (1 + exp(-x)) -> x = ln(p/(1-p))
        eps = 1e-6
        p = max(eps, min(1 - eps, last_price))
        logit = np.log(p / (1 - p))

        # Apply temperature scaling (dampening)
        # temperature > 1 makes it more uniform (closer to 0.5)
        scaled_logit = logit / self.temperature
        calibrated_p = 1 / (1 + np.exp(-scaled_logit))

        return Prediction(
            market_id=data.market_id,
            timestamp=datetime.now(),
            model_name=self.name,
            predicted_value=float(calibrated_p),
            confidence=0.8,
            horizon="1d",
            metadata={"temperature": self.temperature, "base_price": last_price},
        )
