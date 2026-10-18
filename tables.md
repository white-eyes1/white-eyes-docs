# 테이블 명세

> 원본: 명세서 시트 '테이블 명세서'에서 옮김. 이후로는 이 파일이 원본이다.


## 공통 규칙

- MySQL 8, InnoDB, 문자셋 utf8mb4. 날짜·시각은 모두 한국 시간(KST)으로 저장한다.
- COMMENT: 칼럼에 담기는 데이터(DB 칼럼 COMMENT로도 넣는다). 비고: 칼럼의 용도와 관련 요구사항 ID.
- 코드 값(상태·종류 등)은 VARCHAR에 영문 대문자로 저장한다(ENUM을 쓰지 않아 값 추가 시 테이블 변경이 없음).
- 삭제: 계정은 상태만 바꾸고, 구역·캠은 삭제 표시(deleted_at, 가동 이력이 없으면 실제 삭제)한다.
- 2순위 기능의 테이블(행사, 로그인 실패 잠금, 고객별 열람 지역)은 '2순위 기능' 시트에 초안을 둔다.
- DB에 넣지 않는 것: 다시보기 박스 좌표(녹화 옆 좌표 파일), 더미 캠 분석 캐시(분석 서버 로컬), 1초 단위 분석 결과(관리자 앱 메모리에서 1분으로 묶음).
- 계정은 사용자(user_account)와 관리자(admin_account)를 나눈다. 앱마다 DB 계정을 따로 두고, 사용자 앱 DB 계정에는 admin_account·SPRING_SESSION_ADMIN 권한을 주지 않는다(설정·규약 'DB 계정').
- 라이브러리 구조를 따르는 테이블: flyway_schema_history(Flyway가 만듦, 관리자 앱만 실행), 세션 테이블 두 쌍(SPRING_SESSION_USER·SPRING_SESSION_ADMIN과 각각의 _ATTRIBUTES). 세션 테이블은 Spring Session 표준 구조에 이름만 바꾼 것이라 Flyway 마이그레이션으로 만든다(아래 명세는 확인용).

## user_account

사용자 계정. 사용자 앱이 로그인에 쓰고, 관리자 앱은 목록·승인·수정에 쓴다. 탈퇴해도 행을 지우지 않는다.

| 컬럼명 | 키 | 타입 | 길이 | DEFAULT | NOT NULL | COMMENT | 비고 |
|---|---|---|---|---|---|---|---|
| id | PK | BIGINT | - | AUTO_INCREMENT | Y | 사용자 번호 | 다른 테이블이 사용자를 가리킬 때 쓰는 키 |
| login_id | UK | VARCHAR | 20 | - | Y | 로그인 아이디 | 로그인, 가입 시 중복 확인. 탈퇴해도 남겨 같은 아이디로 재가입을 막음(auth-005). 관리자 아이디와는 별개(같은 아이디가 있을 수 있음) |
| password | - | VARCHAR | 60 | - | Y | bcrypt로 암호화한 비밀번호 | 로그인 확인(sec-001). bcrypt 결과는 항상 60자 |
| name | - | VARCHAR | 50 | - | Y | 이름 | 목록 표시·검색(aclst-003) |
| email | - | VARCHAR | 100 | NULL | N | 메일 주소 | 연락용 정보(메일 발송 기능은 없음). 유일 조건 없음 — 아이디만 중복 확인 |
| phone | - | VARCHAR | 20 | NULL | N | 연락처 | 연락용 정보 |
| status | - | VARCHAR | 20 | PENDING | Y | 계정 상태: PENDING(미승인) / ACTIVE(정상) / WITHDRAWN(탈퇴) | 로그인 허용 판정(ACTIVE는 서비스 이용, PENDING은 승인 대기 화면만), 목록 필터. 가입 시 PENDING, 승인 취소 시 PENDING으로 되돌림(acman-002·003) |
| must_change_password | - | TINYINT | 1 | 0 | Y | 1이면 다음 로그인 때 비밀번호를 바꿔야 함 | 관리자가 임시 비밀번호로 재설정한 뒤 변경 강제(acman-001) |
| last_login_at | - | DATETIME | - | NULL | N | 마지막 로그인 성공 시각 | 세션이 만료돼 지워진 뒤에도 '최근 활동' 시각을 보여주기 위함(aclst-004). 세션이 있으면 세션의 마지막 접근 시각이 우선 |
| withdrawn_at | - | DATETIME | - | NULL | N | 탈퇴 시각 | 탈퇴 계정 표시·정렬 |
| created_at | - | DATETIME | - | CURRENT_TIMESTAMP | Y | 가입 시각 | 가입일 필터·정렬(aclst-003) |
| updated_at | - | DATETIME | - | CURRENT_TIMESTAMP<br>ON UPDATE | Y | 마지막 수정 시각 | 변경 추적 |

- **인덱스**: UK(login_id) / (status, created_at) — 목록 필터·정렬

## admin_account

관리자 계정(관리자·최고 관리자). 관리자 앱만 쓴다. 회원가입이 아니라 최고 관리자가 만들고(최고 관리자는 서버 최초 실행 때 자동 등록), 지우지 않고 비활성화만 한다.

