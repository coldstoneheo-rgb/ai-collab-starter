# Phase 3 작업 계획 (선별적 자동화)

**작성일**: 2026-04-28  
**작성자**: Claude Code (PM)  
**기준 문서**: CLAUDE.md, PRD.md, HANDOFF.md, ROADMAP_PR_UNITS.md

---

## 1. 현재 상태 점검

### 1.1 Phase 2 완료 항목 (branch: claude/phase2-pr-collector-Zf1Dg)

| 항목 | 파일 | 상태 |
|---|---|---|
| PR Collector | `ai/utils/pr_collector.py` | ✅ 완료 |
| Data Models | `ai/utils/models.py` | ✅ 완료 |
| Base AI Client | `ai/runners/clients/base_client.py` | ✅ 완료 |
| Claude Client | `ai/runners/clients/claude_client.py` | ✅ 완료 |
| Audit Logger | `ai/utils/audit_logger.py` | ✅ 완료 |
| Safety Policy | `ai/utils/safety_policy.py` | ✅ 완료 |
| Prompt Loader | `ai/utils/prompt_loader.py` | ✅ 완료 |
| 테스트 스위트 | `tests/` | ✅ 완료 (37 tests) |
| Daily Report Script | `scripts/daily_ai_report.py` | ✅ 완료 |

### 1.2 Phase 2 미완료 항목 (Phase 3 선행 조건)

| 항목 | 파일 | 우선순위 |
|---|---|---|
| Gemini Client | `ai/runners/clients/gemini_client.py` | **P0** |
| Perplexity Client | `ai/runners/clients/perplexity_client.py` | **P0** |
| GPT Client | `ai/runners/clients/gpt_client.py` | **P0** |
| Chroma RAG 통합 | `ai/context7/chroma_pipeline.py` | **P1** |
| Cost Monitor Service | `ai/utils/cost_monitor.py` | **P1** |
| AI Disagreement Report | `ai/utils/compare_report.py` | **P2** |

### 1.3 Phase 2 → Phase 3 Gate 기준

CLAUDE.md §13 기준. 아래를 **모두** 충족해야 Phase 3 진입 가능:

- [ ] PR 성공률 ≥ 95% (최근 50 PRs) — **현재 측정 중**
- [ ] AI 제안 거부율 ≤ 30% (최근 30 PRs)
- [ ] PR당 평균 비용 ≤ $1
- [ ] Audit logs 100+ actions 보관

> ⚠️ Gate 미충족 시 Phase 3 작업 시작 금지 (CLAUDE.md §6)

---

## 2. Phase 3 목표

**목표**: 저위험 영역에서 선별적 자동화를 검증한다.

**핵심 철학**:
- 자동화는 lint/format/docs 변경에만 적용
- 모든 자동 merge는 feature flag로 제어
- 즉시 롤백 가능 구조 필수
- 상세한 감사 로그 유지

---

## 3. Phase 3 PR 단위 작업 계획

### 선행 작업 (Phase 2 마무리)

---

#### PR-P2-FIN-01: Gemini/Perplexity/GPT Client 구현

**목적**: 나머지 AI 클라이언트 구현으로 전체 AI 팀 활성화

**변경 파일**:
```
ai/runners/clients/gemini_client.py    ← 신규
ai/runners/clients/perplexity_client.py ← 신규
ai/runners/clients/gpt_client.py       ← 신규
ai/runners/run_gemini_review.py        ← 실제 API 연동으로 업그레이드
ai/runners/run_perplexity_review.py    ← 실제 API 연동으로 업그레이드
tests/test_gemini_client.py            ← 신규
tests/test_perplexity_client.py        ← 신규
tests/test_gpt_client.py               ← 신규
```

**완료 기준**:
- 각 클라이언트가 `AIClient` ABC 계약 준수
- 비용 계산 로직 구현 (토큰 기반)
- API 키 없는 환경에서도 테스트 통과 (mock)
- `GEMINI_API_KEY`, `PERPLEXITY_API_KEY`, `OPENAI_API_KEY` 환경변수 지원

