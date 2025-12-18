# SYSTEM_STATE.md

## Repository Structure (Relevant)

ai/
  router.py
  router_dispatcher.py
  plugins/
    project_scan.py
    cost_checker.py
    mode_map.py
  runners/
    run_claude_review.py
    run_gemini_review.py   # TODO: PR diff integration
  utils/
    collect_pr_diff.py
  context7/
    rag_pipeline.py

.github/
  workflows/
    ai_review.yml
  AI_PROMPTS/
    claude_review.txt

## Router Behavior
- Router runs first in GitHub Actions
- Outputs:
  - mode
  - agents
  - reason
- Router does NOT execute AI calls

## Workflow Behavior
- AI jobs execute only if included in router `agents`
- Conditional execution via `if: contains(...)`
- Claude review posts PR comments automatically

## RAG (Current)
- fetch_top_k() keyword-based retrieval
- Used to inject project context into AI prompts

## Autofix
- Disabled for merge
- No autonomous code changes allowed
- Human approval required

## Logging
- AI outputs saved for audit
- No automatic pruning yet

## Governance State

- Branch protection: enabled
- Human PR review: required
- Auto-merge: disabled by default
- Kill-switch supported via repo secret

## Mode Control
- Supports manual override
- Defaults to router decision

## Monitoring
- Metrics collection planned (Phase 2)
- Logs currently stored locally under ai/logs/