| 컬럼명 | 키 | 타입 | 길이 | DEFAULT | NOT NULL | COMMENT | 비고 |
|---|---|---|---|---|---|---|---|
| id | PK | BIGINT | - | AUTO_INCREMENT | Y | 관리자 번호 | 이벤트 처리자·계정 생성자 등 관리자를 가리킬 때 쓰는 키 |
| login_id | UK | VARCHAR | 20 | - | Y | 로그인 아이디 | 로그인, 계정 생성 시 중복 확인. 사용자 아이디와는 별개 |
| password | - | VARCHAR | 60 | - | Y | bcrypt로 암호화한 비밀번호 | 로그인 확인(sec-001) |
| name | - | VARCHAR | 50 | - | Y | 이름 | 목록 표시·검색(aclst-003) |
| email | - | VARCHAR | 100 | NULL | N | 메일 주소 | 연락용 정보 |
| phone | - | VARCHAR | 20 | NULL | N | 연락처 | 연락용 정보 |
| role | - | VARCHAR | 20 | ADMIN | Y | 권한 등급: ADMIN / SUPER_ADMIN | 최고 관리자 전용 기능 판정(perm-004·5) |
| status | - | VARCHAR | 20 | ACTIVE | Y | 계정 상태: ACTIVE(정상) / DISABLED(비활성화) | 로그인 허용 판정(ACTIVE만), 목록 필터(acman-006) |
| must_change_password | - | TINYINT | 1 | 1 | Y | 1이면 다음 로그인 때 비밀번호를 바꿔야 함 | 첫 로그인, 임시 비밀번호로 재설정한 뒤 변경 강제(acman-004·009) |
| last_login_at | - | DATETIME | - | NULL | N | 마지막 로그인 성공 시각 | 최근 활동 표시(aclst-004) |
| created_by | FK | BIGINT | - | NULL | N | 이 계정을 만든 최고 관리자(admin_account.id). 자동 등록된 최고 관리자는 NULL | 관리자 계정 생성 책임 확인(acman-009) |
| created_at | - | DATETIME | - | CURRENT_TIMESTAMP | Y | 생성 시각 | 목록 정렬 |
| updated_at | - | DATETIME | - | CURRENT_TIMESTAMP<br>ON UPDATE | Y | 마지막 수정 시각 | 변경 추적 |

- **인덱스**: UK(login_id) / (role, status, created_at) — 목록 필터·정렬

## SPRING_SESSION_USER / SPRING_SESSION_ADMIN

로그인 세션(Spring Session JDBC 표준 구조). 앱마다 같은 구조의 테이블을 따로 둔다: 사용자 앱 SPRING_SESSION_USER, 관리자 앱 SPRING_SESSION_ADMIN. 쿠키 이름도 앱별로 다르다(USER_SESSION / ADMIN_SESSION). 관리자 앱은 사용자 강제 로그아웃·최근 활동을 위해 SPRING_SESSION_USER도 조회·삭제한다.

| 컬럼명 | 키 | 타입 | 길이 | DEFAULT | NOT NULL | COMMENT | 비고 |
|---|---|---|---|---|---|---|---|
| PRIMARY_ID | PK | CHAR | 36 | - | Y | 세션 내부 키 | 속성 테이블과 연결 |
| SESSION_ID | UK | CHAR | 36 | - | Y | 쿠키에 담기는 세션 ID | 요청마다 세션을 찾음 |
| CREATION_TIME | - | BIGINT | - | - | Y | 세션 생성 시각(밀리초) | 로그인 시각 확인 |
| LAST_ACCESS_TIME | - | BIGINT | - | - | Y | 마지막 요청 시각(밀리초) | 최근 활동 시각, 활동 중 여부(최근 30분 안) 판정(aclst-004) |
| MAX_INACTIVE_INTERVAL | - | INT | - | - | Y | 만료까지 허용하는 무활동 시간(초) | 30분 자동 로그아웃(sec-003) |
| EXPIRY_TIME | - | BIGINT | - | - | Y | 만료 예정 시각(밀리초) | 만료 세션 정리 작업이 지울 대상 찾기 |
| PRINCIPAL_NAME | - | VARCHAR | 100 | NULL | N | 로그인한 계정의 아이디(그 앱 계정 테이블의 login_id) | 계정별 세션 조회·삭제 = 강제 로그아웃, 승인 취소·비활성화 시 즉시 차단(acman-003·006~008) |

- **인덱스**: UK(SESSION_ID) / (EXPIRY_TIME) / (PRINCIPAL_NAME)

## SPRING_SESSION_USER_ATTRIBUTES / SPRING_SESSION_ADMIN_ATTRIBUTES

세션에 담긴 값(Spring Session JDBC 표준 구조, 세션 테이블마다 하나).

| 컬럼명 | 키 | 타입 | 길이 | DEFAULT | NOT NULL | COMMENT | 비고 |
|---|---|---|---|---|---|---|---|
| SESSION_PRIMARY_ID | PK, FK | CHAR | 36 | - | Y | 세션 내부 키(각 세션 테이블의 PRIMARY_ID) | 세션이 지워지면 함께 지워짐(ON DELETE CASCADE) |
| ATTRIBUTE_NAME | PK | VARCHAR | 200 | - | Y | 속성 이름 | 속성 구분 |
| ATTRIBUTE_BYTES | - | BLOB | - | - | Y | 직렬화된 속성 값(로그인 인증 정보 등) | Spring Security가 로그인 상태를 복원 |

