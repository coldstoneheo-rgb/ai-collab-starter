# AI Collab Guide

This guide explains how to run and operate `ai-collab-starter` in a controlled, cost-aware way.

## 1. Operating principles

- `CLAUDE.md` is the highest-priority rulebook. `AGENTS.md` defines AI team roles.
- Router decides mode and enabled agents.
- Workflow executes router outputs and should not add new decision logic.
- Human approval remains mandatory for risky changes.

## 2. Local setup

### Linux/macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
./scripts/init_project.sh
```

### Windows PowerShell

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -U pip
pip install -r requirements.txt
.\scripts\init_project.ps1
```

## 3. Environment variables

Use `.env.example` as the template.

Required for most local/CI operations:
- `GITHUB_TOKEN`
- `CLAUDE_API_KEY`
- `GEMINI_API_KEY`
- `PERPLEXITY_API_KEY`

Project convention:
- `OPENAI_API_KEY`

Legacy key name still referenced by current autofix workflow:
- `GPT_API_KEY`

## 4. Core flow (safe mode)

1. PR is opened or updated.
2. `ai_review.yml` runs index and router jobs.
3. Router returns:
   - `mode`
   - `enabled_agents`
   - `autofix_allowed`
4. Workflow runs only selected agent jobs.
5. Human reviews results and decides merge.

## 5. Local smoke tests

### Router only

Linux/macOS:
```bash
PYTHONPATH=. python -c "from ai.router import decide_mode; print(decide_mode('.'))"
```

Windows PowerShell:
```powershell
$env:PYTHONPATH='.'
python -c "from ai.router import decide_mode; print(decide_mode('.'))"
```

### Claude runner (dry run example)

Linux/macOS:
```bash
PYTHONPATH=. python ai/runners/run_claude_review.py --pr-number 1 --dry-run
```

Windows PowerShell:
```powershell
$env:PYTHONPATH='.'
python ai/runners/run_claude_review.py --pr-number 1 --dry-run
```

## 6. Configuration map

- `.ai/config.yml`: feature flags, retries, timeouts, paths.
- `.ai/budget.json`: monthly budget and per-agent spend tracking.
- `.github/ai_team.yml`: role ownership and merge/safety policy.
- `.github/AI_PROMPTS/*_v1.txt`: versioned prompts.

## 7. Cost and reliability guardrails

- Keep mode pinned to conservative defaults during early rollout.
- Enforce budget thresholds before expensive calls.
- Avoid retry storms; cap retries per PR.
- Do not hide failures as success in CI.

## 8. Troubleshooting

### `ModuleNotFoundError: ai`

Set `PYTHONPATH` to repo root before running scripts.

### Missing SDK packages (`anthropic`, `github`, etc.)

Install dependencies:
```bash
pip install -r requirements.txt
```

### Prompt file not found

Confirm files exist under `.github/AI_PROMPTS/` with `_v1` suffix.

### Git safe directory warning on Windows

If Git reports dubious ownership, register the repository as safe:
```bash
git config --global --add safe.directory C:/Users/colds/ai-collab-starter
```

## 9. Governance and roadmap

- Governance source: `AGENTS.md`
- Product constraints: `PRD.md`
- Execution roadmap by PR unit: `docs/ROADMAP_PR_UNITS.md`

Use the PR-unit roadmap to sequence changes and keep each PR single-purpose.
