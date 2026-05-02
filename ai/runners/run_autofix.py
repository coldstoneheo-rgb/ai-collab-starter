#!/usr/bin/env python3
"""
Autofix runner with safety guard.

Exit codes:
  0 — safe (no sensitive paths) or intentionally blocked by policy
  1 — unexpected error (path detection failed)
"""
import argparse
from pathlib import Path

from ai.utils.safety_policy import (
    MANUAL_APPROVAL_REQUIRED_MSG,
    collect_changed_paths_from_git,
    detect_sensitive_paths,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run autofix with safety guard")
    parser.add_argument(
        "--base-path",
        default=".",
        help="Repository base path for git diff detection",
    )
    args = parser.parse_args()

    _ = Path(".github/AI_PROMPTS/autofix_v1.txt").read_text(encoding="utf-8")
    changed_paths = collect_changed_paths_from_git(base_path=args.base_path)
    if changed_paths is None:
        print("=== AUTOFIX ERROR ===")
        print("Unable to detect changed paths safely. Check git history depth.")
        return 1  # actual unexpected error

    sensitive_hits = detect_sensitive_paths(changed_paths)

    if sensitive_hits:
        # Intentional policy block — not an error, human review is expected
        print("=== AUTOFIX BLOCKED (policy) ===")
        print(MANUAL_APPROVAL_REQUIRED_MSG)
        print("Sensitive paths detected:")
        for path in sensitive_hits:
            print(f"  - {path}")
        print("Action: open a PR and request human review for these paths.")
        return 0  # policy working as intended, not a workflow failure

    print("=== AUTOFIX SAFE MODE ===")
    print("No sensitive paths detected. Placeholder mode keeps code unchanged.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