- **인덱스**: PK(SESSION_PRIMARY_ID, ATTRIBUTE_NAME)

## region

행정구역(시·구·동). 공개 경계 데이터를 초기 데이터로 넣고 화면에서는 수정하지 않는다.

| 컬럼명 | 키 | 타입 | 길이 | DEFAULT | NOT NULL | COMMENT | 비고 |
|---|---|---|---|---|---|---|---|
| id | PK | BIGINT | - | AUTO_INCREMENT | Y | 행정구역 번호 | 구역이 지역을 가리키는 키 |
| parent_id | FK | BIGINT | - | NULL | N | 상위 행정구역(region.id). 시는 NULL | 시 → 구 → 동 계층 탐색, 상위 지역 합산(stats-008) |
| level | - | VARCHAR | 10 | - | Y | 단위: SI / GU / DONG | 지도 단계 구분, 합산 단위 구분 |
| code | UK | VARCHAR | 10 | - | Y | 행정구역 코드(경계 데이터 원본 코드) | 경계 데이터를 다시 넣을 때 같은 지역 식별 |
| name | - | VARCHAR | 50 | - | Y | 행정구역 이름(예: 문화동) | 화면·엑셀 표시 |
| boundary | - | JSON | - | - | Y | 경계 다각형(GeoJSON, 위도·경도 WGS84) | 지도 경계 표시(map-001), 구역 소속 동 자동 판정(JTS) |
| center_lat | - | DECIMAL | 9,6 | - | Y | 경계 중심점 위도(경계 안의 점) | 지도 초기 위치 |
| center_lng | - | DECIMAL | 9,6 | - | Y | 경계 중심점 경도 | 위와 같음 |
| created_at | - | DATETIME | - | CURRENT_TIMESTAMP | Y | 초기 데이터 적재 시각 | 적재 이력 확인 |

- **인덱스**: UK(code) / (parent_id)

## zone

구역(캠 1대가 촬영하는 범위). 관리자가 지도에 다각형을 그려 등록한다.

| 컬럼명 | 키 | 타입 | 길이 | DEFAULT | NOT NULL | COMMENT | 비고 |
|---|---|---|---|---|---|---|---|
| id | PK | BIGINT | - | AUTO_INCREMENT | Y | 구역 번호 | 통계·캠·이벤트가 구역을 가리키는 키 |
| dong_id | FK | BIGINT | - | - | Y | 소속 동(region.id) | 동·구·시 합산. 다각형 중심점이 속한 동으로 자동 판정(loca-003). 같은 동 안에서만 수정 가능(loca-002) |
| name | - | VARCHAR | 50 | - | Y | 구역 이름 | 화면·엑셀 표시. 같은 동의 삭제되지 않은 구역끼리 중복 불가(앱에서 확인 — 삭제된 구역 이름을 다시 쓸 수 있게 DB 유일 조건은 걸지 않음) |
| area_m2 | - | DECIMAL | 10,2 | - | Y | 면적(㎡). 다각형에서 자동 계산 | 밀집도 = 인원 ÷ 면적(stats-004). 바꾸면 이후 통계부터 적용 |
| boundary | - | JSON | - | - | Y | 구역 다각형(GeoJSON, WGS84) | 지도 표시·색칠·히트맵, 면적·소속 동 계산 |
| center_lat | - | DECIMAL | 9,6 | - | Y | 구역 중심점 위도(다각형 안의 점) | 지도 핀 위치(SCR-C-003). 등록·수정 때 다각형에서 자동 계산(FNC-A-014·015) |
| center_lng | - | DECIMAL | 9,6 | - | Y | 구역 중심점 경도 | 위와 같음 |
| deleted_at | - | DATETIME | - | NULL | N | 삭제 시각(NULL이면 사용 중) | 소프트 삭제(loca-005). 목록·지도에서 빼고, 지난 기록에는 '(삭제됨)' 표시. 가동 이력이 없으면 행을 실제로 지움 |
| created_at | - | DATETIME | - | CURRENT_TIMESTAMP | Y | 등록 시각 | 정렬·추적 |
| updated_at | - | DATETIME | - | CURRENT_TIMESTAMP<br>ON UPDATE | Y | 마지막 수정 시각 | 변경 추적 |

- **인덱스**: (dong_id, deleted_at)

## zone_neighbor

구역의 방향별 이웃. 행이 없는 방향은 '관측 범위 밖'이다.

| 컬럼명 | 키 | 타입 | 길이 | DEFAULT | NOT NULL | COMMENT | 비고 |
|---|---|---|---|---|---|---|---|
| zone_id | PK, FK | BIGINT | - | - | Y | 기준 구역(zone.id) | 구역 간 이동 계산의 출발 구역 |
| direction | PK | CHAR | 1 | - | Y | 방향: N / E / S / W | 유출 방향(out_n 등)과 이웃 구역 짝짓기 |
| neighbor_id | FK | BIGINT | - | - | Y | 그 방향의 이웃 구역(zone.id) | A의 동쪽 유출 = 동쪽 이웃 B로 간 인원(stats-006, map-002). 이웃이 삭제되면 이 행도 지움 |

