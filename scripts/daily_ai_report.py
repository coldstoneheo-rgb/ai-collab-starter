#!/usr/bin/env python3
"""
Generate daily AI observability summary from audit logs.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from ai.utils.audit_logger import build_daily_summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate daily AI summary")
    parser.add_argument(
        "--day",
        default=None,
        help="UTC day in YYYY-MM-DD format (default: today UTC)",
    )
    args = parser.parse_args()

    summary = build_daily_summary(day=args.day)
    day = summary["day"]
    out_dir = Path("ai/logs") / day
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "daily_summary.json"
    out_file.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Daily summary written: {out_file}")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
