## 1. 프로젝트 정의 (명확화)

**AI-Collab-Starter**는  
“AI가 코드를 대신 짜주는 도구”가 아니라,

> **여러 AI를 ‘조직 구조’처럼 배치하고,  
> 사람이 최종 책임을 지는 GitHub 기반 AI 협업 개발 시스템**이다.

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