- **인덱스**: PK(zone_id, direction) / (neighbor_id)

## camera

캠(구역 1개에 1대). 상태는 분석 서버가 보고한 값으로 바꾼다.

| 컬럼명 | 키 | 타입 | 길이 | DEFAULT | NOT NULL | COMMENT | 비고 |
|---|---|---|---|---|---|---|---|
| id | PK | BIGINT | - | AUTO_INCREMENT | Y | 캠 번호 | 녹화·이벤트가 캠을 가리키는 키, 분석 서버 지시에 쓰는 번호 |
| zone_id | FK | BIGINT | - | - | Y | 담당 구역(zone.id) | 분석 결과를 구역 통계로 모음. 구역당 삭제되지 않은 캠 1대(앱에서 확인) |
| name | - | VARCHAR | 50 | - | Y | 캠 이름 | 화면 표시 |
| source_type | - | VARCHAR | 10 | - | Y | 입력 방식: LIVE / DUMMY | 분석 서버가 실시간 분석과 캐시 재생 중 고름 |
| source_uri | - | VARCHAR | 255 | - | Y | 영상 주소: LIVE는 RTSP 주소, DUMMY는 공유 폴더 기준 상대경로 | 가동 지시 때 분석 서버에 전달(caman-001) |
| run_requested | - | TINYINT | 1 | 0 | Y | 1이면 가동을 원하는 상태(관리자가 가동하면 1, 정지하면 0) | 분석 서버가 다시 켜졌을 때 다시 가동할 캠 목록(vanly-008). 실제 상태(status)와 따로 둠 — 오류 상태여도 1이면 재시작 때 다시 가동 |
| status | - | VARCHAR | 20 | STOPPED | Y | 실제 상태: STOPPED / PREPARING / RUNNING / ERROR | 캠 상태 화면(caman-004), 캠 이상 감지 대상 판정(RUNNING만, evtdet-003) |
| progress | - | TINYINT | - | 0 | Y | 분석 준비 진행률(0~100) | 더미 캠 준비 진행률 표시(caman-005) |
| error_message | - | VARCHAR | 500 | NULL | N | 마지막 오류 내용 | 오류 원인 표시(파일 없음, 스트림 연결 실패 등) |
| first_started_at | - | DATETIME | - | NULL | N | 처음 가동된 시각 | 완전 삭제 가능 여부 판정(NULL이면 가동 이력 없음, caman-006·loca-005), 시연용 데이터를 가동 시작 전날까지만 만드는 기준 |
| deleted_at | - | DATETIME | - | NULL | N | 삭제 시각(NULL이면 사용 중) | 소프트 삭제(caman-006). 지난 녹화·이벤트에는 '(삭제됨)' 표시 |
| created_at | - | DATETIME | - | CURRENT_TIMESTAMP | Y | 등록 시각 | 정렬·추적 |
| updated_at | - | DATETIME | - | CURRENT_TIMESTAMP<br>ON UPDATE | Y | 마지막 수정 시각 | 변경 추적 |

- **인덱스**: (zone_id, deleted_at) / (run_requested)

## recording

녹화 기록(영상 1개 + 좌표 파일 1개). 30일 지난 행은 매일 지운다. 더미 캠은 같은 파일을 가리키는 행이 반복마다 추가된다.

| 컬럼명 | 키 | 타입 | 길이 | DEFAULT | NOT NULL | COMMENT | 비고 |
|---|---|---|---|---|---|---|---|
| id | PK | BIGINT | - | AUTO_INCREMENT | Y | 녹화 번호 | 다시보기 요청에서 녹화를 가리키는 번호(파일 경로 대신 노출) |
| camera_id | FK | BIGINT | - | - | Y | 녹화한 캠(camera.id) | 그래프에서 고른 구역·시각의 녹화 찾기 |
| started_at | - | DATETIME(3) | - | - | Y | 녹화 시작 시각(밀리초까지) | 재생 시작 위치 = 클릭한 시각 − started_at. 좌표 파일의 시간 기준 |
| ended_at | - | DATETIME(3) | - | NULL | N | 녹화 종료 시각. 진행 중이면 NULL | 그 시각을 포함하는 녹화인지 판정, 이어 재생할 다음 녹화 찾기(repfocus-003) |
| video_path | - | VARCHAR | 255 | - | Y | 영상 파일 경로(공유 폴더 기준 상대경로) | 웹 서버 내부 경로로 바꿔 전송. 브라우저에는 노출하지 않음(sec-004) |
| box_path | - | VARCHAR | 255 | - | Y | 좌표 파일 경로(.json.gz, 공유 폴더 기준 상대경로) | 다시보기 박스 그리기(repfocus-004). 영상과 같은 방식으로 전송 |
| created_at | - | DATETIME | - | CURRENT_TIMESTAMP | Y | 기록 등록 시각 | 등록 지연 확인 |

- **인덱스**: (camera_id, started_at) — 시각으로 녹화 찾기 / (started_at) — 30일 정리

## zone_stat_minute

