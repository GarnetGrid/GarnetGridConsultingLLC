#!/usr/bin/env python3
"""Fetch a curated list of internet pages and write them into the local KB as clean Markdown.

Usage (from jgpt-api/):
  python scripts/ingest_web.py
  python scripts/ingest_web.py --force
  python scripts/ingest_web.py --max 5

Then ingest into pgvector:
  curl -s -X POST http://localhost:8000/ingest/kb
"""

from __future__ import annotations

import asyncio
import sys
import argparse
from pathlib import Path

# Add project root to path to allow importing app modules
ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from app.services.web_ingest import run_ingest

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true", help="Overwrite existing files.")
    ap.add_argument("--max", type=int, default=0, help="Max pages to fetch (0 = all).")
    args = ap.parse_args()

    print("Starting Web Ingestion (Async)...")
    try:
        result = asyncio.run(run_ingest(force=args.force, max_pages=args.max))
        
        if not result["ok"]:
            print(f"Error: {result['error']}", file=sys.stderr)
            return 1
            
        summary = result["details"]
        print(f"\nDone.")
        print(f"Total: {summary['total']}")
        print(f"Saved: {summary['saved']}")
        print(f"Skipped: {summary['skipped']}")
        print(f"Failed: {summary['failed']}")
        
        return 0 if summary["failed"] == 0 else 1
    except KeyboardInterrupt:
        print("\nCancelled.")
        return 130
    except Exception as e:
        print(f"\nFatal Error: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
