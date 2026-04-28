# PRD — AI-Collab-Starter

**버전**: 2.0  
**최종 업데이트**: 2026-04-28  
**최우선 문서**: `CLAUDE.md` (이 문서보다 우선)

---

## 1. 프로젝트 정의

**AI-Collab-Starter**는
"AI가 코드를 대신 짜주는 도구"가 아니라,

> **여러 AI를 '조직 구조'처럼 배치하고,
> 사람이 최종 책임을 지는 GitHub 기반 AI 협업 개발 시스템**

### 핵심 목표

| 목표 | 설명 |
|---|---|
| 상호 보완적 협업 | AI들이 서로의 약점을 보완 |
| 일관된 방향 유지 | 목표/철학이 AI 교체에도 유지됨 |
| 자동화된 컨텍스트 공유 | GitHub + RAG 기반 인수인계 |
| 엄격한 품질 관리 | 다중 관점의 코드 리뷰 |

### 성공 기준

> 자동화 ❌ 생산성 ❌ → **통제·안전·예측 가능성 ⭕**

---

## 2. 핵심 철학 (변경 불가)

1. **사람이 최종 책임을 진다**
2. **AI는 제안하고, 사람이 결정한다**
3. **안전이 속도보다 우선한다**
4. **투명성과 감사 가능성을 유지한다**
5. **단계적으로 확장하고, 검증 후 진행한다**

---

## 3. 아키텍처 원칙 (SRP, 변경 불가)

| 레이어 | 책임 | 금지 |
|---|---|---|
| `router` | **결정**만 | 실행 ❌ |
| `plugin` | 정보 수집 | 판단 ❌ |
| `workflow` | 실행 | 결정 ❌ |
| `runner` | AI API 호출 | 정책 ❌ |

**Router 계약 출력 (변경 불가):**
```json
{
  "mode": "lite | pro | enterprise",
  "enabled_agents": ["claude", "gemini", "perplexity"],
  "autofix_allowed": false
}
```

> 이 계약을 어기면 PR 즉시 중단

---

## 4. 운영 정책

### 비용 통제 우선순위
1. CI 안정성
2. 운영 비용 상한 준수
3. 유지보수 단순성
4. 기능 확장

### 비용 통제 규칙
- 월 예산 초과 시 enterprise 모드 실행 금지
- 동일 PR 재시도 최대 1회 → 이후 사람 검토
- 고비용 모델 호출 전 저비용 모드 선검토
- 비용 리포트(`.ai/budget.json`) 갱신 실패 시 AI 실행 중단

### 민감 경로 정책
다음 경로 변경 시 무조건 enterprise + autofix_allowed=false:
- `.github/workflows/**`
- `infra/**`, `db/**`, `security/**`, `auth/**`, `payments/**`

### GitHub 운영 정책
- main 브랜치: force push ❌, direct push ❌, PR + human review ≥ 1 필수

---

## 5. 단계별 로드맵

> **상세 실행 계획**: `docs/ROADMAP_PR_UNITS.md`
> **Phase 3 상세**: `docs/PHASE3_PLAN.md`

### Phase 1 — Safe Modular System ✅ 완료
**목표**: Router 중심 의사결정, 민감 경로 보호, 자동 수정 차단

---

### Phase 2 — Stabilization & RAG Upgrade (진행 중)
**목표**: RAG 정확도 향상, 비용 모니터링, 전체 AI 팀 활성화

**핵심 항목:**
1. PR context extractor (GitHub API 활용) ← 완료
2. Claude Client + Audit logging ← 완료
3. Gemini / Perplexity / GPT Client ← 구현 필요
4. Chroma 벡터 RAG ← 구현 필요
5. Cost monitor + 알림 ← 구현 필요

**Phase 2 → Phase 3 Gate:**
- Workflow 성공률 ≥ 95% (최근 50 PRs)
- AI 제안 거부율 ≤ 30% (최근 30 PRs)
- PR당 평균 비용 ≤ $1
- Audit logs 100+ actions

---

### Phase 3 — Selective Automation (Gate 통과 후)
**목표**: 저위험 영역 자동 merge 실험 (lint/format only)

**Phase 3 → Phase 4 Gate:**
- 테스트 커버리지 ≥ 70%
- 5회 canary 성공 + auto-revert 검증
- SAST HIGH 0건
- 거부율 ≤ 20%

---

### Phase 4 — Full AI Dev Studio (매우 신중)
**목표**: Hyper-router, serverless orchestration, autonomous PR loop

> ⚠️ CLAUDE.md §12 경고 참조. Phase 3 Gate 충족 + 90일 안정 운영 후에만 고려.

---

## 6. 절대 금지 항목 (전 Phase)

> 상세: `CLAUDE.md` §12

- AI끼리 자율 토론/릴레이 PR
- 사람 승인 없는 코드 자동 merge (Phase 3 lint/format 제외)
- AI가 AI 코드를 수정하는 루프
- 자동 패키지 매니저
- Serverless AI orchestrator (Phase 4 이전)

---

## 7. 비용 추정

| Mode | 활성 AI | PR당 예상 비용 | 월 예상 (50 PRs) |
|---|---|---|---|
| Lite | 1개 | $0.10–$0.30 | $5–$15 |
| Pro | 3개 | $0.50–$1.00 | $25–$50 |
| Enterprise | 4개 | $1.50–$3.00 | $75–$150 |