구역별 1분 통계. 실제 분석 데이터만 넣고 90일만 보관한다.

| 컬럼명 | 키 | 타입 | 길이 | DEFAULT | NOT NULL | COMMENT | 비고 |
|---|---|---|---|---|---|---|---|
| zone_id | PK, FK | BIGINT | - | - | Y | 구역(zone.id) | 구역별 조회, 동·구·시 합산 |
| stat_at | PK | DATETIME | - | - | Y | 1분 구간 시작 시각(KST, 초는 0) | 조회 기간 조건, 정시 집계의 묶음 기준. (구역, 시각) 덮어쓰기 저장의 키 |
| count_avg | - | DECIMAL | 7,2 | - | Y | 1분 평균 인원 | 인원 그래프·대시보드·히트맵. 1초 결과의 평균 |
| count_max | - | INT | - | - | Y | 1분 최대 인원 | 최대 인원 표시, 피크 확인 |
| count_min | - | INT | - | - | Y | 1분 최저 인원 | 최저 인원 표시 |
| density | - | DECIMAL | 8,4 | - | Y | 평균 밀집도(명/㎡) = 평균 인원 ÷ 당시 구역 면적 | 혼잡 단계 판정·지도 색·이벤트 검사. 면적이 나중에 바뀌어도 당시 값을 유지하려고 계산값을 저장 |
| in_n | - | INT | - | 0 | Y | 북쪽 변을 넘어 들어온 인원 합 | 방향별 유입 표시, 이웃 구역의 유출과 짝지어 구역 간 이동 계산 |
| in_e | - | INT | - | 0 | Y | 동쪽 변을 넘어 들어온 인원 합 | 방향별 유입 표시, 이웃 구역의 유출과 짝지어 구역 간 이동 계산 |
| in_s | - | INT | - | 0 | Y | 남쪽 변을 넘어 들어온 인원 합 | 방향별 유입 표시, 이웃 구역의 유출과 짝지어 구역 간 이동 계산 |
| in_w | - | INT | - | 0 | Y | 서쪽 변을 넘어 들어온 인원 합 | 방향별 유입 표시, 이웃 구역의 유출과 짝지어 구역 간 이동 계산 |
| out_n | - | INT | - | 0 | Y | 북쪽 변을 넘어 나간 인원 합 | 방향별 유출 표시. 북쪽 이웃(zone_neighbor)으로 간 인원으로 계산(이웃 없으면 '관측 범위 밖') |
| out_e | - | INT | - | 0 | Y | 동쪽 변을 넘어 나간 인원 합 | 방향별 유출 표시. 동쪽 이웃(zone_neighbor)으로 간 인원으로 계산(이웃 없으면 '관측 범위 밖') |
| out_s | - | INT | - | 0 | Y | 남쪽 변을 넘어 나간 인원 합 | 방향별 유출 표시. 남쪽 이웃(zone_neighbor)으로 간 인원으로 계산(이웃 없으면 '관측 범위 밖') |
| out_w | - | INT | - | 0 | Y | 서쪽 변을 넘어 나간 인원 합 | 방향별 유출 표시. 서쪽 이웃(zone_neighbor)으로 간 인원으로 계산(이웃 없으면 '관측 범위 밖') |
| dwell_sum_sec | - | INT | - | 0 | Y | 구역을 떠난 사람들의 체류 시간 합(초) | 평균 체류 시간 = dwell_sum_sec ÷ dwell_count. 평균 대신 합을 저장해야 시간별·일별로 묶을 때 평균이 정확함 |
| dwell_count | - | INT | - | 0 | Y | 체류 시간을 잰(구역을 떠난) 인원 | 평균 체류 시간의 분모 |
| sample_sec | - | SMALLINT | - | 0 | Y | 결과가 실제로 들어온 초 수(0~60) | 캠 끊김 구간 구분(그래프에 빈 구간 표시), 상위 통계로 묶을 때 평균의 가중치 |

- **인덱스**: PK(zone_id, stat_at) / (stat_at) — 90일 정리·전체 구역 조회

## zone_stat_hourly

구역별 시간별 통계. 매 정시에 1분 통계를 묶어 만들고, 시연용 과거 데이터도 여기에 넣는다.