**작업 규모**: 1-2일

---

#### PR-P2-FIN-02: Chroma RAG 통합

**목적**: naive 키워드 검색을 벡터 임베딩 기반으로 교체

**변경 파일**:
```
ai/context7/chroma_pipeline.py  ← 신규 (기존 rag_pipeline.py 대체)
ai/context7/indexer.py          ← Chroma 저장 로직 추가
requirements.txt                ← chromadb, sentence-transformers 추가
.github/workflows/ai_review.yml ← index job에 Chroma 설치 추가
```

**완료 기준**:
- Chroma 로컬 DB 생성 및 쿼리 동작
- `fetch_top_k()` 인터페이스 유지 (기존 코드 호환)
- GitHub Actions에서 index job 성공
- 키워드 검색 대비 관련도 향상 확인

**CLAUDE.md 제약**:
- 중간 파일 사용 금지 — Chroma DB는 Actions artifact로 공유 검토 필요
- 각 job은 독립 실행 가능해야 함 (index 없으면 빈 결과 반환)

**작업 규모**: 2-3일

---

#### PR-P2-FIN-03: Cost Monitor Service

**목적**: 비용 임계치 알림 및 자동 차단 강화

**변경 파일**:
```
ai/utils/cost_monitor.py         ← 신규
scripts/daily_ai_report.py       ← 기존 스크립트 개선
.github/workflows/ai_nightly.yml ← 신규 (야간 비용 리포트)
```

**완료 기준**:
- 월 예산 80% 도달 시 경고 로그 출력
- 월 예산 100% 도달 시 자동 차단 (AI 호출 중단)
- 일간 비용 집계 리포트 생성

**작업 규모**: 0.5일

---

### Phase 3 핵심 작업

---

#### PR-P3-001: 저위험 변경 분류기

**목적**: 자동 merge 대상 여부를 판단하는 분류 로직

**변경 파일**:
```
ai/utils/risk_classifier.py  ← 신규
tests/test_risk_classifier.py ← 신규
```

**분류 기준**:
```python
LOW_RISK_PATTERNS = [
    "*.md",           # 문서
    "*.txt",          # 텍스트
    "*.yml",          # 설정 (단, .github/workflows/ 제외)
    "*.json",         # 설정 (단, package.json 제외)
]

LOW_RISK_CONTENT_PATTERNS = [
    r"^[-+]\s*#",     # 주석 추가/삭제
    r"^[-+]\s*$",     # 빈 줄
    r"import\s+",     # import 순서 변경
]

# 무조건 HIGH_RISK (CLAUDE.md §6 + safety_policy.py)
HIGH_RISK_PATHS = [
    ".github/workflows/",
    "infra/", "db/", "security/", "auth/", "payments/",
]
```

**완료 기준**:
- HIGH_RISK 경로는 항상 high_risk 반환
- LOW_RISK 패턴만 포함된 PR → low_risk 반환
- 혼합 PR → high_risk (보수적 판단)
- 테스트 커버리지 ≥ 70%

**작업 규모**: 0.5일

---

#### PR-P3-002: Auto-merge Feature Flag 인프라

**목적**: 자동 merge를 feature flag로 제어하는 안전한 인프라

**변경 파일**:
```
ai/utils/feature_flags.py        ← 신규
.ai/config.yml                   ← auto_merge 섹션 추가
.github/workflows/ai_review.yml  ← auto-merge job 추가 (disabled by default)
```

**설계 원칙** (CLAUDE.md §12.1 준수):
```yaml
# .ai/config.yml
auto_merge:
  enabled: false                    # 기본 비활성화
  allowed_modes:
    - lint_fixes
    - format_changes
    - doc_updates
  canary_percentage: 5             # 5% PR만 적용
  require_all_checks_pass: true    # 모든 체크 통과 필수
  sensitive_paths_exempt: true     # 민감 경로 절대 제외
```

