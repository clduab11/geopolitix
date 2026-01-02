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

    # Markets Lab Integration (Feature Flagged)
    if Settings.ENABLE_MARKETS_LAB:
        import flask
        from scripts.run_markets_pipeline import main as run_pipeline_main

        @app.server.route("/markets/health")
        def markets_health():
            return flask.jsonify({"status": "ok", "lab_enabled": True})

        @app.server.route("/markets/providers")
        def list_providers():
            return flask.jsonify(["mock", "polymarket"])

        @app.server.route("/markets/<provider>/run", methods=["POST"])
        def run_provider_pipeline(provider):
            try:
                # Basic validation
                if provider not in ["mock", "polymarket"]:
                    return flask.jsonify(
                        {"status": "error", "message": "Invalid provider"}
                    ), 400

                # Input args
                data = flask.request.get_json() or {}
                symbol = data.get("symbol", "GPT5")
                days = int(data.get("days", 30))

                logger.info(f"Received request to run {provider} pipeline for {symbol}")

                # Execute pipeline via Shell for clean isolation (simplest integration)
                import subprocess
                import sys

                # Construct command
                cmd = [
                    sys.executable,
                    "scripts/run_markets_pipeline.py",
                    "--provider",
                    provider,
                    "--symbol",
                    symbol,
                    "--days",
                    str(days),
                ]

                # Run synchronously
                result = subprocess.run(cmd, capture_output=True, text=True)

                if result.returncode != 0:
                    raise Exception(f"Script failed: {result.stderr}")

                return flask.jsonify(
                    {
                        "status": "success",
                        "message": f"{provider} pipeline executed",
                        "output": result.stdout,
                    }
                )

            except Exception as e:
                logger.error(f"Pipeline execution failed: {e}")
                return flask.jsonify({"status": "error", "message": str(e)}), 500

        logger.info("Markets Lab endpoints registered")

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