| 컬럼명 | 키 | 타입 | 길이 | DEFAULT | NOT NULL | COMMENT | 비고 |
|---|---|---|---|---|---|---|---|
| zone_id | PK, FK | BIGINT | - | - | Y | 구역(zone.id) | 구역별 조회, 동·구·시 합산 |
| stat_at | PK | DATETIME | - | - | Y | 1시간 구간 시작 시각(KST, 정시) | 시간대 분석·히트맵·기간 비교의 조회 기준. (구역, 시각) 덮어쓰기 저장의 키 |
| count_avg | - | DECIMAL | 7,2 | - | Y | 1시간 평균 인원 | 인원 그래프·대시보드·히트맵. 하위 통계를 묶을 때 sample_sec로 가중 평균(끊긴 구간이 평균을 낮추지 않도록) |
| count_max | - | INT | - | - | Y | 1시간 최대 인원 | 최대 인원 표시, 피크 확인 |
| count_min | - | INT | - | - | Y | 1시간 최저 인원 | 최저 인원 표시 |
| density | - | DECIMAL | 8,4 | - | Y | 평균 밀집도(명/㎡) = 평균 인원 ÷ 당시 구역 면적 | 혼잡 단계 판정·지도 색. 면적이 나중에 바뀌어도 당시 값을 유지하려고 계산값을 저장 |
| in_n | - | INT | - | 0 | Y | 북쪽 변을 넘어 들어온 인원 합 | 방향별 유입 표시, 이웃 구역의 유출과 짝지어 구역 간 이동 계산 |
| in_e | - | INT | - | 0 | Y | 동쪽 변을 넘어 들어온 인원 합 | 방향별 유입 표시, 이웃 구역의 유출과 짝지어 구역 간 이동 계산 |
| in_s | - | INT | - | 0 | Y | 남쪽 변을 넘어 들어온 인원 합 | 방향별 유입 표시, 이웃 구역의 유출과 짝지어 구역 간 이동 계산 |
| in_w | - | INT | - | 0 | Y | 서쪽 변을 넘어 들어온 인원 합 | 방향별 유입 표시, 이웃 구역의 유출과 짝지어 구역 간 이동 계산 |
| out_n | - | INT | - | 0 | Y | 북쪽 변을 넘어 나간 인원 합 | 방향별 유출 표시. 북쪽 이웃(zone_neighbor)으로 간 인원으로 계산(이웃 없으면 '관측 범위 밖') |
| out_e | - | INT | - | 0 | Y | 동쪽 변을 넘어 나간 인원 합 | 방향별 유출 표시. 동쪽 이웃(zone_neighbor)으로 간 인원으로 계산(이웃 없으면 '관측 범위 밖') |
| out_s | - | INT | - | 0 | Y | 남쪽 변을 넘어 나간 인원 합 | 방향별 유출 표시. 남쪽 이웃(zone_neighbor)으로 간 인원으로 계산(이웃 없으면 '관측 범위 밖') |
| out_w | - | INT | - | 0 | Y | 서쪽 변을 넘어 나간 인원 합 | 방향별 유출 표시. 서쪽 이웃(zone_neighbor)으로 간 인원으로 계산(이웃 없으면 '관측 범위 밖') |
| dwell_sum_sec | - | BIGINT | - | 0 | Y | 구역을 떠난 사람들의 체류 시간 합(초) | 평균 체류 시간 = dwell_sum_sec ÷ dwell_count. 평균 대신 합을 저장해야 시간별·일별로 묶을 때 평균이 정확함 |
| dwell_count | - | INT | - | 0 | Y | 체류 시간을 잰(구역을 떠난) 인원 | 평균 체류 시간의 분모 |
| sample_sec | - | INT | - | 0 | Y | 결과가 실제로 들어온 초 수(0~3600) | 캠 끊김 구간 구분(그래프에 빈 구간 표시), 상위 통계로 묶을 때 평균의 가중치. 시연용 데이터는 가득 찬 값으로 넣음 |
| is_demo | - | TINYINT | 1 | 0 | Y | 1이면 생성 스크립트로 넣은 시연용 데이터 | 화면·엑셀의 '시연용 데이터' 표시, 시연용 데이터 일괄 삭제(demo-002) |

- **인덱스**: PK(zone_id, stat_at) / (stat_at) / (is_demo)

## zone_stat_daily

구역별 일별 통계. 매일 자정에 시간별 통계를 묶어 만든다.

