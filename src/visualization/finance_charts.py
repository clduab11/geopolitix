"""Financial chart generation functions using Plotly."""

from typing import Any, Dict, List, Optional

import plotly.graph_objects as go
from plotly.subplots import make_subplots


def create_stock_chart(
    historical_data: List[Dict[str, Any]],
    ticker: str,
    period: str = "1M",
    chart_type: str = "line",
) -> go.Figure:
    """
    Create a stock price chart.

    Args:
        historical_data: List of OHLCV data points
        ticker: Stock ticker symbol
        period: Time period for the chart
        chart_type: Type of chart ('line', 'candle', 'area')

    Returns:
        Plotly Figure object
    """
    if not historical_data:
        return create_empty_chart(f"No data available for {ticker}")

    # Extract data
    dates = [d.get("date", "") for d in historical_data]
    opens = [d.get("open", 0) for d in historical_data]
    highs = [d.get("high", 0) for d in historical_data]
    lows = [d.get("low", 0) for d in historical_data]
    closes = [d.get("close", 0) for d in historical_data]
    volumes = [d.get("volume", 0) for d in historical_data]

    # Reverse for chronological order
    dates = dates[::-1]
    opens = opens[::-1]
    highs = highs[::-1]
    lows = lows[::-1]
    closes = closes[::-1]
    volumes = volumes[::-1]

    # Create figure with secondary y-axis for volume
    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=[0.7, 0.3],
    )

    # Determine color based on price change
    is_positive = closes[-1] >= closes[0] if len(closes) >= 2 else True
    line_color = "#2ecc71" if is_positive else "#e74c3c"

    if chart_type == "candle" and period not in ["1D", "5D"]:
        # Candlestick chart
        fig.add_trace(
            go.Candlestick(
                x=dates,
                open=opens,
                high=highs,
                low=lows,
                close=closes,
                increasing_line_color="#2ecc71",
                decreasing_line_color="#e74c3c",
                name=ticker,
            ),
            row=1,
            col=1,
        )
    elif chart_type == "area":
        # Area chart
        fig.add_trace(
            go.Scatter(
                x=dates,
                y=closes,
                fill="tozeroy",
                fillcolor=f"rgba({46 if is_positive else 231}, {204 if is_positive else 76}, {113 if is_positive else 60}, 0.2)",
                line=dict(color=line_color, width=2),
                name=ticker,
            ),
            row=1,
            col=1,
        )
    else:
        # Line chart (default)
        fig.add_trace(
            go.Scatter(
                x=dates,
                y=closes,
                mode="lines",
                line=dict(color=line_color, width=2),
                name=ticker,
            ),
            row=1,
            col=1,
        )

    # Add volume bars
    volume_colors = [
        "#2ecc71" if closes[i] >= opens[i] else "#e74c3c"
        for i in range(len(closes))
    ]

    fig.add_trace(
        go.Bar(
            x=dates,
            y=volumes,
            marker_color=volume_colors,
            opacity=0.5,
            name="Volume",
        ),
        row=2,
        col=1,
    )

    # Update layout
    fig.update_layout(
        title=None,
        showlegend=False,
        xaxis_rangeslider_visible=False,
        margin=dict(l=0, r=0, t=10, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(
            showgrid=False,
            showticklabels=False,
        ),
        xaxis2=dict(
            showgrid=False,
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="rgba(128,128,128,0.1)",
            side="right",
        ),
        yaxis2=dict(
            showgrid=False,
            showticklabels=False,
        ),
    )

    return fig


def create_metrics_chart(metrics: Dict[str, Any]) -> go.Figure:
    """
    Create a metrics comparison chart.

    Args:
        metrics: Dictionary of metric values

    Returns:
        Plotly Figure object
    """
    if not metrics:
        return create_empty_chart("No metrics available")

    # Select key metrics for visualization
    display_metrics = {
        "P/E Ratio": metrics.get("pe_ratio", 0),
        "P/S Ratio": metrics.get("price_to_sales", 0),
        "ROE": metrics.get("roe", 0) * 100 if metrics.get("roe") else 0,
        "ROA": metrics.get("roa", 0) * 100 if metrics.get("roa") else 0,
        "Debt/Equity": metrics.get("debt_to_equity", 0),
    }

    labels = list(display_metrics.keys())
    values = list(display_metrics.values())

    fig = go.Figure(
        data=[
            go.Bar(
                x=labels,
                y=values,
                marker_color="#3498db",
                text=[f"{v:.2f}" for v in values],
                textposition="auto",
            )
        ]
    )

    fig.update_layout(
        title=None,
        showlegend=False,
        margin=dict(l=20, r=20, t=20, b=40),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False),
        yaxis=dict(
            showgrid=True,
            gridcolor="rgba(128,128,128,0.1)",
        ),
    )

    return fig


