# 화면 시안(design)

screens.md의 화면(SCR-…)마다 모양을 정한 시안이다. **동작·데이터·예외 처리는 명세(screens.md, features/, api/)가 기준이고, 이 폴더는 모양(배치·색·간격·문구)의 기준이다.** 둘이 다르면 명세를 따르고, 시안을 고치는 PR을 올린다.

## 폴더
| 경로 | 내용 | 누가 보나 |
|---|---|---|
| `screens/*.html` | 화면마다 하나. 브라우저에서 바로 열리는 정적 HTML(`../we.css`를 씀) | 구현할 때 읽는 파일 |
| `png/*.png` | 같은 화면의 캡처 | 사람이 GitHub에서 보기, PR에서 구현 결과와 나란히 비교 |
| `we.css` | 공통 색·글꼴·버튼·입력·칩·표·모달 스타일 | 공통 틀(spring #136)이 `common/static/css`로 옮김 |
| `src/*.dc.html` | 시안 원본(캔버스 형식). 시안을 고칠 때만 씀 | 시안 수정자 |
| `tools/export_design.py` | `src/` → `screens/`·`png/` 다시 만들기 | 시안 수정자 |

보기용 캔버스: https://claude.ai/artifact/SQiTRLBomKU8oxuxDLvaaM (사람이 훑어보는 용도. AI 도구는 원문을 못 읽으므로 이 폴더를 본다)

## 시안 읽는 법
- **`data-api` 속성**: 그 요소에 들어갈 값을 주는 API와 필드. 예: `data-api="GET /api/v1/dashboard/summary → countAvg,density,…"`. 구현에서는 이 속성을 옮기지 않는다.
- **`data-fnc` 속성**: 그 요소가 속한 기능 ID. 이 기능의 이슈에서 이 요소를 만든다. `(2단계)`처럼 단계가 붙으면 그 단계의 이슈 몫이다.
- **`.anno` 요소(보라 점선 테두리)**: 시안 표시용. 다른 단계 기능의 자리, 구현 안내다. **실제 화면에는 만들지 않는다**(자리만 비워 두거나 그 단계에 만든다).
- **값은 모두 예시**다. 이름·숫자·시각은 가짜이고, `[메일 주소]`처럼 대괄호는 자리 표시다.
- **지도·그래프·영상은 자리 그림**이다. 지도는 Leaflet + OSM(`map/` 모듈), 그래프는 Chart.js(`chart/` 모듈), 영상은 `<video>`/MJPEG로 구현한다. 시안의 SVG를 옮기지 않는다.
- **반복 행이 있는 표**는 시안에서 `div` grid(`.dtable`)로 그렸다. 구현은 `<table>` + `th:each`로 해도 된다(열 순서·내용만 맞춘다).
- 화면 폭은 1440px 기준이다(창·모달은 그 크기).

## 화면 ↔ 파일
| 화면 | 파일 | 단계 | 비고 |
|---|---|---|---|
| 공통 틀 | `_common-styleguide.html` | 1 | spring #136 |
| SCR-A-013 관리자 공통 헤더 | `SCR-A-013-admin-header.html` | 1(배지·토스트 2) | spring #136 |
| SCR-U-004 사용자 공통 헤더 | `SCR-U-004-user-header.html` | 2 | |
| SCR-C-001 로그인 | `SCR-C-001-login.html`(관리자 앱, 오류 상태), `SCR-C-001-login-user-app.html`(사용자 앱, 가입 완료 안내 상태) | 1·2 | |
| SCR-C-002 비밀번호 변경(강제) | `SCR-C-002-password-forced.html` | 2 | spring #24 |
| SCR-C-003 통계 메인 | `SCR-C-003-dashboard.html`(캠 패널 접힘), `SCR-C-003-dashboard-deck-expanded.html`(펼침), `SCR-C-003-stats-panel-all.html`(통계 패널 모두 펼침) | 1 + 2·3 | spring #139, #140. 캠 카드 그래프는 결정 0016이 우선(시안 갱신 전, docs #119) |
| SCR-C-004 통계 그래프 | `SCR-C-004-graph.html` | 2·3 | 그래프 4칸·색은 결정 0016이 우선(시안 갱신 전, docs #119) |
| SCR-C-005 기간 비교 분석 | (삭제, 결정 0016) | - | |
| SCR-C-006 엑셀 다운로드 창 | `SCR-C-006-excel.html` | 2 | |
| SCR-U-001 회원가입 | `SCR-U-001-signup.html` | 2 | |
| SCR-U-002 승인 대기 | `SCR-U-002-pending.html` | 2 | |
| SCR-U-003 회원 탈퇴 창 | `SCR-U-003-withdraw.html` | 3 | |
| SCR-A-001 사용자 관리 | `SCR-A-001-users.html` | 2·3 | |
| SCR-A-002 사용자 상세 창 | `SCR-A-002-user-detail.html` | 3 | |
| SCR-A-003 관리자 관리 | `SCR-A-003-admins.html` | 2·3 | |
| SCR-A-004 구역 관리 | `SCR-A-004-zones.html` | 1(이웃 2, 수정·삭제 3) | spring #137 |
| SCR-A-005 구역 이웃 설정 창 | `SCR-A-005-zone-neighbors.html` | 2 | |
| SCR-A-006 캠 관리 | `SCR-A-006-cameras.html` | 1(실시간 보기 2, 수정·삭제 3) | spring #138 |
| SCR-A-007 캠 등록·수정 창 | `SCR-A-007-camera-form.html`(주소 규칙 오류 상태) | 1(수정 3) | spring #138 |
| SCR-A-008 실시간 보기 창 | `SCR-A-008-live-view.html` | 2 | 영상 아래 그래프·배치는 결정 0016이 우선(시안 갱신 전, docs #119) |
| SCR-A-009 다시보기 | `SCR-A-009-playback.html` | 2 | 통계 시간축(repfocus-005) |
| SCR-A-010 이벤트 로그 | `SCR-A-010-events.html` | 2 | |
| SCR-A-011 이벤트 상세 창 | `SCR-A-011-event-detail.html`, `SCR-A-011-action.html`(조치 완료 창) | 2 | |
| SCR-A-012 작업 기록 | `SCR-A-012-history.html` | 3 | |

## 상태가 시안에 없는 경우
시안은 화면마다 대표 상태 하나(일부는 두 개)만 그렸다. 빈 목록·로딩·오류·권한 없음 같은 다른 상태는 screens.md의 '유효성/예외 처리' 칸을 따르고, 모양은 `_common-styleguide.html`의 컴포넌트(칩·입력 오류·토스트)를 쓴다.

## 시안을 고칠 때
1. `src/*.dc.html`을 고친다(캔버스에서 고쳤다면 캔버스 파일을 받아 `src/`에 덮어쓴다).
2. `screens/`·`png/`를 다시 만든다(Playwright Chromium 필요).
   ```bash
   python tools/export_design.py src .
   ```
3. 명세와 함께 바뀌면 screens.md도 같은 PR에서 고친다.