| 컬럼명 | 키 | 타입 | 길이 | DEFAULT | NOT NULL | COMMENT | 비고 |
|---|---|---|---|---|---|---|---|
| zone_id | PK, FK | BIGINT | - | - | Y | 구역(zone.id) | 구역별 조회, 동·구·시 합산 |
| stat_date | PK | DATE | - | - | Y | 집계 날짜(KST) | 1일~1년 단위 그래프·추세 조회 기준. (구역, 날짜) 덮어쓰기 저장의 키 |
| count_avg | - | DECIMAL | 7,2 | - | Y | 하루 평균 인원 | 인원 그래프·대시보드·히트맵. 하위 통계를 묶을 때 sample_sec로 가중 평균(끊긴 구간이 평균을 낮추지 않도록) |
| count_max | - | INT | - | - | Y | 하루 최대 인원 | 최대 인원 표시, 피크 확인 |
| count_min | - | INT | - | - | Y | 하루 최저 인원 | 최저 인원 표시 |
| density | - | DECIMAL | 8,4 | - | Y | 평균 밀집도(명/㎡) = 평균 인원 ÷ 당시 구역 면적 | 혼잡 단계 판정·지도 색. 면적이 나중에 바뀌어도 당시 값을 유지하려고 계산값을 저장 |
| in_n | - | INT | - | 0 | Y | 북쪽 변을 넘어 들어온 인원 합 | 방향별 유입 표시, 이웃 구역의 유출과 짝지어 구역 간 이동 계산 |
| in_e | - | INT | - | 0 | Y | 동쪽 변을 넘어 들어온 인원 합 | 방향별 유입 표시, 이웃 구역의 유출과 짝지어 구역 간 이동 계산 |
| in_s | - | INT | - | 0 | Y | 남쪽 변을 넘어 들어온 인원 합 | 방향별 유입 표시, 이웃 구역의 유출과 짝지어 구역 간 이동 계산 |
| in_w | - | INT | - | 0 | Y | 서쪽 변을 넘어 들어온 인원 합 | 방향별 유입 표시, 이웃 구역의 유출과 짝지어 구역 간 이동 계산 |
| out_n | - | INT | - | 0 | Y | 북쪽 변을 넘어 나간 인원 합 | 방향별 유출 표시. 북쪽 이웃(zone_neighbor)으로 간 인원으로 계산(이웃 없으면 '관측 범위 밖') |
| out_e | - | INT | - | 0 | Y | 동쪽 변을 넘어 나간 인원 합 | 방향별 유출 표시. 동쪽 이웃(zone_neighbor)으로 간 인원으로 계산(이웃 없으면 '관측 범위 밖') |
| out_s | - | INT | - | 0 | Y | 남쪽 변을 넘어 나간 인원 합 | 방향별 유출 표시. 남쪽 이웃(zone_neighbor)으로 간 인원으로 계산(이웃 없으면 '관측 범위 밖') |
| out_w | - | INT | - | 0 | Y | 서쪽 변을 넘어 나간 인원 합 | 방향별 유출 표시. 서쪽 이웃(zone_neighbor)으로 간 인원으로 계산(이웃 없으면 '관측 범위 밖') |
| dwell_sum_sec | - | BIGINT | - | 0 | Y | 구역을 떠난 사람들의 체류 시간 합(초) | 평균 체류 시간 = dwell_sum_sec ÷ dwell_count. 평균 대신 합을 저장해야 시간별·일별로 묶을 때 평균이 정확함 |
| dwell_count | - | INT | - | 0 | Y | 체류 시간을 잰(구역을 떠난) 인원 | 평균 체류 시간의 분모 |
| sample_sec | - | INT | - | 0 | Y | 결과가 실제로 들어온 초 수(0~86400) | 캠 끊김 구간 구분(그래프에 빈 구간 표시), 상위 통계로 묶을 때 평균의 가중치. 시연용 데이터는 가득 찬 값으로 넣음 |
| is_demo | - | TINYINT | 1 | 0 | Y | 1이면 생성 스크립트로 넣은 시연용 데이터 | 화면·엑셀의 '시연용 데이터' 표시, 시연용 데이터 일괄 삭제(demo-002) |

- **인덱스**: PK(zone_id, stat_date) / (stat_date) / (is_demo)

## event

이벤트(혼잡 단계 상승·급증·캠 이상). 같은 구역·종류의 열린 이벤트는 하나만 둔다. 처리 이력은 별도 테이블 없이 작업 기록(work_history)에 남긴다.

| 컬럼명 | 키 | 타입 | 길이 | DEFAULT | NOT NULL | COMMENT | 비고 |
|---|---|---|---|---|---|---|---|
| id | PK | BIGINT | - | AUTO_INCREMENT | Y | 이벤트 번호 | 처리·다시보기 이동 대상 지정 |
| type | - | VARCHAR | 20 | - | Y | 종류: CONGESTION(혼잡 단계 상승) / SURGE(급증) / CAM_FAULT(캠 이상) | 목록 필터·색상 구분, 사용자 대시보드는 CONGESTION·SURGE만 셈(das-003) |
| zone_id | FK | BIGINT | - | - | Y | 발생 구역(zone.id) | 지역 필터, 다시보기 이동 |
| camera_id | FK | BIGINT | - | NULL | N | 대상 캠(camera.id). 캠 이상일 때만 | 캠 이상 이벤트의 대상 표시, 복구 시 자동 종료 |
| started_at | - | DATETIME | - | - | Y | 발생 시각(판정한 1분 통계의 시각) | 목록 정렬·기간 필터, 다시보기 이동 시점(evt-004) |
| ended_at | - | DATETIME | - | NULL | N | 종료 시각. 열려 있으면 NULL | 열린 이벤트 찾기 = 중복 방지(evtdet-004). 지속 시간 = ended_at − started_at |
| peak_level | - | TINYINT | - | NULL | N | 최고 혼잡 단계(2: 주의, 3: 위험). 혼잡 이벤트만 | “주의” 이상으로 오를 때만 이벤트 생성(evtdet-001). 열려 있는 동안 더 오르면 갱신, 단계별 색상(evt-002) |
| peak_value | - | DECIMAL | 10,4 | NULL | N | 최고 값: 혼잡은 밀집도(명/㎡), 급증은 증가율(%) | 상세 화면 표시(evt-003) |
| peak_count | - | INT | - | NULL | N | 이벤트 동안 최고 인원(1분 평균 인원의 최댓값). 캠 이상은 NULL | 이벤트 로그의 인원 표시(SCR-A-010). 혼잡·급증 판정(FNC-A-033·034)에서 최고 값과 함께 갱신 |
| below_since | - | DATETIME | - | NULL | N | 기준 아래로 내려간 시각(혼잡: 단계가 '주의' 미만, 급증: 증가율이 기준 미만이거나 검사 조건 미충족). 다시 넘으면 NULL | 이 상태가 일정 시간(예: 5분) 유지되면 닫음(evtdet-005) |
| threshold_snapshot | - | JSON | - | - | Y | 발생 당시 기준값(혼잡: 단계 경계 밀도, 급증: 비교 시간·증가율·최소 밀집도, 캠 이상: 결과 없음 허용 시간). 설정 파일 값 | 설정을 바꿔 재배포해도 지난 이벤트를 당시 기준으로 해석(evtdet-006) |
| status | - | VARCHAR | 20 | UNCHECKED | Y | 처리 상태: UNCHECKED(미확인) / CHECKED(확인 중) / RESOLVED(조치완료) | 처리 상태 필터, 미확인 배지 수(evt-005·006) |
| action_code | - | VARCHAR | 20 | NULL | N | 조치 항목: ONSITE_OK(현장 확인·정상) / STAFF(인력 배치) / FALSE_ALARM(오탐) / CAM_CHECK(캠 점검 요청) / OTHER(기타). 조치완료일 때만 | 조치완료 시 필수(evt-007). 항목은 코드에 고정 — 오탐 비율 같은 집계에 사용 |
| action_note | - | VARCHAR | 200 | NULL | N | 직접 입력한 조치 내용 | OTHER일 때 필수, 다른 항목일 때는 선택 |
| handled_by | FK | BIGINT | - | NULL | N | 마지막으로 처리 상태를 바꾼 관리자(admin_account.id) | 목록·상세의 처리자 표시(evt-008). 확인·조치완료를 각각 누가 했는지는 작업 기록(histwr-002)으로 확인 |
| handled_at | - | DATETIME | - | NULL | N | 마지막 처리 시각 | 처리 일시 표시(evt-008) |
| created_at | - | DATETIME | - | CURRENT_TIMESTAMP | Y | 기록 시각 | 정렬·추적 |
| updated_at | - | DATETIME | - | CURRENT_TIMESTAMP<br>ON UPDATE | Y | 마지막 수정 시각 | 변경 추적 |