def create_peer_comparison_chart(
    company_data: Dict[str, Any],
    peers_data: List[Dict[str, Any]],
    metric: str = "pe_ratio",
) -> go.Figure:
    """
    Create a peer comparison bar chart.

    Args:
        company_data: Data for the main company
        peers_data: Data for peer companies
        metric: Metric to compare

    Returns:
        Plotly Figure object
    """
    if not company_data and not peers_data:
        return create_empty_chart("No comparison data available")

    tickers = [company_data.get("ticker", "N/A")]
    values = [company_data.get(metric, 0)]
    colors = ["#3498db"]

    for peer in peers_data:
        tickers.append(peer.get("ticker", ""))
        values.append(peer.get(metric, 0))
        colors.append("#95a5a6")

    metric_labels = {
        "pe_ratio": "P/E Ratio",
        "market_cap": "Market Cap ($B)",
        "change_percent": "Change %",
        "volume": "Volume (M)",
    }

    # Normalize market cap to billions
    if metric == "market_cap":
        values = [v / 1e9 for v in values]
    elif metric == "volume":
        values = [v / 1e6 for v in values]

    fig = go.Figure(
        data=[
            go.Bar(
                x=tickers,
                y=values,
                marker_color=colors,
                text=[f"{v:.2f}" for v in values],
                textposition="auto",
            )
        ]
    )

    fig.update_layout(
        title=metric_labels.get(metric, metric),
        showlegend=False,
        margin=dict(l=20, r=20, t=40, b=40),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False),
        yaxis=dict(
            showgrid=True,
            gridcolor="rgba(128,128,128,0.1)",
        ),
    )

    return fig


def create_geographic_exposure_chart(
    segments: List[Dict[str, Any]],
    risk_scores: Optional[Dict[str, float]] = None,
) -> go.Figure:
    """
    Create a geographic revenue exposure chart with risk overlay.

    Args:
        segments: Geographic revenue segments
        risk_scores: Optional dictionary of region to risk score

    Returns:
        Plotly Figure object
    """
    if not segments:
        return create_empty_chart("No geographic data available")

    # Aggregate by region
    region_totals: Dict[str, float] = {}
    for seg in segments:
        region = seg.get("region", "Other")
        revenue = seg.get("revenue", 0)
        if region in region_totals:
            region_totals[region] += revenue
        else:
            region_totals[region] = revenue

    regions = list(region_totals.keys())
    revenues = list(region_totals.values())
    total = sum(revenues)
    percentages = [(r / total * 100) if total > 0 else 0 for r in revenues]

    # Color by risk if available
    if risk_scores:
        colors = [
            get_risk_color(risk_scores.get(region, 50))
            for region in regions
        ]
    else:
        colors = ["#3498db"] * len(regions)

    fig = go.Figure(
        data=[
            go.Pie(
                labels=regions,
                values=revenues,
                hole=0.4,
                marker=dict(colors=colors),
                textinfo="label+percent",
                textposition="outside",
            )
        ]
    )

    fig.update_layout(
        title=None,
        showlegend=False,
        margin=dict(l=20, r=20, t=20, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        annotations=[
            dict(
                text=f"${total/1e9:.1f}B",
                x=0.5,
                y=0.5,
                font_size=16,
                showarrow=False,
            )
        ],
    )

    return fig


def create_financial_statement_chart(
    statement_data: List[Dict[str, Any]],
    metric: str = "revenue",
) -> go.Figure:
    """
    Create a chart for financial statement data.

    Args:
        statement_data: List of statement data points
        metric: Metric to visualize

    Returns:
        Plotly Figure object
    """
    if not statement_data:
        return create_empty_chart("No statement data available")

    dates = [s.get("date", "") for s in statement_data]
    values = [s.get(metric, 0) for s in statement_data]

    # Reverse for chronological order
    dates = dates[::-1]
    values = values[::-1]

    # Format values for display (convert to billions/millions)
    display_values = values
    suffix = ""
    if any(abs(v) >= 1e9 for v in values):
        display_values = [v / 1e9 for v in values]
        suffix = "B"
    elif any(abs(v) >= 1e6 for v in values):
        display_values = [v / 1e6 for v in values]
        suffix = "M"

    # Determine growth direction
    is_growing = display_values[-1] > display_values[0] if len(display_values) >= 2 else True
    bar_color = "#2ecc71" if is_growing else "#e74c3c"

    metric_labels = {
        "revenue": "Revenue",
        "net_income": "Net Income",
        "gross_profit": "Gross Profit",
        "operating_income": "Operating Income",
        "ebitda": "EBITDA",
        "total_assets": "Total Assets",
        "total_equity": "Total Equity",
        "operating_cash_flow": "Operating Cash Flow",
        "free_cash_flow": "Free Cash Flow",
    }

    fig = go.Figure(
        data=[
            go.Bar(
                x=dates,
                y=display_values,
                marker_color=bar_color,
                text=[f"${v:.1f}{suffix}" for v in display_values],
                textposition="auto",
            )
        ]
    )

    fig.update_layout(
        title=metric_labels.get(metric, metric),
        showlegend=False,
        margin=dict(l=20, r=20, t=40, b=40),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False),
        yaxis=dict(
            showgrid=True,
            gridcolor="rgba(128,128,128,0.1)",
            title=f"${suffix}",
        ),
    )

    return fig


