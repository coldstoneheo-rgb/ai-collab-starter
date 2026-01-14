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

“보통 이렇게 합니다” ❌