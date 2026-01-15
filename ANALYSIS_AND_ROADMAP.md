# AI-Collab-Starter: 종합 분석 및 진화 로드맵

**작성일**: 2026-01-15
**목적**: 현재 레포지토리 상태를 분석하고 AI Collab Orchestrator로 진화하기 위한 Big Picture와 리팩토링 계획 수립

---

## 목차

1. [현재 상태 분석](#1-현재-상태-분석)
2. [아키텍처 Gap 분석](#2-아키텍처-gap-분석)
3. [Big Picture: AI Collab Orchestrator로의 진화](#3-big-picture-ai-collab-orchestrator로의-진화)
4. [상세 리팩토링 계획](#4-상세-리팩토링-계획)
5. [실행 우선순위](#5-실행-우선순위)
6. [리스크 및 완화 전략](#6-리스크-및-완화-전략)

---

## 1. 현재 상태 분석

### 1.1 구현된 핵심 컴포넌트

#### ✅ **Router System** (`ai/router.py`)
**상태**: 완전 구현
**기능**:
- 4단계 의사결정 로직:
  1. User override 지원 (`user_force_mode`)
  2. Project scan 기반 분석
  3. Budget checking
  4. Rule-based decision tree
- 민감 경로 감지 (10개 prefix)
- Mode별 autofix 권한 관리
- `RouterDecision` dataclass 출력

**강점**:
- 단일 책임 원칙 준수
- 명확한 결정 흐름
- 확장 가능한 구조

**약점**:
- Emergency kill-switch 미구현
- 비용 한도 초과 시 강제 중단 미구현
- Audit logging 없음

---

#### ✅ **Plugins** (`ai/plugins/`)

| Plugin | 상태 | 기능 | 이슈 |
|--------|------|------|------|
| `mode_map.py` | 완료 | Lite/Pro/Enterprise 매핑 | None |
| `project_scan.py` | 완료 | 코드 파일 수, UI/결제/개인정보 감지, Git diff 검출 | `git diff origin/main...HEAD` 실패 가능 |
| `cost_checker.py` | 완료 | `.ai/budget.json` 로딩, 예산 확인 | 실제 비용 추적 없음 |

**강점**:
- 플러그인 아키텍처로 확장 용이
- 각 플러그인이 독립적

**약점**:
- `project_scan.py`가 main 브랜치 없으면 실패
- `cost_checker.py`가 실제 API 호출 비용을 추적하지 않음
- 모든 플러그인에 `__init__.py` 없음 (Python 패키지 구조 아님)

---

#### ⚠️ **Runners** (`ai/runners/`)

| Runner | 상태 | 구현 수준 | 이슈 |
|--------|------|-----------|------|
| `run_claude_review.py` | STUB | RAG 로딩, 프롬프트 로딩까지만 | `send_to_claude()` 빈 껍데기 |
| `run_gemini_review.py` | STUB | 콘솔 출력만 | 실제 API 호출 없음 |
| `run_perplexity_review.py` | STUB | 콘솔 출력만 | 실제 API 호출 없음 |
| `run_autofix.py` | PLACEHOLDER | 메시지만 출력 | 기능 없음 |

**핵심 문제**:
- **모든 runner가 placeholder 수준**
- 실제 AI API 호출 로직 없음
- PR diff 수집 로직 없음
- GitHub PR 코멘트 생성 로직 없음

---

#### ⚠️ **RAG System** (`ai/context7/`)

| 파일 | 상태 | 기능 | 이슈 |
|------|------|------|------|
| `indexer.py` | 완료 | 파일 스캔, JSON 인덱스 생성 | 20KB 제한, 메타데이터 부족 |
| `rag_pipeline.py` | NAIVE | 단순 substring 검색 | **벡터 검색 아님**, 정확도 낮음 |

**핵심 문제**:
- CLAUDE.md는 Chroma/Context7 벡터 DB 요구
- 현재는 단순 키워드 카운트 방식
- 임베딩, 시맨틱 검색 없음

---

#### ✅ **GitHub Workflows** (`.github/workflows/`)

**ai_review.yml**:
- ✅ 구조 완벽
- ✅ Router 출력 기반 조건부 실행
- ✅ 순차 의존성 (claude → gemini → perplexity)
- ❌ `requirements.txt` 없어서 `pip install` 실패
- ❌ Status check가 성공/실패 여부를 실제 AI 출력에 반영 안 함

**autofix.yml**:
- ✅ 기본 구조 완료
- ❌ Branch protection 우회 방지 로직 없음
- ❌ 안전 검증 없음

---

#### ✅ **AI Prompts** (`.github/AI_PROMPTS/`)

| 파일 | 상태 | 포맷 | 이슈 |
|------|------|------|------|
| `claude_review.txt` | 완료 | JSON 출력 | 버전 번호 없음 (`_v1` 필요) |
| `gemini_uiux.txt` | 완료 | Markdown | 버전 번호 없음 |
| `perplexity_compliance.txt` | 완료 | Markdown | 버전 번호 없음 |
| `autofix.txt` | 완료 | Diff 포맷 | 버전 번호 없음 |

**문제**:
- CLAUDE.md 섹션 10에서 요구하는 버전 관리 규칙 미준수
- 프롬프트 변경 이력 추적 불가

---

### 1.2 누락된 핵심 컴포넌트

#### ❌ **Critical Missing Items**

1. **API 통합**
   - Claude API 클라이언트 미구현
   - Gemini API 클라이언트 미구현
   - Perplexity API 클라이언트 미구현
   - GPT API 클라이언트 미구현

2. **Audit Logging**
   - `ai/logs/` 디렉토리 없음
   - 프롬프트/응답 저장 로직 없음
   - Append-only log 메커니즘 없음

3. **AI Team Configuration**
   - `.github/ai_team.yml` 없음 (CLAUDE.md 섹션 7.3 요구)
   - 프로젝트별 AI 역할 정의 불가

4. **Context Structure**
   - `/docs/CONTEXT/` 디렉토리 구조 없음
   - `business/`, `compliance/`, `architecture/` 등 하위 디렉토리 없음

5. **Emergency Controls**
   - `DISABLE_AI_AUTOMATION` secret 체크 로직 없음
   - Emergency kill-switch 미구현

6. **Cost Enforcement**
   - 예산 초과 시 강제 중단 없음
   - 실시간 비용 추적 없음

7. **Python Package Structure**
   - 모든 디렉토리에 `__init__.py` 없음
   - `requirements.txt` 없음

8. **PR Diff Collection**
   - GitHub API를 통한 PR diff 수집 로직 없음
   - Changed files 목록 수집 없음

---

## 2. 아키텍처 Gap 분석

### 2.1 CLAUDE.md 요구사항 vs 현재 구현

| CLAUDE.md 섹션 | 요구사항 | 현재 상태 | Gap |
|----------------|----------|----------|-----|
| §7.2 AI 역할 분담 | Claude=PM, Gemini=FE, Perplexity=Compliance, GPT=Backend | Mode map에 정의됨 | ✅ 개념적 정의만, 실제 역할 분리 없음 |
| §7.3 AI 팀 구성 | `.github/ai_team.yml` | 없음 | ❌ **Critical** |
| §8.1 모드 시스템 | Lite/Pro/Enterprise | 완전 구현 | ✅ |
| §8.2 자동 분기 | Router 로직 | 완전 구현 | ✅ (kill-switch 제외) |
| §8.3 민감 경로 | Enterprise 강제 | 완전 구현 | ✅ |
| §9.1 Context 구조 | `/docs/CONTEXT/` 하위 구조 | 없음 | ❌ **High Priority** |
| §9.2 RAG 규칙 | Chroma 벡터 DB | Naive substring | ❌ **Medium Priority** |
| §9.3 Context 업데이트 | PR 기반 변경 | N/A | - |
| §10.1 프롬프트 버전 | `_v1` suffix | 없음 | ❌ **Low Priority** |
| §10.2 프롬프트 변경 규칙 | PR 기반 | 구조만 있음 | ⚠️ 강제 메커니즘 없음 |
| §11.1 안전장치 | 7가지 체크리스트 | 부분적 | ⚠️ Audit log, kill-switch 없음 |
| §11.2 충돌 해결 | 우선순위 규칙 | 문서화만 | - |
| §12 위험 경고 | Phase 1-2 금지 목록 | 문서화만 | ✅ |
| §13 Phase Gate | 계량적 기준 | 문서화만 | - |
| §14 템플릿 적용 | `init_ai_project.py` | scripts 있음 | ⚠️ 테스트 필요 |

---

### 2.2 PRD.md 요구사항 vs 현재 구현

| PRD 섹션 | 요구사항 | 현재 상태 | Gap |
|----------|----------|----------|-----|
| §10 AI 역할 | 상세 역할 정의 | 문서화만 | - |
| §11 리포 구조 | 권장 디렉토리 구조 | 부분적 | ⚠️ `/docs/CONTEXT/` 등 누락 |
| §12 PR 워크플로우 | 5단계 프로세스 | 구조만 | ⚠️ Runner 미구현 |
| §13 Phase 로드맵 | Phase 0-4 계획 | 문서화만 | - |
| §14 비용 관리 | Budget guard | 체크만, 강제 없음 | ❌ **High Priority** |
| §15 메트릭 | 4개 메트릭 카테고리 | 없음 | ❌ **Phase 2** |
| §17 위험 관리 | 롤백, kill-switch | kill-switch 없음 | ❌ **High Priority** |
| §18 템플릿 가이드 | 신규/기존 프로젝트 적용 | Scripts 있음 | ⚠️ 테스트 필요 |

---

### 2.3 핵심 Gap 우선순위

#### **🔴 Critical (Phase 1 블로커)**
1. **API 통합**: 모든 runner 실제 구현 필요
2. **PR Diff Collection**: GitHub API 통합
3. **`requirements.txt`**: Python 의존성 정의
4. **`__init__.py`**: Python 패키지 구조

#### **🟠 High (Phase 1 완성)**
5. **Audit Logging**: `ai/logs/` + append-only
6. **Emergency Kill-Switch**: `DISABLE_AI_AUTOMATION` 체크
7. **AI Team Config**: `.github/ai_team.yml`
8. **Context Structure**: `/docs/CONTEXT/` 생성
9. **Cost Enforcement**: 예산 초과 시 중단

#### **🟡 Medium (Phase 2)**
10. **Vector RAG**: Chroma 통합
11. **Metrics Collection**: 비용/효과성/신뢰성 추적
12. **Status Check Logic**: AI 출력 기반 pass/fail
13. **Prompt Versioning**: `_v1` suffix + 추적

#### **🟢 Low (Phase 2-3)**
14. **Compare Reports**: AI 간 충돌 시 자동 생성
15. **Slack/Email Alerts**: 알림 시스템
16. **Budget JSON Template**: 기본 파일 생성

---

## 3. Big Picture: AI Collab Orchestrator로의 진화

### 3.1 비전 (Vision)

**AI-Collab-Starter**는 단순한 "AI 코드 리뷰 도구"가 아니라,
**"AI를 조직처럼 운영하는 멀티-에이전트 개발 오케스트레이터"**로 진화합니다.

#### **최종 목표**:
> 1인 개발자도 Claude(PM) + Gemini(FE) + Perplexity(Compliance) + GPT(BE)로 구성된
> **4인 개발팀**을 GitHub 위에서 자동 운영하며,
> 엔터프라이즈급 품질의 소프트웨어를 안전하고 통제 가능하게 개발할 수 있도록 지원

---

### 3.2 진화 단계 (4 Phases)

```
현재 (Phase 0) → Phase 1 → Phase 2 → Phase 3 → Phase 4
   ⬇              ⬇         ⬇         ⬇         ⬇
Scaffold      MVP      Production  Selective  Full AI
                                    Auto      Studio
```

#### **Phase 0 (현재): Architectural Scaffold**
- ✅ Router + Plugins + Workflows 구조 완성
- ✅ 문서화 (CLAUDE.md, PRD.md)
- ⚠️ Runners는 placeholder
- ❌ 실제 동작 불가

---

#### **Phase 1: MVP (Minimum Viable Product)**

**목표**: 실제 프로젝트에 투입 가능한 최소 기능

**완성 조건** (CLAUDE.md §13):
- [ ] PR 성공률 ≥ 95% (최근 50 PRs)
- [ ] AI 제안 거부율 ≤ 30%
- [ ] PR당 평균 비용 ≤ $1
- [ ] Audit logs 100+ actions 보관

**핵심 구현 항목**:

| 항목 | 설명 | 우선순위 |
|------|------|----------|
| **API 통합** | Claude, Gemini, Perplexity, GPT API 클라이언트 | 🔴 Critical |
| **PR Diff Collector** | GitHub API로 PR diff, changed files 수집 | 🔴 Critical |
| **Audit Logging** | 모든 프롬프트/응답을 `ai/logs/` 저장 | 🟠 High |
| **Kill-Switch** | `DISABLE_AI_AUTOMATION` secret 체크 | 🟠 High |
| **AI Team YAML** | `.github/ai_team.yml` 생성 | 🟠 High |
| **Context Dirs** | `/docs/CONTEXT/` 구조 생성 | 🟠 High |
| **Cost Enforcement** | 예산 초과 시 workflow 중단 | 🟠 High |
| **Status Checks** | AI 출력 기반 pass/fail | 🟡 Medium |
| **Python Package** | `__init__.py`, `requirements.txt` | 🔴 Critical |

**제약**:
- ❌ 자동 merge 금지
- ❌ Autofix PR은 생성만, merge는 사람
- ✅ Branch protection 필수
- ✅ Human approval ≥ 1

**산출물**:
- 실제 동작하는 AI PR 리뷰 시스템
- Claude PM이 실제 PRD 기반 검토
- Gemini가 실제 UI/UX 피드백
- Perplexity가 실제 컴플라이언스 검토
- 모든 액션이 로그에 기록

---

#### **Phase 2: Production Ready**

**목표**: RAG 정확도 향상, 비용 자동 관리, 메트릭 수집

**완성 조건** (CLAUDE.md §13):
- [ ] PR 성공률 ≥ 95%
- [ ] AI 제안 거부율 ≤ 30%
- [ ] PR당 평균 비용 ≤ $1
- [ ] Audit logs 100+ actions

**핵심 구현 항목**:

| 항목 | 설명 | 기대 효과 |
|------|------|----------|
| **Chroma 벡터 DB** | Naive search → 벡터 임베딩 검색 | RAG 정확도 10배 향상 |
| **Metrics Dashboard** | 비용/효과성/신뢰성 추적 | 데이터 기반 의사결정 |
| **Cost Monitor** | API 호출 비용 실시간 추적 | 예산 초과 방지 |
| **Prompt Versioning** | `_v1` suffix + Git 기반 추적 | 프롬프트 변경 이력 관리 |
| **Compare Reports** | AI 간 충돌 시 자동 생성 | 의사결정 지원 |
| **Slack/Email Alerts** | Critical 이슈 자동 알림 | 빠른 대응 |

**산출물**:
- 프로덕션급 안정성
- 비용 예측 가능
- 메트릭 기반 개선 가능

---

#### **Phase 3: Selective Automation**

**목표**: 저위험 영역 자동 merge 실험

**완성 조건** (CLAUDE.md §13):
- [ ] AI 패치 테스트 커버리지 ≥ 70%
- [ ] Auto-revert 검증 완료 (5+ canary)
- [ ] SAST 통과
- [ ] 거부율 ≤ 20%

**핵심 구현 항목**:

| 항목 | 설명 | 위험 완화 |
|------|------|----------|
| **Low-Risk Auto-Merge** | Lint/format만 자동 merge | Feature flag 제어 |
| **Canary Rollout** | 5% PR만 자동화 테스트 | 점진적 확대 |
| **Auto-Revert** | Merge 후 CI 실패 시 자동 롤백 | 안전망 |
| **Router Intelligence** | 비용 기반 모델 자동 선택 | 비용 최적화 |

**경고**:
- 매우 신중하게 접근
- Feature flag로 즉시 롤백 가능해야 함
- 상세한 모니터링 필수

---

#### **Phase 4: Full AI Dev Studio** (매우 신중)

**목표**: Hyper-Router + Serverless orchestrator

**완성 조건** (CLAUDE.md §13):
- [ ] 월간 비용 예측 가능
- [ ] 90일간 critical incident 0건
- [ ] 법률/컴플라이언스 승인 완료

**핵심 구현 항목**:

| 항목 | 설명 | 위험도 |
|------|------|--------|
| **Serverless Router** | Cloud Function 기반 고속 처리 | 🔴 High |
| **Auto PR Generation** | AI가 자동으로 개선 PR 생성 | 🔴 Very High |
| **AI Knowledge OS** | 프로젝트 전체 히스토리 학습 | 🟡 Medium |
| **Explainability UI** | AI 액션 추적 웹 대시보드 | 🟢 Low |

**위험 (CLAUDE.md §12)**:
- AI 간 토론 폭증 (20~40회 릴레이)
- 예측 불가능한 코드 변경
- 비용 폭발
- RAG drifting
- 디버깅 난이도 극상승

**금지 항목** (Phase 1-2):
- ❌ AI끼리 자율 토론
- ❌ 사람 승인 없는 자동 merge
- ❌ AI가 AI 코드를 수정하는 루프
- ❌ 자동 패키지 매니저
- ❌ 실시간 로컬 코파일럿
- ❌ Serverless AI orchestrator

---

### 3.3 아키텍처 진화 비전

#### **현재 (Phase 0) 아키텍처**

```
PR Opened
    ↓
[Router] → Mode 결정 (lite/pro/enterprise)
    ↓
[Conditional Jobs]
    ├─ Claude Review (stub)
    ├─ Gemini Review (stub)
    └─ Perplexity Review (stub)
    ↓
[Human Review] → Merge
```

---

#### **Phase 1 목표 아키텍처**

```
PR Opened
    ↓
[Router] → Mode 결정 + Kill-switch 체크
    ↓
[RAG Indexer] → Context 추출
    ↓
[Conditional Jobs]
    ├─ Claude PM Review → 실제 API 호출
    │   ├─ PRD 기반 검증
    │   ├─ 아키텍처 리뷰
    │   └─ 보안 체크
    ├─ Gemini FE Review → 실제 API 호출
    │   ├─ UI/UX 분석
    │   ├─ 컴포넌트 구조
    │   └─ 멀티 페르소나 분석
    └─ Perplexity Compliance → 실제 API 호출
        ├─ 법규 검토
        ├─ 리스크 분석
        └─ 정책 체크
    ↓
[Audit Logger] → 모든 입출력 저장
    ↓
[Status Checks] → Pass/Fail 판정
    ↓
[Human Review] → 최종 승인
    ↓
Merge
```

---

#### **Phase 2-3 목표 아키텍처**

```
PR Opened
    ↓
[Router] + [Cost Monitor] + [Metrics Collector]
    ↓
[Chroma Vector DB] → 고정밀 Context 검색
    ↓
[Multi-Agent Parallel Review]
    ├─ Claude PM (GPT-4.5 Sonnet)
    ├─ Gemini FE (Gemini 2.0)
    ├─ Perplexity Compliance (Pro API)
    └─ GPT BE (GPT-4.1)
    ↓
[AI Conflict Resolver] → Compare Report 생성
    ↓
[Status Checks] + [Test Coverage] + [SAST]
    ↓
[Autofix Generator] → 간단한 수정 자동 생성
    ↓
[Canary Auto-Merge] → 5% PR만 자동 (lint/format)
    ├─ Success → Continue
    └─ Fail → Auto-Revert
    ↓
[Human Review] → 최종 승인 (나머지 95%)
```

---

#### **Phase 4 비전 (매우 신중)**

```
Developer: push 1회
    ↓
[Hyper-Router] (Serverless)
    ├─ Project Intelligence
    ├─ Cost Optimizer
    └─ Risk Assessor
    ↓
[AI Team Orchestration]
    ├─ Claude PM → 전략/설계
    ├─ Gemini FE → UI 구현
    ├─ GPT BE → API/DB
    └─ Perplexity → 규제 검토
    ↓
[AI-to-AI Collaboration]
    ├─ 자동 PR 생성
    ├─ 상호 리뷰
    └─ Dispute Resolution
    ↓
[Automated Testing]
    ├─ Unit Tests
    ├─ E2E Tests
    └─ Performance Tests
    ↓
[Guardrail AI] → 위험 감지
    ↓
[Human Checkpoint] → 고위험만 승인
    ↓
[Progressive Deployment]
```

**경고**: 이 단계는 CLAUDE.md §12에서 "위험한 완전 자동화"로 분류됨.
90일간 안정성 검증 + 법률 승인 필요.

---

### 3.4 핵심 설계 원칙 (불변)

1. **사람이 최종 책임을 진다**
   - AI는 제안, 사람이 결정
   - Phase 4에서도 고위험 작업은 사람 승인

2. **안전이 속도보다 우선한다**
   - Emergency kill-switch 항상 작동
   - Branch protection 우회 불가
   - Audit log는 변경 불가

3. **투명성과 감사 가능성**
   - 모든 AI 액션 로깅
   - 프롬프트 버전 추적
   - 비용 추적

4. **단계적 확장과 검증**
   - Phase 전환은 Gate 기준 충족 후에만
   - 점진적 권한 확대
   - 롤백 메커니즘 필수

5. **비용 통제**
   - 예산 한도 강제
   - 모델 선택 최적화
   - 비용 알림

---

## 4. 상세 리팩토링 계획

### 4.1 Phase 1 완성을 위한 리팩토링

#### **4.1.1 Python 패키지 구조 정리**

**목표**: 올바른 Python 프로젝트 구조 확립

**작업**:
1. 모든 디렉토리에 `__init__.py` 생성:
   ```
   ai/__init__.py
   ai/plugins/__init__.py
   ai/runners/__init__.py
   ai/context7/__init__.py
   ai/utils/__init__.py
   ```

2. `requirements.txt` 생성:
   ```
   anthropic>=0.18.0
   google-generativeai>=0.3.0
   openai>=1.0.0
   chromadb>=0.4.0
   PyGithub>=2.0.0
   pyyaml>=6.0
   ```

3. `setup.py` 또는 `pyproject.toml` 생성 (선택)

**예상 시간**: 1시간
**우선순위**: 🔴 Critical

---

#### **4.1.2 API 클라이언트 구현**

**목표**: 실제 동작하는 AI API 통합

**작업**:

**1) Claude API 클라이언트**
- 파일: `ai/runners/clients/claude_client.py`
- 기능:
  - Anthropic SDK 사용
  - 프롬프트 전송
  - JSON 응답 파싱
  - 에러 핸들링 (rate limit, timeout)
  - 비용 추적

**2) Gemini API 클라이언트**
- 파일: `ai/runners/clients/gemini_client.py`
- 기능:
  - Google Generative AI SDK 사용
  - 멀티 페르소나 프롬프트 지원
  - Markdown 응답 파싱

**3) Perplexity API 클라이언트**
- 파일: `ai/runners/clients/perplexity_client.py`
- 기능:
  - REST API 직접 호출
  - 컴플라이언스 검색

**4) GPT API 클라이언트**
- 파일: `ai/runners/clients/gpt_client.py`
- 기능:
  - OpenAI SDK 사용
  - Function calling 지원

**공통 인터페이스**:
```python
class AIClient(ABC):
    @abstractmethod
    def send_prompt(self, prompt: str, **kwargs) -> dict:
        pass

    @abstractmethod
    def estimate_cost(self, prompt: str) -> float:
        pass
```

**예상 시간**: 2-3일
**우선순위**: 🔴 Critical

---

#### **4.1.3 PR Diff Collector 구현**

**목표**: GitHub API로 PR 정보 수집

**작업**:

**파일**: `ai/utils/pr_collector.py`

**기능**:
- GitHub API를 통한 PR diff 수집
- Changed files 목록
- PR 메타데이터 (title, description, author)
- Commit 메시지 수집
- PR 코멘트 생성 기능

**의존성**: PyGithub

**예상 시간**: 1-2일
**우선순위**: 🔴 Critical

---

#### **4.1.4 Audit Logging 시스템**

**목표**: 모든 AI 입출력을 append-only log에 저장

**작업**:

**파일**: `ai/utils/audit_logger.py`

**기능**:
- 로그 디렉토리: `ai/logs/YYYY-MM-DD/`
- 파일 포맷: `{timestamp}_{pr_number}_{agent}.json`
- 저장 내용:
  - 프롬프트 전문
  - AI 응답 전문
  - 메타데이터 (모델, 비용, 시각)
  - PR 정보
- Append-only 강제

**예시 로그**:
```json
{
  "timestamp": "2026-01-15T10:30:45Z",
  "pr_number": 123,
  "agent": "claude",
  "model": "claude-sonnet-4-5",
  "prompt": "...",
  "response": "...",
  "cost_usd": 0.05,
  "metadata": {...}
}
```

**예상 시간**: 1일
**우선순위**: 🟠 High

---

#### **4.1.5 Emergency Kill-Switch**

**목표**: `DISABLE_AI_AUTOMATION` secret으로 즉시 중단

**작업**:

**수정 파일**: `ai/router.py`

**추가 로직**:
```python
def decide_mode(repo_path='.', user_force_mode=None):
    # 0) Emergency kill-switch check
    if os.getenv('DISABLE_AI_AUTOMATION', '').lower() == 'true':
        raise RuntimeError("AI Automation is disabled by kill-switch")

    # ... 기존 로직 ...
```

**Workflow 수정**:
- Router job에서 실패 시 모든 후속 job 스킵
- 명확한 에러 메시지 출력

**예상 시간**: 2시간
**우선순위**: 🟠 High

---

#### **4.1.6 Cost Enforcement**

**목표**: 예산 초과 시 workflow 중단

**작업**:

**수정 파일**: `ai/plugins/cost_checker.py`

**추가 로직**:
```python
def check_budget():
    b = load_budget()
    remaining = b['monthly_budget_usd'] - b.get('monthly_spent_usd', 0)

    if remaining <= 0:
        raise RuntimeError(f"Budget exceeded: ${b['monthly_spent_usd']} / ${b['monthly_budget_usd']}")

    return {
        'monthly_budget_usd': b['monthly_budget_usd'],
        'monthly_spent_usd': b.get('monthly_spent_usd', 0),
        'remaining_usd': remaining,
        'low_budget': remaining < 5
    }
```

**Cost Tracker**:
- 파일: `ai/utils/cost_tracker.py`
- 각 API 호출 후 `.ai/budget.json` 업데이트
- Lock 파일로 동시성 제어

**예상 시간**: 1일
**우선순위**: 🟠 High

---

#### **4.1.7 AI Team Configuration**

**목표**: `.github/ai_team.yml`로 프로젝트별 팀 정의

**작업**:

**파일 생성**: `.github/ai_team.yml`

**예시**:
```yaml
project_name: ai-collab-starter
version: 1.0

team:
  pm:
    agent: claude
    model: claude-sonnet-4-5
    responsibilities:
      - product_requirement
      - acceptance_criteria
      - architecture_review
      - release_plan

  frontend_lead:
    agent: gemini
    model: gemini-2.0-flash-thinking-exp
    responsibilities:
      - uiux_design
      - component_structure
      - responsiveness
      - persona_analysis

  compliance:
    agent: perplexity
    model: llama-3.1-sonar-large-128k-online
    responsibilities:
      - legal_review
      - policy_check
      - risk_analysis

  backend_engineer:
    agent: gpt
    model: gpt-4.5-preview
    responsibilities:
      - api_design
      - database_schema
      - infrastructure
      - devops

rules:
  merge_requires:
    - pm
    - frontend_lead

  enterprise_required_for:
    - infra/**
    - security/**
    - payments/**
```

**파서**:
- 파일: `ai/utils/team_config.py`
- Router가 로딩하여 mode에 따라 agent 선택

**예상 시간**: 4시간
**우선순위**: 🟠 High

---

#### **4.1.8 Context 구조 생성**

**목표**: `/docs/CONTEXT/` 디렉토리 구조

**작업**:

**생성할 디렉토리**:
```
docs/
  CONTEXT/
    business/
      README.md
    compliance/
      README.md
    architecture/
      README.md
      system_overview.md
    uiux/
      README.md
      design_guidelines.md
    data_model/
      README.md
      schema.md
  project_vision.md
  compliance.md
```

**자동 생성 스크립트**:
- 파일: `scripts/init_context_structure.py`
- README 템플릿 자동 생성

**예상 시간**: 2시간
**우선순위**: 🟠 High

---

#### **4.1.9 Workflow 개선**

**목표**: Status check 로직 개선

**작업**:

**수정 파일**: `.github/workflows/ai_review.yml`

**개선 사항**:
1. Runner 출력을 파일로 저장
2. 출력 파일 기반으로 status check 생성
3. 실패 시 명확한 에러 메시지
4. Cost tracking 통합

**예시**:
```yaml
- name: Run Claude Review
  id: claude
  run: |
    python ai/runners/run_claude_review.py \
      --pr-number ${{ github.event.pull_request.number }} \
      --output claude_output.json

- name: Create Claude status check
  uses: actions/github-script@v7
  with:
    script: |
      const fs = require('fs');
      const output = JSON.parse(fs.readFileSync('claude_output.json'));

      github.checks.create({
        owner: context.repo.owner,
        repo: context.repo.repo,
        name: "claude-pm-review",
        head_sha: context.payload.pull_request.head.sha,
        status: "completed",
        conclusion: output.verdict === 'APPROVE' ? 'success' : 'failure',
        output: {
          title: "Claude PM Review",
          summary: output.summary,
          text: JSON.stringify(output.issues, null, 2)
        }
      });
```

**예상 시간**: 1일
**우선순위**: 🟡 Medium

---

#### **4.1.10 Prompt 버전 관리**

**목표**: Prompt 파일명에 버전 추가

**작업**:

**리네임**:
```
claude_review.txt → claude_pm_review_v1.txt
gemini_uiux.txt → gemini_uiux_v1.txt
perplexity_compliance.txt → perplexity_compliance_v1.txt
autofix.txt → autofix_v1.txt
```

**Prompt Loader 수정**:
- 파일: `ai/utils/prompt_loader.py`
- 버전 자동 감지
- 버전 기록 로깅

**예상 시간**: 2시간
**우선순위**: 🟡 Medium

---

### 4.2 코드 품질 개선

#### **4.2.1 Type Hints 추가**

**목표**: Python 3.11+ type hints 전체 추가

**작업**:
- 모든 함수에 type hints
- `typing` 모듈 활용
- mypy 검증

**예상 시간**: 1일
**우선순위**: 🟢 Low

---

#### **4.2.2 Error Handling 강화**

**목표**: 명확한 에러 메시지와 복구 로직

**작업**:
- Custom exception 클래스
- Retry 로직 (API rate limit)
- Graceful degradation

**예상 시간**: 1일
**우선순위**: 🟡 Medium

---

#### **4.2.3 Unit Tests**

**목표**: 핵심 로직 테스트 커버리지 ≥ 70%

**작업**:
- `tests/` 디렉토리 생성
- Router 테스트
- Plugin 테스트
- Mock API 클라이언트

**예상 시간**: 2-3일
**우선순위**: 🟡 Medium

---

### 4.3 문서화 개선

#### **4.3.1 API Documentation**

**파일**: `docs/API_REFERENCE.md`

**내용**:
- Router API
- Plugin API
- Runner API
- Client API

**예상 시간**: 1일
**우선순위**: 🟢 Low

---

#### **4.3.2 Developer Guide**

**파일**: `docs/DEVELOPER_GUIDE.md`

**내용**:
- 로컬 개발 환경 설정
- 새 runner 추가 방법
- 새 plugin 추가 방법
- Debugging tips

**예상 시간**: 1일
**우선순위**: 🟢 Low

---

## 5. 실행 우선순위

### 5.1 Sprint 1: Critical Blockers (1-2주)

**목표**: Phase 1 MVP 동작 가능하게 만들기

| 순위 | 작업 | 예상 시간 | 담당 |
|------|------|----------|------|
| 1 | Python 패키지 구조 | 1시간 | 즉시 |
| 2 | `requirements.txt` 생성 | 30분 | 즉시 |
| 3 | PR Diff Collector | 1-2일 | Week 1 |
| 4 | Claude API 클라이언트 | 1일 | Week 1 |
| 5 | Gemini API 클라이언트 | 1일 | Week 1 |
| 6 | Perplexity API 클라이언트 | 1일 | Week 1 |
| 7 | GPT API 클라이언트 | 1일 | Week 2 |
| 8 | Runner 리팩토링 | 1일 | Week 2 |
| 9 | Workflow 통합 테스트 | 1일 | Week 2 |

**완료 기준**: 실제 PR에 AI 리뷰가 동작함

---

### 5.2 Sprint 2: High Priority (2-3주)

**목표**: Phase 1 안정화 및 거버넌스 강화

| 순위 | 작업 | 예상 시간 |
|------|------|----------|
| 1 | Audit Logging | 1일 |
| 2 | Emergency Kill-Switch | 2시간 |
| 3 | Cost Enforcement | 1일 |
| 4 | AI Team Configuration | 4시간 |
| 5 | Context 구조 생성 | 2시간 |
| 6 | Status Check 개선 | 1일 |
| 7 | Error Handling 강화 | 1일 |

**완료 기준**: Phase 1 Gate 기준 충족 가능

---

### 5.3 Sprint 3: Phase 1 완성 (1-2주)

**목표**: 프로덕션 준비

| 순위 | 작업 | 예상 시간 |
|------|------|----------|
| 1 | Prompt 버전 관리 | 2시간 |
| 2 | Unit Tests | 2-3일 |
| 3 | Documentation | 2일 |
| 4 | 실제 프로젝트 파일럿 | 1주 |
| 5 | Bug fixes | 변동 |

**완료 기준**: 50 PRs 처리, 95% 성공률

---

### 5.4 Sprint 4+: Phase 2 준비

**목표**: Chroma RAG, Metrics, Phase 2 기능

- Chroma 벡터 DB 통합
- Metrics collection
- Compare reports
- Slack/Email alerts

---

## 6. 리스크 및 완화 전략

### 6.1 기술적 리스크

| 리스크 | 영향도 | 완화 전략 |
|--------|--------|----------|
| **API 비용 폭발** | 🔴 High | Budget guard + Cost tracker + Alert |
| **API rate limit** | 🟠 Medium | Retry logic + Exponential backoff |
| **RAG 정확도 낮음** | 🟡 Medium | Phase 2 Chroma 전환 |
| **Workflow 실패** | 🟠 Medium | Error handling + Fallback |
| **Python 의존성 충돌** | 🟢 Low | `requirements.txt` 버전 고정 |

---

### 6.2 운영 리스크

| 리스크 | 영향도 | 완화 전략 |
|--------|--------|----------|
| **AI 출력 신뢰성** | 🟠 Medium | Human-in-the-loop + Audit log |
| **보안 취약점** | 🔴 High | Sensitive path 강제 enterprise + SAST |
| **프라이버시** | 🔴 High | PR diff만 전송, 코드 전체 전송 금지 |
| **Vendor lock-in** | 🟡 Medium | 공통 인터페이스 + 교체 가능 설계 |

---

### 6.3 조직적 리스크

| 리스크 | 영향도 | 완화 전략 |
|--------|--------|----------|
| **개발자 신뢰 부족** | 🟠 Medium | 투명성 + Audit log + Override 가능 |
| **과도한 의존** | 🟡 Medium | Kill-switch + Manual mode |
| **AI 편향** | 🟡 Medium | 다중 AI 사용 + Human review |

---

## 7. 다음 단계 (Immediate Actions)

### 7.1 오늘 할 일

1. ✅ **Python 패키지 구조 정리**
   ```bash
   touch ai/__init__.py
   touch ai/plugins/__init__.py
   touch ai/runners/__init__.py
   touch ai/context7/__init__.py
   touch ai/utils/__init__.py
   ```

2. ✅ **`requirements.txt` 생성**

3. ✅ **Context 디렉토리 생성**
   ```bash
   mkdir -p docs/CONTEXT/{business,compliance,architecture,uiux,data_model}
   ```

4. ✅ **AI Team YAML 생성**
   - `.github/ai_team.yml` 작성

---

### 7.2 이번 주 목표

1. **PR Diff Collector 구현**
2. **Claude API 클라이언트 구현**
3. **첫 실제 AI 리뷰 동작 확인**

---

### 7.3 다음 주 목표

1. **모든 API 클라이언트 완성**
2. **Audit Logging 구현**
3. **Kill-Switch 구현**
4. **첫 파일럿 프로젝트 적용**

---

## 8. 결론

### 8.1 현재 상태 요약

**강점**:
- ✅ 견고한 아키텍처 설계
- ✅ 명확한 문서화
- ✅ 확장 가능한 플러그인 구조
- ✅ 안전 중심 철학

**약점**:
- ❌ Runner가 모두 stub
- ❌ 실제 API 통합 없음
- ❌ Audit logging 없음
- ❌ 일부 거버넌스 메커니즘 누락

---

### 8.2 핵심 메시지

**이 프로젝트는 "코드를 자동으로 짜주는 도구"가 아닙니다.**

> **AI를 조직처럼 운영하여,
> 1인 개발자도 엔터프라이즈급 품질을 달성할 수 있도록 지원하는
> "AI 멀티-에이전트 개발 오케스트레이터"입니다.**

**성공을 위한 3가지 핵심**:
1. **안전 우선**: 자동화보다 통제
2. **단계적 확장**: 검증 후 진행
3. **사람 중심**: AI는 도구, 사람이 주인

---

### 8.3 비전

**Phase 1 완료 후**:
- 실제 프로젝트에서 AI 팀 협업 가능
- Claude PM + Gemini FE + Perplexity Compliance + GPT BE
- 모든 액션이 감사 가능하고 통제 가능

**Phase 2-3 후**:
- 벡터 RAG로 정확도 10배 향상
- 메트릭 기반 지속적 개선
- 저위험 작업 자동화

**Phase 4 (매우 신중)**:
- 진짜 AI Dev Studio
- 하지만 안전장치는 절대 제거하지 않음

---

**다음 단계**: 이 문서를 기반으로 실제 리팩토링 작업 시작

---

*문서 끝*