**완료 기준**:
- `DISABLE_AI_AUTOMATION=true` 시 완전 비활성화
- `auto_merge.enabled=false` 기본값
- 민감 경로 포함 PR은 feature flag 무관하게 차단
- workflow에 `if: env.AUTO_MERGE_ENABLED == 'true'` 조건

**작업 규모**: 1일

---

#### PR-P3-003: Canary Rollout 시스템

**목적**: PR의 5%만 자동 merge를 경험하도록 샘플링

**변경 파일**:
```
ai/utils/canary_sampler.py        ← 신규
ai/logs/canary/                   ← 신규 (canary 결과 저장)
tests/test_canary_sampler.py      ← 신규
```

**샘플링 로직**:
```python
import hashlib

def is_canary_pr(pr_number: int, percentage: int = 5) -> bool:
    """
    Deterministic canary sampling by PR number.
    PR number hash 기반으로 일관된 결과 보장.
    """
    h = int(hashlib.md5(str(pr_number).encode()).hexdigest(), 16)
    return (h % 100) < percentage
```

**완료 기준**:
- PR 번호 기반 결정적(deterministic) 샘플링
- 결과가 ai/logs/canary/ 에 기록
- 5회 이상 canary 성공 후 확대 가능
- 실패 시 즉시 비활성화 가능

**작업 규모**: 0.5일

---

#### PR-P3-004: Auto-revert 메커니즘

**목적**: 자동 merge된 PR이 CI 실패 시 자동으로 revert

**변경 파일**:
```
ai/utils/auto_reverter.py          ← 신규
.github/workflows/auto_revert.yml  ← 신규
tests/test_auto_reverter.py        ← 신규
```

**동작 흐름**:
1. `ai_review.yml`에서 auto-merge 실행
2. merge 후 `auto_revert.yml` workflow 트리거
3. CI 체크 대기 (최대 10분)
4. CI 실패 시:
   - revert commit 생성
   - revert PR 오픈
   - Audit 로그에 기록
   - GitHub Issue 자동 생성

**완료 기준**:
- CI 실패 후 5분 내 revert PR 생성
- revert 내용이 audit log에 기록
- 5회 canary 테스트에서 revert 정상 동작 확인
- 민감 경로 포함 PR에서는 revert 로직 무관하게 차단

**CLAUDE.md 제약**:
- auto-merge는 CLAUDE.md §12.1에서 Phase 3부터 허용
- lint/format 변경에만 적용 (코드 변경 금지)

**작업 규모**: 1-2일

---

#### PR-P3-005: Router 지능 확장 (비용 기반 모델 선택)

**목적**: 비용 잔여량에 따라 호출 모델 자동 조정

**변경 파일**:
```
ai/router.py                  ← 비용 기반 모델 선택 로직 추가
ai/plugins/cost_checker.py    ← 상세 잔여 예산 반환
tests/test_router_cost.py     ← 신규
```

**확장 로직**:
```python
def _select_model_by_budget(cost_status: dict, base_model: str) -> str:
    """
    비용 잔여량에 따라 더 저렴한 모델로 fallback.
    단, 모델 변경은 router 계약의 mode만 변경하지 않음.
    """
    budget_remaining_pct = cost_status.get('remaining_pct', 100)
    
    if budget_remaining_pct < 20:
        # 예산 20% 미만 → lite 모드 강제
        return 'lite'
    elif budget_remaining_pct < 50:
        # 예산 50% 미만 → pro 모드 상한
        return min(current_mode, 'pro')
    return current_mode
```

**완료 기준**:
- 예산 20% 미만 시 lite 강제 동작 확인
- router 출력 계약 구조 변경 없음 (CLAUDE.md §2)
- 비용 계산 실패 시 보수적 동작 (lite 전환)

**작업 규모**: 0.5일

---

#### PR-P3-006: SAST 통합

**목적**: Python 보안 취약점 자동 스캔으로 Phase 3 Gate 충족

**변경 파일**:
```
.github/workflows/sast.yml    ← 신규
requirements-dev.txt          ← bandit 추가
scripts/run_sast.sh           ← 신규
```

