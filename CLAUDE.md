1. 이 문서는 “법”이다

이 문서는:

PRD보다 우선

AI의 기본 판단보다 우선

편의성보다 우선

2. Codex/Claude/GPT 공통 금지 목록 (확장)
❌ 절대 금지

workflow에서 if:로 판단 로직 추가

router 출력 구조 변경

브랜치 보호 없는 상태에서 자동화 제안

“임시로”라는 명목의 shortcut

3. Branch & CI 규칙 (추가)
Branch 규칙

main: 보호 필수

test-*, codex/*: 실험 브랜치

실험 브랜치는 main에 직접 merge 불가

CI 규칙

workflow가 깨지면 즉시 복구 우선

기능 추가보다 CI 안정성 우선

4. Workflow 수정 규칙 (강화)

Workflow를 수정할 때:

job은 반드시 steps를 가져야 함

$GITHUB_OUTPUT는 표준 echo 방식만 허용

중간 파일 사용 ❌

5. Codex 작업 방식 규정 (중요)

Codex는:

한 PR = 한 목적

“설계 개선”이라는 명목으로 리팩토링 ❌

문서 수정 없이 구조 변경 ❌

6. 실패 시 행동 규칙

애매하면 STOP

추측 ❌

"보통 이렇게 합니다" ❌

---

## 7. AI 역할 분담 및 책임 (AI-Collab Core)

### 7.1 기본 원칙

> **Claude Code = Main Project Manager (PM / Orchestrator)**
> **다른 AI들 = Execution & Analysis Agents**

### 7.2 AI별 역할 및 특성

| AI | 역할 | 책임 | 특장점 |
|---|---|---|---|
| **Claude Code** | Main PM / Orchestrator | PRD/CLAUDE.md 관리, 기능 우선순위, 아키텍처 리뷰, 논리/보안 검증, 최종 merge 승인 | 창의성, 논리력, 프로젝트 기획과 관리, 직관적인 코드 디버깅 |
| **Gemini** | Frontend Lead / Multi-perspective Analyst | UI/UX 설계, 컴포넌트 구조, 멀티 페르소나 분석, 프론트엔드 성능 시뮬레이션 | 프론트엔드 디자인, 멀티 태스킹(다양한 관점에서 동시 분석) |
| **Perplexity** | Compliance Lead / Researcher | 법률/규제 검토, 정책 체크, 리스크 분석, 시장 조사 | 최신 정보 검색, 컴플라이언스 검증 |
| **GPT** | Backend Engineer / Documentation | API 설계, 데이터베이스 스키마, 인프라, DevOps, 문서화 | 백엔드 로직, 데이터 모델링, 기술 문서 작성 |

### 7.3 AI 팀 구성 규칙

**프로젝트마다 AI 팀 구성이 달라질 수 있다.**

`.github/ai_team.yml` 파일로 관리:

```yaml
project_name: your-project-name

team:
  pm:
    agent: claude
    responsibilities:
      - product_requirement
      - acceptance_criteria
      - architecture_review
      - release_plan

  frontend_lead:
    agent: gemini
    responsibilities:
      - uiux_design
      - component_structure
      - responsiveness
      - persona_analysis

  compliance:
    agent: perplexity
    responsibilities:
      - legal_review
      - policy_check
      - risk_analysis

  backend_engineer:
    agent: gpt
    responsibilities:
      - api_design
      - database_schema
      - infrastructure
      - devops

rules:
  merge_requires:
    - pm
    - frontend_lead  # 프로젝트에 따라 조정
```

**중요:**
- `ai_team.yml` 변경은 반드시 PR로 진행
- 역할 변경 시 PRD.md에 변경 사유 명시 필수

---

## 8. 자동 분기 로직 (Mode Selection)

### 8.1 3가지 모드 (고정)

| 모드 | 사용 조건 | 동작 | 비용 |
|---|---|---|---|
| **Lite** | 작은 스크립트, 단순 문서, 개인 프로젝트 | Claude 또는 GPT 한 모델만, 리뷰/autofix 없음, RAG 없음 | 저비용 |
| **Pro** | 일반 앱/웹/백엔드, 적당한 규모 | Claude(PM) + GPT(문서/테스트) + Perplexity(리서치), RAG 최소, PR 리뷰 자동화 | 중간 |
| **Enterprise** | 대규모 모듈, 팀 프로젝트, 민감 데이터 | 모든 AI 병렬 협업, 고정밀 PR 리뷰, RAG full, 위험 작업 human-in-loop | 높음 |

### 8.2 모드 결정 기준

**자동 판단 (router.py):**

```python
if cost.low_budget:
    mode = "lite"
elif project.has_payment or project.touches_personal_data:
    mode = "enterprise"
elif project.has_ui or project.code_files > 50:
    mode = "pro"
else:
    mode = "lite"
```

**수동 고정 (우선순위 높음):**
- `.ai/config.yml`에 `mode: pro` 명시
- Repository Secret `AI_FORCE_MODE` 설정

### 8.3 민감 경로 강제 Enterprise

다음 경로 변경 시 무조건 Enterprise:
- `/infra/**`
- `/db/**`
- `/security/**`
- `.github/workflows/**`

---

## 9. Context & RAG 관리

### 9.1 Context 구조

```
/docs
  /CONTEXT
    business/         # 비즈니스 로직, 도메인 지식
    compliance/       # 법률, 규제, 정책
    architecture/     # 시스템 설계, API 스펙
    uiux/            # 디자인 가이드, UX 플로우
    data_model/      # 데이터베이스 스키마
  project_vision.md
  prd.md
  claude.md
  gemini.md
  compliance.md
```

### 9.2 RAG 규칙

- 모든 `.md`, `.py`, `.ts`, `.js` 파일 자동 인덱싱
- `node_modules`, `.git`, `__pycache__`, `dist` 제외
- 벡터 DB: Chroma (local) 또는 Context7 (cloud)
- 재인덱싱: 매 커밋 또는 nightly job

### 9.3 Context 업데이트 규칙

**AI가 Context를 업데이트하려면:**
1. PR로 변경 제안
2. 변경 사유 명시
3. 사람 승인 필수

**AI는 절대:**
- Context를 직접 수정할 수 없음
- 자동으로 삭제할 수 없음

---

## 10. 프롬프트 관리 규칙

### 10.1 프롬프트 버전 관리

```
.github/AI_PROMPTS/
  claude_pm_review_v1.txt
  gemini_uiux_v1.txt
  perplexity_compliance_v1.txt
  gpt_backend_v1.txt
```

### 10.2 프롬프트 변경 규칙

**절대 규칙:**
- 프롬프트 변경은 반드시 PR로 진행
- 버전 번호 필수 (`_v1`, `_v2`, ...)
- 변경 사유를 PR description에 명시
- 이전 버전 보관 (삭제 금지)
- 사람 승인 없이 프롬프트 변경 불가

**AI는:**
- 프롬프트 개선을 제안할 수 있음
- 직접 수정할 수 없음
- 버전을 임의로 변경할 수 없음

---

## 11. 안전장치 및 거버넌스 (강화)

### 11.1 필수 안전장치

- [x] Branch protection: PR review ≥ 1 human
- [x] Status checks: mode별 AI checks 필수
- [x] Autofix PRs는 bot이 merge 불가
- [x] Audit logs 저장 (append-only)
- [x] 민감 경로 변경 시 자동 block
- [x] Cost guard: 월 예산 초과 시 중단
- [x] Emergency kill-switch: `DISABLE_AI_AUTOMATION=true`

### 11.2 AI 간 충돌 해결 정책

**우선순위:**
1. 보안/법규 이슈 → Claude(PM) 최종 결정
2. UX/시각적 이슈 → Gemini 우선
3. 기술 스택 선택 → Claude(PM) + GPT 합의
4. 컴플라이언스 → Perplexity 우선

**Dispute Resolution:**
- AI 간 의견 불일치 시 `compare-report` 생성
- 사람이 48시간 내 최종 결정
- Slack/Email 알림

---

## 12. 위험한 완전 자동화 버전 경고

### 12.1 절대 금지 (Phase 1-2)

GPT와의 대화에서 논의된 "위험한 완전 자동화 버전"은 현재 구현하지 않는다:

❌ **금지 항목:**
- AI끼리 자율 토론 (릴레이 PR 생성)
- 자동 merge (사람 승인 없이)
- AI가 AI 코드를 수정하는 루프
- 자동 패키지 매니저
- 실시간 로컬 코파일럿 (IDE 통합)
- Serverless AI orchestrator

### 12.2 이유

> **"너무 똑똑한 엔진은 통제 난이도가 크다"**

위험 요소:
- AI 간 토론 폭증 (20~40회 릴레이)
- 예상치 못한 기술 스택 선택
- 비용 폭발
- RAG drifting
- 디버깅 난이도 극상승

### 12.3 Phase 3 이후 고려사항

**Phase 3 이후 제한적 허용 가능:**
- 저위험 영역만 자동 merge (lint, format)
- Canary rollout (5% PR만 자동화)
- Auto-revert 기능 필수
- 상세한 감사 로그

**Phase 4 고려 (매우 신중):**
- Hyper-Router
- Serverless backend
- Full-cycle automation

---

## 13. Phase별 Gate 기준 (추가)

### Phase 1 → Phase 2

- PR 성공률 ≥ 95% (최근 50 PRs)
- AI 제안 거부율 ≤ 30% (최근 30 PRs)
- PR당 평균 비용 ≤ $1
- Audit logs 100+ actions 보관

### Phase 2 → Phase 3

- AI 패치 테스트 커버리지 ≥ 70%
- Auto-revert 검증 완료 (5+ canary)
- SAST 통과
- 거부율 ≤ 20%

### Phase 3 → Phase 4

- 월간 비용 예측 가능
- 90일간 critical incident 0건
- 법률/컴플라이언스 승인 완료

---

## 14. 템플릿 적용 (ai-collab-starter)

### 14.1 새 프로젝트

```bash
npx ai-collab-starter init my-project
# 또는
python scripts/init_ai_project.py
```

### 14.2 기존 프로젝트

```bash
python scripts/apply_ai_collab.py /path/to/project
```

**자동 생성:**
- `ai/` 디렉토리
- `.github/workflows/`
- `.github/AI_PROMPTS/`
- `docs/CONTEXT/`
- 기본 설정 파일들

---

## 15. 최종 철학 (변경 불가)

1. **사람이 최종 책임을 진다**
2. **AI는 제안하고, 사람이 결정한다**
3. **안전이 속도보다 우선한다**
4. **투명성과 감사 가능성을 유지한다**
5. **단계적으로 확장하고, 검증 후 진행한다**

---

이 문서의 모든 규칙은 PRD.md보다 우선하며, AI의 기본 판단보다 우선한다.