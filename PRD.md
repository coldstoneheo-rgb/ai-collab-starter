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

## 3. 시스템 아키텍처 (강화)

### 3.1 단일 책임 규칙 (SRP, 변경 불가)

|레이어|책임|금지|
|---|---|---|
|router|**결정**|실행 ❌|
|plugin|정보 수집|판단 ❌|
|workflow|실행|결정 ❌|
|runner|API 호출|정책 ❌|

> 이 규칙을 어기면 **PR 즉시 중단**

---

## 4. Router 결정 계약 (Contract)

Router는 항상 다음 **계약된 출력**만 낸다.

`{   "mode": "lite | pro | enterprise",   "enabled_agents": ["claude", "gemini", "perplexity"],   "autofix_allowed": false }`

### 절대 규칙

- 출력 키 이름 변경 ❌
    
- 조건부 출력 ❌
    
- workflow에서 재해석 ❌
    

---

## 5. 민감 경로 정책 (강화)

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

## 6. GitHub 운영 정책 (PRD에 명시)

### 필수 조건

- `main` 브랜치 보호 필수
    
    - force push ❌
        
    - direct push ❌
        
    - PR + 1 human review 필수
        

> **브랜치 보호 없이는 Phase 1 완료 선언 불가**

---

## 7. Phase 1 완료 기준 (Gate, 재정의)

Phase 1은 아래 **모두** 만족해야 종료된다.

1. router job이 항상 실행됨
    
2. workflow가 router outputs를 소비함
    
3. 민감 경로 PR에서 enterprise 강제 로그 확인
    
4. autofix 관련 workflow 전부 비활성화
    
5. main 브랜치 보호 설정 완료