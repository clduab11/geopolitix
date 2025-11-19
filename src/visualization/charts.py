"""Chart components for risk analytics."""

from typing import Any, Dict, List, Optional
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from config.risk_thresholds import RiskThresholds


def create_trend_chart(
    data: pd.DataFrame,
    x_column: str = "date",
    y_column: str = "composite_score",
    country_column: str = "country",
    title: str = "Risk Score Trends",
) -> go.Figure:
    """
    Create time-series line chart for risk trends.

    Args:
        data: DataFrame with time series data
        x_column: Column for x-axis (time)
        y_column: Column for y-axis (values)
        country_column: Column for grouping
        title: Chart title

    Returns:
        Plotly figure object
    """
    fig = px.line(
        data,
        x=x_column,
        y=y_column,
        color=country_column,
        title=title,
        labels={
            y_column: "Risk Score",
            x_column: "Date",
        },
    )

    # Add threshold lines
    fig.add_hline(
        y=75,
        line_dash="dash",
        line_color=RiskThresholds.RISK_COLORS["critical"],
        annotation_text="Critical",
    )
    fig.add_hline(
        y=50,
        line_dash="dash",
        line_color=RiskThresholds.RISK_COLORS["high"],
        annotation_text="High",
    )
    fig.add_hline(
        y=25,
        line_dash="dash",
        line_color=RiskThresholds.RISK_COLORS["moderate"],
        annotation_text="Moderate",
    )

    fig.update_layout(
        height=400,
        xaxis_title="Date",
        yaxis_title="Risk Score",
        yaxis=dict(range=[0, 100]),
        hovermode="x unified",
    )

    return fig


def create_comparison_chart(
    data: pd.DataFrame,
    countries: List[str],
    chart_type: str = "bar",
) -> go.Figure:
    """
    Create comparison chart for multiple countries.

    Args:
        data: DataFrame with country scores
        countries: List of countries to compare
        chart_type: Type of chart (bar or radar)

    Returns:
        Plotly figure object
    """
    filtered = data[data["country"].isin(countries)]

    if chart_type == "radar":
        return _create_radar_chart(filtered)
    else:
        return _create_bar_comparison(filtered)


def _create_bar_comparison(data: pd.DataFrame) -> go.Figure:
    """Create grouped bar chart comparison."""
    factors = ["political", "economic", "security", "trade"]

    fig = go.Figure()

    for factor in factors:
        if factor in data.columns:
            fig.add_trace(
                go.Bar(
                    name=factor.capitalize(),
                    x=data["country"],
                    y=data[factor],
                    text=data[factor].round(1),
                    textposition="auto",
                )
            )

    fig.update_layout(
        title="Risk Factor Comparison",
        barmode="group",
        xaxis_title="Country",
        yaxis_title="Risk Score",
        yaxis=dict(range=[0, 100]),
        height=400,
    )

    return fig


def _create_radar_chart(data: pd.DataFrame) -> go.Figure:
    """Create radar chart comparison."""
    factors = ["political", "economic", "security", "trade"]

    fig = go.Figure()

    for _, row in data.iterrows():
        values = [row.get(f, 0) for f in factors]
        values.append(values[0])  # Close the polygon

        fig.add_trace(
            go.Scatterpolar(
                r=values,
                theta=factors + [factors[0]],
                fill="toself",
                name=row["country"],
            )
        )

    fig.update_layout(
        title="Risk Profile Comparison",
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100]),
        ),
        showlegend=True,
        height=450,
    )

    return fig


def create_correlation_matrix(
    data: pd.DataFrame,
    columns: Optional[List[str]] = None,
) -> go.Figure:
    """
    Create correlation heatmap for risk factors.

    Args:
        data: DataFrame with risk factors
        columns: Columns to include in correlation

    Returns:
        Plotly figure object
    """
    if columns is None:
        columns = ["political", "economic", "security", "trade", "composite_score"]

    # Filter to available columns
    available = [c for c in columns if c in data.columns]

    if len(available) < 2:
        # Return empty figure if not enough data
        return go.Figure()

    corr_matrix = data[available].corr()

    fig = go.Figure(
        data=go.Heatmap(
            z=corr_matrix.values,
            x=corr_matrix.columns,
            y=corr_matrix.index,
            colorscale="RdBu",
            zmid=0,
            text=corr_matrix.round(2).values,
            texttemplate="%{text}",
            textfont={"size": 12},
            colorbar=dict(title="Correlation"),
        )
    )

    fig.update_layout(
        title="Risk Factor Correlation Matrix",
        height=400,
        xaxis_title="",
        yaxis_title="",
    )

    return fig


