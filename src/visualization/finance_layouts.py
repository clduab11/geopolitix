"""Finance dashboard layout components for Perplexity-powered financial analysis."""

import dash_bootstrap_components as dbc
from dash import dcc, html

from src.data_sources.perplexity_api import MODEL_CONFIG


def create_finance_tab() -> html.Div:
    """
    Create the Finance Analysis tab content.

    Returns:
        Dash HTML Div component
    """
    return html.Div(
        [
            # Search and Model Selection Header
            create_finance_search_header(),
            html.Hr(className="my-3"),
            # Two-column layout
            dbc.Row(
                [
                    # Left column: AI Analysis (8/12 width)
                    dbc.Col(
                        [
                            create_ai_analysis_section(),
                            create_followup_section(),
                        ],
                        width=12,
                        lg=8,
                    ),
                    # Right column: Financial Data (4/12 width)
                    dbc.Col(
                        [
                            create_financial_data_section(),
                            create_key_metrics_section(),
                            create_financial_statements_section(),
                        ],
                        width=12,
                        lg=4,
                    ),
                ],
                className="g-3",
            ),
        ],
        id="finance-tab-content",
    )


def create_finance_search_header() -> html.Div:
    """Create the search header with ticker input and model selector."""
    return html.Div(
        [
            dbc.Row(
                [
                    # Ticker search
                    dbc.Col(
                        [
                            dbc.InputGroup(
                                [
                                    dbc.InputGroupText(
                                        html.I(className="fas fa-search"),
                                    ),
                                    dbc.Input(
                                        id="finance-ticker-search",
                                        type="text",
                                        placeholder="Search ticker or company (e.g., AAPL, Microsoft)",
                                        debounce=True,
                                        className="finance-ticker-input",
                                    ),
                                    dbc.Button(
                                        "Search",
                                        id="btn-finance-search",
                                        color="primary",
                                        className="ms-2",
                                    ),
                                ],
                            ),
                            html.Div(
                                id="ticker-autocomplete-results",
                                className="autocomplete-dropdown",
                            ),
                        ],
                        width=12,
                        md=6,
                    ),
                    # Model selector
                    dbc.Col(
                        [
                            dbc.InputGroup(
                                [
                                    dbc.InputGroupText("AI Model"),
                                    dbc.Select(
                                        id="finance-model-selector",
                                        options=[
                                            {
                                                "label": f"Sonar Pro (Detailed)",
                                                "value": "sonar-pro",
                                            },
                                            {
                                                "label": "Sonar (Quick)",
                                                "value": "sonar",
                                            },
                                            {
                                                "label": "Deep Research (Comprehensive)",
                                                "value": "sonar-deep-research",
                                            },
                                        ],
                                        value="sonar-pro",
                                    ),
                                ],
                            ),
                            html.Small(
                                id="model-description",
                                className="text-muted",
                                children="Complex financial analysis with citations",
                            ),
                        ],
                        width=12,
                        md=4,
                    ),
                    # Analysis type
                    dbc.Col(
                        [
                            dbc.InputGroup(
                                [
                                    dbc.InputGroupText("Analysis"),
                                    dbc.Select(
                                        id="finance-analysis-type",
                                        options=[
                                            {
                                                "label": "Overview",
                                                "value": "overview",
                                            },
                                            {
                                                "label": "Earnings Analysis",
                                                "value": "earnings",
                                            },
                                            {
                                                "label": "Risk Assessment",
                                                "value": "risk",
                                            },
                                            {
                                                "label": "Geopolitical Impact",
                                                "value": "geopolitical",
                                            },
                                            {
                                                "label": "Peer Comparison",
                                                "value": "peer",
                                            },
                                        ],
                                        value="overview",
                                    ),
                                ],
                            ),
                        ],
                        width=12,
                        md=2,
                    ),
                ],
                className="g-2 align-items-start",
            ),
            # Quick access tabs
            html.Div(
                [
                    dbc.ButtonGroup(
                        [
                            dbc.Button(
                                "Stocks",
                                id="btn-quick-stocks",
                                color="outline-secondary",
                                size="sm",
                                active=True,
                            ),
                            dbc.Button(
                                "Indices",
                                id="btn-quick-indices",
                                color="outline-secondary",
                                size="sm",
                            ),
                            dbc.Button(
                                "Sectors",
                                id="btn-quick-sectors",
                                color="outline-secondary",
                                size="sm",
                            ),
                        ],
                        className="mt-2",
                    ),
                ],
            ),
        ],
        className="finance-search-header",
    )


