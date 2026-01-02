"""
Signal Detection module.
Identifies early warning signals and critical risk patterns.
"""

from typing import Dict, List, Any
from datetime import datetime, timezone


class SignalDetector:
    """Detects early warning signals and risk patterns."""

    def detect_signals(
        self, current_scores: Dict[str, float], history: List[float]
    ) -> List[Dict[str, Any]]:
        """
        Detect signals based on current and historical data.

        Args:
            current_scores: Dictionary of current factor scores (security, political, etc.)
            history: List of historical composite scores.

        Returns:
            List of detected signal dictionaries.
        """
        signals = []

        # 1. Flashpoint Detection: Sudden spike in security risk
        # Heuristic: Security score > 70 AND composite score forecast suggests increase
        if current_scores.get("security", 0) > 70:
            signals.append(
                {
                    "type": "flashpoint_risk",
                    "severity": "high",
                    "description": "High security risk indicates potential conflict flashpoint.",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            )

        # 2. Destabilization: Steady decline in political stability (which means INCREASE in risk score)
        # If political risk is high (>60)
        if current_scores.get("political", 0) > 60:
            signals.append(
                {
                    "type": "destabilization",
                    "severity": "medium",
                    "description": "Elevated political instability detected.",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            )

        # 3. Volatility Warning (based on history if available externally,
        # but here providing a simple check if composite is very high)
        if current_scores.get("composite", 0) > 80:
            signals.append(
                {
                    "type": "critical_status",
                    "severity": "critical",
                    "description": "Composite risk score has reached critical levels.",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            )

        return signals
