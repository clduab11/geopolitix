"""Weight management for risk factor calculations."""

from typing import Dict, Optional
from config.risk_thresholds import RiskThresholds


class WeightManager:
    """Manage and customize risk factor weights."""

    def __init__(self):
        """Initialize with default weights."""
        self._weights = RiskThresholds.FACTOR_WEIGHTS.copy()
        self._political_subfactors = RiskThresholds.POLITICAL_SUBFACTORS.copy()
        self._economic_subfactors = RiskThresholds.ECONOMIC_SUBFACTORS.copy()
        self._security_subfactors = RiskThresholds.SECURITY_SUBFACTORS.copy()
        self._trade_subfactors = RiskThresholds.TRADE_SUBFACTORS.copy()

    @property
    def weights(self) -> Dict[str, float]:
        """Get current factor weights."""
        return self._weights.copy()

    def set_weights(self, weights: Dict[str, float]) -> None:
        """
        Set custom factor weights.

        Args:
            weights: Dictionary of factor weights (must sum to 1.0)

        Raises:
            ValueError: If weights don't sum to 1.0
        """
        total = sum(weights.values())
        if abs(total - 1.0) > 0.001:
            raise ValueError(f"Weights must sum to 1.0, got {total}")

        required_keys = {"political", "economic", "security", "trade"}
        if set(weights.keys()) != required_keys:
            raise ValueError(f"Must provide all weights: {required_keys}")

        self._weights = weights.copy()

    def reset_weights(self) -> None:
        """Reset weights to defaults."""
        self._weights = RiskThresholds.FACTOR_WEIGHTS.copy()

    def get_subfactor_weights(self, factor: str) -> Dict[str, float]:
        """
        Get subfactor weights for a main factor.

        Args:
            factor: Main factor name

        Returns:
            Subfactor weights dictionary
        """
        subfactors = {
            "political": self._political_subfactors,
            "economic": self._economic_subfactors,
            "security": self._security_subfactors,
            "trade": self._trade_subfactors,
        }
        return subfactors.get(factor, {}).copy()

    def set_subfactor_weights(
        self,
        factor: str,
        subfactors: Dict[str, float],
    ) -> None:
        """
        Set custom subfactor weights.

        Args:
            factor: Main factor name
            subfactors: Subfactor weights dictionary
        """
        total = sum(subfactors.values())
        if abs(total - 1.0) > 0.001:
            raise ValueError(f"Subfactor weights must sum to 1.0, got {total}")

        if factor == "political":
            self._political_subfactors = subfactors.copy()
        elif factor == "economic":
            self._economic_subfactors = subfactors.copy()
        elif factor == "security":
            self._security_subfactors = subfactors.copy()
        elif factor == "trade":
            self._trade_subfactors = subfactors.copy()
        else:
            raise ValueError(f"Unknown factor: {factor}")

    def calculate_weighted_score(
        self,
        scores: Dict[str, float],
        custom_weights: Optional[Dict[str, float]] = None,
    ) -> float:
        """
        Calculate weighted composite score.

        Args:
            scores: Dictionary of factor scores
            custom_weights: Optional custom weights to use

        Returns:
            Weighted composite score
        """
        weights = custom_weights or self._weights

        total = 0.0
        for factor, score in scores.items():
            if factor in weights:
                total += score * weights[factor]

        return round(total, 1)

    def get_weight_presets(self) -> Dict[str, Dict[str, float]]:
        """
        Get predefined weight presets for different use cases.

        Returns:
            Dictionary of preset names to weight configurations
        """
        return {
            "balanced": {
                "political": 0.25,
                "economic": 0.25,
                "security": 0.25,
                "trade": 0.25,
            },
            "security_focused": {
                "political": 0.20,
                "economic": 0.15,
                "security": 0.50,
                "trade": 0.15,
            },
            "economic_focused": {
                "political": 0.15,
                "economic": 0.50,
                "security": 0.15,
                "trade": 0.20,
            },
            "trade_focused": {
                "political": 0.15,
                "economic": 0.25,
                "security": 0.10,
                "trade": 0.50,
            },
            "political_focused": {
                "political": 0.50,
                "economic": 0.20,
                "security": 0.15,
                "trade": 0.15,
            },
        }

    def apply_preset(self, preset_name: str) -> None:
        """
        Apply a weight preset.

        Args:
            preset_name: Name of the preset to apply
        """
        presets = self.get_weight_presets()
        if preset_name not in presets:
            raise ValueError(f"Unknown preset: {preset_name}")

        self._weights = presets[preset_name].copy()
