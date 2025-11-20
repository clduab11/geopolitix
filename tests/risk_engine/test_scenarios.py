"""Tests for scenario modeling."""

import pytest
from src.risk_engine.scenarios import ScenarioModeler


class TestScenarioModeler:
    """Test cases for ScenarioModeler."""

    def test_init(self):
        """Test modeler initialization."""
        modeler = ScenarioModeler()
        assert modeler.scenarios == []

    def test_create_scenario(self):
        """Test creating a custom scenario."""
        modeler = ScenarioModeler()
        scenario = modeler.create_scenario(
            name="Test Scenario",
            description="Test description",
            affected_countries=["Country A", "Country B"],
            factor_impacts={"political": 20, "economic": 30},
            severity=1.5,
            duration_months=6,
        )

        assert scenario["name"] == "Test Scenario"
        assert len(scenario["affected_countries"]) == 2
        assert scenario["severity"] == 1.5
        assert "id" in scenario

    def test_create_scenario_severity_bounds(self):
        """Test severity is bounded correctly."""
        modeler = ScenarioModeler()

        # Test upper bound
        scenario = modeler.create_scenario(
            name="High Severity",
            description="Test",
            affected_countries=["A"],
            factor_impacts={"security": 50},
            severity=5.0,  # Should be capped at 2.0
        )
        assert scenario["severity"] == 2.0

        # Test lower bound
        scenario = modeler.create_scenario(
            name="Low Severity",
            description="Test",
            affected_countries=["A"],
            factor_impacts={"security": 50},
            severity=0.01,  # Should be capped at 0.1
        )
        assert scenario["severity"] == 0.1

    def test_create_from_template(self):
        """Test creating scenario from template."""
        modeler = ScenarioModeler()
        scenario = modeler.create_from_template(
            "trade_embargo",
            {
                "country_a": "USA",
                "country_b": "China",
                "severity": 1.5,
            },
        )

        assert "Trade Embargo" in scenario["name"]
        assert "USA" in scenario["affected_countries"]
        assert "China" in scenario["affected_countries"]

    def test_create_from_template_invalid(self):
        """Test creating from invalid template."""
        modeler = ScenarioModeler()

        with pytest.raises(ValueError):
            modeler.create_from_template("invalid_template", {})

    def test_create_from_template_missing_params(self):
        """Test creating from template with missing parameters."""
        modeler = ScenarioModeler()

        with pytest.raises(ValueError):
            modeler.create_from_template("trade_embargo", {})

    def test_calculate_impact(self):
        """Test impact calculation."""
        modeler = ScenarioModeler()

        scenario = modeler.create_scenario(
            name="Test",
            description="Test",
            affected_countries=["Country A"],
            factor_impacts={"political": 20, "security": 30},
            severity=1.0,
        )

        current_scores = {
            "Country A": {
                "political": 40,
                "economic": 50,
                "security": 35,
                "trade": 45,
            }
        }

        impact = modeler.calculate_impact(scenario, current_scores)

        assert "Country A" in impact
        assert impact["Country A"]["projected_scores"]["political"] == 60  # 40 + 20
        assert impact["Country A"]["projected_scores"]["security"] == 65  # 35 + 30

    def test_calculate_impact_with_severity(self):
        """Test impact calculation with severity multiplier."""
        modeler = ScenarioModeler()

        scenario = modeler.create_scenario(
            name="Test",
            description="Test",
            affected_countries=["Country A"],
            factor_impacts={"political": 20},
            severity=0.5,  # Half severity
        )

        current_scores = {
            "Country A": {"political": 40, "economic": 50, "security": 35, "trade": 45}
        }

        impact = modeler.calculate_impact(scenario, current_scores)

        # Impact should be 20 * 0.5 = 10
        assert impact["Country A"]["changes"]["political"] == 10

    def test_compare_scenarios(self):
        """Test scenario comparison."""
        modeler = ScenarioModeler()

        scenario1 = modeler.create_scenario(
            name="Scenario 1",
            description="Test",
            affected_countries=["A"],
            factor_impacts={"security": 30},
        )

        scenario2 = modeler.create_scenario(
            name="Scenario 2",
            description="Test",
            affected_countries=["A", "B"],
            factor_impacts={"security": 50},
        )

        current_scores = {
            "A": {"political": 40, "economic": 50, "security": 35, "trade": 45},
            "B": {"political": 30, "economic": 40, "security": 25, "trade": 35},
        }

        comparison = modeler.compare_scenarios([scenario1, scenario2], current_scores)

        assert len(comparison["scenarios"]) == 2
        assert (
            comparison["scenarios"][1]["total_impact"]
            > comparison["scenarios"][0]["total_impact"]
        )

    def test_export_scenario(self):
        """Test scenario export."""
        modeler = ScenarioModeler()

        scenario = modeler.create_scenario(
            name="Export Test",
            description="Test",
            affected_countries=["A"],
            factor_impacts={"security": 30},
        )

        exported = modeler.export_scenario(scenario["id"], "json")

        assert "Export Test" in exported
        assert "security" in exported

    def test_export_scenario_not_found(self):
        """Test export with invalid scenario ID."""
        modeler = ScenarioModeler()

        with pytest.raises(ValueError):
            modeler.export_scenario("invalid_id")

    def test_get_all_scenarios(self):
        """Test getting all scenarios."""
        modeler = ScenarioModeler()

        modeler.create_scenario("S1", "D1", ["A"], {"security": 10})
        modeler.create_scenario("S2", "D2", ["B"], {"security": 20})

        scenarios = modeler.get_all_scenarios()
        assert len(scenarios) == 2

    def test_delete_scenario(self):
        """Test deleting a scenario."""
        modeler = ScenarioModeler()

        scenario = modeler.create_scenario("Test", "Desc", ["A"], {"security": 10})
        scenario_id = scenario["id"]

        assert modeler.delete_scenario(scenario_id) is True
        assert len(modeler.scenarios) == 0

    def test_delete_scenario_not_found(self):
        """Test deleting non-existent scenario."""
        modeler = ScenarioModeler()
        assert modeler.delete_scenario("invalid_id") is False

    def test_get_template_list(self):
        """Test getting template list."""
        modeler = ScenarioModeler()
        templates = modeler.get_template_list()

        assert len(templates) > 0
        assert any(t["name"] == "trade_embargo" for t in templates)