def create_ai_analysis_section() -> dbc.Card:
    """Create the AI analysis output section."""
    return dbc.Card(
        [
            dbc.CardHeader(
                [
                    html.H5("AI Analysis", className="mb-0 d-inline"),
                    dbc.Spinner(
                        html.Span(id="analysis-loading-indicator"),
                        size="sm",
                        color="primary",
                        type="border",
                        spinner_class_name="ms-2",
                    ),
                ],
            ),
            dbc.CardBody(
                [
                    # Analysis output
                    html.Div(
                        id="finance-ai-analysis-output",
                        className="ai-analysis-content",
                        children=[
                            html.P(
                                "Enter a ticker symbol and click Search to get AI-powered analysis.",
                                className="text-muted",
                            ),
                        ],
                    ),
                    html.Hr(),
                    # Citations
                    html.Div(
                        [
                            html.H6("Sources & Citations", className="text-muted"),
                            html.Div(
                                id="finance-citations-list",
                                className="citations-list",
                            ),
                        ],
                    ),
                ],
            ),
        ],
        className="mb-3",
    )


def create_followup_section() -> dbc.Card:
    """Create the follow-up question section."""
    return dbc.Card(
        [
            dbc.CardHeader("Follow-up Questions"),
            dbc.CardBody(
                [
                    # Suggested questions
                    html.Div(
                        id="suggested-followups",
                        className="mb-3",
                    ),
                    # Custom follow-up input
                    dbc.InputGroup(
                        [
                            dbc.Textarea(
                                id="finance-followup-query",
                                placeholder="Ask a follow-up question about this analysis...",
                                rows=2,
                                className="followup-input",
                            ),
                            dbc.Button(
                                html.I(className="fas fa-paper-plane"),
                                id="btn-send-followup",
                                color="primary",
                                className="followup-send-btn",
                            ),
                        ],
                    ),
                ],
            ),
        ],
        className="mb-3",
    )


def create_financial_data_section() -> dbc.Card:
    """Create the financial data and chart section."""
    return dbc.Card(
        [
            dbc.CardHeader(
                [
                    html.Span(id="stock-ticker-display", children="Stock Data"),
                    dbc.Badge(
                        id="stock-exchange-badge",
                        color="secondary",
                        className="ms-2",
                    ),
                ],
            ),
            dbc.CardBody(
                [
                    # Price display
                    html.Div(
                        [
                            html.H2(
                                id="stock-price-display",
                                children="--",
                                className="stock-price mb-0",
                            ),
                            html.Span(
                                id="stock-change-display",
                                children="",
                                className="stock-change",
                            ),
                        ],
                        className="mb-3",
                    ),
                    # Chart period selector
                    dbc.ButtonGroup(
                        [
                            dbc.Button("1D", id="btn-period-1d", size="sm", outline=True, color="secondary"),
                            dbc.Button("5D", id="btn-period-5d", size="sm", outline=True, color="secondary"),
                            dbc.Button("1M", id="btn-period-1m", size="sm", outline=True, color="secondary", active=True),
                            dbc.Button("3M", id="btn-period-3m", size="sm", outline=True, color="secondary"),
                            dbc.Button("6M", id="btn-period-6m", size="sm", outline=True, color="secondary"),
                            dbc.Button("1Y", id="btn-period-1y", size="sm", outline=True, color="secondary"),
                            dbc.Button("5Y", id="btn-period-5y", size="sm", outline=True, color="secondary"),
                        ],
                        className="mb-2 w-100 chart-period-selector",
                    ),
                    # Stock chart
                    dcc.Graph(
                        id="finance-stock-chart",
                        config={"displayModeBar": False},
                        style={"height": "250px"},
                    ),
                ],
            ),
        ],
        className="mb-3",
    )


def create_key_metrics_section() -> dbc.Card:
    """Create the key metrics panel."""
    return dbc.Card(
        [
            dbc.CardHeader("Key Metrics"),
            dbc.CardBody(
                [
                    html.Div(
                        id="finance-key-metrics",
                        className="key-metrics-grid",
                        children=[
                            create_metric_item("Market Cap", "--", "market-cap"),
                            create_metric_item("P/E Ratio", "--", "pe-ratio"),
                            create_metric_item("Volume", "--", "volume"),
                            create_metric_item("52-Week High", "--", "high-52"),
                            create_metric_item("52-Week Low", "--", "low-52"),
                            create_metric_item("Dividend Yield", "--", "div-yield"),
                            create_metric_item("Beta", "--", "beta"),
                            create_metric_item("EPS", "--", "eps"),
                        ],
                    ),
                ],
            ),
        ],
        className="mb-3",
    )


def create_metric_item(label: str, value: str, metric_id: str) -> html.Div:
    """Create a single metric display item."""
    return html.Div(
        [
            html.Small(label, className="metric-label text-muted"),
            html.Div(
                id=f"metric-{metric_id}",
                children=value,
                className="metric-value",
            ),
        ],
        className="metric-item",
    )


