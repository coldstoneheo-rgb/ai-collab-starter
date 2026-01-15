## 1. 프로젝트 정의 및 비전

### 1.1 프로젝트 배경

**문제 인식:**
- 단일 AI만 사용하면 프로젝트가 "산으로 간다" - 목표, 목적, 철학, 컨셉에서 벗어남
- 여러 AI를 번갈아 사용하면 인수인계 문제 발생
- 인수인계 문서가 제대로 작성되지 않으면 협업 실패
- AI가 놓치는 부분을 상호 보완할 방법 필요

**해결 방안:**
두 AI를 함께 사용하는 목적은 서로 코드를 **분석, 감시, 보완**하면서 누군가 놓치는 것들을 보완하고 협업하면서 시너지를 내어 최종적으로 **효율적이고 목표에 부합하는 퀄리티 높은 엔터프라이즈 앱**을 구현하는 것.

### 1.2 정의

**AI-Collab-Starter**는
"AI가 코드를 대신 짜주는 도구"가 아니라,

> **여러 AI를 '조직 구조'처럼 배치하고,
> 사람이 최종 책임을 지는 GitHub 기반 AI 협업 개발 시스템**이다.

### 1.3 핵심 목표

1. **상호 보완적 협업**: AI들이 서로의 약점을 보완
2. **일관된 프로젝트 방향**: 목표와 철학 유지
3. **자동화된 컨텍스트 공유**: GitHub + RAG 기반 인수인계
4. **엄격한 품질 관리**: 다중 관점의 코드 리뷰

### 1.4 성공 기준

이 프로젝트의 성공 기준은:

- 자동화 ❌

- 생산성 ❌
    👉 **통제·안전·예측 가능성 ⭕**
    
---

## 2. 현재 Phase 명확화

### 현재 상태

- **Phase 1 — Safe Modular System**
    
- 목적:
    
    - Router 중심 의사결정 구조를 **실제로 CI에서 강제**
        
    - 민감 경로 보호
        
    - 자동 수정 차단
        

### Phase 1에서 “하면 안 되는 것”

- 자동 merge
    
- auto-fix on push
    
- router 우회 로직
    
- workflow에서 조건 판단
    

---

## 3. 핵심 철학 (변경 불가)

  1. Router 단일 결정 원칙

    - 어떤 AI가 실행될지, 어떤 모드인지 판단은 오직 router만 한다.

  2. 모듈식 설계

    - router / plugins / runners / workflow는 서로 책임이 분리된다.

  3. 자동 수정은 PR까지만

    - 자동 merge는 Phase 3 이전까지 절대 금지.

  4. 민감 경로 우선 보호

    - infra, db, security 관련 변경은 무조건 enterprise 모드.

  5. 비용은 기능보다 우선 고려

    - 예산 초과 시 기능이 아니라 AI 호출을 제한한다

---

## 4. 시스템 아키텍처 (강화)

### 4.1 단일 책임 규칙 (SRP, 변경 불가)

|레이어|책임|금지|
|---|---|---|
|router|**결정**|실행 ❌|
|plugin|정보 수집|판단 ❌|
|workflow|실행|결정 ❌|
|runner|API 호출|정책 ❌|

> 이 규칙을 어기면 **PR 즉시 중단**

### 4.2 주요 컴포넌트

| 컴포넌트                              | 역할                   |
| --------------------------------- | -------------------- |
| `ai/router.py`                    | 프로젝트/PR 컨텍스트 기반 의사결정 |
| `ai/plugins/*`                    | 판단에 필요한 정보 수집        |
| `ai/runners/*`                    | 실제 AI API 호출         |
| `.github/workflows/ai_review.yml` | 실행 파이프라인             |
| `ai/logs/`                        | 모든 AI 입력/출력 기록       |

---

## 5. Router 결정 계약 (Contract)

Router는 항상 다음 **계약된 출력**만 낸다.

```bash
{
   "mode": "lite | pro | enterprise",
   "enabled_agents": ["claude", "gemini", "perplexity"],
   "autofix_allowed": false
 }
```

### 절대 규칙

- 출력 키 이름 변경 ❌
    
- 조건부 출력 ❌
    
- workflow에서 재해석 ❌
    

---

## 6. 민감 경로 정책 (강화)

### 민감 경로 정의

