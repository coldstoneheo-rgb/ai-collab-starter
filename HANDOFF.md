# HANDOFF.md

## Project
ai-collab-starter  
Multi-AI collaboration system for GitHub-based development  
(Claude PM, Gemini FE, Perplexity Research/Compliance, GPT Core Logic)

## Current Phase
**Phase 1 — Safe Modular System (ACTIVE)**

This project is intentionally NOT fully automated yet.
The current goal is to deliver value fast on real projects
while minimizing risk, cost explosion, and architectural entanglement.

## Strategic Direction (Authoritative)

### Long-term Goal
Evolve into a **Fully Automated AI Development Environment**
(Hyper-router, multi-agent orchestration, minimal human intervention).

### Current Priority (DO NOT SKIP)
Build a **Safe Modular System first**, then mature in controlled phases.

This is a deliberate risk-control strategy.

### Core Principles
- Start small, expand safely
- One decision point only (router)
- Router decides, runners execute
- Execution logic must stay modular
- Human-in-the-loop is mandatory in early phases
- Cost, safety, and auditability are first-class concerns

### Fixed Modes (Do Not Add More)
- lite
- pro
- enterprise

## Phased Roadmap (Locked Concept)

### Phase 1 — Safe Modular System (CURRENT)
**Goal**
- Deploy to real projects quickly
- Prove value without structural risk

**Rules**
- Router only decides (no execution logic)
- GitHub Actions execute conditionally
- No autofix merge
- All AI prompts and outputs logged
- Human approval required for all code changes

**Key Deliverables**
- ai/router.py
- ai/plugins/*
- Conditional AI workflows
- Claude PR review with diff + RAG
- Audit logging

---

### Phase 2 — Stabilization & RAG Upgrade
**Goal**
- Improve accuracy and observability

**Planned**
- Chroma-based vector RAG
- Improved PR diff & context extraction
- Cost monitoring + alerts
- Prompt versioning via PR
- AI disagreement report (compare & escalate)

---

### Phase 3 — Selective Automation
**Goal**
- Carefully test automation where risk is low

**Planned**
- Auto-merge ONLY for low-risk fixes (lint, format, docs)
- Canary rollout (≤5% of PRs)
- Auto-rollback on CI failure
- Cost-aware router decisions

---

### Phase 4 — Full AI Dev Studio (FUTURE)
**Goal**
- End-to-end AI-driven development loop

**Planned**
- Hyper-router
- Serverless orchestration backend
- Autonomous PR generation loops
- Advanced audit & explainability UI
- Legal & ethical compliance layer

### Important Warning
Any attempt to:
- Introduce full automation early
- Add intelligence into GitHub Actions instead of router
- Remove human-in-the-loop prematurely

is considered a **design regression**.

## Current Next Tasks (Ordered)
1. Add PR diff support to Gemini runner
2. Block autofix automatically in enterprise mode
3. Upgrade RAG to Chroma-based indexing

## Safety & Governance Checklist (MANDATORY)

The following rules are non-negotiable and must always be enforced.

### Branch & Review Protection
- Branch protection enabled
- Require ≥ 1 human PR review
- AI-generated PRs must never bypass human review

### Required Status Checks
- claude-check (always required)
- gemini-check (required for pro / enterprise)
- perplexity-check (optional, enterprise only)

### Autofix Rules
- Autofix PRs are **non-mergeable by bots**
- Auto-merge is disabled by default
- Auto-merge can only be enabled via explicit feature flag
- Even with auto-merge enabled, sensitive paths are excluded

### Audit & Logging
- All AI prompts and outputs must be logged
- Logs are append-only (immutable)
- Logs must be retained for at least 90 days

### Sensitive Paths Protection
If an AI-generated patch touches any of the following:
- DB migrations
- Infrastructure code
- Secrets / auth
- Payment or billing logic

→ **All auto actions are blocked**

### Cost Guard
- Heavy model calls are blocked if monthly budget exceeds threshold
- Budget is enforced before AI execution, not after

### Prompt Governance
- Prompt templates are code
- Prompt changes must go through PR review

### Emergency Kill Switch
- Repo secret: `DISABLE_AI_AUTOMATION=true`
- When enabled:
  - Router returns no agents
  - All AI jobs are skipped

## Mode Decision Policy

### Manual Override
- Mode can be pinned via:
  - `.ai/config.yml`
  - Repo secret: `AI_FORCE_MODE`

### Router Inputs
From project_scan plugin:
- is_large
- has_ui
- has_payment
- touches_personal_data

From cost_checker plugin:
- low_budget (boolean)

### Router Output
- mode: lite | pro | enterprise
- enabled_ai_list (e.g. ['claude', 'gpt'])

### Design Rule
- Router logic must remain simple and explainable
- No ML-based decision-making at this stage

## PR Action Flow (Safe Mode)

1. PR opened
2. ai_review workflow triggers
3. index_and_scan step:
   - Loads or builds Chroma index
   - Runs project_scan plugin
4. Router invoked with:
   - project_info
   - cost_status
5. Router returns:
   - mode
   - list of AI agents to run
6. Workflow triggers ONLY selected AI jobs
7. Each agent:
   - Logs prompt & response to ai/logs/
   - Posts PR comment
8. If autofix generates patch:
   - Creates ai/autofix/* branch
   - Opens PR
   - Auto-merge is disabled
9. If any agent reports critical issue:
   - Status check fails
   - Human notification (Slack / email)
10. Human reviews and merges or requests changes

## Monitoring Metrics

### Cost Metrics
- Cost per PR
- Cost per day
- Monthly spend per model

### Effectiveness Metrics
- AI suggestion acceptance rate
- Human override rate

### Reliability Metrics
- Workflow success rate
- Runner error rate

### Safety Metrics
- Number of blocked auto-merges
- Incidents (data leak, infra changes)

### Latency Metrics
- Average AI review time per PR

## Operating Tips

- Prompt changes must go through PR review
- Start with a fixed monthly budget and adjust based on real PR cost
- Pin mode via `.ai/config.yml` during early rollout
- Retain AI logs for at least 90 days
- Train developers:
  "AI-generated PRs must be reviewed by humans"
