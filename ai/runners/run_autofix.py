#!/usr/bin/env python3
"""
Autofix runner with safety guard.

Policy:
- If sensitive paths are detected, block auto actions and fail.
- Otherwise, continue in placeholder mode (no code changes yet).
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
        print("=== AUTOFIX BLOCKED ===")
        print(
            "MANUAL APPROVAL REQUIRED: Unable to detect changed paths safely. "
            "Auto actions are blocked."
        )
        return 1

    sensitive_hits = detect_sensitive_paths(changed_paths)

    if sensitive_hits:
        print("=== AUTOFIX BLOCKED ===")
        print(MANUAL_APPROVAL_REQUIRED_MSG)
        print("Sensitive paths:")
        for path in sensitive_hits:
            print(f"- {path}")
        return 1

    print("=== AUTOFIX SAFE MODE ===")
    print("No sensitive paths detected. Placeholder mode keeps code unchanged.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
