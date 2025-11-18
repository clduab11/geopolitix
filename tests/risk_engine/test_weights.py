"""Tests for weight management."""

import pytest
from src.risk_engine.weights import WeightManager


class TestWeightManager:
    """Test cases for WeightManager."""

    def test_init(self):
        """Test weight manager initialization."""
        manager = WeightManager()
        weights = manager.weights

        assert "political" in weights
        assert "economic" in weights
        assert "security" in weights
        assert "trade" in weights
        assert abs(sum(weights.values()) - 1.0) < 0.001

    def test_set_weights_valid(self):
        """Test setting valid weights."""
        manager = WeightManager()
        new_weights = {
            "political": 0.4,
            "economic": 0.3,
            "security": 0.2,
            "trade": 0.1,
        }

        manager.set_weights(new_weights)
        assert manager.weights == new_weights

    def test_set_weights_invalid_sum(self):
        """Test setting weights that don't sum to 1."""
        manager = WeightManager()
        invalid_weights = {
            "political": 0.5,
            "economic": 0.5,
            "security": 0.5,
            "trade": 0.5,
        }

        with pytest.raises(ValueError):
            manager.set_weights(invalid_weights)

    def test_set_weights_missing_keys(self):
        """Test setting weights with missing keys."""
        manager = WeightManager()
        incomplete = {
            "political": 0.5,
            "economic": 0.5,
        }

        with pytest.raises(ValueError):
            manager.set_weights(incomplete)

    def test_reset_weights(self):
        """Test resetting weights to defaults."""
        manager = WeightManager()

        # Change weights
        manager.set_weights({
            "political": 0.4,
            "economic": 0.3,
            "security": 0.2,
            "trade": 0.1,
        })

        # Reset
        manager.reset_weights()

        # Should be back to defaults
        assert manager.weights["security"] == 0.30

    def test_get_subfactor_weights(self):
        """Test getting subfactor weights."""
        manager = WeightManager()
        political_subs = manager.get_subfactor_weights("political")

        assert "government_stability" in political_subs
        assert abs(sum(political_subs.values()) - 1.0) < 0.001

    def test_get_subfactor_weights_invalid(self):
        """Test getting subfactor weights for invalid factor."""
        manager = WeightManager()
        result = manager.get_subfactor_weights("invalid")
        assert result == {}

    def test_set_subfactor_weights(self):
        """Test setting subfactor weights."""
        manager = WeightManager()
        new_subs = {
            "government_stability": 0.5,
            "regime_type": 0.2,
            "corruption": 0.2,
            "rule_of_law": 0.1,
        }

        manager.set_subfactor_weights("political", new_subs)
        result = manager.get_subfactor_weights("political")
        assert result["government_stability"] == 0.5

    def test_set_subfactor_weights_invalid_sum(self):
        """Test setting invalid subfactor weights."""
        manager = WeightManager()
        invalid = {
            "government_stability": 0.5,
            "regime_type": 0.5,
            "corruption": 0.5,
            "rule_of_law": 0.5,
        }

        with pytest.raises(ValueError):
            manager.set_subfactor_weights("political", invalid)

    def test_set_subfactor_weights_invalid_factor(self):
        """Test setting subfactors for invalid factor."""
        manager = WeightManager()

        with pytest.raises(ValueError):
            manager.set_subfactor_weights("invalid", {"a": 1.0})

    def test_calculate_weighted_score(self):
        """Test weighted score calculation."""
        manager = WeightManager()
        scores = {
            "political": 40,
            "economic": 60,
            "security": 80,
            "trade": 50,
        }

        result = manager.calculate_weighted_score(scores)

        # Manual calculation with default weights
        expected = (
            40 * 0.25 +
            60 * 0.25 +
            80 * 0.30 +
            50 * 0.20
        )
        assert abs(result - expected) < 0.1

    def test_calculate_weighted_score_custom(self):
        """Test weighted score with custom weights."""
        manager = WeightManager()
        scores = {
            "political": 100,
            "economic": 0,
            "security": 0,
            "trade": 0,
        }

        custom_weights = {
            "political": 1.0,
            "economic": 0.0,
            "security": 0.0,
            "trade": 0.0,
        }

        result = manager.calculate_weighted_score(scores, custom_weights)
        assert result == 100.0

    def test_get_weight_presets(self):
        """Test getting weight presets."""
        manager = WeightManager()
        presets = manager.get_weight_presets()

        assert "balanced" in presets
        assert "security_focused" in presets
        assert "economic_focused" in presets

        # All presets should sum to 1
        for name, weights in presets.items():
            assert abs(sum(weights.values()) - 1.0) < 0.001

    def test_apply_preset(self):
        """Test applying a weight preset."""
        manager = WeightManager()
        manager.apply_preset("security_focused")

        assert manager.weights["security"] == 0.50

    def test_apply_preset_invalid(self):
        """Test applying invalid preset."""
        manager = WeightManager()

        with pytest.raises(ValueError):
            manager.apply_preset("invalid_preset")
