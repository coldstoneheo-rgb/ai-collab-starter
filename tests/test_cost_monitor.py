# tests/test_cost_monitor.py
"""
Unit tests for cost_monitor.py — budget tracking and enforcement.
"""
import json
import pytest
from pathlib import Path

from ai.utils.cost_monitor import (
    record_cost,
    get_budget_status,
    BudgetExceededError,
    _current_month,
)


def _write_budget(tmp_path: Path, data: dict) -> Path:
    p = tmp_path / ".ai" / "budget.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data), encoding="utf-8")
    return p


class TestRecordCost:

    def test_records_cost_and_returns_state(self, tmp_path):
        p = _write_budget(tmp_path, {
            "monthly_budget_usd": 10.0,
            "monthly_spent_usd": 0.0,
            "last_reset": _current_month(),
            "agents": {"claude": 0.0},
        })
        state = record_cost("claude", 1.0, path=p)
        assert state["monthly_spent_usd"] == pytest.approx(1.0)
        assert state["agents"]["claude"] == pytest.approx(1.0)

    def test_accumulates_across_calls(self, tmp_path):
        p = _write_budget(tmp_path, {
            "monthly_budget_usd": 10.0,
            "monthly_spent_usd": 0.0,
            "last_reset": _current_month(),
            "agents": {"claude": 0.0},
        })
        record_cost("claude", 1.0, path=p)
        record_cost("claude", 2.5, path=p)
        state = record_cost("claude", 0.5, path=p)
        assert state["monthly_spent_usd"] == pytest.approx(4.0)
        assert state["agents"]["claude"] == pytest.approx(4.0)

    def test_raises_when_budget_exhausted(self, tmp_path):
        p = _write_budget(tmp_path, {
            "monthly_budget_usd": 5.0,
            "monthly_spent_usd": 5.0,
            "last_reset": _current_month(),
            "agents": {"claude": 5.0},
        })
        with pytest.raises(BudgetExceededError):
            record_cost("claude", 0.01, path=p)

    def test_raises_when_spent_exceeds_budget(self, tmp_path):
        p = _write_budget(tmp_path, {
            "monthly_budget_usd": 5.0,
            "monthly_spent_usd": 6.0,
            "last_reset": _current_month(),
            "agents": {},
        })
        with pytest.raises(BudgetExceededError):
            record_cost("claude", 0.01, path=p)

    def test_warn_threshold_prints(self, tmp_path, capsys):
        p = _write_budget(tmp_path, {
            "monthly_budget_usd": 10.0,
            "monthly_spent_usd": 7.9,
            "last_reset": _current_month(),
            "agents": {"claude": 7.9},
        })
        record_cost("claude", 0.2, path=p)
        captured = capsys.readouterr()
        assert "warning" in captured.out.lower() or "Budget" in captured.out

    def test_budget_exceeded_print_warning(self, tmp_path, capsys):
        p = _write_budget(tmp_path, {
            "monthly_budget_usd": 10.0,
            "monthly_spent_usd": 9.95,
            "last_reset": _current_month(),
            "agents": {"claude": 9.95},
        })
        record_cost("claude", 0.1, path=p)
        captured = capsys.readouterr()
        assert "BUDGET EXCEEDED" in captured.out or "EXCEEDED" in captured.out.upper()

    def test_auto_reset_new_month(self, tmp_path):
        p = _write_budget(tmp_path, {
            "monthly_budget_usd": 10.0,
            "monthly_spent_usd": 9.0,
            "last_reset": "2000-01",
            "agents": {"claude": 9.0},
        })
        state = record_cost("claude", 1.0, path=p)
        # After reset, only the new cost should be recorded
        assert state["monthly_spent_usd"] == pytest.approx(1.0)
        assert state["agents"]["claude"] == pytest.approx(1.0)

    def test_new_agent_created_on_first_use(self, tmp_path):
        p = _write_budget(tmp_path, {
            "monthly_budget_usd": 10.0,
            "monthly_spent_usd": 0.0,
            "last_reset": _current_month(),
            "agents": {},
        })
        state = record_cost("gemini", 0.5, path=p)
        assert "gemini" in state["agents"]
        assert state["agents"]["gemini"] == pytest.approx(0.5)

    def test_persists_to_file(self, tmp_path):
        p = _write_budget(tmp_path, {
            "monthly_budget_usd": 10.0,
            "monthly_spent_usd": 0.0,
            "last_reset": _current_month(),
            "agents": {"claude": 0.0},
        })
        record_cost("claude", 3.14, path=p)
        saved = json.loads(p.read_text(encoding="utf-8"))
        assert saved["monthly_spent_usd"] == pytest.approx(3.14)

    def test_creates_file_if_missing(self, tmp_path):
        p = tmp_path / ".ai" / "budget.json"
        state = record_cost("claude", 0.01, path=p)
        assert p.exists()
        assert state["monthly_spent_usd"] == pytest.approx(0.01)


