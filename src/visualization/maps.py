"""Choropleth map visualizations."""

import plotly.graph_objects as go
import pandas as pd

from config.risk_thresholds import RiskThresholds
from src.utils.transformers import country_to_iso


def create_choropleth_map(
    data: pd.DataFrame,
    value_column: str = "composite_score",
    title: str = "Global Geopolitical Risk Map",
) -> go.Figure:
    """
    Create an interactive choropleth map showing risk scores.

    Args:
        data: DataFrame with country and risk score data
        value_column: Column name for values to display
        title: Map title

    Returns:
        Plotly figure object
    """
    # Ensure ISO codes are present
    if "iso_code" not in data.columns and "country" in data.columns:
        data = data.copy()
        data["iso_code"] = data["country"].apply(country_to_iso)

    fig = go.Figure(
        data=go.Choropleth(
            locations=data["iso_code"],
            z=data[value_column],
            text=data["country"],
            colorscale=RiskThresholds.CHOROPLETH_COLORSCALE,
            autocolorscale=False,
            reversescale=False,
            marker_line_color="darkgray",
            marker_line_width=0.5,
            colorbar=dict(
                title="Risk Score",
                thickness=15,
                len=0.7,
                x=1.0,
                tickvals=[0, 25, 50, 75, 100],
                ticktext=["Low", "Moderate-Low", "Moderate", "High", "Critical"],
            ),
            hovertemplate=(
                "<b>%{text}</b><br>" "Risk Score: %{z:.1f}<br>" "<extra></extra>"
            ),
        )
    )

    fig.update_layout(
        title=dict(
            text=title,
            x=0.5,
            xanchor="center",
            font=dict(size=20),
        ),
        geo=dict(
            showframe=False,
            showcoastlines=True,
            coastlinecolor="lightgray",
            projection_type="equirectangular",
            showland=True,
            landcolor="rgb(243, 243, 243)",
            showocean=True,
            oceancolor="rgb(204, 229, 255)",
            showlakes=True,
            lakecolor="rgb(204, 229, 255)",
        ),
        margin=dict(l=0, r=0, t=50, b=0),
        height=500,
    )

    return fig


def create_region_map(
    data: pd.DataFrame,
    region: str,
    value_column: str = "composite_score",
) -> go.Figure:
    """
    Create a regional focused choropleth map.

    Args:
        data: DataFrame with country data
        region: Region to focus on
        value_column: Column for values

    Returns:
        Plotly figure object
    """
    # Region scope mappings for Plotly
    region_scopes = {
        "Europe": "europe",
        "Asia": "asia",
        "Africa": "africa",
        "North America": "north america",
        "South America": "south america",
        "Middle East": "asia",
    }

    scope = region_scopes.get(region, "world")

    fig = create_choropleth_map(data, value_column, f"{region} Risk Map")

    fig.update_geos(
        scope=scope,
        showcountries=True,
        countrycolor="darkgray",
    )

    return fig


def create_risk_bubble_map(
    data: pd.DataFrame,
    size_column: str = "composite_score",
    color_column: str = "risk_level",
) -> go.Figure:
    """
    Create a bubble map showing risk levels.

    Args:
        data: DataFrame with country data including lat/lon
        size_column: Column for bubble size
        color_column: Column for bubble color

    Returns:
        Plotly figure object
    """
    # Country centroids (simplified)
    country_coords = {
        "United States": (39.8, -98.5),
        "China": (35.0, 105.0),
        "Russia": (61.5, 105.0),
        "India": (20.0, 77.0),
        "Brazil": (-14.2, -51.9),
        "United Kingdom": (55.4, -3.4),
        "Germany": (51.2, 10.5),
        "France": (46.2, 2.2),
        "Japan": (36.2, 138.3),
        "South Korea": (35.9, 127.8),
    }

    # Add coordinates
    data = data.copy()
    data["lat"] = data["country"].apply(lambda x: country_coords.get(x, (0, 0))[0])
    data["lon"] = data["country"].apply(lambda x: country_coords.get(x, (0, 0))[1])

    # Color mapping
    color_map = {
        "low": RiskThresholds.RISK_COLORS["low"],
        "moderate": RiskThresholds.RISK_COLORS["moderate"],
        "high": RiskThresholds.RISK_COLORS["high"],
        "critical": RiskThresholds.RISK_COLORS["critical"],
    }

    fig = go.Figure()

    for level in ["low", "moderate", "high", "critical"]:
        level_data = data[data[color_column] == level]
        if not level_data.empty:
            fig.add_trace(
                go.Scattergeo(
                    lon=level_data["lon"],
                    lat=level_data["lat"],
                    text=level_data["country"],
                    marker=dict(
                        size=level_data[size_column] / 3,
                        color=color_map[level],
                        line=dict(width=1, color="white"),
                        sizemode="area",
                    ),
                    name=level.capitalize(),
                    hovertemplate=(
                        "<b>%{text}</b><br>"
                        f"Risk Level: {level.capitalize()}<br>"
                        "<extra></extra>"
                    ),
                )
            )

    fig.update_layout(
        title="Risk Bubble Map",
        geo=dict(
            showframe=False,
            showcoastlines=True,
            projection_type="natural earth",
        ),
        showlegend=True,
        margin=dict(l=0, r=0, t=50, b=0),
    )

    return fig


def create_risk_heatmap_overlay(
    data: pd.DataFrame,
    time_column: str = "timestamp",
    country_column: str = "country",
    value_column: str = "composite_score",
) -> go.Figure:
    """
    Create a heatmap showing risk evolution over time.

    Args:
        data: DataFrame with time series risk data
        time_column: Column with timestamps
        country_column: Column with country names
        value_column: Column with risk values

    Returns:
        Plotly figure object
    """
    # Pivot data for heatmap
    pivot = data.pivot_table(
        index=country_column,
        columns=time_column,
        values=value_column,
        aggfunc="mean",
    ).fillna(0)

    fig = go.Figure(
        data=go.Heatmap(
            z=pivot.values,
            x=pivot.columns,
            y=pivot.index,
            colorscale=RiskThresholds.CHOROPLETH_COLORSCALE,
            colorbar=dict(title="Risk Score"),
        )
    )

    fig.update_layout(
        title="Risk Evolution Heatmap",
        xaxis_title="Time",
        yaxis_title="Country",
        height=400,
    )

    return fig
