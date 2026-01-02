"""
Script to run the Web Signals Feedforward Layer manually.
Usage:
  python scripts/run_signals_pack.py --query "Will the fed cut rates?" --providers tavily,jina --max-sources 5
"""

import sys
import os
import argparse
import logging
import json
import time
from datetime import datetime
from dataclasses import asdict

# Ensure src is in path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from markets.signals.orchestrator import SignalsOrchestrator
from markets.signals.types import EvidencePack

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

ARTIFACTS_DIR = "artifacts/runs"


def main():
    parser = argparse.ArgumentParser(description="Run Web Signals Feedforward Layer")
    parser.add_argument("--query", required=True, help="Search query context")
    parser.add_argument(
        "--providers",
        default=None,
        help="Comma-separated providers (tavily,firecrawl,jina)",
    )
    parser.add_argument(
        "--allowlist", default=None, help="Comma-separated domain allowlist"
    )
    parser.add_argument(
        "--max-sources", type=int, default=5, help="Max search hits to process"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Run but don't save full artifacts?"
    )
    # Actually dry run usually means don't hit external APIs, but here we probably want to real run or mock run.
    # The user requirements said: "dry mode" with mocked HTTP OR with real keys if present.
    # For this script we will assume real keys unless env vars are missing.

    args = parser.parse_args()

    # Load default config
    config_path = os.path.join("config", "signals.json")
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            config = json.load(f)
    else:
        config = {}

    # Overrides
    if args.providers:
        config["default_providers"] = args.providers.split(",")
    if args.allowlist:
        config["allowlist"] = args.allowlist.split(",")
    if args.max_sources:
        config["max_sources"] = args.max_sources

    logger.info(f"Starting Signals Run with query: {args.query}")
    logger.info(f"Config: {config}")

    orchestrator = SignalsOrchestrator(config)

    run_id = f"run_{int(time.time())}"
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")

    try:
        pack = orchestrator.build_evidence_pack(args.query, run_id=run_id)

        logger.info(
            f"Run Complete. Docs: {pack.doc_count}, Links: {len(pack.search_hits)}"
        )

        # Save Artifacts
        output_dir = os.path.join(ARTIFACTS_DIR, timestamp, "signals")
        os.makedirs(output_dir, exist_ok=True)

        # 1. Evidence Pack Summary (sans heavy embeddings/docs if desired, but requirements say full pack)
        # We will dump the structure as is, dataclass to dict

        # Helper to convert dataclass to dict with enum handling
        def complex_dumper(obj):
            if hasattr(obj, "value"):  # Enum
                return obj.value
            if isinstance(obj, datetime):
                return obj.isoformat()
            return obj.__dict__

        # We split outputs as requested:
        # signals_config.json
        # sources.json
        # documents.jsonl
        # embeddings.jsonl
        # index.json

        # Config
        with open(os.path.join(output_dir, "signals_config.json"), "w") as f:
            json.dump(config, f, indent=2)

        # Sources (Hits)
        sources = [asdict(h) for h in pack.search_hits]
        with open(os.path.join(output_dir, "sources.json"), "w") as f:
            json.dump(sources, f, indent=2, default=str)

        # Documents (JSONL)
        with open(os.path.join(output_dir, "documents.jsonl"), "w") as f:
            for doc in pack.documents:
                # Handle enum in doc provider
                d_dict = asdict(doc)
                d_dict["provider"] = (
                    str(doc.provider.value)
                    if hasattr(doc.provider, "value")
                    else str(doc.provider)
                )
                f.write(json.dumps(d_dict, default=str) + "\n")

        # Embeddings (JSONL)
        with open(os.path.join(output_dir, "embeddings.jsonl"), "w") as f:
            for emb in pack.embeddings:
                f.write(json.dumps(emb, default=str) + "\n")

        logger.info(f"Artifacts saved to {output_dir}")
        print(f"SUCCESS: {output_dir}")

    except Exception as e:
        logger.error(f"Run Failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
