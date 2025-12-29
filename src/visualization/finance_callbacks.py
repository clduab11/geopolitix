"""Dash callbacks for the Finance Dashboard."""

from typing import Any, Dict, List, Optional, Tuple
import json

from dash import Input, Output, State, callback_context, no_update, html, dcc
import dash_bootstrap_components as dbc

from src.data_sources.perplexity_api import PerplexityClient, MODEL_CONFIG
from src.data_sources.fmp_api import FMPClient
from src.data_sources.finance_prompts import (
    format_prompt,
    get_followup_suggestions,
    get_system_prompt,
)
from src.visualization.finance_charts import (
    create_stock_chart,
    create_empty_chart,
    format_number,
    format_percent,
)
from src.utils.logger import get_logger

logger = get_logger(__name__)


def register_finance_callbacks(app):
    """Register all finance-related callbacks with the app."""

    # Initialize clients
    perplexity_client = PerplexityClient()
    fmp_client = FMPClient()

    @app.callback(
        Output("ticker-autocomplete-results", "children"),
        Input("finance-ticker-search", "value"),
        prevent_initial_call=True,
    )
    def update_autocomplete(search_value: str) -> List:
        """Update ticker autocomplete suggestions."""
        if not search_value or len(search_value) < 2:
            return []

        results = fmp_client.search_ticker(search_value, limit=5)

        if not results:
            return []

        suggestions = []
        for r in results:
            suggestions.append(
                dbc.ListGroupItem(
                    [
                        html.Strong(r.get("ticker", "")),
                        html.Span(f" - {r.get('name', '')}", className="text-muted"),
                        dbc.Badge(
                            r.get("exchange", ""),
                            color="secondary",
                            className="ms-2",
                        ),
                    ],
                    id={"type": "ticker-suggestion", "ticker": r.get("ticker", "")},
                    action=True,
                    className="autocomplete-item",
                )
            )

        return dbc.ListGroup(suggestions, flush=True)

    @app.callback(
        Output("model-description", "children"),
        Input("finance-model-selector", "value"),
    )
    def update_model_description(model: str) -> str:
        """Update model description based on selection."""
        if model in MODEL_CONFIG:
            return MODEL_CONFIG[model].get("use_case", "")
        return ""

    @app.callback(
        [
            Output("finance-ai-analysis-output", "children"),
            Output("finance-citations-list", "children"),
            Output("suggested-followups", "children"),
            Output("stock-ticker-display", "children"),
            Output("stock-exchange-badge", "children"),
            Output("stock-price-display", "children"),
            Output("stock-change-display", "children"),
            Output("stock-change-display", "className"),
            Output("finance-stock-chart", "figure"),
            Output("metric-market-cap", "children"),
            Output("metric-pe-ratio", "children"),
            Output("metric-volume", "children"),
            Output("metric-high-52", "children"),
            Output("metric-low-52", "children"),
            Output("metric-div-yield", "children"),
            Output("metric-beta", "children"),
            Output("metric-eps", "children"),
        ],
        Input("btn-finance-search", "n_clicks"),
        [
            State("finance-ticker-search", "value"),
            State("finance-model-selector", "value"),
            State("finance-analysis-type", "value"),
        ],
        prevent_initial_call=True,
    )
    def perform_stock_analysis(
        n_clicks: int,
        ticker: str,
        model: str,
        analysis_type: str,
    ) -> Tuple:
        """Perform comprehensive stock analysis."""
        if not n_clicks or not ticker:
            return (no_update,) * 17

        ticker = ticker.strip().upper()
        logger.info(f"Analyzing {ticker} with model {model}, type {analysis_type}")

        # Default empty values
        empty_outputs = (
            html.P("No data available", className="text-muted"),  # analysis
            [],  # citations
            [],  # followups
            ticker,  # ticker display
            "",  # exchange
            "--",  # price
            "",  # change
            "stock-change",  # change class
            create_empty_chart(f"No data for {ticker}"),  # chart
            "--", "--", "--", "--", "--", "--", "--", "--",  # metrics
        )

        try:
            # Get stock quote
            quote = fmp_client.get_stock_quote(ticker)

            if not quote or quote.get("error"):
                return (
                    html.Div(
                        [
                            html.I(className="fas fa-exclamation-triangle text-warning me-2"),
                            f"Unable to find data for ticker: {ticker}",
                        ]
                    ),
                    *empty_outputs[1:],
                )

            # Get company profile
            profile = fmp_client.get_company_profile(ticker)

            # Get historical prices
            historical = fmp_client.get_historical_prices(ticker, period="1M")

            # Get key metrics
            metrics = fmp_client.get_key_metrics(ticker)

            # Build AI analysis prompt based on type
            company_name = profile.get("name", ticker)

            if analysis_type == "overview":
                analysis = perplexity_client.analyze_stock(ticker, "overview")
            elif analysis_type == "earnings":
                analysis = perplexity_client.analyze_stock(ticker, "earnings")
            elif analysis_type == "risk":
                analysis = perplexity_client.analyze_stock(ticker, "risk")
            elif analysis_type == "geopolitical":
                analysis = perplexity_client.get_geopolitical_impact(
                    company_name, "global"
                )
            elif analysis_type == "peer":
                peers = fmp_client.get_peer_comparison(ticker)
                if peers.get("peers"):
                    peer_ticker = peers["peers"][0].get("ticker", "")
                    analysis = perplexity_client.compare_stocks(ticker, peer_ticker)
                else:
                    analysis = perplexity_client.analyze_stock(ticker, "overview")
            else:
                analysis = perplexity_client.analyze_stock(ticker, "overview")

            # Format AI analysis output
            analysis_content = analysis.get("content", "")
            if analysis_content:
                # Convert markdown-style content to HTML
                analysis_output = html.Div(
                    [
                        html.H5(f"{company_name} ({ticker})", className="mb-3"),
                        html.Div(
                            analysis_content,
                            className="ai-analysis-text",
                            style={"whiteSpace": "pre-wrap"},
                        ),
                        html.Small(
                            f"Model: {analysis.get('model', 'N/A')} | "
                            f"Tokens: {analysis.get('usage', {}).get('total_tokens', 0)}",
                            className="text-muted mt-2 d-block",
                        ),
                    ]
                )
            else:
                analysis_output = html.P(
                    "Analysis not available. Please check API configuration.",
                    className="text-muted",
                )

            # Format citations
            citations = analysis.get("citations", [])
            if citations:
                citation_items = [
                    html.A(
                        [
                            html.Span(f"[{c.get('index', i+1)}] ", className="citation-number"),
                            c.get("url", "Source"),
                        ],
                        href=c.get("url", "#"),
                        target="_blank",
                        className="citation-link d-block mb-1",
                    )
                    for i, c in enumerate(citations)
                ]
            else:
                citation_items = [html.Small("No citations available", className="text-muted")]

            # Generate follow-up suggestions
            followups = get_followup_suggestions(analysis_type)
            followup_buttons = [
                dbc.Button(
                    q,
                    id={"type": "followup-btn", "question": q},
                    color="outline-secondary",
                    size="sm",
                    className="me-2 mb-2",
                )
                for q in followups[:4]
            ]

            # Format price and change
            price = quote.get("price", 0)
            change = quote.get("change", 0)
            change_pct = quote.get("change_percent", 0)
            is_positive = change >= 0

            price_display = f"${price:,.2f}"
            change_display = f"{'+' if change >= 0 else ''}{change:.2f} ({'+' if change_pct >= 0 else ''}{change_pct:.2f}%)"
            change_class = "stock-change text-success" if is_positive else "stock-change text-danger"

            # Create stock chart
            chart = create_stock_chart(
                historical.get("historical", []),
                ticker,
                "1M",
            )

            # Format metrics
            metrics_data = metrics.get("metrics", {})

            return (
                analysis_output,
                citation_items,
                followup_buttons,
                f"{company_name} ({ticker})",
                profile.get("exchange", ""),
                price_display,
                change_display,
                change_class,
                chart,
                format_number(quote.get("market_cap", 0)),
                f"{quote.get('pe_ratio', 0):.2f}" if quote.get("pe_ratio") else "--",
                format_number(quote.get("volume", 0), prefix=""),
                f"${quote.get('year_high', 0):,.2f}" if quote.get("year_high") else "--",
                f"${quote.get('year_low', 0):,.2f}" if quote.get("year_low") else "--",
                f"{metrics_data.get('dividend_yield', 0)*100:.2f}%" if metrics_data.get("dividend_yield") else "--",
                f"{profile.get('beta', 0):.2f}" if profile.get("beta") else "--",
                f"${quote.get('eps', 0):.2f}" if quote.get("eps") else "--",
            )

        except Exception as e:
            logger.exception(f"Error analyzing {ticker}: {e}")
            return (
                html.Div(
                    [
                        html.I(className="fas fa-exclamation-circle text-danger me-2"),
                        f"Error analyzing {ticker}: {str(e)}",
                    ]
                ),
                *empty_outputs[1:],
            )

    @app.callback(
        Output("finance-stock-chart", "figure", allow_duplicate=True),
        [
            Input("btn-period-1d", "n_clicks"),
            Input("btn-period-5d", "n_clicks"),
            Input("btn-period-1m", "n_clicks"),
            Input("btn-period-3m", "n_clicks"),
            Input("btn-period-6m", "n_clicks"),
            Input("btn-period-1y", "n_clicks"),
            Input("btn-period-5y", "n_clicks"),
        ],
        State("finance-ticker-search", "value"),
        prevent_initial_call=True,
    )
    def update_chart_period(
        n1d, n5d, n1m, n3m, n6m, n1y, n5y,
        ticker: str,
    ):
        """Update chart based on selected time period."""
        if not ticker:
            return no_update

        ctx = callback_context
        if not ctx.triggered:
            return no_update

        button_id = ctx.triggered[0]["prop_id"].split(".")[0]

        period_map = {
            "btn-period-1d": "1D",
            "btn-period-5d": "5D",
            "btn-period-1m": "1M",
            "btn-period-3m": "3M",
            "btn-period-6m": "6M",
            "btn-period-1y": "1Y",
            "btn-period-5y": "5Y",
        }

        period = period_map.get(button_id, "1M")
        ticker = ticker.strip().upper()

        try:
            historical = fmp_client.get_historical_prices(ticker, period=period)
            return create_stock_chart(
                historical.get("historical", []),
                ticker,
                period,
            )
        except Exception as e:
            logger.error(f"Error updating chart for {ticker}: {e}")
            return create_empty_chart(f"Error loading {period} data")

    @app.callback(
        [
            Output("finance-income-statement", "children"),
            Output("finance-balance-sheet", "children"),
            Output("finance-cash-flow", "children"),
        ],
        [
            Input("finance-statements-tabs", "active_tab"),
            Input("statement-period-selector", "value"),
        ],
        State("finance-ticker-search", "value"),
        prevent_initial_call=True,
    )
    def update_financial_statements(
        active_tab: str,
        period: str,
        ticker: str,
    ) -> Tuple:
        """Update financial statement tables."""
        if not ticker:
            empty = html.P("Search for a stock to see financial statements", className="text-muted small")
            return empty, empty, empty

        ticker = ticker.strip().upper()

        try:
            # Get all statements
            income = fmp_client.get_income_statement(ticker, period=period)
            balance = fmp_client.get_balance_sheet(ticker, period=period)
            cashflow = fmp_client.get_cash_flow(ticker, period=period)

            return (
                format_statement_table(income.get("statements", []), "income"),
                format_statement_table(balance.get("statements", []), "balance"),
                format_statement_table(cashflow.get("statements", []), "cashflow"),
            )

        except Exception as e:
            logger.error(f"Error fetching statements for {ticker}: {e}")
            error = html.P(f"Error loading data: {str(e)}", className="text-danger small")
            return error, error, error

    @app.callback(
        Output("download-financial-data", "data"),
        Input("btn-export-csv", "n_clicks"),
        [
            State("finance-ticker-search", "value"),
            State("statement-period-selector", "value"),
        ],
        prevent_initial_call=True,
    )
    def export_financial_data(
        n_clicks: int,
        ticker: str,
        period: str,
    ):
        """Export financial statements as CSV."""
        if not n_clicks or not ticker:
            return no_update

        ticker = ticker.strip().upper()

        try:
            income = fmp_client.get_income_statement(ticker, period=period)
            statements = income.get("statements", [])

            if statements:
                # Convert to CSV format
                import csv
                import io

                output = io.StringIO()
                if statements:
                    writer = csv.DictWriter(output, fieldnames=statements[0].keys())
                    writer.writeheader()
                    writer.writerows(statements)

                return dcc.send_string(
                    output.getvalue(),
                    f"{ticker}_income_statement.csv",
                )

        except Exception as e:
            logger.error(f"Error exporting data for {ticker}: {e}")

        return no_update

    @app.callback(
        Output("finance-ai-analysis-output", "children", allow_duplicate=True),
        Input("btn-send-followup", "n_clicks"),
        [
            State("finance-followup-query", "value"),
            State("finance-ticker-search", "value"),
            State("finance-ai-analysis-output", "children"),
        ],
        prevent_initial_call=True,
    )
    def handle_followup_question(
        n_clicks: int,
        followup_query: str,
        ticker: str,
        current_analysis,
    ):
        """Handle follow-up questions."""
        if not n_clicks or not followup_query or not ticker:
            return no_update

        ticker = ticker.strip().upper()

        try:
            # Extract text from current analysis for context
            original_text = ""
            if current_analysis and isinstance(current_analysis, dict):
                # Try to get text content
                props = current_analysis.get("props", {})
                children = props.get("children", [])
                if children:
                    for child in children:
                        if isinstance(child, dict):
                            child_props = child.get("props", {})
                            if "children" in child_props:
                                text = child_props["children"]
                                if isinstance(text, str):
                                    original_text += text + " "

            # Make follow-up query
            result = perplexity_client.ask_followup(
                original_query=f"Analysis of {ticker}",
                original_response=original_text[:2000] if original_text else f"Previous analysis of {ticker}",
                followup_question=followup_query,
            )

            if result.get("content"):
                return html.Div(
                    [
                        html.H5(f"Follow-up: {followup_query}", className="mb-3"),
                        html.Div(
                            result["content"],
                            className="ai-analysis-text",
                            style={"whiteSpace": "pre-wrap"},
                        ),
                        html.Hr(),
                        html.Small(
                            [
                                html.A(
                                    "← Back to original analysis",
                                    href="#",
                                    id="btn-back-to-original",
                                    className="text-primary",
                                ),
                            ]
                        ),
                    ]
                )

        except Exception as e:
            logger.error(f"Error handling followup for {ticker}: {e}")

        return no_update

    return app