class TestGetBudgetStatus:

    def test_returns_all_expected_keys(self, tmp_path):
        p = _write_budget(tmp_path, {
            "monthly_budget_usd": 20.0,
            "monthly_spent_usd": 5.0,
            "last_reset": _current_month(),
            "agents": {"claude": 5.0},
        })
        status = get_budget_status(path=p)
        assert "monthly_budget_usd" in status
        assert "monthly_spent_usd" in status
        assert "remaining_usd" in status
        assert "usage_pct" in status
        assert "is_over_budget" in status
        assert "is_near_limit" in status
        assert "agents" in status

    def test_remaining_calculated_correctly(self, tmp_path):
        p = _write_budget(tmp_path, {
            "monthly_budget_usd": 20.0,
            "monthly_spent_usd": 5.0,
            "last_reset": _current_month(),
            "agents": {},
        })
        status = get_budget_status(path=p)
        assert status["remaining_usd"] == pytest.approx(15.0)

    def test_is_over_budget_false(self, tmp_path):
        p = _write_budget(tmp_path, {
            "monthly_budget_usd": 20.0,
            "monthly_spent_usd": 19.99,
            "last_reset": _current_month(),
            "agents": {},
        })
        status = get_budget_status(path=p)
        assert status["is_over_budget"] is False

    def test_is_over_budget_true(self, tmp_path):
        p = _write_budget(tmp_path, {
            "monthly_budget_usd": 20.0,
            "monthly_spent_usd": 20.0,
            "last_reset": _current_month(),
            "agents": {},
        })
        status = get_budget_status(path=p)
        assert status["is_over_budget"] is True

    def test_is_near_limit_true(self, tmp_path):
        p = _write_budget(tmp_path, {
            "monthly_budget_usd": 10.0,
            "monthly_spent_usd": 8.5,
            "last_reset": _current_month(),
            "agents": {},
        })
        status = get_budget_status(path=p)
        assert status["is_near_limit"] is True

    def test_is_near_limit_false(self, tmp_path):
        p = _write_budget(tmp_path, {
            "monthly_budget_usd": 10.0,
            "monthly_spent_usd": 7.0,
            "last_reset": _current_month(),
            "agents": {},
        })
        status = get_budget_status(path=p)
        assert status["is_near_limit"] is False

    def test_remaining_clamped_to_zero_when_over(self, tmp_path):
        p = _write_budget(tmp_path, {
            "monthly_budget_usd": 10.0,
            "monthly_spent_usd": 15.0,
            "last_reset": _current_month(),
            "agents": {},
        })
        status = get_budget_status(path=p)
        assert status["remaining_usd"] == 0.0

    def test_default_budget_when_no_file(self, tmp_path):
        p = tmp_path / ".ai" / "budget.json"
        status = get_budget_status(path=p)
        assert status["monthly_budget_usd"] == 50.0
        assert status["monthly_spent_usd"] == 0.0
