# ai-collab-starter

Safe, modular starter template for multi-agent AI code review on GitHub.

This project prioritizes:
- control and governance
- cost limits
- maintainability
- phased rollout over risky full automation

## Current state

- Phase 1 (Safe Modular System): ✅ Complete
- Phase 2 (Stabilization & RAG Upgrade): 🔄 In progress
  - Core implementation on `claude/phase2-pr-collector` branch, pending main merge
  - Remaining: Gemini/Perplexity/GPT clients, Chroma RAG, Cost monitor
- Phase 3 planning complete. Starts after Phase 2 Gate criteria met.

See:
- `CLAUDE.md` for hard rules (highest priority).
- `AGENTS.md` for AI team roles and governance.
- `PRD.md` for product direction and operating constraints.
- `HANDOFF.md` for current phase status and next tasks.
- `docs/ROADMAP_PR_UNITS.md` for PR-by-PR execution plan.

## Repository layout

```text
ai/
  router.py
  plugins/
  runners/
  context7/
  utils/
.github/
  workflows/
  AI_PROMPTS/
  ai_team.yml
.ai/
  config.yml
  budget.json
docs/
  CONTEXT/
```

## Quick start

### 1) Install dependencies

Linux/macOS:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
```

Windows PowerShell:
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -U pip
pip install -r requirements.txt
```

### 2) Initialize local template assets

Linux/macOS:
```bash
./scripts/init_project.sh
```

Windows PowerShell:
```powershell
.\scripts\init_project.ps1
```

### 3) Configure environment variables

Copy `.env.example` and set required values.

Primary keys used in the current project:
- `GITHUB_TOKEN`
- `CLAUDE_API_KEY`
- `GEMINI_API_KEY`
- `PERPLEXITY_API_KEY`
- `OPENAI_API_KEY` (project-wide convention)
- `GPT_API_KEY` (legacy key name still referenced by `autofix.yml`)

### 4) Smoke test router locally

Linux/macOS:
```bash
PYTHONPATH=. python -c "from ai.router import decide_mode; print(decide_mode('.'))"
```

Windows PowerShell:
```powershell
$env:PYTHONPATH='.'
python -c "from ai.router import decide_mode; print(decide_mode('.'))"
```

## GitHub Actions

Current workflows:
- `.github/workflows/ai_review.yml`
- `.github/workflows/autofix.yml`

Notes:
- `ai_review.yml` is the main PR review pipeline.
- `autofix.yml` exists but is considered high risk and should be treated conservatively.
- Governance rules in `CLAUDE.md` take precedence over convenience.

## Configuration files

- `.ai/config.yml`: project-level behavior toggles and paths.
- `.ai/budget.json`: budget and spend tracking.
- `.github/ai_team.yml`: role definitions and merge/safety rules.
- `.github/AI_PROMPTS/*_v1.txt`: prompt templates (versioned).

## Known limitations

- Full production runner parity is not complete yet.
- Some tests require optional external SDK dependencies.
- Cost controls and workflow hardening are being finalized in roadmap PRs.

## Contribution model

- One PR = one purpose.
- Update docs with structural changes.
- Prefer stable and reversible changes over clever shortcuts.
