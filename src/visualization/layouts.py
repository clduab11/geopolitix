"""Dash layout components for the dashboard."""

from typing import Any, Dict, List
import dash_bootstrap_components as dbc
from dash import dcc, html


def create_layout() -> html.Div:
    """
    Create the main dashboard layout.

    Returns:
        Dash HTML Div component
    """
    return html.Div([
        # Header
        create_header(),

        # Main content
        dbc.Container([
            # Tabs for different views
            dbc.Tabs([
                dbc.Tab(
                    create_overview_tab(),
                    label="Global Overview",
                    tab_id="tab-overview",
                ),
                dbc.Tab(
                    create_analytics_tab(),
                    label="Risk Analytics",
                    tab_id="tab-analytics",
                ),
                dbc.Tab(
                    create_scenario_tab(),
                    label="Scenario Modeling",
                    tab_id="tab-scenarios",
                ),
                dbc.Tab(
                    create_exposure_tab(),
                    label="Company Exposure",
                    tab_id="tab-exposure",
                ),
            ], id="main-tabs", active_tab="tab-overview"),
        ], fluid=True, className="mt-3"),

        # Auto-refresh interval
        dcc.Interval(
            id="interval-refresh",
            interval=900000,  # 15 minutes
            n_intervals=0,
        ),

        # Store for shared data
        dcc.Store(id="risk-data-store"),
        dcc.Store(id="scenario-store"),
        dcc.Store(id="exposure-store"),
    ])


def create_header() -> html.Div:
    """Create the dashboard header."""
    return html.Div([
        dbc.Navbar(
            dbc.Container([
                dbc.Row([
                    dbc.Col([
                        html.H3("GEOPOLITIX", className="text-white mb-0"),
                        html.Small(
                            "Geopolitical Risk Analysis Dashboard",
                            className="text-light",
                        ),
                    ]),
                    dbc.Col([
                        dbc.Button(
                            "Refresh Data",
                            id="btn-refresh",
                            color="light",
                            outline=True,
                            className="me-2",
                        ),
                        html.Span(
                            id="last-updated",
                            className="text-light",
                        ),
                    ], width="auto"),
                ], justify="between", align="center", className="w-100"),
            ], fluid=True),
            color="dark",
            dark=True,
            className="mb-3",
        ),
    ])


def create_overview_tab() -> html.Div:
    """Create the global overview tab content."""
    return html.Div([
        dbc.Row([
            # World map
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Global Risk Map"),
                    dbc.CardBody([
                        dcc.Graph(id="world-map"),
                    ]),
                ]),
            ], width=12),
        ], className="mb-3"),

        dbc.Row([
            # Summary statistics
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Risk Summary"),
                    dbc.CardBody([
                        html.Div(id="risk-summary-cards"),
                    ]),
                ]),
            ], width=4),

            # Alert feed
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Recent Alerts"),
                    dbc.CardBody([
                        html.Div(id="alert-feed"),
                    ]),
                ]),
            ], width=4),

            # Top risk countries
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Highest Risk Countries"),
                    dbc.CardBody([
                        html.Div(id="top-risk-list"),
                    ]),
                ]),
            ], width=4),
        ]),
    ])


def create_analytics_tab() -> html.Div:
    """Create the risk analytics tab content."""
    return html.Div([
        dbc.Row([
            # Controls
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Analysis Controls"),
                    dbc.CardBody([
                        html.Label("Select Countries"),
                        dcc.Dropdown(
                            id="country-select",
                            multi=True,
                            placeholder="Select countries...",
                        ),
                        html.Hr(),
                        html.Label("Time Range"),
                        dcc.Dropdown(
                            id="time-range-select",
                            options=[
                                {"label": "7 Days", "value": 7},
                                {"label": "30 Days", "value": 30},
                                {"label": "90 Days", "value": 90},
                                {"label": "1 Year", "value": 365},
                            ],
                            value=30,
                        ),
                        html.Hr(),
                        html.Label("Chart Type"),
                        dcc.RadioItems(
                            id="chart-type-select",
                            options=[
                                {"label": "Bar Chart", "value": "bar"},
                                {"label": "Radar Chart", "value": "radar"},
                            ],
                            value="bar",
                            inline=True,
                        ),
                    ]),
                ]),
            ], width=3),

            # Charts
            dbc.Col([
                dbc.Tabs([
                    dbc.Tab([
                        dcc.Graph(id="trend-chart"),
                    ], label="Trends"),
                    dbc.Tab([
                        dcc.Graph(id="comparison-chart"),
                    ], label="Comparison"),
                    dbc.Tab([
                        dcc.Graph(id="correlation-matrix"),
                    ], label="Correlations"),
                ]),
            ], width=9),
        ]),
    ])


