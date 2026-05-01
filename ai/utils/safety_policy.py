"""
Shared safety policy utilities.
"""
from __future__ import annotations

import subprocess
from typing import Iterable, List, Optional


SENSITIVE_PREFIXES = (
    "migrations/",
    "db/",
    "infra/",
    "terraform/",
    "k8s/",
    "security/",
    "auth/",
    "payments/",
    ".github/workflows/",
    ".env",
)

MANUAL_APPROVAL_REQUIRED_MSG = (
    "MANUAL APPROVAL REQUIRED: Sensitive paths detected. "
    "Auto actions are blocked for this change set."
)


def detect_sensitive_paths(paths: Iterable[str]) -> List[str]:
    """
    Return matching sensitive paths from an iterable of relative file paths.
    """
    hits: List[str] = []
    for raw_path in paths:
        path = str(raw_path or "").strip().lower()
        if not path:
            continue
        if any(path.startswith(prefix) for prefix in SENSITIVE_PREFIXES):
            hits.append(path)
    return hits


def collect_changed_paths_from_git(base_path: str = ".") -> Optional[List[str]]:
    """
    Collect changed file paths from the latest commit range.

    Tries HEAD~1..HEAD first (requires fetch-depth >= 2).
    Falls back to files listed in the HEAD commit (git show) when
    the parent commit is unavailable (shallow clone, initial commit).
    """
    def _run(cmd: list) -> Optional[str]:
        try:
            return subprocess.check_output(
                cmd, stderr=subprocess.DEVNULL, text=True, timeout=10
            )
        except Exception:
            return None

    # Primary: diff against parent commit
    out = _run(["git", "-C", base_path, "diff", "--name-only", "HEAD~1..HEAD"])
    if out is not None:
        paths = [line.strip() for line in out.splitlines() if line.strip()]
        if paths:
            return paths

    # Fallback: list files touched in HEAD commit (works on shallow clones)
    out = _run([
        "git", "-C", base_path, "show", "--stat", "--name-only",
        "--format=", "HEAD",
    ])
    if out is not None:
        paths = [line.strip() for line in out.splitlines() if line.strip()]
        if paths:
            return paths

    return None
