"""
Trend Analysis module.
Calculates velocity, acceleration, and volatility of risk scores.
"""

from typing import List, Dict, Any
import numpy as np


class TrendAnalyzer:
    """Analyzes trends in risk scores."""

    def analyze_trend(self, history: List[float]) -> Dict[str, Any]:
        """
        Analyze the trend of risk scores.

        Args:
            history: List of historical risk scores (ordered chronologically).

        Returns:
            Dictionary containing trend metrics.
        """
        if not history or len(history) < 2:
            return {
                "velocity": 0.0,
                "acceleration": 0.0,
                "volatility": 0.0,
                "direction": "stable",
            }

        # Calculate Velocity (Rate of Change)
        # Simple derivative of the last step
        velocity = history[-1] - history[-2]

        # Calculate Acceleration (Change in Velocity)
        acceleration = 0.0
        if len(history) >= 3:
            prev_velocity = history[-2] - history[-3]
            acceleration = velocity - prev_velocity

        # Calculate Volatility (Standard Deviation of recent history)
        # Use last 10 points or all points if less than 10
        window = history[-10:] if len(history) > 10 else history
        volatility = float(np.std(window)) if len(window) > 1 else 0.0

        # Determine Direction
        if velocity > 5.0:
            direction = "rapidly_increasing"
        elif velocity > 1.0:
            direction = "increasing"
        elif velocity < -5.0:
            direction = "rapidly_decreasing"
        elif velocity < -1.0:
            direction = "decreasing"
        else:
            direction = "stable"

        return {
            "velocity": round(velocity, 2),
            "acceleration": round(acceleration, 2),
            "volatility": round(volatility, 2),
            "direction": direction,
        }
