# AGENTS.md: Agentic Refactor Guide

This document guides the AI agents and human developers working on the Geopolitix refactor.

## Coding Principles

1.  **Small, Atomic PRs**: Changes should be focused and reviewable. Avoid massive "rewrite everything" commits.
2.  **Test-Driven**: Every new feature or fix must have accompanying unit tests.
3.  **Type Hints**: Use python type hinting (`typing`) strictly for all function signatures and class attributes.
4.  **Deterministic Pipelines**: Data processing and model training steps must be reproducible. Set seeds where applicable.
5.  **Reproducible Backtests**: Simulation results must be saved with full configuration metadata to allow exact reproduction.
6.  **Logging**: Use structured logging instead of print statements for tracking pipeline progress and errors.

## Refactor Strategy

- **Separation of Concerns**: Keep the legacy "Geopolitical Risk Dashboard" separate from the new "Prediction Market Analysis" modules (`src/markets/`).
- **Feature Flagging**: Keep old functionality operational. Hide unstable new features behind configuration flags until they are "Definition of Done".
- **Parallel Development**: We build the `src/markets` package alongside the existing `src/risk_engine` without breaking the current `app.py`.

## Initial Tickets Checklist

- [ ] **Docs Outline**: Create `docs/prediction_markets.md` with section headers (Methodology, Data Sources, Metrics).
- [ ] **New Package Init**: Create `src/markets/__init__.py`.
- [ ] **Connectors**:
  - [ ] Define abstract base class for connectors in `src/markets/connectors/base.py`.
  - [ ] Implement `MockConnector` in `src/markets/connectors/mock.py`.
- [ ] **Feature Extraction**:
  - [ ] Create `src/markets/features/` module.
  - [ ] Implement basic time-series feature extractors.
- [ ] **Models**:
  - [ ] Create `src/markets/models/`.
  - [ ] Implement Baseline (Moving Average).
  - [ ] Implement Logistic Calibration model.
- [ ] **Evaluation**:
  - [ ] Create `src/markets/eval/`.
  - [ ] Implement backtest harness to run models against historical data.
- [ ] **Tests**:
  - [ ] Create `tests/markets/` directory.
  - [ ] Add unit tests for all above components.

## Experiment Record Format

All model runs and backtests should save artifacts to a local directory: `artifacts/runs/YYYYMMDD_HHMM/`.

**Required Metadata (`meta.json`):**

```json
{
  "timestamp": "2023-10-27T10:00:00Z",
  "commit_hash": "a1b2c3d...",
  "config": {
    "model": "logistic_calibration",
    "features": ["30d_vol", "news_sentiment"],
    "window_size": 100
  },
  "metrics": {
    "log_loss": 0.45,
    "accuracy": 0.62
  }
}
```

## Definition of Done

- **Connector Done**: Can fetch data (real or mock), parse it into the standard internal schema, and handle connection errors gracefully.
- **Features Done**: Input raw market data -> Output distinct feature dataframe. Unit tested for NaN handling and edge cases.
- **Model Done**: `train()`, `predict()`, and `save/load` methods implemented. Performance metrics logged.
- **Eval Done**: Harness runs a full simulation without crashing and produces a valid `meta.json` and result plots.