- `/infra/**`
    
- `/db/**`
    
- `/security/**`
    
- `.github/workflows/**`
    

### 정책

- **하나라도 변경되면 무조건 enterprise**
    
- autofix_allowed = false 강제
    
- 예외 없음
    

---

## 7. GitHub 운영 정책 (PRD에 명시)

### 필수 조건

- `main` 브랜치 보호 필수
    
    - force push ❌
        
    - direct push ❌
        
    - PR + 1 human review 필수
        

> **브랜치 보호 없이는 Phase 1 완료 선언 불가**

---

## 8. Phase 1 완료 기준 (Gate, 재정의)

Phase 1은 아래 **모두** 만족해야 종료된다.

1. router job이 항상 실행됨
    
2. workflow가 router outputs를 소비함
    
3. 민감 경로 PR에서 enterprise 강제 로그 확인
    
4. autofix 관련 workflow 전부 비활성화
    
5. main 브랜치 보호 설정 완료

---

## 8. 단계별 로드맵 요약

Phase 0: 준비 (템플릿, secrets)

Phase 1: 안전한 모듈형 시스템 (현재 목표)

Phase 2: RAG 고도화 (Chroma)

Phase 3: 제한적 자동화

Phase 4: 실험적 완전 자동화

---

## 9. 운영 모드(고정)

| Mode       | 목적         |
| ---------- | ---------- |
| lite       | 저비용, 단순 리뷰 |
| pro        | 일반 프로젝트 기본 |
| enterprise | 민감/대규모/상용  |

---

## 10. AI 역할 및 특성 (상세)

### 10.1 AI 선정 기준

GPT와의 대화를 통해 각 AI의 특장점을 분석하여 역할을 배정:

| AI | 주요 강점 | 선정 이유 |
|---|---|---|
| **Claude Code** | 창의성, 논리력, 프로젝트 기획 및 관리, 직관적인 디버깅 | PRD/CLAUDE.md 관리에 특화, 전체 프로젝트 방향성 제시 능력 |
| **Gemini Antigravity** | 프론트엔드 디자인, 멀티 태스킹(다양한 페르소나 동시 분석) | UI/UX 설계, 여러 관점에서 동시 데이터 분석 |
| **Perplexity** | 최신 정보 검색, 법률/규제 지식 | 실시간 시장 조사, 컴플라이언스 검증 |
| **GPT** | 백엔드 로직, 데이터 모델링, 기술 문서 작성 | API 설계, 인프라, DevOps 지원 |

### 10.2 역할 배치 원칙

**Main PM (Claude Code):**
- PRD.md, CLAUDE.md 등 기획·정리·논리·디버깅에 강함
- 전체 프로젝트의 방향·목표·철학·릴리즈 스펙 관리
- 초안 코드 리뷰 (논리·아키텍처·보안·성능)
- Merge 승인 전 최종 체크리스트 검증

**Execution & Analysis Agents:**
- Gemini: 구현·검증·디자인 담당
- Perplexity: 컴플라이언스·리서치
- GPT: 백엔드·문서화·테스트

### 10.3 멀티 페르소나 분석 예시

Gemini의 멀티 태스킹 활용 예:
- 주식 분석 시스템: 워렌 버핏, 피터 린치, 20년차 퀀트 투자자, 15년차 차트분석 트레이더 관점에서 동시 분석
- 결과 통합하여 최적의 결론 도출

---

## 11. 리포지토리 구조 (권장)

```
/project-root
  /ai
    /context7           # RAG 인덱서 및 파이프라인
    /runners            # AI API 호출 스크립트
    /plugins            # Router용 플러그인 (project_scan, cost_checker 등)
    /logs               # AI 입출력 감사 로그
    router.py           # 중앙 의사결정 엔진

  /frontend
  /backend
  /infra

  /docs
    /CONTEXT            # RAG 소스 문서
      business/
      compliance/
      architecture/
      uiux/
      data_model/
    CLAUDE.md
    GEMINI.md
    PRD.md
    ARCHITECTURE.md

  /.github
    /workflows
      ai_review.yml     # PR 자동 리뷰
      ai_index.yml      # RAG 인덱싱
    /AI_PROMPTS         # 프롬프트 템플릿 (버전관리)
      claude_pm_review_v1.txt
      gemini_uiux_v1.txt
      perplexity_compliance_v1.txt
      gpt_backend_v1.txt

  /scripts
    init_ai_project.py
    apply_ai_collab.py

  /tests
```

