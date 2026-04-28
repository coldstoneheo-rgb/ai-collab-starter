"""
Unit tests for shared safety policy.
"""
from ai.utils.safety_policy import (
    MANUAL_APPROVAL_REQUIRED_MSG,
    detect_sensitive_paths,
)


def test_detect_sensitive_paths_hits():
    paths = [
        "src/app.py",
        "infra/main.tf",
        ".github/workflows/ai_review.yml",
        "docs/readme.md",
    ]
    hits = detect_sensitive_paths(paths)
    assert "infra/main.tf" in hits
    assert ".github/workflows/ai_review.yml" in hits
    assert "src/app.py" not in hits


def test_detect_sensitive_paths_empty():
    hits = detect_sensitive_paths(["src/main.py", "docs/guide.md"])
    assert hits == []


def test_manual_approval_message_defined():
    assert "MANUAL APPROVAL REQUIRED" in MANUAL_APPROVAL_REQUIRED_MSG
