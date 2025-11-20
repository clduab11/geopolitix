#!/usr/bin/env python3
"""
GEOPOLITIX - Geopolitical Risk Analysis Dashboard

Main application entry point for the Dash dashboard.
"""

import dash
import dash_bootstrap_components as dbc

from config.settings import Settings
from src.visualization.layouts import create_layout
from src.visualization.callbacks import register_callbacks
from src.utils.logger import get_logger

logger = get_logger(__name__)


def create_app() -> dash.Dash:
    """
    Create and configure the Dash application.

    Returns:
        Configured Dash application instance
    """
    # Initialize Dash app with Bootstrap theme
    app = dash.Dash(
        __name__,
        external_stylesheets=[
            dbc.themes.FLATLY,
            "https://use.fontawesome.com/releases/v5.15.4/css/all.css",
        ],
        title="GEOPOLITIX - Geopolitical Risk Dashboard",
        update_title="Loading...",
        suppress_callback_exceptions=True,
    )

    # Set app layout
    app.layout = create_layout()

    # Register callbacks
    register_callbacks(app)

    logger.info("GEOPOLITIX application initialized")

    return app


def main():
    """Run the application."""
    app = create_app()

    logger.info(f"Starting GEOPOLITIX on {Settings.HOST}:{Settings.PORT}")

    app.run_server(
        host=Settings.HOST,
        port=Settings.PORT,
        debug=Settings.DEBUG,
    )


if __name__ == "__main__":
    main()
