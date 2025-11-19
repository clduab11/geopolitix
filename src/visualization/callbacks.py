"""Dash callback registrations."""

from datetime import datetime
import json
import pandas as pd
import base64
import io

from dash import Input, Output, State, no_update, dcc, html
import dash_bootstrap_components as dbc
import plotly.express as px

from src.risk_engine.scoring import RiskScorer, get_default_countries
from src.risk_engine.scenarios import ScenarioModeler
from src.visualization.maps import create_choropleth_map
from src.visualization.charts import (
    create_trend_chart,
    create_comparison_chart,
    create_correlation_matrix,
    create_scenario_comparison,
    create_exposure_pie,
)
from src.visualization.layouts import create_summary_card, create_alert_item
from config.risk_thresholds import RiskThresholds
from src.utils.logger import get_logger

logger = get_logger(__name__)


def register_callbacks(app):
    """Register all dashboard callbacks with the app."""

    # Initialize components
    scorer = RiskScorer()
    scenario_modeler = ScenarioModeler()

    @app.callback(
        [
            Output("world-map", "figure"),
            Output("risk-data-store", "data"),
            Output("last-updated", "children"),
            Output("country-select", "options"),
            Output("scenario-countries", "options"),
        ],
        [
            Input("btn-refresh", "n_clicks"),
            Input("interval-refresh", "n_intervals"),
        ],
    )
    def update_main_data(n_clicks, n_intervals):
        """Update main dashboard data."""
        # Get risk scores for default countries
        countries = get_default_countries()
        scores_df = scorer.get_batch_scores(countries)

        if scores_df.empty:
            # Return empty/default state
            return {}, {}, "No data", [], []

        # Create map
        fig = create_choropleth_map(scores_df)

        # Store data
        store_data = scores_df.to_dict("records")

        # Last updated
        last_updated = f"Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}"

        # Country options
        country_options = [
            {"label": c, "value": c} for c in scores_df["country"].tolist()
        ]

        return fig, store_data, last_updated, country_options, country_options

    @app.callback(
        [
            Output("risk-summary-cards", "children"),
            Output("alert-feed", "children"),
            Output("top-risk-list", "children"),
        ],
        Input("risk-data-store", "data"),
    )
    def update_overview_panels(data):
        """Update overview tab panels."""
        if not data:
            return [], [], []

        df = pd.DataFrame(data)

        # Summary cards
        avg_score = df["composite_score"].mean()
        high_risk = len(df[df["composite_score"] >= 70])
        critical = len(df[df["composite_score"] >= 85])

        summary_cards = dbc.Row(
            [
                dbc.Col(
                    create_summary_card(
                        "Average Risk",
                        f"{avg_score:.1f}",
                        "primary",
                    ),
                    width=4,
                ),
                dbc.Col(
                    create_summary_card(
                        "High Risk",
                        str(high_risk),
                        "warning",
                    ),
                    width=4,
                ),
                dbc.Col(
                    create_summary_card(
                        "Critical",
                        str(critical),
                        "danger",
                    ),
                    width=4,
                ),
            ]
        )

        # Alert feed
        alerts = scorer.generate_alerts(
            df, threshold=RiskThresholds.ALERT_THRESHOLD_ABSOLUTE
        )
        alert_items = []
        for alert in alerts[:5]:
            alert_items.append(
                create_alert_item(
                    alert["country"],
                    f"Risk score: {alert['score']:.1f}",
                    alert["risk_level"],
                    alert["timestamp"][:16],
                )
            )

        if not alert_items:
            alert_items = [html.P("No active alerts", className="text-muted")]

        # Top risk list
        top_risk = df.nlargest(5, "composite_score")
        risk_list = []
        for _, row in top_risk.iterrows():
            color = RiskThresholds.get_risk_color(row["composite_score"])
            risk_list.append(
                html.Div(
                    [
                        html.Strong(row["country"]),
                        dbc.Badge(
                            f"{row['composite_score']:.1f}",
                            style={"backgroundColor": color},
                            className="float-end",
                        ),
                        html.Hr(),
                    ]
                )
            )

        return summary_cards, alert_items, risk_list

    @app.callback(
        [
            Output("trend-chart", "figure"),
            Output("comparison-chart", "figure"),
            Output("correlation-matrix", "figure"),
        ],
        [
            Input("country-select", "value"),
            Input("time-range-select", "value"),
            Input("chart-type-select", "value"),
        ],
        State("risk-data-store", "data"),
    )
    def update_analytics(countries, time_range, chart_type, data):
        """Update analytics tab charts."""
        if not data:
            return {}, {}, {}

        df = pd.DataFrame(data)

        # Filter by selected countries
        if countries:
            df = df[df["country"].isin(countries)]

        if df.empty:
            return {}, {}, {}

        # Create synthetic trend data (in real app, fetch historical)
        trend_data = []
        for _, row in df.iterrows():
            for i in range(time_range):
                trend_data.append(
                    {
                        "country": row["country"],
                        "date": pd.Timestamp.now() - pd.Timedelta(days=time_range - i),
                        "composite_score": row["composite_score"]
                        + (i - time_range / 2) * 0.5,
                    }
                )

        trend_df = pd.DataFrame(trend_data)
        trend_fig = create_trend_chart(trend_df)

        # Comparison chart
        comparison_fig = create_comparison_chart(df, df["country"].tolist(), chart_type)

        # Correlation matrix
        corr_fig = create_correlation_matrix(df)

        return trend_fig, comparison_fig, corr_fig

    @app.callback(
        [
            Output("scenario-results", "children"),
            Output("scenario-chart", "figure"),
        ],
        Input("btn-run-scenario", "n_clicks"),
        [
            State("scenario-template", "value"),
            State("scenario-countries", "value"),
            State("severity-slider", "value"),
            State("duration-input", "value"),
            State("risk-data-store", "data"),
        ],
    )
    def run_scenario(n_clicks, template, countries, severity, duration, data):
        """Run scenario simulation."""
        if not n_clicks or not countries or not data:
            return html.P("Configure and run a scenario", className="text-muted"), {}

        df = pd.DataFrame(data)

        # Get current scores
        current_scores = {}
        for _, row in df[df["country"].isin(countries)].iterrows():
            current_scores[row["country"]] = {
                "political": row.get("political", 50),
                "economic": row.get("economic", 50),
                "security": row.get("security", 50),
                "trade": row.get("trade", 50),
            }

        # Create scenario
        try:
            scenario = scenario_modeler.create_from_template(
                template,
                {
                    "countries": countries,
                    "country": countries[0] if countries else "",
                    "severity": severity / 5,  # Normalize 1-10 to 0.2-2.0
                    "duration": duration,
                },
            )
        except (KeyError, ValueError):
            # Fallback for templates that need different params
            scenario = scenario_modeler.create_scenario(
                name=f"{template} Scenario",
                description=f"Custom {template} scenario",
                affected_countries=countries,
                factor_impacts={
                    "political": 20,
                    "economic": 25,
                    "security": 30,
                    "trade": 25,
                },
                severity=severity / 5,
                duration_months=duration,
            )

        # Calculate impact
        impact = scenario_modeler.calculate_impact(scenario, current_scores)

        # Build results display
        results = []
        for country, impact_data in impact.items():
            change = impact_data["composite_change"]
            color = "danger" if change > 10 else "warning" if change > 5 else "success"

            results.append(
                dbc.Card(
                    [
                        dbc.CardBody(
                            [
                                html.H5(country),
                                html.P(
                                    [
                                        "Current: ",
                                        html.Strong(
                                            f"{impact_data['current_composite']:.1f}"
                                        ),
                                        " → Projected: ",
                                        html.Strong(
                                            f"{impact_data['projected_composite']:.1f}"
                                        ),
                                    ]
                                ),
                                dbc.Badge(
                                    f"+{change:.1f}" if change > 0 else f"{change:.1f}",
                                    color=color,
                                ),
                            ]
                        ),
                    ],
                    className="mb-2",
                )
            )

        # Create comparison chart for first country
        if impact:
            first_country = list(impact.keys())[0]
            fig = create_scenario_comparison(
                impact[first_country]["current_scores"],
                impact[first_country]["projected_scores"],
                first_country,
            )
        else:
            fig = {}

        return results, fig

    @app.callback(
        Output("download-scenario", "data"),
        Input("btn-export-json", "n_clicks"),
        State("scenario-store", "data"),
        prevent_initial_call=True,
    )
    def export_scenario(n_clicks, scenario_data):
        """Export scenario as JSON."""
        if not scenario_data:
            return no_update

        return dcc.send_string(
            json.dumps(scenario_data, indent=2),
            "scenario_export.json",
        )

    @app.callback(
        [
            Output("exposure-list", "children"),
            Output("exposure-store", "data"),
        ],
        [
            Input("upload-exposure", "contents"),
            Input("btn-add-location", "n_clicks"),
        ],
        [
            State("upload-exposure", "filename"),
            State("manual-country", "value"),
            State("manual-type", "value"),
            State("manual-value", "value"),
            State("exposure-store", "data"),
        ],
    )
    def update_exposure_data(
        contents, n_clicks, filename, country, loc_type, value, current_data
    ):
        """Update company exposure data."""
        exposure_data = current_data or []

        # Handle file upload
        if contents and filename:
            _content_type, content_string = contents.split(",")
            decoded = base64.b64decode(content_string)

            try:
                if filename.strip() and "csv" in filename.lower():
                    df = pd.read_csv(io.StringIO(decoded.decode("utf-8")))
                    for _, row in df.iterrows():
                        exposure_data.append(
                            {
                                "country": row.get("country", ""),
                                "type": row.get("type", ""),
                                "value": float(row.get("value", 0)),
                            }
                        )
            except (UnicodeDecodeError, ValueError, pd.errors.ParserError) as e:
                logger.exception(f"Error parsing CSV file {filename}: {e}")

        # Handle manual entry
        if n_clicks and country and loc_type and value:
            exposure_data.append(
                {
                    "country": country,
                    "type": loc_type,
                    "value": float(value),
                }
            )

        # Build list display
        list_items = []
        for loc in exposure_data:
            list_items.append(
                html.Div(
                    [
                        html.Strong(loc["country"]),
                        html.Span(f" - {loc['type']}"),
                        dbc.Badge(
                            f"${loc['value']}M", color="secondary", className="ms-2"
                        ),
                        html.Hr(),
                    ]
                )
            )

        if not list_items:
            list_items = [html.P("No locations added", className="text-muted")]

        return list_items, exposure_data

    @app.callback(
        [
            Output("exposure-summary", "children"),
            Output("exposure-pie", "figure"),
            Output("exposure-bar", "figure"),
            Output("priority-actions", "children"),
        ],
        Input("exposure-store", "data"),
        State("risk-data-store", "data"),
    )
    def calculate_exposure(exposure_data, risk_data):
        """Calculate and display exposure analysis."""
        if not exposure_data or not risk_data:
            return (
                html.P("Add exposure data to see analysis", className="text-muted"),
                {},
                {},
                [],
            )

        risk_df = pd.DataFrame(risk_data)
        exposure_df = pd.DataFrame(exposure_data)

        # Calculate weighted risk
        total_value = exposure_df["value"].sum()
        weighted_risk = 0
        location_risks = []

        for _, loc in exposure_df.iterrows():
            country_risk = risk_df[risk_df["country"] == loc["country"]]
            if not country_risk.empty:
                risk_score = country_risk.iloc[0]["composite_score"]
            else:
                risk_score = 50

            weight = loc["value"] / total_value if total_value > 0 else 0
            weighted_risk += risk_score * weight

            location_risks.append(
                {
                    "country": loc["country"],
                    "type": loc["type"],
                    "value": loc["value"],
                    "risk_score": risk_score,
                    "weighted_risk": risk_score * weight,
                }
            )

        # Summary
        summary = dbc.Row(
            [
                dbc.Col(
                    [
                        create_summary_card(
                            "Total Exposure", f"${total_value:.1f}M", "primary"
                        ),
                    ],
                    width=4,
                ),
                dbc.Col(
                    [
                        create_summary_card(
                            "Weighted Risk", f"{weighted_risk:.1f}", "warning"
                        ),
                    ],
                    width=4,
                ),
                dbc.Col(
                    [
                        create_summary_card(
                            "Risk Level",
                            RiskThresholds.get_risk_level(weighted_risk).upper(),
                            "danger" if weighted_risk > 70 else "warning",
                        ),
                    ],
                    width=4,
                ),
            ]
        )

        # Pie chart by type
        type_exposure = exposure_df.groupby("type")["value"].sum().to_dict()
        pie_fig = create_exposure_pie(type_exposure, "Exposure by Type")

        # Bar chart by location risk
        loc_df = pd.DataFrame(location_risks)
        if not loc_df.empty:
            bar_fig = px.bar(
                loc_df,
                x="country",
                y="risk_score",
                color="type",
                title="Risk by Location",
            )
        else:
            bar_fig = {}

        # Priority actions
        loc_df = loc_df.sort_values("weighted_risk", ascending=False)
        actions = []
        for _, loc in loc_df.head(3).iterrows():
            if loc["risk_score"] > 70:
                action = "Immediate review required"
                color = "danger"
            elif loc["risk_score"] > 50:
                action = "Monitor closely"
                color = "warning"
            else:
                action = "Maintain current status"
                color = "success"

            actions.append(
                dbc.Alert(
                    [
                        html.Strong(loc["country"]),
                        f" ({loc['type']}): {action}",
                    ],
                    color=color,
                )
            )

        return summary, pie_fig, bar_fig, actions

    return app