---

## 12. PR 워크플로우 (자세한 흐름)

### 12.1 PR 생성 시 자동화 프로세스

1. **PR opened** → GitHub Actions 트리거

2. **Pre-merge AI Review**:
   - `router` Job: 프로젝트 스캔, 모드 결정, 실행할 AI 목록 반환
   - `claude-orchestrator` Job: 구조적 검토, 보안 리스크, Acceptance Criteria 검증
   - `gemini-analyst` Job: UI/UX 피드백, 성능/접근성 분석
   - `perplexity-compliance` Job (enterprise 모드만): 법규 위반 검사
   - `gpt-backend` Job: 코드 구조, 모델링, 아키텍처 제안

3. **자동 수정 제안** (옵션):
   - AI가 작은 코드 스타일 문제는 자동 branch+PR 생성
   - 큰 변경은 코멘트로 제안

4. **사람 리뷰**:
   - 모든 AI 체크 통과 + 사람 승인 1명 이상 필수
   - 민감 경로 변경 시 enterprise 모드 강제

5. **병합 후**:
   - 릴리즈 노트 자동 생성 (옵션)
   - RAG 인덱스 업데이트

### 12.2 Status Checks

필수 Status Checks:
- `router-check`: 항상 실행
- `claude-check`: mode에 따라
- `gemini-check`: pro/enterprise
- `perplexity-check`: enterprise only
- `ci-lint`, `unit-tests`, `e2e-tests`: 기본 CI

---

## 13. Phase별 상세 로드맵

### Phase 0: 준비 (완료)

**목표**: 기본 템플릿 및 환경 설정

**산출물**:
- `.github/AI_PROMPTS/` 템플릿
- 기본 workflows 스켈레톤
- GitHub Secrets 등록
- 프로젝트 문서 초안

---

### Phase 1: 안전한 모듈형 시스템 (현재, MVP)

**목표**: 실제 프로젝트에 투입 가능한 최소 기능

**핵심 항목**:
1. Router 최소 구현 (결정만)
2. Plugins: project_scan, cost_checker, mode_map
3. Workflow 분기 (mode별 조건부 실행)
4. Autofix 안전 모드 (PR 생성만, merge 불가)
5. Audit logging (모든 AI 입출력 저장)
6. Budget guard (일/월 한도 검사)
7. Branch protection + CODEOWNERS

**운영 규칙**:
- 모든 autofix PR은 자동 merge 금지
- 보안/DB/infra 변경은 manual 필수

**완료 기준** (CLAUDE.md 섹션 8 참조):
- Router job 항상 실행
- Workflow가 router outputs 소비
- 민감 경로 PR에서 enterprise 강제
- Autofix workflow 비활성화
- Main 브랜치 보호 설정

---

### Phase 2: 고도화 (안정화 + RAG 개선)

**목표**: RAG 정확도 향상, 비용 모니터링 자동화

**핵심 항목**:
1. Chroma 인덱스 정교화 (임베딩 파라미터, chunking)
2. Cost monitor service (Slack/Email 알림)
3. PR context extractor 개선 (GitHub API 활용)
4. Prompt versioning + review process
5. AI disagreement → compare-report 생성

**완료 기준**:
- PR 성공률 ≥ 95% (최근 50 PRs)
- AI 제안 거부율 ≤ 30%
- PR당 평균 비용 ≤ $1
- Audit logs 100+ actions

---

### Phase 3: 선별적 자동화 (실험)

**목표**: 저위험 영역 자동 merge 실험

**핵심 항목**:
1. Low-risk autofix PRs 자동 merge (lint/format only)
2. Canary rollout (5% PR만 자동화)
3. Rollback hooks + auto-revert
4. Router 지능 확장 (비용 기반 모델 선택)

**완료 기준**:
- AI 패치 테스트 커버리지 ≥ 70%
- Auto-revert 검증 완료 (5+ canary)
- SAST 통과
- 거부율 ≤ 20%

**위험 관리**:
- Feature flag로 제어
- 즉시 롤백 가능
- 상세 모니터링

---

### Phase 4: 완전 자동화 (매우 신중)

