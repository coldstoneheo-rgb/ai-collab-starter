"""
Unit tests for audit logger utilities.
"""
from pathlib import Path
import shutil

from ai.utils import audit_logger


def _workspace_tmp_dir(name: str) -> Path:
    root = Path("tests") / ".tmp" / name
    if root.exists():
        shutil.rmtree(root, ignore_errors=True)
    root.mkdir(parents=True, exist_ok=True)
    return root


def test_log_and_load_events(monkeypatch):
    tmp_root = _workspace_tmp_dir("audit_case_1")
    monkeypatch.setattr(audit_logger, "LOG_ROOT", tmp_root / "logs")

    out_path = audit_logger.log_ai_event(
        agent="claude",
        pr_number=10,
        status="success",
        decision_reason="test",
        input_tokens=10,
        output_tokens=20,
        total_tokens=30,
        cost_usd=0.0123,
        tags=["unit"],
        metadata={"k": "v"},
    )
    assert out_path.exists()

    day = out_path.parent.name
    rows = audit_logger.load_events(day=day)
    assert len(rows) == 1
    assert rows[0]["agent"] == "claude"
    assert rows[0]["tokens"]["total"] == 30
    assert rows[0]["cost_usd"] == 0.0123


def test_build_daily_summary(monkeypatch):
    tmp_root = _workspace_tmp_dir("audit_case_2")
    monkeypatch.setattr(audit_logger, "LOG_ROOT", tmp_root / "logs")

    path1 = audit_logger.log_ai_event(
        agent="claude",
        pr_number=1,
        status="success",
        decision_reason="ok",
        total_tokens=100,
        cost_usd=0.05,
    )
    audit_logger.log_ai_event(
        agent="claude",
        pr_number=2,
        status="failed",
        decision_reason="failed_case",
        error_type="api_error",
        error_message="boom",
    )

    # Derive actual_day from the written path to avoid date mismatch
    actual_day = path1.parent.name
    summary = audit_logger.build_daily_summary(day=actual_day)
    assert summary["event_count"] == 2
    assert summary["success_count"] == 1
    assert summary["failed_count"] == 1
    assert "claude" in summary["agents"]
