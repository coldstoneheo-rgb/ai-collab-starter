# AGENTS.md — AI 팀 역할 및 거버넌스 가이드

> **최우선 규칙**: 이 문서보다 `CLAUDE.md`가 우선한다.
> 금지 목록, CI 규칙, Workflow 수정 규칙은 `CLAUDE.md` §1-6을 따른다.

---

## 1. AI 팀 역할 분담

| AI | 역할 | 핵심 책임 | 특장점 |
|---|---|---|---|
| **Claude Code** | Main PM / Orchestrator | PRD/CLAUDE.md 관리, 아키텍처 리뷰, 보안 검증, 최종 merge 승인 | 논리력, 프로젝트 기획, 직관적 디버깅 |
| **Gemini** | Frontend Lead / Multi-perspective Analyst | UI/UX 설계, 컴포넌트 구조, 멀티 페르소나 분석 | 프론트엔드 디자인, 다각도 동시 분석 |
| **Perplexity** | Compliance Lead / Researcher | 법률/규제 검토, 리스크 분석, 시장 조사 | 최신 정보 검색, 컴플라이언스 검증 |
| **GPT** | Backend Engineer / Documentation | API 설계, 데이터베이스 스키마, 인프라, 기술 문서화 | 백엔드 로직, 데이터 모델링 |

### AI 간 충돌 해결 우선순위

1. 보안/법규 이슈 → Claude Code(PM) 최종 결정
2. UX/시각적 이슈 → Gemini 우선
3. 기술 스택 선택 → Claude Code(PM) + GPT 합의
4. 컴플라이언스 → Perplexity 우선
5. 의견 불일치 → `compare-report` 생성, 사람이 48시간 내 결정

---

## 2. AI 팀 구성 설정

팀 구성은 `.github/ai_team.yml`로 관리한다.

```yaml
project_name: ai-collab-starter

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
```

**중요:**
- `ai_team.yml` 변경은 반드시 PR로 진행
- 역할 변경 시 PRD.md에 변경 사유 명시 필수

---

## 3. 운영 모드 (고정, 변경 불가)

| 모드 | 사용 조건 | 활성 AI | 비용 |
|---|---|---|---|
| **lite** | 소규모 스크립트, 단순 문서, 개인 프로젝트 | Claude 또는 GPT (1개) | 저비용 |
| **pro** | 일반 앱/웹/백엔드 | Claude + GPT + Perplexity | 중간 |
| **enterprise** | 대규모, 민감 데이터, 팀 프로젝트 | 모든 AI 병렬 협업 | 높음 |

### 모드 결정 흐름 (`ai/router.py`)

```
1. DISABLE_AI_AUTOMATION=true → 즉시 중단
2. AI_FORCE_MODE 또는 .ai/config.yml mode 설정 → 해당 모드 적용
3. 민감 경로 변경 (.github/workflows/, infra/, db/, security/) → enterprise 강제
4. 예산 초과 → lite 강제
5. 프로젝트 스캔 (payment/개인정보/UI 여부, 코드 파일 수) → 자동 결정
```

**Router 계약 출력 (변경 불가):**
```json
{
  "mode": "lite | pro | enterprise",
  "enabled_agents": ["claude", "gemini", "perplexity"],
  "autofix_allowed": false
}
```

---

## 4. 안전장치 체크리스트

운영 전 반드시 확인:

- [ ] Branch protection 활성화 (main: PR + human review ≥ 1)
- [ ] Status checks 설정 (claude-check 필수)
- [ ] `DISABLE_AI_AUTOMATION` Secret 등록 (비상 시 `true`로 설정)
- [ ] `.ai/budget.json` 월 예산 설정
- [ ] Audit logs 보관 (`ai/logs/`, 90일 이상)
- [ ] Autofix PR은 bot이 merge 불가 설정

---

## 5. Phase Gate 기준

### Phase 1 → Phase 2 진입 조건
- Workflow 성공률 ≥ 95% (최근 50 PRs)
- AI 제안 거부율 ≤ 30% (최근 30 PRs)
- PR당 평균 비용 ≤ $1
- Audit logs 100+ actions 보관

### Phase 2 → Phase 3 진입 조건
- AI 패치 테스트 커버리지 ≥ 70%
- Auto-revert 검증 완료 (5회 이상 canary)
- SAST 통과 (bandit HIGH 0건)
- AI 제안 거부율 ≤ 20%

### Phase 3 → Phase 4 진입 조건
- 월간 비용 예측 가능 (변동 ≤ 10%)
- 90일간 critical incident 0건
- 법률/컴플라이언스 승인 완료

---

## 6. 절대 금지 (전 Phase 공통)

> 상세 규칙은 `CLAUDE.md` §2, §4, §12 참조

- ❌ AI끼리 자율 토론/릴레이 PR 생성
- ❌ 사람 승인 없는 자동 merge (Phase 3 lint/format 제외)
- ❌ router 출력 구조 변경
- ❌ workflow에서 if: 판단 로직 추가
- ❌ 민감 경로 자동 수정
- ❌ 비상 kill-switch 우회