def create_sector_performance_chart(
    sector_data: List[Dict[str, Any]],
) -> go.Figure:
    """
    Create a sector performance chart.

    Args:
        sector_data: List of sector performance data

    Returns:
        Plotly Figure object
    """
    if not sector_data:
        return create_empty_chart("No sector data available")

    # Sort by performance
    sorted_data = sorted(
        sector_data,
        key=lambda x: x.get("change_percent", 0),
        reverse=True,
    )

    sectors = [d.get("sector", "") for d in sorted_data]
    changes = [d.get("change_percent", 0) for d in sorted_data]

    colors = ["#2ecc71" if c >= 0 else "#e74c3c" for c in changes]

    fig = go.Figure(
        data=[
            go.Bar(
                x=changes,
                y=sectors,
                orientation="h",
                marker_color=colors,
                text=[f"{c:+.2f}%" for c in changes],
                textposition="auto",
            )
        ]
    )

    fig.update_layout(
        title="Sector Performance",
        showlegend=False,
        margin=dict(l=100, r=20, t=40, b=40),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(
            showgrid=True,
            gridcolor="rgba(128,128,128,0.1)",
            zeroline=True,
            zerolinecolor="rgba(128,128,128,0.3)",
        ),
        yaxis=dict(showgrid=False),
    )

    return fig


def create_empty_chart(message: str = "No data available") -> go.Figure:
    """
    Create an empty chart with a message.

    Args:
        message: Message to display

    Returns:
        Plotly Figure object
    """
    fig = go.Figure()

    fig.add_annotation(
        text=message,
        xref="paper",
        yref="paper",
        x=0.5,
        y=0.5,
        showarrow=False,
        font=dict(size=14, color="#95a5a6"),
    )

    fig.update_layout(
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=20, b=20),
    )

    return fig


def get_risk_color(score: float) -> str:
    """
    Get color based on risk score.

    Args:
        score: Risk score (0-100)

    Returns:
        Hex color string
    """
    if score >= 75:
        return "#8e44ad"  # Purple - Critical
    elif score >= 50:
        return "#e74c3c"  # Red - High
    elif score >= 25:
        return "#f39c12"  # Yellow/Orange - Moderate
    else:
        return "#2ecc71"  # Green - Low


def format_number(value: float, prefix: str = "$") -> str:
    """
    Format a number for display.

    Args:
        value: Number to format
        prefix: Prefix to add (e.g., '$')

    Returns:
        Formatted string
    """
    if value is None or value == 0:
        return "--"

    abs_val = abs(value)

    if abs_val >= 1e12:
        formatted = f"{value/1e12:.2f}T"
    elif abs_val >= 1e9:
        formatted = f"{value/1e9:.2f}B"
    elif abs_val >= 1e6:
        formatted = f"{value/1e6:.2f}M"
    elif abs_val >= 1e3:
        formatted = f"{value/1e3:.2f}K"
    else:
        formatted = f"{value:.2f}"

    return f"{prefix}{formatted}" if prefix else formatted


def format_percent(value: float) -> str:
    """
    Format a percentage for display with color indicator.

    Args:
        value: Percentage value

    Returns:
        Formatted string
    """
    if value is None:
        return "--"

    sign = "+" if value >= 0 else ""
    return f"{sign}{value:.2f}%"
