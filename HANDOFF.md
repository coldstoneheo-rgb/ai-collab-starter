# HANDOFF.md

## Project

ai-collab-starter
Multi-AI collaboration system for GitHub-based development
(Claude PM, Gemini FE, Perplexity Compliance, GPT Backend)

---

## Current Phase

**Phase 2 — Stabilization & RAG Upgrade (진행 중)**

Phase 1 (Safe Modular System)은 완료됨.
Phase 2 코어 구현은 `claude/phase2-pr-collector-Zf1Dg` 브랜치에 완료, main merge 대기 중.

---

## Phase 2 완료 항목 (branch: claude/phase2-pr-collector-Zf1Dg)

| 항목 | 파일 | 상태 |
|---|---|---|
| PR Collector | `ai/utils/pr_collector.py` | ✅ |
| Data Models | `ai/utils/models.py` | ✅ |
| Base AI Client | `ai/runners/clients/base_client.py` | ✅ |
| Claude Client | `ai/runners/clients/claude_client.py` | ✅ |
| Audit Logger | `ai/utils/audit_logger.py` | ✅ |
| Safety Policy | `ai/utils/safety_policy.py` | ✅ |
| Prompt Loader | `ai/utils/prompt_loader.py` | ✅ |
| Test Suite | `tests/` (37 tests) | ✅ |
| CLAUDE.md 위반 수정 | workflows, AGENTS.md | ✅ |

## Phase 2 미완료 항목 (main merge 후 구현 필요)

| 항목 | 파일 | 우선순위 |
|---|---|---|
| Gemini Client | `ai/runners/clients/gemini_client.py` | P0 |
| Perplexity Client | `ai/runners/clients/perplexity_client.py` | P0 |
| GPT Client | `ai/runners/clients/gpt_client.py` | P0 |
| Chroma RAG 통합 | `ai/context7/chroma_pipeline.py` | P1 |
| Cost Monitor Service | `ai/utils/cost_monitor.py` | P1 |

---

## 다음 즉시 수행 작업 (Ordered)

1. `claude/phase2-pr-collector-Zf1Dg` → main PR 생성 및 merge
2. Gemini / Perplexity / GPT Client 구현 (PR-P2-FIN-01)
3. Chroma RAG 통합 (PR-P2-FIN-02)
4. Cost Monitor Service 구현 (PR-P2-FIN-03)
5. Phase 2 Gate 기준 달성 확인 → Phase 3 진입

---

## Strategic Direction

### Long-term Goal
Fully Automated AI Development Environment (Hyper-router, multi-agent orchestration, minimal human intervention).

### Current Priority
Phase 2 안정화 우선. Gate 기준 충족 전까지 Phase 3 자동화 작업 시작 금지.

### Core Principles
- One decision point only (router)
- Router decides, runners execute
- Human-in-the-loop mandatory
- Cost, safety, auditability are first-class

---

## Safety & Governance Checklist

### Branch & Review Protection
- [x] Branch protection enabled (main)
- [x] Require ≥ 1 human PR review
- [x] AI-generated PRs must never bypass human review

### Required Status Checks
- claude-check (항상 필수)
- gemini-check (pro / enterprise)
- perplexity-check (enterprise only)

### Autofix Rules
- Autofix PRs: 봇이 merge 불가
- Auto-merge: 기본 비활성화
- 민감 경로 포함 PR: autofix 생성 자체 금지

### Audit & Logging
- 모든 AI 프롬프트/응답 로깅 필수
- Logs는 append-only
- 90일 이상 보관

### Emergency Kill Switch
- Repo Secret: `DISABLE_AI_AUTOMATION=true`
- 활성화 시: Router가 no agents 반환, 모든 AI job skip

---

## PR Action Flow (Safe Mode)

1. PR opened → ai_review workflow 트리거
2. `index` job: RAG 인덱스 빌드
3. `router` job: 프로젝트 스캔 → 모드/에이전트 결정
4. 선택된 AI job만 실행 (claude → gemini → perplexity)
5. 각 agent: 프롬프트/응답 로깅 + PR 코멘트 게시
6. Human이 리뷰하고 merge 결정

---

## Document Map

| 문서 | 역할 |
|---|---|
| `CLAUDE.md` | **최우선 규칙 (법)** |
| `AGENTS.md` | AI 팀 역할 및 거버넌스 가이드 |
| `PRD.md` | 제품 요구사항 및 운영 원칙 |
| `DECISIONS.md` | 아키텍처 결정 이유 |
| `HANDOFF.md` | 현재 Phase 상태 및 다음 작업 (이 문서) |
| `docs/ROADMAP_PR_UNITS.md` | PR 단위 실행 계획 |
| `docs/PHASE3_PLAN.md` | Phase 3 상세 계획 |
| `docs/AI_COLLAB_GUIDE.md` | 로컬 설정 및 운영 가이드 |