def create_financial_statements_section() -> dbc.Card:
    """Create the financial statements tabs."""
    return dbc.Card(
        [
            dbc.CardHeader("Financial Statements"),
            dbc.CardBody(
                [
                    dbc.Tabs(
                        [
                            dbc.Tab(
                                label="Income",
                                tab_id="tab-income",
                                children=[
                                    html.Div(
                                        id="finance-income-statement",
                                        className="statement-table mt-2",
                                    ),
                                ],
                            ),
                            dbc.Tab(
                                label="Balance",
                                tab_id="tab-balance",
                                children=[
                                    html.Div(
                                        id="finance-balance-sheet",
                                        className="statement-table mt-2",
                                    ),
                                ],
                            ),
                            dbc.Tab(
                                label="Cash Flow",
                                tab_id="tab-cashflow",
                                children=[
                                    html.Div(
                                        id="finance-cash-flow",
                                        className="statement-table mt-2",
                                    ),
                                ],
                            ),
                        ],
                        id="finance-statements-tabs",
                        active_tab="tab-income",
                    ),
                    # Statement period selector
                    dbc.RadioItems(
                        id="statement-period-selector",
                        options=[
                            {"label": "Annual", "value": "annual"},
                            {"label": "Quarterly", "value": "quarter"},
                        ],
                        value="annual",
                        inline=True,
                        className="mt-2",
                    ),
                    # Export buttons
                    html.Div(
                        [
                            dbc.Button(
                                [html.I(className="fas fa-download me-1"), "CSV"],
                                id="btn-export-csv",
                                color="outline-secondary",
                                size="sm",
                                className="me-2",
                            ),
                            dcc.Download(id="download-financial-data"),
                        ],
                        className="mt-2",
                    ),
                ],
            ),
        ],
    )


def create_geopolitical_overlay_section() -> dbc.Card:
    """Create the geopolitical risk overlay section for company exposure."""
    return dbc.Card(
        [
            dbc.CardHeader(
                [
                    html.I(className="fas fa-globe-americas me-2"),
                    "Geopolitical Risk Overlay",
                ],
            ),
            dbc.CardBody(
                [
                    html.P(
                        "Company geographic exposure with GEOPOLITIX risk scores",
                        className="text-muted small",
                    ),
                    # Geographic exposure map
                    dcc.Graph(
                        id="company-exposure-map",
                        config={"displayModeBar": False},
                        style={"height": "200px"},
                    ),
                    # Risk exposure summary
                    html.Div(
                        id="geographic-risk-summary",
                        className="mt-2",
                    ),
                    # Scenario impact link
                    dbc.Button(
                        [
                            html.I(className="fas fa-chart-line me-1"),
                            "Analyze Scenario Impact",
                        ],
                        id="btn-scenario-impact",
                        color="outline-primary",
                        size="sm",
                        className="w-100 mt-2",
                    ),
                ],
            ),
        ],
        className="mb-3",
    )


def create_peer_comparison_section() -> dbc.Card:
    """Create the peer comparison section."""
    return dbc.Card(
        [
            dbc.CardHeader("Peer Comparison"),
            dbc.CardBody(
                [
                    html.Div(
                        id="peer-comparison-table",
                        className="peer-table",
                    ),
                ],
            ),
        ],
        className="mb-3",
    )


def create_news_sentiment_section() -> dbc.Card:
    """Create the news and sentiment section."""
    return dbc.Card(
        [
            dbc.CardHeader(
                [
                    "Latest News",
                    dbc.Badge(
                        id="news-sentiment-badge",
                        color="secondary",
                        className="ms-2",
                    ),
                ],
            ),
            dbc.CardBody(
                [
                    html.Div(
                        id="company-news-feed",
                        className="news-feed",
                        style={"maxHeight": "300px", "overflowY": "auto"},
                    ),
                ],
            ),
        ],
        className="mb-3",
    )


def create_model_info_popover() -> dbc.Popover:
    """Create popover with model information."""
    return dbc.Popover(
        [
            dbc.PopoverHeader("AI Model Selection"),
            dbc.PopoverBody(
                [
                    html.Div(
                        [
                            html.Strong("Sonar Pro"),
                            html.P(
                                MODEL_CONFIG["sonar-pro"]["use_case"],
                                className="small mb-2",
                            ),
                        ],
                    ),
                    html.Div(
                        [
                            html.Strong("Sonar"),
                            html.P(
                                MODEL_CONFIG["sonar"]["use_case"],
                                className="small mb-2",
                            ),
                        ],
                    ),
                    html.Div(
                        [
                            html.Strong("Deep Research"),
                            html.P(
                                MODEL_CONFIG["sonar-deep-research"]["use_case"],
                                className="small mb-0",
                            ),
                            html.Small(
                                "Note: Processing time 30+ minutes",
                                className="text-warning",
                            ),
                        ],
                    ),
                ],
            ),
        ],
        target="finance-model-selector",
        trigger="hover",
        placement="bottom",
    )