- **인덱스**: (zone_id, type, ended_at) — 열린 이벤트 찾기 / (started_at) — 목록 / (status)

## work_history

작업 기록. 수정·삭제 없이 쌓기만 한다. 로그인·조회 같은 일반 활동은 넣지 않는다. 이벤트 처리 이력도 여기서 찾는다.

| 컬럼명 | 키 | 타입 | 길이 | DEFAULT | NOT NULL | COMMENT | 비고 |
|---|---|---|---|---|---|---|---|
| id | PK | BIGINT | - | AUTO_INCREMENT | Y | 작업 기록 번호 | 정렬 |
| actor_type | - | VARCHAR | 10 | - | Y | 행동한 계정 종류: USER / ADMIN | 사용자·관리자 계정 테이블이 나뉘어 있어 actor_id만으로는 어느 계정인지 알 수 없음 |
| actor_id | - | BIGINT | - | - | Y | 행동한 계정 번호(user_account.id 또는 admin_account.id) | 두 테이블 중 하나를 가리키므로 FK는 걸지 않는다. 계정은 지워지지 않아 참조가 깨지지 않음 |
| actor_login_id | - | VARCHAR | 20 | - | Y | 기록 당시 행동한 계정의 아이디 | 계정 필터(histre-002)·목록 표시를 조인 없이 처리. 사용자와 관리자가 같은 아이디일 수 있어 actor_type과 함께 표시 |
| action | - | VARCHAR | 30 | - | Y | 행동 종류: EXCEL_DOWNLOAD / EVENT_STATUS / ACCOUNT_CHANGE / CAMERA_RUN / ZONE_CHANGE / CAMERA_CHANGE | 행동 종류 필터(histre-002), 기록 대상 범위(histwr-001~003·005·006) |
| target_type | - | VARCHAR | 20 | NULL | N | 대상 종류: USER_ACCOUNT / ADMIN_ACCOUNT / ZONE / CAMERA / EVENT / REGION / ALL. 통계 다운로드는 범위에 따라 ZONE·REGION·ALL, 이벤트 다운로드는 EVENT(target_id 없음) | 대상 표시, 이벤트 상세의 처리 이력 조회(EVENT) |
| target_id | - | BIGINT | - | NULL | N | 대상 번호(전체 다운로드면 NULL) | 대상 화면으로 이동, 대상별 이력 조회 |
| target_name | - | VARCHAR | 100 | NULL | N | 기록 당시 대상 이름(아이디·구역명 등) | 대상이 삭제되거나 이름이 바뀌어도 기록을 그대로 읽을 수 있게 |
| detail | - | JSON | - | NULL | N | 상세: 다운로드 조건(종류·지역·기간·항목), 이전 값·바뀐 값(이벤트는 처리 상태·조치 항목·메모), 가동/정지 등 | 행동마다 내용이 달라 JSON 하나로 둠. 비밀번호 값은 넣지 않고 '변경됨'만 남김(histwr-003) |
| created_at | - | DATETIME | - | CURRENT_TIMESTAMP | Y | 기록 시각 | 기간 필터·최신순 정렬(histre-001) |

- **인덱스**: (created_at) / (actor_type, actor_login_id, created_at) / (action, created_at) / (target_type, target_id, created_at) — 이벤트 처리 이력 조회
