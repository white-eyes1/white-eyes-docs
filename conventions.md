# 설정·규약

> 원본: 명세서 시트 '설정·규약'에서 옮김. 이후로는 이 파일이 원본이다.


> 설정·규약 (개발 공통 기준: 모든 기능 명세서가 이 시트를 참조함)

## 모듈·포트

| 항목 | 값/규칙 | 설명 |
|---|---|---|
| 사용자 앱(user) | Spring Boot, 포트 8080, 컨텍스트 경로 / | 외부 공개. nginx가 / 이하 요청을 전달 |
| 관리자 앱(admin) | Spring Boot, 웹 포트 8081(컨텍스트 경로 /admin), 내부 통신 포트 8082 | 8082에는 /internal/** 만 연결하고 내부 토큰으로 확인. 포트별 접근 제한(VM별 방화벽)은 2순위 |
| 공통 모듈(common) | Gradle 모듈, 단독 실행 없음 | 엔티티·리포지토리·통계 조회·공통 화면(Thymeleaf 템플릿·정적 파일)·작업 기록 저장·예외 처리·보안 공통 설정 |
| 분석 서버(analyzer) | Flask, 포트 5000, 경로 /analyzer/v1/** | 관리자 앱(시작·정지 지시)과 웹 서버(실시간 화면)만 접근 |
| 웹 서버(nginx) | 포트 80 | 외부에서 접근 가능한 유일한 입구 |
| DB | MySQL 8, 포트 3306, 문자셋 utf8mb4, 시간대 Asia/Seoul | 사용자 앱·관리자 앱만 접근 |
| 공유 스토리지 | NFS v4, 포트 2049, 내보내기 /srv/media(영상), /srv/backup(DB 백업) | 분석 서버: /srv/media 읽기·쓰기 / 웹 서버: /srv/media 읽기 전용 / DB 서버: /srv/backup 읽기·쓰기 |

## nginx 경로 규칙

| 항목 | 값/규칙 | 설명 |
|---|---|---|
| / | 사용자 앱(8080)으로 전달 | - |
| /admin/ | 관리자 앱(8081)으로 전달 | 관리자 앱 경로 IP 제한은 2순위(외부 도메인 적용 시) |
| /admin/live/{cameraId} | auth_request로 관리자 앱 GET /admin/api/v1/live/auth?cameraId={cameraId} 확인 → 204면 분석 서버 /analyzer/v1/cameras/{cameraId}/live 로 전달 | proxy_buffering off(스트림). 분석 서버로 보낼 때 X-Internal-Token 헤더를 붙임 |
| /admin/live/{cameraId}/snapshot | auth_request로 관리자 앱 GET /admin/api/v1/live/auth?cameraId={cameraId} 확인 → 204면 분석 서버 /analyzer/v1/cameras/{cameraId}/snapshot 으로 전달 | /admin/live/{cameraId} 규칙보다 먼저 맞도록 둠. 요청마다 권한 확인, 캐시하지 않음. 분석 서버로 보낼 때 X-Internal-Token 헤더를 붙임 |
| SSE: /api/v1/stats/stream, /admin/api/v1/stats/stream, /admin/api/v1/notifications/stream | 해당 앱으로 전달(/ · /admin/ 규칙보다 먼저 맞도록 정확히 일치하는 location) | proxy_buffering off, proxy_read_timeout 1h(앱이 30초마다 주석 줄을 보내 연결 유지), proxy_http_version 1.1, Connection 헤더 비움. 앱도 응답에 X-Accel-Buffering: no를 붙임 |
| /protected/media/ | internal 설정, alias /srv/media/(읽기 전용 마운트) | 외부에서 직접 요청하면 404. 관리자 앱이 X-Accel-Redirect 헤더로 지정할 때만 전송. Range 요청 지원(영상 구간 이동) |
| *.json.gz (좌표 파일) | /protected/media/ 아래에서 Content-Type: application/json, Content-Encoding: gzip 로 응답 | 브라우저가 자동으로 압축을 풀어 JSON으로 받음 |
| /internal/, /admin/internal/ | deny(404) | 내부 API는 관리자 앱 8082 포트로만 열려 있으나, 실수로 노출되지 않도록 한 번 더 막음 |

## 내부 통신 인증

| 항목 | 값/규칙 | 설명 |
|---|---|---|
| X-Internal-Token | 환경변수 INTERNAL_API_TOKEN 값(32자 이상 임의 문자열) | 관리자 앱 ↔ 분석 서버, nginx → 분석 서버 요청에 모두 붙임. 값이 다르면 401. VM별 방화벽은 2순위라 지금은 이 토큰이 서버 간 요청의 확인 수단 |

## 공통 API 규칙

| 항목 | 값/규칙 | 설명 |
|---|---|---|
| 경로 | 공통 API는 두 앱에 같은 경로로 존재. 사용자 앱은 /api/v1/..., 관리자 앱은 /admin/api/v1/... | 공통 모듈의 컨트롤러를 두 앱이 함께 등록. API 명세서의 경로는 컨텍스트 경로를 뺨 값 |
| 데이터 형식 | 요청·응답 본문은 JSON(UTF-8). 필드 이름은 camelCase | 파일 다운로드·영상·SSE는 예외 |
| 시각 형식 | ISO-8601, 한국 시간 오프셋 포함. 예: 2026-10-12T14:03:00+09:00 / 날짜만: 2026-10-12 | DB에는 KST로 저장(오프셋 없이). 화면 표시는 yyyy-MM-dd HH:mm |
| 기간 조회 | from 이상 ~ to 미만(반열린 구간) | 예: 하루 = from=2026-10-12T00:00, to=2026-10-13T00:00 |
| 페이지 | 요청: page(0부터), size(기본 20, 최대 100). 응답: {items, page, size, totalElements, totalPages} | 목록 API 공통 |
| 오류 응답 | {"code": "ZONE_NOT_FOUND", "message": "구역을 찾을 수 없습니다.", "fieldErrors": [{"field": "name", "message": "필수입니다."}]} | code는 영문 대문자 상수, message는 화면에 그대로 띄울 수 있는 한국어 문장. fieldErrors는 입력 검증 오류일 때만 |
| 인증 오류 | 로그인 안 됨: 401(API) / 로그인 화면으로 이동(화면). 권한 없음: 403 | API 요청인지는 경로(/api/)로 판단 |
| CSRF | Spring Security CSRF 사용. 화면은 meta 태그로 토큰을 받고, fetch 요청에 X-CSRF-TOKEN 헤더로 보냄 | /internal/** 는 CSRF 제외(토큰 헤더로 인증) |

## 세션·로그인

| 항목 | 값/규칙 | 설명 |
|---|---|---|
| 세션 저장 | Spring Session JDBC. 세션 테이블은 앱마다 따로: 사용자 앱 SPRING_SESSION_USER, 관리자 앱 SPRING_SESSION_ADMIN(spring.session.jdbc.table-name) | 만료 세션 정리 작업은 각 앱이 자기 테이블만 맡음(spring.session.jdbc.cleanup-cron 두 앱 모두 켬). 관리자 앱은 SPRING_SESSION_USER용 세션 저장소(JdbcIndexedSessionRepository, 테이블 이름 지정)를 하나 더 두어 사용자 강제 로그아웃·최근 활동 조회에 씀 |
| 쿠키 이름 | 사용자 앱 USER_SESSION, 관리자 앱 ADMIN_SESSION | HttpOnly 켬. Secure는 HTTPS 적용(2순위) 때 켬 |
| 세션 만료 | 30분(환경변수 SESSION_TIMEOUT, 기본 30m) | sec-003. 실시간 화면·미리보기 권한 확인(/admin/api/v1/live/auth)은 세션 마지막 접근 시각을 갱신하지 않음(FNC-A-041) |
| 세션 주인 이름 | PRINCIPAL_NAME = 그 앱 계정 테이블(user_account / admin_account)의 login_id | 강제 로그아웃·최근 활동 조회 기준. FindByIndexNameSessionRepository로 조회·삭제(SQL 직접 작성 금지 — Redis 전환 대비). 사용자와 관리자는 같은 아이디를 가질 수 있지만 세션 테이블이 달라 섞이지 않음 |
| 활동 중 판단 | 최근 활동 시각이 30분 이내(환경변수 ACTIVE_WINDOW, 기본 30m) | 최근 활동 시각 = 그 계정 세션들의 LAST_ACCESS_TIME 중 최댓값, 세션이 없으면 계정 테이블의 last_login_at |

## 입력값 규칙

| 항목 | 값/규칙 | 설명 |
|---|---|---|
| 아이디(login_id) | 4~20자, 영문 소문자로 시작, 영문 소문자·숫자만 | 탈퇴 계정 아이디도 중복으로 봄 |
| 비밀번호 | 8~64자, 영문과 숫자를 각각 1자 이상 포함 | bcrypt 저장(sec-001) |
| 임시 비밀번호 | 영문 대소문자·숫자 12자 무작위 | 관리자가 재설정·계정 생성할 때 발급. 화면에 한 번만 보여주고 저장하지 않음. 다음 로그인 때 변경 강제(must_change_password=1) |
| 이름 | 1~50자 | - |
| 메일 | 선택. 100자 이하, 메일 형식 | - |
| 연락처 | 선택. 숫자와 - 만, 20자 이하 | - |
| 구역 이름 | 1~50자. 같은 동의 삭제되지 않은 구역끼리 중복 불가 | - |
| 캠 이름 | 1~50자 | - |
| 캠 영상 주소 | LIVE: rtsp:// 로 시작, 255자 이하 / DUMMY: 공유 폴더(/srv/media) 기준 상대경로, dummy/videos/ 로 시작, .mp4 로 끝남, '..' 포함 불가 | - |
| 조치 메모 | 200자 이하. 조치 항목이 OTHER면 필수 | - |

## 코드 값

| 항목 | 값/규칙 | 설명 |
|---|---|---|
| admin_account.role | ADMIN(관리자) / SUPER_ADMIN(최고 관리자) | 사용자 앱은 user_account로만, 관리자 앱은 admin_account로만 로그인(사용자에는 role이 없음) |
| user_account.status | PENDING(미승인) / ACTIVE(정상) / WITHDRAWN(탈퇴) | 로그인 가능: ACTIVE, PENDING(승인 대기 화면만) |
| admin_account.status | ACTIVE(정상) / DISABLED(비활성화) | 로그인 가능: ACTIVE. 최고 관리자는 비활성화 불가 |
| region.level | SI / GU / DONG | - |
| camera.source_type | LIVE / DUMMY | - |
| camera.status | STOPPED(정지) / PREPARING(준비 중) / RUNNING(가동 중) / ERROR(오류) | 화면 표시 이름은 괄호 안 |
| 혼잡 단계 | 1 정상(초록 #3BC99B) / 2 주의(주황 #F59E0B) / 3 위험(빨강 #EF4D55) | 단계는 코드에 고정. 히트맵은 다른 색 계열(파랑 그라데이션) |
| event.type | CONGESTION(혼잡 단계 상승) / SURGE(급증) / CAM_FAULT(캠 이상) | - |
| event.status | UNCHECKED(미확인) / CHECKED(확인 중) / RESOLVED(조치완료) | 앞으로만 바꿀 수 있음(UNCHECKED→RESOLVED 바로 가능). 되돌리기 불가 |
| event.action_code | ONSITE_OK(현장 확인·정상) / STAFF(인력 배치) / FALSE_ALARM(오탐) / CAM_CHECK(캠 점검 요청) / OTHER(기타) | RESOLVED로 바꿀 때 필수 |
| work_history.action | EXCEL_DOWNLOAD / EVENT_STATUS / ACCOUNT_CHANGE / CAMERA_RUN / ZONE_CHANGE / CAMERA_CHANGE | work_history.target_type: USER_ACCOUNT / ADMIN_ACCOUNT / ZONE / CAMERA / EVENT / REGION / ALL. 통계 다운로드는 범위에 따라 ZONE·REGION·ALL, 이벤트 다운로드는 EVENT(target_id 없음), 이벤트 처리는 EVENT(target_id=이벤트 번호) |
| 통계 단위(interval) | 1m / 1h / 1d / 1w / 1M / 1y | 1m=1분 통계, 1h=시간별 통계, 1d 이상=일별 통계를 묶어 계산. 1w는 월요일 시작, 1M은 달력 월, 1y는 달력 연도 |
| 통계 항목(item) | COUNT(인원) / DENSITY(밀집도) / INFLOW(유입) / OUTFLOW(유출) / DWELL(평균 체류 시간) | 히트맵은 COUNT/DENSITY/INFLOW/OUTFLOW만 |
| 방향 | N(북) / E(동) / S(남) / W(서) | 화면 위쪽을 북쪽으로 봄(드론 영상은 북쪽 정렬로 촬영한다고 가정) |

## 설정값(환경변수, 기본값)

| 항목 | 값/규칙 | 설명 |
|---|---|---|
| THRESHOLD_WARN_DENSITY / THRESHOLD_DANGER_DENSITY | 0.7 / 1.5 (명/㎡) | 주의·위험이 시작되는 밀집도. 개발 중 실제 영상으로 조정(evthres-002) |
| SURGE_WINDOW_MIN / SURGE_RATE_PCT / SURGE_MIN_DENSITY | 10 / 50 / 0.2 | 급증 비교 시간(분)·증가율(%)·최소 밀집도(evthres-003) |
| EVENT_CLOSE_HOLD_MIN | 5 | 경계 아래로 이 시간 유지되면 혼잡·급증 이벤트 종료(evtdet-005) |
| EVENT_MIN_SAMPLE_SEC | 30 | 1분 통계의 결과 초 수가 이보다 적으면 혼잡·급증 검사 안 함(캠 시작 직후 등 불완전한 1분 제외) |
| CAM_FAULT_TIMEOUT_SEC | 60 | 가동 중 캠의 결과가 이 시간 이상 없으면 캠 이상(evtdet-003) |
| MINUTE_CLOSE_GRACE_SEC | 5 | 1분 마감 대기 시간. 14:03 구간은 14:04:05에 마감, 이후 도착한 14:03 결과는 버림 |
| STAT_MINUTE_RETENTION_DAYS | 90 | 1분 통계 보관(stagg-004) |
| RECORDING_RETENTION_DAYS | 30 | 녹화 기록 보관(rec-002). 파일은 스토리지 서버가 31일에 삭제 |
| RESULT_RETRY_BUFFER_SEC | 300 | 분석 서버의 전송 실패 결과 보관 한도(vanly-006) |
| ANALYZE_FPS | 5 | 분석 프레임 수(초당) |
| DETECT_CONF / DETECT_IMGSZ / YOLO_WEIGHTS | 0.3 / 960 / yolo-crowd.pt | 탐지 신뢰도 하한·입력 크기·가중치 파일. YOLO-CROWD(사람 머리 탐지). VisDrone 사진 120장 측정: 입력 960에서 센 수는 실제의 약 30%, 상관계수 0.70. 1280은 약 43%, 0.73이지만 이미지당 약 0.5초(CPU)라 초당 5프레임을 못 맞춤. 실제 더미 영상으로 다시 재고 조정 |
| EDGE_MARGIN_RATIO | 0.05 | 판정선 위치: 화면 각 변에서 안쪽으로 너비·높이의 5% |
| RECORD_WIDTH / RECORD_HEIGHT / RECORD_FPS | 1280 / 720 / 10 | 라이브 녹화 해상도·프레임(rec-002 용량 조절) |
| LIVE_RECONNECT_FAIL_SEC | 30 | 라이브 스트림이 이 시간 동안 다시 연결되지 않으면 ERROR 보고(vanly-007) |
| CARD_SNAPSHOT_INTERVAL_SEC | 2 | 관리자 대시보드 캠 카드 미리보기 갱신 간격(live-002). 관리자 앱이 화면에 전달 |
| COMPARE_ABNORMAL_PCT | 30 | 기간 비교의 비정상 변동 기본 기준(cmp-003, 화면에서 조절) |
| STATS_MAX_RANGE | 1m: 1일 / 1h: 31일 / 1d: 1년 / 1w: 3년 / 1M: 5년 / 1y: 10년 | 단위별 최대 조회 기간(stagraph-001). 넘으면 400 |
| EXPORT_MAX_RANGE | 1m: 7일 / 1h: 93일 / 1d 이상: 10년, 예상 행 수 100만 이하 | 엑셀 최대 기간(xlsx-002) |
| COMPARE_MAX_CHILDREN | 10 | 여러 지역 비교 최대 개수(stagraph-002) |
| SUPER_ADMIN_LOGIN_ID / SUPER_ADMIN_INITIAL_PASSWORD | (비밀값) | 최고 관리자 최초 등록용(perm-005) |
| DB_URL / DB_USERNAME / DB_PASSWORD (DB 계정) | (비밀값) 앱마다 다른 DB 계정 | 사용자 앱 계정: admin_account·SPRING_SESSION_ADMIN 권한 없음, 테이블 변경(DDL) 권한 없음. 관리자 앱 계정: 전체 테이블 + Flyway 실행(DDL). 권한 부여(GRANT)는 DB 초기화 스크립트로 환경마다 같게 적용 |
| ANALYZER_BASE_URL / ADMIN_INTERNAL_BASE_URL | http://{분석 서버 IP}:5000 / http://{관리자 앱 IP}:8082 | 서버 주소는 모두 환경변수(DMZ 전환 대비) |

## 공유 폴더 구조(/srv/media)

| 항목 | 값/규칙 | 설명 |
|---|---|---|
| dummy/videos/ | 더미 원본 영상(사람이 미리 편집해 올림) | 캠 등록 시 source_uri로 지정 |
| dummy/boxes/{영상 파일명}.json.gz | 더미 좌표 파일(분석 준비 때 한 번 생성) | 같은 영상을 쓰는 캠끼리 공유 |
| recordings/live/cam{cameraId}/{yyyyMMdd}/cam{cameraId}_{yyyyMMdd_HHmm}.mp4 / .json.gz | 라이브 녹화 영상·좌표 파일 | 스토리지 서버 cron이 31일 지난 파일 삭제 |
| 분석 서버 로컬 | /var/lib/analyzer/cache/(더미 분석 캐시), /var/lib/analyzer/tmp/(녹화 중인 파일) | 공유 폴더가 아님 |

## 좌표 파일 형식

| 항목 | 값/규칙 | 설명 |
|---|---|---|
| 구조 | {"version": 1, "fps": 5, "frames": [{"t": 0.2, "b": [[17, 0.4123, 0.2210, 0.0150, 0.0300], ...]}, ...]} | t: 녹화 시작부터의 초. b: [추적 번호, x, y, 너비, 높이], 좌표는 영상 크기 대비 0~1 비율(왼쪽 위 기준, 소수 4자리) |
| 그리기 규칙 | 재생 위치 p초에서 t ≤ p 인 마지막 프레임의 박스를 그림 | 다음 프레임까지 직전 박스 유지(repfocus-004) |

## 혼잡 단계 판정

| 항목 | 값/규칙 | 설명 |
|---|---|---|
| 구역 | 밀집도 = count_avg ÷ 구역 면적. 1(정상) 기본, WARN 이상이면 2(주의), DANGER 이상이면 3(위험) | - |
| 지역(동·구·시) | 밀집도 = 소속 구역 count_avg 합 ÷ 소속 구역 면적 합(현재 면적). 판정 기준은 구역과 같음 | stats-008 |

## 주요 라이브러리

| 항목 | 값/규칙 | 설명 |
|---|---|---|
| 앱(Spring) | Spring Security, Spring Session JDBC, Spring Data JPA, Thymeleaf | 버전은 프로젝트 개요의 기술 스택을 따름 |
| 다각형 계산 | JTS(org.locationtech.jts) | 다각형 검증(isValid)·내부 점(getInteriorPoint)·포함 여부 |
| 엑셀 | Apache POI SXSSF | 스트리밍 작성(대용량 메모리 방지) |
| 화면 | Leaflet + Leaflet-Geoman(지도·구역 그리기), Chart.js(그래프) | 공통 정적 파일로 두 앱이 함께 사용. 지도 코드는 지도 모듈 한 파일에만 둠 |
| 분석 서버 | Flask, YOLO-CROWD(YOLOv5 코드 + yolo-crowd.pt), ultralytics(ByteTrack 추적기만), OpenCV, ffmpeg(녹화) | GPU 없음 기준. YOLO-CROWD는 yolov5 저장소의 모델 코드가 필요하고 ultralytics로 불러올 수 없음. 가중치는 pickle 형식이라 torch 2.6 이상에서는 torch.load(weights_only=False)로 읽어야 함(신뢰할 수 있는 파일만) |
| DB 마이그레이션 | Flyway | 관리자 앱만 실행(두 앱이 동시에 돌리면 충돌). 사용자 앱은 spring.flyway.enabled=false |