**목표**: Hyper-Router + Serverless orchestrator

**핵심 항목**:
1. Router를 serverless backend로 이동
2. Auto-generation of PRs + full code-change loop
3. Advanced audit & explainability UI
4. Legal/ethical compliance certification

**완료 기준**:
- 월간 비용 예측 가능
- 90일간 critical incident 0건
- 법률/컴플라이언스 승인 완료

**경고**:
이 Phase는 CLAUDE.md 섹션 12에서 설명한 "위험한 완전 자동화 버전"을 포함합니다.
매우 신중하게 접근하며, 충분한 검증 없이 진행하지 않습니다.

---

## 14. 비용 및 예산 관리

### 14.1 비용 추정

| Mode | AI 사용 | PR당 예상 비용 | 월 예상 (50 PRs 기준) |
|---|---|---|---|
| Lite | Claude 또는 GPT | $0.10 - $0.30 | $5 - $15 |
| Pro | Claude + GPT + Perplexity | $0.50 - $1.00 | $25 - $50 |
| Enterprise | 4 AI 전체 | $1.50 - $3.00 | $75 - $150 |

### 14.2 예산 제어

**Budget guard 메커니즘**:
- `.ai/budget.json` 또는 Repository Secret
- 일일/월간 한도 설정
- 한도 80% 도달 시 경고
- 한도 초과 시 자동 중단 또는 lite 모드 전환

**Cost tracking**:
- 각 AI 호출 비용 로깅
- 주간/월간 리포트 생성
- 프로젝트별 비용 추적

---

## 15. 메트릭 및 모니터링

### 15.1 핵심 메트릭

**비용 메트릭**:
- Cost per PR
- Cost per day
- Monthly spend by model

**효과성 메트릭**:
- AI suggestion acceptance rate
- Human override rate
- Time to merge (PR → merge)

**신뢰성 메트릭**:
- Action run success rate
- Runner error rate
- False positive rate

**안전 메트릭**:
- Incidents (data leak, infra changes)
- Blocked auto-merges
- Emergency kill-switch activations

### 15.2 알림 및 대응

**알림 조건**:
- AI가 critical 이슈 발견
- 비용 한도 80% 도달
- Action 연속 실패 (3회 이상)
- 민감 경로 변경 감지

**알림 채널**:
- Slack
- Email
- GitHub Issues (자동 생성)

---

## 16. 확장 로드맵 (미래)

### 16.1 단기 확장 (Phase 2-3)

- **다국어 지원**: 문서 및 코멘트 자동 번역
- **테스트 자동 생성**: AI가 제안한 테스트 케이스 자동 구현
- **성능 분석**: 자동 벤치마크 및 최적화 제안
- **보안 스캔 통합**: SAST/DAST 도구 자동 실행

### 16.2 중기 확장 (Phase 3-4)

- **AI-to-AI PR**: AI가 자동으로 변경 제안 PR 생성
- **Local IDE 통합**: 실시간 코파일럿 기능
- **Simulated stakeholder 회의**: 다중 관점 시뮬레이션
- **Automated release management**: 릴리즈 노트, 배포 자동화

### 16.3 장기 비전 (Phase 4+)

- **Serverless AI orchestrator**: Cloud function 기반 고속 처리
- **AI Knowledge OS**: 프로젝트 전체 히스토리 학습
- **Guardrail AI**: AI가 AI를 감시하는 이중 안전장치
- **Cost-aware optimization**: 자동 비용 최적화

---

## 17. 제약사항 및 위험 관리

### 17.1 현재 제약사항

**기술적 제약**:
- API rate limits
- 토큰 길이 제한
- 네트워크 latency
- GitHub Actions 실행 시간 제한

**비용 제약**:
- 월 예산 한도
- PR당 비용 상한

**안전 제약**:
- 자동 merge 금지 (Phase 1-2)
- 민감 경로 변경 제한
- Human-in-the-loop 필수

### 17.2 위험 요소

**높은 위험** (Phase 1-2 금지):
- AI 간 자율 토론 루프
- 예측 불가능한 코드 변경
- 비용 폭발
- RAG drifting

**중간 위험** (Phase 3 신중 접근):
- 자동 merge 오류
- 테스트 커버리지 부족
- 컨텍스트 손실

