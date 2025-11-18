"""Scenario modeling for geopolitical risk simulation."""

from typing import Any, Dict, List, Optional
from datetime import datetime
import json

from config.risk_thresholds import RiskThresholds
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ScenarioModeler:
    """Model hypothetical geopolitical scenarios and their impact."""

    # Predefined scenario templates
    SCENARIO_TEMPLATES = {
        "trade_embargo": {
            "name": "Trade Embargo",
            "description": "Trade embargo between two countries",
            "affected_factors": {
                "trade": 40,
                "economic": 25,
                "political": 15,
            },
            "required_params": ["country_a", "country_b", "severity"],
        },
        "military_conflict": {
            "name": "Military Conflict",
            "description": "Armed conflict or military intervention",
            "affected_factors": {
                "security": 50,
                "political": 30,
                "economic": 20,
            },
            "required_params": ["countries", "severity", "duration"],
        },
        "sanctions": {
            "name": "Economic Sanctions",
            "description": "International sanctions imposed",
            "affected_factors": {
                "economic": 35,
                "trade": 35,
                "political": 20,
            },
            "required_params": ["target_country", "imposing_countries", "severity"],
        },
        "political_crisis": {
            "name": "Political Crisis",
            "description": "Government instability or regime change",
            "affected_factors": {
                "political": 45,
                "economic": 25,
                "security": 20,
            },
            "required_params": ["country", "crisis_type", "severity"],
        },
        "natural_disaster": {
            "name": "Natural Disaster",
            "description": "Major natural disaster affecting region",
            "affected_factors": {
                "economic": 30,
                "security": 25,
                "trade": 20,
            },
            "required_params": ["country", "disaster_type", "severity"],
        },
    }

    def __init__(self):
        """Initialize scenario modeler."""
        self.scenarios: List[Dict[str, Any]] = []

    def create_scenario(
        self,
        name: str,
        description: str,
        affected_countries: List[str],
        factor_impacts: Dict[str, float],
        severity: float = 1.0,
        duration_months: int = 6,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create a custom scenario.

        Args:
            name: Scenario name
            description: Scenario description
            affected_countries: List of affected countries
            factor_impacts: Impact on each risk factor (0-100)
            severity: Severity multiplier (0.1-2.0)
            duration_months: Expected duration
            parameters: Additional parameters

        Returns:
            Scenario dictionary
        """
        scenario = {
            "id": f"scenario_{len(self.scenarios) + 1}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            "name": name,
            "description": description,
            "affected_countries": affected_countries,
            "factor_impacts": factor_impacts,
            "severity": min(max(severity, 0.1), 2.0),
            "duration_months": duration_months,
            "parameters": parameters or {},
            "created_at": datetime.utcnow().isoformat(),
        }

        self.scenarios.append(scenario)
        return scenario

    def create_from_template(
        self,
        template_name: str,
        parameters: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Create scenario from predefined template.

        Args:
            template_name: Name of template to use
            parameters: Template parameters

        Returns:
            Scenario dictionary
        """
        if template_name not in self.SCENARIO_TEMPLATES:
            raise ValueError(f"Unknown template: {template_name}")

        template = self.SCENARIO_TEMPLATES[template_name]

        # Validate required parameters
        for param in template["required_params"]:
            if param not in parameters:
                raise ValueError(f"Missing required parameter: {param}")

        # Extract affected countries from parameters
        affected_countries = []
        if "country" in parameters:
            affected_countries.append(parameters["country"])
        if "countries" in parameters:
            affected_countries.extend(parameters["countries"])
        if "country_a" in parameters:
            affected_countries.append(parameters["country_a"])
        if "country_b" in parameters:
            affected_countries.append(parameters["country_b"])
        if "target_country" in parameters:
            affected_countries.append(parameters["target_country"])

        severity = parameters.get("severity", 1.0)
        duration = parameters.get("duration", 6)

        return self.create_scenario(
            name=f"{template['name']} - {', '.join(affected_countries[:2])}",
            description=template["description"],
            affected_countries=affected_countries,
            factor_impacts=template["affected_factors"],
            severity=severity,
            duration_months=duration,
            parameters=parameters,
        )

    def calculate_impact(
        self,
        scenario: Dict[str, Any],
        current_scores: Dict[str, Dict[str, float]],
    ) -> Dict[str, Dict[str, Any]]:
        """
        Calculate scenario impact on risk scores.

        Args:
            scenario: Scenario dictionary
            current_scores: Current risk scores by country

        Returns:
            Impact analysis by country
        """
        results = {}
        severity = scenario.get("severity", 1.0)
        factor_impacts = scenario.get("factor_impacts", {})

        for country in scenario.get("affected_countries", []):
            if country not in current_scores:
                continue

            current = current_scores[country]
            projected = {}
            changes = {}

            for factor, impact in factor_impacts.items():
                if factor in current:
                    current_value = current[factor]
                    # Apply impact with severity multiplier
                    change = impact * severity
                    new_value = min(100, current_value + change)

                    projected[factor] = round(new_value, 1)
                    changes[factor] = round(change, 1)

            # Calculate new composite score
            weights = RiskThresholds.FACTOR_WEIGHTS
            new_composite = sum(
                projected.get(f, current.get(f, 50)) * w
                for f, w in weights.items()
            )

            current_composite = sum(
                current.get(f, 50) * w
                for f, w in weights.items()
            )

            results[country] = {
                "current_scores": current,
                "projected_scores": projected,
                "changes": changes,
                "current_composite": round(current_composite, 1),
                "projected_composite": round(new_composite, 1),
                "composite_change": round(new_composite - current_composite, 1),
                "current_risk_level": RiskThresholds.get_risk_level(current_composite),
                "projected_risk_level": RiskThresholds.get_risk_level(new_composite),
            }

        return results

    def compare_scenarios(
        self,
        scenarios: List[Dict[str, Any]],
        current_scores: Dict[str, Dict[str, float]],
    ) -> Dict[str, Any]:
        """
        Compare impact of multiple scenarios.

        Args:
            scenarios: List of scenarios to compare
            current_scores: Current risk scores

        Returns:
            Comparison analysis
        """
        comparison = {
            "scenarios": [],
            "max_impact_country": None,
            "max_impact_value": 0,
        }

        for scenario in scenarios:
            impact = self.calculate_impact(scenario, current_scores)

            total_impact = 0
            max_country = None
            max_change = 0

            for country, data in impact.items():
                change = data.get("composite_change", 0)
                total_impact += change

                if change > max_change:
                    max_change = change
                    max_country = country

            scenario_summary = {
                "id": scenario.get("id"),
                "name": scenario.get("name"),
                "total_impact": round(total_impact, 1),
                "avg_impact": round(total_impact / max(len(impact), 1), 1),
                "most_affected_country": max_country,
                "max_change": round(max_change, 1),
                "countries_affected": len(impact),
            }

            comparison["scenarios"].append(scenario_summary)

            if max_change > comparison["max_impact_value"]:
                comparison["max_impact_value"] = max_change
                comparison["max_impact_country"] = max_country

        return comparison

    def export_scenario(
        self,
        scenario_id: str,
        format: str = "json",
    ) -> str:
        """
        Export scenario to specified format.

        Args:
            scenario_id: ID of scenario to export
            format: Export format (json or dict)

        Returns:
            Exported scenario string
        """
        scenario = None
        for s in self.scenarios:
            if s.get("id") == scenario_id:
                scenario = s
                break

        if not scenario:
            raise ValueError(f"Scenario not found: {scenario_id}")

        if format == "json":
            return json.dumps(scenario, indent=2)

        return str(scenario)

    def get_all_scenarios(self) -> List[Dict[str, Any]]:
        """Get all created scenarios."""
        return self.scenarios.copy()

    def delete_scenario(self, scenario_id: str) -> bool:
        """
        Delete a scenario.

        Args:
            scenario_id: ID of scenario to delete

        Returns:
            True if deleted, False if not found
        """
        for i, s in enumerate(self.scenarios):
            if s.get("id") == scenario_id:
                self.scenarios.pop(i)
                return True
        return False

    def get_template_list(self) -> List[Dict[str, str]]:
        """Get list of available templates."""
        return [
            {
                "name": name,
                "description": template["description"],
            }
            for name, template in self.SCENARIO_TEMPLATES.items()
        ]
