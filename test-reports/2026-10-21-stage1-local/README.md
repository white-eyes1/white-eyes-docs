# 1단계 흐름 로컬 확인 — 2026-10-21

1단계 기능(decisions/0011)이 모두 머지된 뒤, 세 앱을 로컬 docker로 띄워 1단계 흐름을 실제로 따라가 보고 명세와 비교했다.

## 요약
- **로그인부터 정지까지 1단계 흐름은 끝까지 동작한다.** 확인한 기능은 명세의 처리 순서·예외 처리와 맞았다.
- **지금 dev만으로는 사람이 이 흐름을 따라갈 수 없다.** 첫 로그인에서 막히고, 화면이 없어 POST API를 부를 방법이 없다. 시험에서는 두 곳을 저장소 밖에서 우회했다(아래 '시험 환경').
- 새로 다뤄야 할 문제 2건은 이슈로 만들었다: white-eyes-flask [#43](https://github.com/white-eyes1/white-eyes-flask/issues/43)(유입/유출 쏠림), [#44](https://github.com/white-eyes1/white-eyes-flask/issues/44)(분석 서버 로그 설정 없음).

## 시험 대상
| 저장소 | 브랜치 | 커밋 |
|---|---|---|
| white-eyes-spring | dev | `29ef132` (PR #135 머지) |
| white-eyes-flask | dev | `ef787c4` (PR #42 머지) |
| white-eyes-docs | main | `44e23a1` (PR #30 머지) |

## 시험 환경
- 저장소에 Dockerfile이 없어 시험용 compose를 저장소 밖에 따로 만들었다. 코드는 바꾸지 않았다.
  - MySQL 8.4(`--default-time-zone=+09:00`)
  - 관리자 앱·사용자 앱: `./gradlew bootJar`로 만든 jar를 `eclipse-temurin:17-jre`에서 `local` 프로필로 실행
  - 분석 서버: `python:3.12-slim` + `uv sync --frozen --no-dev`
  - 컨테이너 사이 주소: `ANALYZER_BASE_URL=http://flask:5000`, `ADMIN_INTERNAL_BASE_URL=http://admin:8082/admin`
- 분석 설정: `DETECTOR=visdrone`(white-eyes-flask README의 가중치, 해시 일치), `DETECT_IMGSZ=640`(분석 속도 때문에 기본 960에서 낮춤), `ANALYZE_FPS=5`, `EDGE_MARGIN_RATIO=0.05`
- 더미 영상: white-eyes-assets `drone-vids-v1`에서 3개(아래 영상 A·B·C). 출처·라이선스 미확인이라 파일 이름과 내용은 이 문서에 싣지 않는다.
- 행정구역: [vuski/admdongkor](https://github.com/vuski/admdongkor) `ver20261001`에서 대전 중구(`25020`) 읍·면·동 17개만 잘라 적재(decisions/0014). 출처: 통계청(SGIS), vuski/admdongkor, CC BY 4.0
- 호출 방법: curl. 로그인은 `/admin/login` 폼, 그 뒤 API는 세션 쿠키 + `X-CSRF-TOKEN` 헤더
- **시험용 우회 2가지(저장소 코드 아님)**
  1. 최고 관리자의 `admin_account.must_change_password`를 DB에서 0으로 바꿈(문제 1)
  2. 로그인한 세션의 CSRF 토큰만 돌려주는 시험용 컨트롤러(`GET /admin/e2e/csrf`)를 따로 컴파일해 `-Dloader.path`로 붙임(문제 2)

## 흐름과 결과
| 순서 | 기능 | 한 일 | 결과 |
|---|---|---|---|
| 1 | FNC-A-012 행정구역 적재 | `--job=load-regions` 두 번 실행 | 시·도 1, 시·군·구 1, 읍·면·동 17. 두 번째 실행 뒤에도 19행(중복 없음), 상위 연결 맞음 ✅ |
| 2 | FNC-A-001 최고 관리자 | 첫 실행, 다른 인스턴스로 재시작 | 한 번만 등록, 재시작 때 "이미 있어 등록하지 않음" ✅ |
| 3 | FNC-C-001 로그인 | 맞는·틀린 비밀번호 | 틀리면 `/login?error` + 공통 문구. 맞으면 `/me/password`로 이동(문제 1) |
| 4 | FNC-C-003·027 권한·오류 | 비로그인, CSRF 없음, 포트·토큰 | 비로그인 API 401·화면 302 → /login, CSRF 없는 POST 403, 8081의 `/internal/**` 404, 8082 토큰 틀림 401, 분석 서버 토큰 없음 401 ✅ |
| 5 | FNC-C-008 지역·구역 목록 | `/api/v1/regions`(3단계), `/api/v1/zones` | 시·도 → 시·군·구 → 읍·면·동 17개, 구역 목록·hasCamera 맞음 ✅ |
| 6 | FNC-A-013·014 구역 | 미리보기, 등록, 중복, 서비스 지역 밖 | 면적 2974㎡(손계산 약 2986㎡), 소속 동 맞음, 409 `DUPLICATE_ZONE_NAME`, 400 `OUT_OF_SERVICE_AREA` ✅ |
| 7 | FNC-A-018 캠 등록 | 정상, 없는 구역, 구역당 2대, 주소 규칙 | 201(STOPPED), 404 `ZONE_NOT_FOUND`, 409 `ZONE_HAS_CAMERA`, 주소 규칙 위반 400(`/etc/passwd`, `..`, `.avi`, LIVE에 http). 명세 처리 순서(구역 → 캠 → 주소)대로 검사 ✅ |
| 8 | FNC-A-020 캠 가동 | 영상 A 가동, 없는 파일, 가동 중 다시 가동 | **PREPARING → RUNNING 전환(검수 기준)**, 진행률 10 → 45 → 85, 없는 파일 422 `SOURCE_NOT_FOUND` + ERROR·'영상 파일·스트림 없음'·run_requested 유지, 가동 중 409 `INVALID_STATUS` ✅ |
| 9 | FNC-S-001~006·009·010 분석 서버 | 더미 분석 준비 → 1초 결과 전송 → 반복 재생 | 캐시·좌표 파일 생성, 결과 전송, 반복(약 22초)마다 녹화 등록, 다음 반복이 이전 녹화를 닫음 ✅ (유입/유출 수는 문제 3) |
| 10 | FNC-A-024·028 결과 수신·1분 통계 | 2분 이상 가동 | 매분 `zone_stat_minute` 1행, `sample_sec` 60, 첫 분은 받은 초만(41) ✅ |
| 11 | FNC-C-009 지도 혼잡 단계 | `/api/v1/map/status`(동·구·ZONE) | 구역 값, 통계 없는 구역 null, 동 값 = 통계 있는 구역의 인원 합 ÷ 면적 합(84.42 + 11.80 = 96.22, 0.0304) ✅ |
| 12 | FNC-C-016 대시보드 요약 | ZONE·동·구·시·도 | 인원·밀집도·유입/유출·주요 방향·캠 수·오늘 최대 인원이 통계와 맞음 ✅ |
| 13 | FNC-C-025 혼잡 단계 기준 | `THRESHOLD_*`를 0.03·0.05로 낮춘 인스턴스 | `/meta/levels` 반영, 0.0284 정상·0.0304 주의·0.0610 위험 ✅ |
| 14 | FNC-A-021 캠 정지 | 가동 중 정지, 준비 중 정지, 분석 서버가 꺼진 상태 | STOPPED·run_requested=0, 마지막 녹화 ended_at 닫힘, **준비 중 정지 시 준비 취소(캐시 안 생김, 검수 기준)**, 분석 서버가 꺼져 있으면 200 + '분석 서버에 전달 실패' ✅ |
| 15 | FNC-A-020 분석 서버 연결 실패 | 분석 서버를 멈추고 가동 | 502 `ANALYZER_UNAVAILABLE`, ERROR·'분석 서버 연결 실패', run_requested=1 유지 ✅ |
| 16 | 다시 가동 | 정지했던 캠 다시 가동 | 캐시가 있어 바로 RUNNING ✅ |
| 17 | FNC-C-026 작업 기록 | 위 작업 전체 | 구역·캠 등록(`*_CHANGE` CREATE), 가동·정지(`CAMERA_RUN` START/STOP) 기록 ✅ |

## 발견한 문제

### 1. 첫 로그인이 비밀번호 변경 화면에 갇힘 — 다른 이슈에서 해결
최고 관리자는 첫 로그인 때 `/me/password`로 이동한다. 그런데 이 화면(FNC-C-007)은 2단계라 404이고, 그 사이 다른 API는 모두 403이다. 1단계는 "관리자 앱 로그인으로 흐름을 확인한다"(0011)고 했으므로, 지금은 DB를 고치지 않으면 누구도 1단계 흐름을 확인할 수 없다.
- 해결 이슈: white-eyes-spring [#24](https://github.com/white-eyes1/white-eyes-spring/issues/24) (2단계, 미배정). 2단계에서 먼저 처리하는 것이 좋다.

### 2. 화면이 없어 POST API를 부를 수 없음 — 다른 이슈에서 해결
CSRF 토큰은 화면의 meta 태그로 받는다(conventions.md 'CSRF'). 그런데 관리자 앱 화면은 로그인 하나뿐이어서, 로그인 뒤 토큰을 받을 곳이 없다. 구역·캠 등록, 가동·정지를 실제 클라이언트로 부를 수 없다.
- 0011의 1단계 기준은 "… → 지도·대시보드 표시"인데, 지금 구현은 API까지다.
- 해결: 2단계 화면 이슈들

### 3. 더미 분석의 유입/유출이 한쪽으로 크게 쏠림 — 새 이슈 flask #43
- 영상 A(21.7초) 캐시 합계: **유입 23, 유출 161**. 같은 시간 인원은 69~103명(평균 약 85)으로 거의 그대로다. 1분 통계로는 1분마다 유입 약 60, 유출 약 440이 쌓였고, 마지막 초에만 유출 24건이 몰렸다.
- 영상 B는 반대로 1분에 유입 54, 유출 4였다.
- overview.md 알려진 한계 17은 "실제보다 적게"라고 적었지만, 이 결과는 실제보다 훨씬 많다.
- 원인 후보(추정): 가장자리에서 늦게 탐지된 사람은 유입으로 세지 않고 유출만 셈, 추적 번호가 바뀐 사람의 유출, 영상 끝에서 남은 유출을 반복 재생마다 다시 더함.

### 4. 분석 서버 로그가 나오지 않음 — 새 이슈 flask #44
`create_app()`에 로그 설정(`dictConfig`)이 없다. 그래서 WARNING 이상만 형식 없이 나오고, INFO(캠 가동·정지·상태 변경 등)는 나오지 않는다. 가동 중 컨테이너 로그에는 werkzeug 접속 로그만 있었다(code-conventions.md 7-5).

### 5. 사용자 앱 통계 API가 로그인 없이 열림 — 다른 이슈에서 해결
사용자 앱(8080)의 `/api/v1/map/status`, `/api/v1/dashboard/summary`, `/api/v1/zones`, `/api/v1/meta/levels`가 로그인 없이 200을 준다. 명세는 '사용자 이상'이다. 사용자 앱에 로그인 처리가 아직 없기 때문이다.
- 해결 이슈: white-eyes-spring #122(첫 SecurityFilterChain), #126(사용자 앱 로그인). 머지 뒤 다시 확인한다.

### 6. 분석 서버 재시작 뒤 캠이 RUNNING인 채로 멈춤 — 다른 이슈에서 해결
분석 서버를 껐다 켜면 가동 중이던 캠은 관리자 앱에서 계속 RUNNING이지만 통계는 끊긴다(1단계 범위에서는 예상된 동작).
- 해결 이슈: white-eyes-flask [#11](https://github.com/white-eyes1/white-eyes-flask/issues/11)(FNC-S-012 재시작 복구), white-eyes-spring [#36](https://github.com/white-eyes1/white-eyes-spring/issues/36)(FNC-A-027 가동 대상 캠 목록), FNC-A-035(캠 이상 감지, 2단계)

### 7. 작은 차이(코드 정리 때 함께 봄)
- 이미 정지한 캠을 다시 정지해도 200이고 작업 기록이 한 번 더 남는다(명세에 정한 것 없음).
- 8082 포트에서 `/internal/**` 밖의 경로는 공통 오류 형식이 아니라 Spring 기본 오류 JSON으로 404가 난다.
- 같은 값의 표기가 응답마다 다르다: `areaM2`(등록 응답 2974.0 / 구역 목록 2974.00), `progress`(등록 응답 0 / 캠 목록 null).
- 관리자 앱 `/actuator/health`도 로그인을 요구한다(사용자 앱은 공개). 명세에 정한 것 없음.

## 확인하지 않은 것
- 실제 화면(없음), 라이브 캠(FNC-S-007·008, 2단계), 이벤트(FNC-A-033~035, 2단계), 실시간 갱신(SSE, 2단계)
- 탐지 정확도(decisions/0015에서 따로 측정), 기본 입력 크기 960
- 자정·날짜를 넘기는 경우, 오래 가동하는 경우, 여러 관리자의 동시 작업