**낮은 위험** (허용):
- 코드 스타일 자동 수정
- 문서 자동 생성
- 간단한 리팩토링 제안

### 17.3 위험 완화 전략

1. **단계적 확장**: Phase별 엄격한 Gate 기준
2. **롤백 메커니즘**: 즉시 이전 상태 복구
3. **Emergency kill-switch**: 전체 자동화 중단
4. **감사 로그**: 모든 AI 행동 추적
5. **사람 승인**: 중요 결정은 항상 사람이

---

## 18. 템플릿 사용 가이드

### 18.1 새 프로젝트 시작

```bash
# Option 1: NPM
npx ai-collab-starter init my-project

# Option 2: Python
python scripts/init_ai_project.py
```

**자동 설정**:
- Git 초기화
- 기본 디렉토리 구조 생성
- AI 팀 구성 파일 생성
- 첫 커밋 자동 생성

### 18.2 기존 프로젝트에 적용

```bash
python scripts/apply_ai_collab.py /path/to/existing-project
```

**주입되는 항목**:
- `ai/` 디렉토리 전체
- `.github/workflows/` AI 관련 workflows
- `.github/AI_PROMPTS/`
- `docs/CONTEXT/` 구조

### 18.3 설정 커스터마이징

**필수 설정**:
1. `.github/ai_team.yml` - AI 팀 구성
2. `.ai/config.yml` - 프로젝트별 설정
3. `.ai/budget.json` - 예산 한도
4. GitHub Secrets - API keys

**선택 설정**:
- Slack webhook (알림용)
- Custom prompts (프로젝트 특화)
- 민감 경로 추가

---

## 19. 성공 사례 및 예시

### 19.1 예상 시나리오

**시나리오: 개인 소장품 경매앱 개발**

1. **Phase 1 적용**:
   - Claude: PRD 작성, 경매 로직 검토
   - Gemini: UI/UX 설계, 입찰 화면 프로토타입
   - Perplexity: 전자상거래법 검토
   - GPT: 백엔드 API 설계

2. **협업 효과**:
   - Claude가 경매 종료 로직의 경계조건 지적
   - Gemini가 입찰 버튼 UX 개선 제안
   - Perplexity가 법적 고지사항 누락 발견
   - GPT가 Redis Streams 기반 스케줄러 제안

3. **결과**:
   - 4가지 관점의 종합적 리뷰
   - 법적 리스크 사전 차단
   - 아키텍처 최적화
   - 개발 시간 단축

---

## 20. FAQ

### Q1: 모든 PR에 AI 리뷰가 필요한가요?

**A**: 기본적으로 모든 PR에 적용되지만, `.ai/config.yml`에서 특정 경로를 제외할 수 있습니다.

### Q2: 비용이 너무 높으면 어떻게 하나요?

**A**: Lite 모드로 전환하거나, `.ai/budget.json`에서 한도를 설정하여 자동 제어할 수 있습니다.

### Q3: AI의 제안을 거부하면 어떻게 되나요?

**A**: 아무 문제 없습니다. AI는 제안만 하고, 최종 결정은 항상 사람이 합니다. 거부율은 메트릭으로 추적됩니다.

### Q4: Phase 4는 언제 적용하나요?

**A**: Phase 3의 모든 Gate 기준을 충족하고, 90일간 안정적으로 운영된 후에만 고려합니다. 매우 신중하게 접근합니다.

### Q5: 소규모 팀도 사용 가능한가요?

**A**: 네. Lite 모드는 1인 개발자도 사용 가능하도록 설계되었습니다.

---

## 21. 결론

**AI-Collab-Starter**는 단순한 자동화 도구가 아닌, **AI를 조직처럼 운영하는 협업 시스템**입니다.

**핵심 가치**:
1. 통제 가능한 자동화
2. 다중 관점의 품질 검증
3. 단계적이고 안전한 확장
4. 투명하고 감사 가능한 프로세스

**원칙**:
- 사람이 최종 책임을 진다
- AI는 제안하고, 사람이 결정한다
- 안전이 속도보다 우선한다

**비전**:
여러 AI가 협업하여 1인 개발자도 엔터프라이즈급 품질의 소프트웨어를 개발할 수 있는 환경을 제공합니다.

---

마지막 업데이트: 2026-01-15
버전: 1.0 (GPT 대화 반영)