def create_scenario_tab() -> html.Div:
    """Create the scenario modeling tab content."""
    return html.Div([
        dbc.Row([
            # Scenario builder
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Scenario Builder"),
                    dbc.CardBody([
                        html.Label("Scenario Template"),
                        dcc.Dropdown(
                            id="scenario-template",
                            options=[
                                {"label": "Trade Embargo", "value": "trade_embargo"},
                                {"label": "Military Conflict", "value": "military_conflict"},
                                {"label": "Economic Sanctions", "value": "sanctions"},
                                {"label": "Political Crisis", "value": "political_crisis"},
                                {"label": "Natural Disaster", "value": "natural_disaster"},
                                {"label": "Custom", "value": "custom"},
                            ],
                            value="trade_embargo",
                        ),
                        html.Hr(),
                        html.Label("Affected Countries"),
                        dcc.Dropdown(
                            id="scenario-countries",
                            multi=True,
                            placeholder="Select countries...",
                        ),
                        html.Hr(),
                        html.Label("Severity (1-10)"),
                        dcc.Slider(
                            id="severity-slider",
                            min=1,
                            max=10,
                            step=1,
                            value=5,
                            marks={i: str(i) for i in range(1, 11)},
                        ),
                        html.Hr(),
                        html.Label("Duration (months)"),
                        dcc.Input(
                            id="duration-input",
                            type="number",
                            value=6,
                            min=1,
                            max=60,
                            className="form-control",
                        ),
                        html.Hr(),
                        dbc.Button(
                            "Run Scenario",
                            id="btn-run-scenario",
                            color="primary",
                            className="w-100",
                        ),
                    ]),
                ]),
            ], width=4),

            # Scenario results
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Scenario Impact Analysis"),
                    dbc.CardBody([
                        html.Div(id="scenario-results"),
                        dcc.Graph(id="scenario-chart"),
                    ]),
                ]),
                dbc.Card([
                    dbc.CardHeader("Export Options"),
                    dbc.CardBody([
                        dbc.Button(
                            "Export as JSON",
                            id="btn-export-json",
                            color="secondary",
                            className="me-2",
                        ),
                        dbc.Button(
                            "Generate Report",
                            id="btn-export-pdf",
                            color="secondary",
                        ),
                        dcc.Download(id="download-scenario"),
                    ]),
                ], className="mt-3"),
            ], width=8),
        ]),
    ])


def create_exposure_tab() -> html.Div:
    """Create the company exposure assessment tab content."""
    return html.Div([
        dbc.Row([
            # Input section
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Company Exposure Data"),
                    dbc.CardBody([
                        html.Label("Upload CSV File"),
                        dcc.Upload(
                            id="upload-exposure",
                            children=html.Div([
                                "Drag and Drop or ",
                                html.A("Select File"),
                            ]),
                            style={
                                "width": "100%",
                                "height": "60px",
                                "lineHeight": "60px",
                                "borderWidth": "1px",
                                "borderStyle": "dashed",
                                "borderRadius": "5px",
                                "textAlign": "center",
                            },
                        ),
                        html.Hr(),
                        html.Label("Or Enter Manually"),
                        html.Div([
                            dbc.InputGroup([
                                dbc.InputGroupText("Country"),
                                dbc.Input(id="manual-country"),
                            ], className="mb-2"),
                            dbc.InputGroup([
                                dbc.InputGroupText("Type"),
                                dcc.Dropdown(
                                    id="manual-type",
                                    options=[
                                        {"label": "Manufacturing", "value": "manufacturing"},
                                        {"label": "Supply Chain", "value": "supply_chain"},
                                        {"label": "Market", "value": "market"},
                                        {"label": "Headquarters", "value": "headquarters"},
                                    ],
                                    style={"flex": 1},
                                ),
                            ], className="mb-2"),
                            dbc.InputGroup([
                                dbc.InputGroupText("Value ($M)"),
                                dbc.Input(id="manual-value", type="number"),
                            ], className="mb-2"),
                            dbc.Button(
                                "Add Location",
                                id="btn-add-location",
                                color="primary",
                                className="w-100",
                            ),
                        ]),
                    ]),
                ]),
                dbc.Card([
                    dbc.CardHeader("Exposure Locations"),
                    dbc.CardBody([
                        html.Div(id="exposure-list"),
                    ]),
                ], className="mt-3"),
            ], width=4),

            # Results section
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Risk Exposure Analysis"),
                    dbc.CardBody([
                        html.Div(id="exposure-summary"),
                    ]),
                ]),
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader("Exposure by Region"),
                            dbc.CardBody([
                                dcc.Graph(id="exposure-pie"),
                            ]),
                        ]),
                    ], width=6),
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader("Risk by Location"),
                            dbc.CardBody([
                                dcc.Graph(id="exposure-bar"),
                            ]),
                        ]),
                    ], width=6),
                ], className="mt-3"),
                dbc.Card([
                    dbc.CardHeader("Priority Actions"),
                    dbc.CardBody([
                        html.Div(id="priority-actions"),
                    ]),
                ], className="mt-3"),
            ], width=8),
        ]),
    ])


def create_summary_card(
    title: str,
    value: str,
    color: str = "primary",
    icon: str = None,
) -> dbc.Card:
    """Create a summary statistic card."""
    return dbc.Card([
        dbc.CardBody([
            html.H6(title, className="text-muted"),
            html.H3(value, className=f"text-{color}"),
        ]),
    ], className="mb-2")


def create_alert_item(
    country: str,
    message: str,
    severity: str,
    timestamp: str,
) -> html.Div:
    """Create an alert list item."""
    color_map = {
        "critical": "danger",
        "high": "warning",
        "moderate": "info",
        "low": "secondary",
    }

    return html.Div([
        dbc.Badge(severity.upper(), color=color_map.get(severity, "secondary")),
        html.Strong(f" {country}: ", className="ms-2"),
        html.Span(message),
        html.Br(),
        html.Small(timestamp, className="text-muted"),
        html.Hr(),
    ])
