"""
Market Pipeline Orchestrator.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from .types import MarketData, Prediction, BacktestResult
from .connectors.base import BaseConnector
from .models.baselines import BaseForecaster
from .eval.backtest import BacktestHarness

logger = logging.getLogger(__name__)


class MarketPipeline:
    """
    Orchestrates the flow of data from connectors to models to evaluation.
    """

    def __init__(
        self,
        connector: BaseConnector,
        models: List[BaseForecaster],
        backtester: Optional[BacktestHarness] = None,
    ):
        self.connector = connector
        self.models = models
        self.backtester = backtester

    def fetch_data(self, symbols: List[str], **kwargs) -> Dict[str, MarketData]:
        """Fetch data for multiple symbols."""
        results = {}
        for symbol in symbols:
            try:
                data = self.connector.fetch_history(symbol, **kwargs)
                results[symbol] = data
            except Exception as e:
                logger.error(f"Failed to fetch data for {symbol}: {e}")
        return results

    def run_predictions(self, market_data: Dict[str, MarketData]) -> List[Prediction]:
        """Generate predictions for current market state."""
        predictions = []
        for symbol, data in market_data.items():
            for model in self.models:
                try:
                    # Expecting model.predict to return a Prediction object
                    # For now, simplistic interface assumption, might refine in BaseForecaster
                    pred = model.train_predict(data)
                    predictions.append(pred)
                except Exception as e:
                    logger.error(f"Model {model.name} failed on {symbol}: {e}")
        return predictions

    def run_backtest(
        self,
        market_data: Dict[str, MarketData],
        start_date: datetime,
        end_date: datetime,
    ) -> List[BacktestResult]:
        """Run backtest on historical data."""
        if not self.backtester:
            logger.warning("No backtester configured.")
            return []

        results = []
        for symbol, data in market_data.items():
            result = self.backtester.run(
                data=data,
                models=self.models,
                start_date=start_date,
                end_date=end_date,
            )
            results.append(result)
        return results

    def run_signals_enrichment(
        self, queries: List[str], run_id: str, config: Optional[Dict[str, Any]] = None
    ) -> List[
        Any
    ]:  # List[EvidencePack] but typed loosely to avoid circular imports if not careful
        """
        Run the Web Signals Feedforward Layer.
        """
        import os

        if str(os.getenv("ENABLE_SIGNALS_LAYER", "false")).lower() != "true":
            logger.info("Signals Layer disabled.")
            return []

        from .signals.orchestrator import SignalsOrchestrator

        orchestrator = SignalsOrchestrator(config)
        packs = []
        for q in queries:
            try:
                pack = orchestrator.build_evidence_pack(q, run_id=run_id)
                packs.append(pack)
            except Exception as e:
                logger.error(f"Signals enrichment failed for query '{q}': {e}")

        return packs
