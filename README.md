# Geopolitix: Prediction Market Intelligence + Geopolitical Event Forecasting Lab

**Geopolitix (v2)** is a research laboratory for market microstructure analysis, price dynamics, and geopolitical event forecasting. We leverage public market prices, news signals, and machine learning to build calibrated forecasting systems.

> [!IMPORTANT] > **Compliance & Risk Disclaimer**
> This project is for **research and educational purposes only**. It involves the analysis of prediction markets which may be regulated in your jurisdiction.
>
> - **Not Financial Advice**: Nothing in this repository constitutes financial, investment, or legal advice.
> - **No Guarantees**: We do not guarantee profit or predictive accuracy. This tool is for simulation, evaluation, and market microstructure analysis.
> - **Compliance**: Users are responsible for complying with all local laws and regulations regarding prediction markets and online trading.
> - **ToS Respect**: Users must respect the Terms of Service and rate limits of all data providers and platforms accessed.

## Why this exists

Prediction markets offer a unique, real-time probability signal for global events. By combining these market signals with traditional news embeddings and causal analysis, we aim to build a more robust geopolitical forecasting engine. This lab exists to reverse-engineer the "wisdom of the crowd" — analyzing liquidity, order book dynamics, and arbitrage opportunities to understand how information flows into prices.

## What we analyze

- **Market Microstructure**: Price time series, bid-ask spreads, volume, liquidity depth, and implied probabilities.
- **Signals**: News/event embeddings, social sentiment, and multi-modal data streams.
- **Model Performance**: Comparative analysis of baseline statistical models vs. ML approaches vs. LLM-assisted feature extraction.
- **Simulation**: A framework for backtesting strategies and paper trading to evaluate theoretically profitable signals over time.
- **Alerting**: Real-time dashboards for anomaly detection and significant probability shifts.

## Architecture at a glance

The repository is structured to support both the legacy risk dashboard and the new prediction market lab:

- `src/`: Core source code.
  - `src/markets/`: **[NEW]** Prediction market intelligence modules (connectors, features, models).
  - `src/risk_engine/`: Legacy geopolitical risk scoring algorithms.
  - `src/data_sources/`: External API integrations (NewsAPI, ACLED, etc.).
- `scripts/`: Utility scripts for data fetching, database migrations, and manual tasks.
- `config/`: Configuration for settings, API endpoints, and risk thresholds.
- `docs/`: Project documentation.
- `tests/`: Unit and integration tests, mirroring the `src/` structure.

## Roadmap (First 2 Weeks)

- **Data Connectors**: Implement CSV/mock connectors and one public API stub for market data.
- **Schema Definitions**: Finalize data models for markets, positions, and order books.
- **Baseline Models**: Implement simple moving average and logistic calibration models for initial benchmarking.
- **Evaluation Harness**: Build the backtesting and paper trading loop.
- **Dashboard Updates**: Integrate preliminary market signals into the main dashboard.

## Quickstart

### Standard Mode (Run the App)

Get the current dashboard up and running:

1.  **Install**:
    ```bash
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```
2.  **Configure**:
    Copy `.env.example` to `.env` and set your API keys (NewsAPI, etc.).
    ```bash
    cp .env.example .env
    ```
3.  **Run**:
    ```bash
    python app.py
    ```

### Refactor Mode (Run New Modules)

To work on the new prediction market components:

1.  **Test the new package**:
    ```bash
    pytest tests/markets/
    ```
2.  **Run a mock simulation** (once implemented):
    ```bash
    python -m src.markets.eval.run_backtest --config config/backtest_default.yaml
    ```

## Docs

- [ARCHITECTURE.md](ARCHITECTURE.md): System design and component interaction.
- [API_REFERENCE.md](API_REFERENCE.md): Internal and external API details.
- [docs/prediction_markets.md](docs/prediction_markets.md): Detailed methodology for market analysis.
- [docs/evaluation.md](docs/evaluation.md): Guide to the backtesting and simulation framework.

## Security

**Never commit API keys or secrets.** Use the `.env` file for all sensitive configuration. Ensure your `.gitignore` includes local environment files and data dumps.

## License

MIT License - see LICENSE file for details.