**스캔 대상**:
```yaml
- bandit: Python 보안 취약점
- safety: 알려진 취약 패키지
- 검사 경로: ai/, scripts/ (tests/ 제외)
```

**완료 기준**:
- bandit HIGH severity 0건
- bandit MEDIUM severity ≤ 5건
- PR 시 자동 실행
- 결과를 PR 코멘트로 게시

**작업 규모**: 0.5일

---

#### PR-P3-007: 운영 메트릭 대시보드

**목적**: Phase 3 Gate 충족 여부를 수치로 측정

**변경 파일**:
```
scripts/metrics_dashboard.py      ← 신규
scripts/weekly_gate_report.py     ← 신규
.github/workflows/weekly_report.yml ← 신규
docs/METRICS.md                   ← 신규
```

**측정 메트릭**:
```
비용 메트릭:
  - PR당 평균 비용 (Gate: ≤ $1)
  - 일간/월간 총 비용

효과성 메트릭:
  - AI 제안 수락률 (Gate: ≥ 70%)
  - AI 제안 거부율 (Gate: ≤ 20%)
  - Canary auto-merge 성공률

신뢰성 메트릭:
  - Workflow 성공률 (Gate: ≥ 95%)
  - Auto-revert 발생 횟수

안전 메트릭:
  - 차단된 민감경로 변경 횟수
  - 비상 kill-switch 활성화 횟수
```

**완료 기준**:
- 주간 리포트 자동 생성 (GitHub Issues)
- Gate 기준 임박 시 경고 (80% 도달)
- audit log 100+ 보관 확인

**작업 규모**: 1일

---

## 4. Phase 3 완료 기준 (Gate)

CLAUDE.md §13 / PRD.md Phase 3 기준:

| 기준 | 목표 | 측정 방법 |
|---|---|---|
| AI 패치 테스트 커버리지 | ≥ 70% | `pytest --cov` |
| Auto-revert 검증 | 5회 이상 canary 성공 | ai/logs/canary/ |
| SAST 통과 | bandit HIGH 0건 | `.github/workflows/sast.yml` |
| AI 제안 거부율 | ≤ 20% | `scripts/metrics_dashboard.py` |

---

## 5. PR 실행 순서 (의존성 고려)

```
선행 (병렬 가능):
  PR-P2-FIN-01 (AI Clients)
  PR-P2-FIN-03 (Cost Monitor)

선행 (직렬):
  PR-P2-FIN-02 (Chroma RAG)  ←  P2-FIN-01 이후

Phase 3 (병렬 가능):
  PR-P3-001 (Risk Classifier)
  PR-P3-005 (Router Cost)
  PR-P3-006 (SAST)

Phase 3 (직렬):
  PR-P3-002 (Feature Flag)    ← P3-001 이후
  PR-P3-003 (Canary)          ← P3-002 이후
  PR-P3-004 (Auto-revert)     ← P3-003 이후

마무리:
  PR-P3-007 (Metrics)         ← 모든 작업 이후
```

---

## 6. 절대 금지 사항 (CLAUDE.md §12.1 재확인)

Phase 3에서도 다음은 **절대 금지**:

- ❌ 코드 변경 PR의 자동 merge
- ❌ 민감 경로 포함 PR의 자동 처리
- ❌ 사람 승인 없는 자동 merge (lint/format 제외)
- ❌ AI끼리 자율 토론 루프
- ❌ router 출력 구조 변경
- ❌ workflow에서 if: 판단 로직 추가

---

## 7. 비상 대응 계획

| 상황 | 조치 |
|---|---|
| Auto-revert 실패 | `DISABLE_AI_AUTOMATION=true` 즉시 설정, 수동 revert |
| 비용 폭발 | Budget 한도 낮추고, lite 모드 강제 |
| Canary 연속 실패 | canary_percentage를 0으로 설정 |
| CI 연속 실패 | Kill-switch 활성화, Phase 2로 롤백 |

---

*최종 승인 전 PM (Claude Code) 검토 필수*  
*문서 변경은 반드시 PR로 진행 (CLAUDE.md §9.3)*
