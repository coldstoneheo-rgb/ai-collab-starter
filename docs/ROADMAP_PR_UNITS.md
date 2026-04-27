# AI-Collab-Starter 권장 개발 로드맵 (PR 단위)

기준일: 2026-04-23  
우선순위: 안정성 > 비용 > 유지보수 > 기능 확장

## 0. 전제

- 한 PR은 한 목적만 가진다.
- AGENTS.md/PRD.md 계약을 먼저 맞춘 뒤 기능을 추가한다.
- 민감 경로(`infra/`, `db/`, `security/`, `.github/workflows/`) 변경은 별도 PR로 분리한다.

## 1. 즉시 수행 (P0)

### PR-001 문서 무결성 복구
- 목적: 절단/오염된 문서를 정상화한다.
- 변경:
  - `README.md` 완성
  - `docs/AI_COLLAB_GUIDE.md` 정식 본문 복구
  - 문서의 프롬프트 파일명/실행 경로를 현재 코드와 일치시킴
- 완료 기준:
  - 두 문서가 끝까지 닫힌 Markdown 구조
  - 빠른 시작 명령이 실제 경로와 일치

### PR-002 워크플로우 실패 위장 제거
- 목적: CI 신뢰도를 확보한다.
- 변경:
  - `.github/workflows/ai_review.yml`의 `|| echo` 제거
  - 실패 시 명확히 실패하도록 step exit 코드 정리
  - `$GITHUB_OUTPUT` 표준 echo 형식으로 정리
- 완료 기준:
  - runner 오류 시 workflow 실패
  - router 출력 파싱 오류가 즉시 감지

### PR-003 mode_map/workflow 동기화
- 목적: router 계약과 실행 파이프라인 정합성 확보
- 변경:
  - `ai/plugins/mode_map.py`와 workflow job 목록 일치
  - 미구현 agent(`gpt`)를 임시 제외하거나 gpt runner/job을 최소 구현
- 완료 기준:
  - `enabled_agents`에 포함된 agent는 모두 실행 가능
  - 포함되지 않은 agent는 workflow에서 참조되지 않음

## 2. 단기 안정화 (P1)

### PR-004 러너 경로/프롬프트 버전 정합성
- 목적: 즉시 실패하는 runner를 복구한다.
- 변경:
  - `run_gemini_review.py`, `run_perplexity_review.py`, `run_autofix.py`가 `_v1` 프롬프트를 사용하도록 수정
  - 공통 `prompt_loader` 사용으로 파일명 하드코딩 제거
- 완료 기준:
  - 로컬 dry-run에서 파일 미존재 에러 0건

### PR-005 테스트 실행성 복구
- 목적: 개발/CI에서 테스트 수집 실패를 없앤다.
- 변경:
  - `PYTHONPATH` 문제를 해결(패키징 or pytest 설정)
  - optional dependency 없는 환경에서도 collection 실패하지 않도록 mock/skip 처리
  - `pr_collector` import 시 `sys.exit()` 제거
- 완료 기준:
  - `pytest -q`가 수집 단계 통과
  - 외부 API 키 없이도 단위 테스트 실행 가능

### PR-006 비용 가드 하드닝
- 목적: 예산 초과 시 안전 중단을 강제한다.
- 변경:
  - budget 초과 하드 스탑
  - 80% 초과 시 enterprise 차단
  - 동일 PR 재시도 횟수 제한(1회)
- 완료 기준:
  - 비용 임계치 시나리오 테스트 통과
  - 비용 계산 실패 시 보수적 중단 동작

## 3. 중기 운영화 (P2)

### PR-007 관측성 최소 세트
- 목적: 운영 판단에 필요한 최소 지표를 고정한다.
- 변경:
  - 로그 스키마 통일(`agent`, `tokens`, `cost`, `decision_reason`)
  - 실패/비용/민감경로 이벤트를 별도 태그로 기록
  - 일간 요약 리포트 스크립트 추가
- 완료 기준:
  - 최근 7일 비용/실패율/평균 처리시간 확인 가능

### PR-008 보안/민감경로 차단 정책 고정
- 목적: 고위험 변경의 자동행동을 완전히 차단한다.
- 변경:
  - 민감경로 감지 시 autofix/auto actions 차단
  - manual approval required 메시지 표준화
- 완료 기준:
  - 민감경로 PR에서 자동패치 미생성
  - 차단 사유가 PR 코멘트로 남음

## 4. 단계 전환 게이트 (P3 진입 전)

- 최근 50 PR 기준 workflow 성공률 95% 이상
- 최근 30 PR 기준 human override 30% 이하
- PR당 평균 비용 $1 이하
- 감사 로그 100건 이상, 필수 필드 누락 0건

위 기준을 만족하지 못하면 자동화 확대(PR-009 이후)는 진행하지 않는다.

## 5. 보류/금지 항목

- AI-to-AI 릴레이 토론 자동화
- push 기반 autofix commit/push
- 사람 승인 없는 자동 merge
- 자동 패키지 매니저
- serverless hyper-router 도입

이 항목들은 연구 트랙으로만 관리하며 운영 트랙에서는 구현하지 않는다.
