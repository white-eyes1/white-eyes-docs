# 심각도: FNC-S-001 캠 시작

> flask 이슈 #1(FNC-S-001 캠 시작)을 구현하면서 확인한 문제와 심각도(2026-10-19). 코드는 white-eyes-flask PR #24다.
> 심각도 기준은 1차 검수(severity.md)와 같다. 상 = 개발을 시작하기 전에 꼭 해결 / 중 = 곧 해결 / 하 = 정리 수준.
> 이 기능에서 '상'으로 본 항목은 없다. 중·하도 빠짐없이 적는다.
> 해결되면 상태를 '해결'로 바꾸고 PR 번호를 적는다. 기록은 지우지 않는다. 등급은 구현한 쪽의 판단이고 PM 확인이 필요하다.

## 요약
| 심각도 | 건수 |
|---|---|
| 상 | 0 |
| 중 | 8 |
| 하 | 4 |

## 중
| 번호 | 항목 | 이유 | 조치 | 상태 |
|---|---|---|---|---|
| 중-1 | 내부 토큰 환경변수 이름이 다르다. flask는 `INTERNAL_TOKEN`, docs와 spring은 `INTERNAL_API_TOKEN` | spring과 연결할 때 이름을 틀리면 flask가 토큰을 못 읽어 모든 요청이 401이 된다(1차 검수 중-1) | docs 기준으로 flask를 `INTERNAL_API_TOKEN`으로 통일. PM 결정 | 열림 |
| 중-2 | 입력 검증 오류 코드가 다르다. flask `INVALID_REQUEST`, spring 공통 오류 처리 `INVALID_INPUT` | 같은 종류의 오류 코드가 둘이 된다 | 통일하면 flask 코드, 테스트, docs를 함께 고친다. PM 결정 | 열림 |
| 중-3 | flask 401 응답 본문이 `{"error": "UNAUTHORIZED"}`라 공통 오류 형식 `{code, message}`와 다르다(기존 코드) | 호출하는 쪽이 오류를 같은 방식으로 읽을 수 없다(1차 검수 중-3) | 분석 서버 오류 형식을 docs에서 먼저 정한다. PM 결정 | 열림 |
| 중-4 | 영문이 아닌 문자가 든 `X-Internal-Token` 헤더가 오면 `hmac.compare_digest`가 `TypeError`를 내 500이 된다(기존 코드) | 잘못된 헤더 하나로 401이 아니라 500이 나간다(1차 검수 중-8) | bytes로 비교하고 테스트를 더한다. 별도 작은 PR | 열림 |
| 중-5 | Black, isort, `.editorconfig` 설정과 CI 형식 검사가 flask 저장소에 없다 | code-conventions.md가 요구하지만 사람이 직접 지켜야 한다. 이번에도 로컬에서만 돌렸다(1차 검수 상-2의 남은 부분) | 설정을 추가하고 CI에 연결. 별도 이슈 | 열림 |
| 중-6 | docs package-structure.md는 `analyzer/` 구조인데 실제 코드와 flask CLAUDE.md는 `src/white_eyes_flask/`다 | 다음 사람이 어느 쪽을 따를지 헷갈린다(1차 검수 중-4) | 실제 구조에 맞춰 docs를 고친다. PM 결정 | 열림 |
| 중-7 | 분석 서버를 WSGI 워커 1개(단일 프로세스)로 돌린다는 전제다 | 워커가 여러 개면 "캠당 스레드 1개"가 보장되지 않는다 | 배포 전제를 docs에 적거나 작업 소유권을 조정한다. PM 결정 | 열림 |
| 중-8 | api/analyzer.md start에 새 오류 응답(400 INVALID_REQUEST, 501 SOURCE_TYPE_NOT_SUPPORTED)을 더했는데, 규칙상 spring과 같은 시점에 고쳐야 하는 API 계약 변경이다 | docs CLAUDE.md '고칠 때 함께 바꿀 문서' 표. spring 쪽 호출 코드는 아직 이 응답을 다루지 않는다 | spring 담당과 처리 방식을 정한다(정상 흐름에서는 나오지 않음) | 열림 |

## 하
| 번호 | 항목 | 이유 | 조치 | 상태 |
|---|---|---|---|---|
| 하-1 | 겪은 문제를 `docs/troubleshooting`에 기록하지 않았다 | PR 템플릿의 확인 항목이다. 예: uv가 `.python-version`의 3.12.15를 몰라 `--python 3.12`로 우회 | 기록 파일을 남긴다 | 열림 |
| 하-2 | `shutdown()`과 `start()`의 경쟁, `CameraJob.status` 동시 접근 | 지금은 호출하는 코드가 없어 문제가 되지 않는다. 준비·재생(이슈 #6, #7)과 운영 종료 절차를 만들 때 문제가 된다 | 그때 함께 처리 | 미룸 |
| 하-3 | 심볼릭 링크 차단 테스트가 윈도우에서 건너뛰어진다. 서버를 실제로 띄워 호출해 보지 않았다 | 리눅스 CI에서 도는지 확인하지 못했다 | PR #24의 Checks에서 확인 | 확인 필요 |
| 하-4 | DUMMY에서 `RUNNING`이 아직 나오지 않는다(캐시 확인이 자리표시) | 캐시는 FNC-S-009(이슈 #6) 범위다 | #6에서 구현 | 열림 |

## 해결한 것
- 리뷰(Gemini, Codex)에서 나온 `sourceType`이 배열이면 500, 이미 도는 캠에 LIVE 요청이 오면 501, 링크로 공유 폴더 밖 파일 허용, `fieldErrors` 누락은 재현 테스트를 먼저 만들고 고쳤다(PR #24).