def format_statement_table(
    statements: List[Dict[str, Any]],
    statement_type: str,
) -> html.Div:
    """
    Format financial statement data as a table.

    Args:
        statements: List of statement data
        statement_type: Type of statement ('income', 'balance', 'cashflow')

    Returns:
        Dash HTML component
    """
    if not statements:
        return html.P("No data available", className="text-muted small")

    # Define which fields to show for each statement type
    field_configs = {
        "income": [
            ("date", "Period"),
            ("revenue", "Revenue"),
            ("gross_profit", "Gross Profit"),
            ("operating_income", "Operating Income"),
            ("net_income", "Net Income"),
            ("eps", "EPS"),
        ],
        "balance": [
            ("date", "Period"),
            ("total_assets", "Total Assets"),
            ("total_liabilities", "Total Liabilities"),
            ("total_equity", "Total Equity"),
            ("cash", "Cash"),
            ("total_debt", "Total Debt"),
        ],
        "cashflow": [
            ("date", "Period"),
            ("operating_cash_flow", "Operating CF"),
            ("investing_cash_flow", "Investing CF"),
            ("financing_cash_flow", "Financing CF"),
            ("free_cash_flow", "Free Cash Flow"),
        ],
    }

    fields = field_configs.get(statement_type, field_configs["income"])

    # Create table header
    header = html.Thead(
        html.Tr([html.Th(label, className="small") for _, label in fields])
    )

    # Create table rows
    rows = []
    for stmt in statements[:5]:  # Limit to 5 periods
        cells = []
        for field_key, _ in fields:
            value = stmt.get(field_key, 0)
            if field_key == "date":
                cells.append(html.Td(value[:10] if value else "--", className="small"))
            elif field_key == "eps":
                cells.append(html.Td(f"${value:.2f}" if value else "--", className="small"))
            else:
                cells.append(html.Td(format_number(value), className="small"))
        rows.append(html.Tr(cells))

    body = html.Tbody(rows)

    return html.Table(
        [header, body],
        className="table table-sm table-hover",
    )
