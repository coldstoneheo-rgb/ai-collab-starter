# ai/utils/cost_monitor.py
"""
Cost monitoring and enforcement.

Reads .ai/budget.json, tracks spend, and enforces limits:
- WARN at 80% of monthly budget
- BLOCK at 100% (raises BudgetExceededError)

budget.json schema:
{
  "monthly_budget_usd": 50.0,
  "monthly_spent_usd": 0.0,
  "last_reset": "YYYY-MM",
  "agents": {
    "claude": 0.0,
    "gemini": 0.0,
    "perplexity": 0.0,
    "gpt": 0.0
  }
}
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any

BUDGET_FILE = Path(".ai/budget.json")
WARN_THRESHOLD = 0.80


class BudgetExceededError(Exception):
    """Raised when monthly budget is exhausted."""
    pass


def _current_month() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m")


def _load_budget(path: Path = BUDGET_FILE) -> Dict[str, Any]:
    if not path.exists():
        return {
            "monthly_budget_usd": 50.0,
            "monthly_spent_usd": 0.0,
            "last_reset": _current_month(),
            "agents": {"claude": 0.0, "gemini": 0.0, "perplexity": 0.0, "gpt": 0.0},
        }
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def _save_budget(data: Dict[str, Any], path: Path = BUDGET_FILE) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)


def _auto_reset_if_new_month(data: Dict[str, Any]) -> Dict[str, Any]:
    """Reset monthly spend if it's a new month."""
    current = _current_month()
    if data.get("last_reset", "") != current:
        data["monthly_spent_usd"] = 0.0
        data["agents"] = {k: 0.0 for k in data.get("agents", {})}
        data["last_reset"] = current
    return data


def record_cost(agent: str, cost_usd: float, path: Path = BUDGET_FILE) -> Dict[str, Any]:
    """
    Record cost for an agent call and enforce budget limits.

    Raises BudgetExceededError if budget is already exhausted before this call.
    Returns the updated budget state.
    """
    data = _load_budget(path)
    data = _auto_reset_if_new_month(data)

    budget = float(data.get("monthly_budget_usd", 50.0))
    spent = float(data.get("monthly_spent_usd", 0.0))

    # Check before adding (pre-flight guard)
    if spent >= budget:
        raise BudgetExceededError(
            f"Monthly budget exhausted: ${spent:.2f} / ${budget:.2f}. "
            "Set a higher monthly_budget_usd in .ai/budget.json or wait for next month."
        )

    # Update spend
    data["monthly_spent_usd"] = round(spent + cost_usd, 6)
    agents = data.setdefault("agents", {})
    agents[agent] = round(float(agents.get(agent, 0.0)) + cost_usd, 6)

    _save_budget(data, path)

    # Emit warnings
    new_spent = data["monthly_spent_usd"]
    ratio = new_spent / budget if budget > 0 else 0.0

    if ratio >= 1.0:
        print(
            f"🚨 BUDGET EXCEEDED: ${new_spent:.2f} / ${budget:.2f}. "
            "AI automation will be blocked on next call."
        )
    elif ratio >= WARN_THRESHOLD:
        remaining = budget - new_spent
        print(
            f"⚠️ Budget warning: {ratio*100:.0f}% used "
            f"(${new_spent:.2f} / ${budget:.2f}, ${remaining:.2f} remaining)"
        )

    return data


def get_budget_status(path: Path = BUDGET_FILE) -> Dict[str, Any]:
    """
    Return current budget status without modifying anything.

    Returns:
        dict with keys: monthly_budget_usd, monthly_spent_usd,
        remaining_usd, usage_pct, is_over_budget, is_near_limit, agents
    """
    data = _load_budget(path)
    data = _auto_reset_if_new_month(data)

    budget = float(data.get("monthly_budget_usd", 50.0))
    spent = float(data.get("monthly_spent_usd", 0.0))
    remaining = max(0.0, budget - spent)
    usage_pct = round((spent / budget * 100) if budget > 0 else 0.0, 1)

    return {
        "monthly_budget_usd": budget,
        "monthly_spent_usd": round(spent, 4),
        "remaining_usd": round(remaining, 4),
        "usage_pct": usage_pct,
        "is_over_budget": spent >= budget,
        "is_near_limit": usage_pct >= WARN_THRESHOLD * 100,
        "agents": data.get("agents", {}),
    }