def create_alert_timeline(
    alerts: List[Dict[str, Any]],
    max_alerts: int = 20,
) -> go.Figure:
    """
    Create timeline visualization of alerts.

    Args:
        alerts: List of alert dictionaries
        max_alerts: Maximum alerts to show

    Returns:
        Plotly figure object
    """
    if not alerts:
        fig = go.Figure()
        fig.add_annotation(
            text="No alerts to display",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
        )
        return fig

    # Take most recent alerts
    recent = alerts[:max_alerts]

    df = pd.DataFrame(recent)

    fig = go.Figure()

    # Color by risk level
    colors = {
        "critical": RiskThresholds.RISK_COLORS["critical"],
        "high": RiskThresholds.RISK_COLORS["high"],
        "moderate": RiskThresholds.RISK_COLORS["moderate"],
        "low": RiskThresholds.RISK_COLORS["low"],
    }

    for level in ["critical", "high", "moderate", "low"]:
        level_df = df[df.get("risk_level", "moderate") == level]
        if not level_df.empty:
            fig.add_trace(
                go.Scatter(
                    x=level_df.get("timestamp", range(len(level_df))),
                    y=level_df.get("score", [50] * len(level_df)),
                    mode="markers+text",
                    marker=dict(
                        size=12,
                        color=colors[level],
                    ),
                    text=level_df.get("country", ""),
                    textposition="top center",
                    name=level.capitalize(),
                )
            )

    fig.update_layout(
        title="Alert Timeline",
        xaxis_title="Time",
        yaxis_title="Risk Score",
        height=300,
        showlegend=True,
    )

    return fig


def create_scenario_comparison(
    before: Dict[str, float],
    after: Dict[str, float],
    country: str,
) -> go.Figure:
    """
    Create before/after comparison for scenario impact.

    Args:
        before: Current risk factors
        after: Projected risk factors
        country: Country name

    Returns:
        Plotly figure object
    """
    factors = ["political", "economic", "security", "trade"]

    fig = go.Figure()

    # Before values
    fig.add_trace(
        go.Bar(
            name="Current",
            x=factors,
            y=[before.get(f, 0) for f in factors],
            marker_color="lightblue",
        )
    )

    # After values
    fig.add_trace(
        go.Bar(
            name="Projected",
            x=factors,
            y=[after.get(f, 0) for f in factors],
            marker_color="coral",
        )
    )

    fig.update_layout(
        title=f"Scenario Impact: {country}",
        barmode="group",
        xaxis_title="Risk Factor",
        yaxis_title="Risk Score",
        yaxis=dict(range=[0, 100]),
        height=350,
    )

    return fig


def create_exposure_pie(
    exposure_data: Dict[str, float],
    title: str = "Risk Exposure Distribution",
) -> go.Figure:
    """
    Create pie chart showing risk exposure distribution.

    Args:
        exposure_data: Dictionary mapping regions/factors to exposure
        title: Chart title

    Returns:
        Plotly figure object
    """
    fig = go.Figure(
        data=go.Pie(
            labels=list(exposure_data.keys()),
            values=list(exposure_data.values()),
            hole=0.3,
            textinfo="percent+label",
        )
    )

    fig.update_layout(
        title=title,
        height=350,
    )

    return fig


def create_gauge_chart(
    value: float,
    title: str = "Risk Score",
    max_value: float = 100,
) -> go.Figure:
    """
    Create gauge chart for single risk score.

    Args:
        value: Risk score value
        title: Chart title
        max_value: Maximum value for gauge

    Returns:
        Plotly figure object
    """
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number+delta",
            value=value,
            domain={"x": [0, 1], "y": [0, 1]},
            title={"text": title},
            gauge={
                "axis": {"range": [0, max_value]},
                "bar": {"color": RiskThresholds.get_risk_color(value)},
                "steps": [
                    {"range": [0, 25], "color": "lightgreen"},
                    {"range": [25, 50], "color": "lightyellow"},
                    {"range": [50, 75], "color": "lightsalmon"},
                    {"range": [75, 100], "color": "lightcoral"},
                ],
                "threshold": {
                    "line": {"color": "red", "width": 4},
                    "thickness": 0.75,
                    "value": 75,
                },
            },
        )
    )

    fig.update_layout(height=250)

    return fig
