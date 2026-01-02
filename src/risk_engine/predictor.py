"""
Risk Predictor module.
Forecasting future risk scores based on historical data using exponential smoothing.
"""

from typing import List


class RiskPredictor:
    """Predicts future risk scores based on historical data."""

    def __init__(self, alpha: float = 0.3):
        """
        Initialize the predictor.

        Args:
            alpha: Smoothing factor (0 < alpha < 1). Higher values weigh recent data more heavily.
        """
        self.alpha = alpha

    def predict_next_score(self, history: List[float]) -> float:
        """
        Predict the next risk score using Simple Exponential Smoothing.

        Args:
            history: List of historical risk scores (ordered chronologically).

        Returns:
            Predicted score for the next time step.
        """
        if not history:
            return 50.0  # Default neutral score if no history

        if len(history) == 1:
            return history[0]

        # Simple Exponential Smoothing
        # S_t = alpha * X_t + (1 - alpha) * S_{t-1}

        # Initialize trend
        forecast = history[0]

        for observation in history:
            forecast = self.alpha * observation + (1 - self.alpha) * forecast

        return round(forecast, 2)

    def generate_feature_vector(
        self,
        political: float,
        economic: float,
        security: float,
        trade: float,
        news_sentiment: float,
    ) -> List[float]:
        """
        Generate a feature vector for potential future ML training.

        Args:
            political: Political risk score
            economic: Economic risk score
            security: Security risk score
            trade: Trade risk score
            news_sentiment: News sentiment score (-1 to 1)

        Returns:
            Normalized feature list
        """
        return [
            political / 100.0,
            economic / 100.0,
            security / 100.0,
            trade / 100.0,
            (news_sentiment + 1) / 2.0,  # Normalize to 0-1
        ]
