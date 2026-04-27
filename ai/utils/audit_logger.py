"""
Lightweight audit logging for AI runner events.

Writes append-only JSONL events under:
  ai/logs/YYYY-MM-DD/events.jsonl
"""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


LOG_ROOT = Path("ai/logs")


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _day_from_iso(iso_ts: str) -> str:
    # Keep UTC day for deterministic CI behavior.
    return iso_ts[:10]


def _safe_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value)


def log_ai_event(
    *,
    agent: str,
    pr_number: int,
    status: str,
    decision_reason: str,
    input_tokens: int = 0,
    output_tokens: int = 0,
    total_tokens: int = 0,
    cost_usd: float = 0.0,
    error_type: str = "",
    error_message: str = "",
    tags: Optional[List[str]] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> Path:
    """
    Append one event record to the daily JSONL log file.
    """
    ts = _utc_now_iso()
    day = _day_from_iso(ts)
    target_dir = LOG_ROOT / day
    target_dir.mkdir(parents=True, exist_ok=True)
    event_path = target_dir / "events.jsonl"

    payload = {
        "event_id": str(uuid.uuid4()),
        "timestamp": ts,
        "agent": _safe_text(agent),
        "pr_number": int(pr_number),
        "status": _safe_text(status),  # success | failed | partial
        "decision_reason": _safe_text(decision_reason),
        "tokens": {
            "input": int(input_tokens),
            "output": int(output_tokens),
            "total": int(total_tokens),
        },
        "cost_usd": round(float(cost_usd), 6),
        "error_type": _safe_text(error_type),
        "error_message": _safe_text(error_message),
        "tags": tags or [],
        "metadata": metadata or {},
    }

    with event_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False) + "\n")

    return event_path


def load_events(day: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Load all events for a UTC day (YYYY-MM-DD). Defaults to today (UTC).
    """
    day = day or _day_from_iso(_utc_now_iso())
    event_path = LOG_ROOT / day / "events.jsonl"
    if not event_path.exists():
        return []

    rows: List[Dict[str, Any]] = []
    with event_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def build_daily_summary(day: Optional[str] = None) -> Dict[str, Any]:
    """
    Build a compact daily summary from JSONL events.
    """
    events = load_events(day=day)
    summary: Dict[str, Any] = {
        "day": day or _day_from_iso(_utc_now_iso()),
        "event_count": len(events),
        "success_count": 0,
        "failed_count": 0,
        "partial_count": 0,
        "total_cost_usd": 0.0,
        "agents": {},
    }

    for event in events:
        status = event.get("status", "")
        agent = event.get("agent", "unknown")
        cost = float(event.get("cost_usd", 0.0) or 0.0)
        tokens = event.get("tokens", {}) or {}
        total_tokens = int(tokens.get("total", 0) or 0)

        if status == "success":
            summary["success_count"] += 1
        elif status == "failed":
            summary["failed_count"] += 1
        else:
            summary["partial_count"] += 1

        summary["total_cost_usd"] = round(summary["total_cost_usd"] + cost, 6)

        agent_row = summary["agents"].setdefault(
            agent,
            {
                "event_count": 0,
                "success_count": 0,
                "failed_count": 0,
                "total_tokens": 0,
                "total_cost_usd": 0.0,
            },
        )
        agent_row["event_count"] += 1
        agent_row["total_tokens"] += total_tokens
        agent_row["total_cost_usd"] = round(agent_row["total_cost_usd"] + cost, 6)
        if status == "success":
            agent_row["success_count"] += 1
        elif status == "failed":
            agent_row["failed_count"] += 1

    return summary
