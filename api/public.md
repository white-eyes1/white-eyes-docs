# API 명세 — 브라우저 → 앱

> 원본: 명세서 시트 'API 명세서'에서 옮김. 이후로는 이 파일이 원본이다.

관리자 앱 API는 브라우저 주소에 /admin 접두사가 붙는다(nginx 경로 규칙은 conventions.md).

## 인증(공통)

### POST /login — 로그인

- **설명**: 폼 로그인(Spring Security). 관리자 앱은 /admin/login
- **관련 요구사항 ID**
  auth-002
  perm-001~005
- **권한**: 공개
- **호출 주체**: 브라우저
- **Request**
  Form
  username, password, _csrf
- **Response**: 302 → /stats (PENDING: /pending, 비밀번호 변경 필요: /me/password)
- **오류 응답**: 302 → /login?error (문구는 FNC-C-001)
- **비고**: FNC-C-001. JSON API 아님

### POST /logout — 로그아웃

- **설명**: 세션을 끝낸다
- **관련 요구사항 ID**: auth-003
- **권한**: 사용자 이상(두 앱)
- **호출 주체**: 브라우저
- **Request**
  Form
  _csrf
- **Response**: 302 → /login
- **오류 응답**: -
- **비고**: FNC-C-002

## 회원가입(사용자 앱)

### GET /api/v1/signup/check-id — 아이디 중복 확인

- **설명**: 아이디 사용 가능 여부
- **관련 요구사항 ID**: auth-001
- **권한**: 공개
- **호출 주체**: 브라우저
- **Request**
  Query
  loginId
- **Response**
  200
  {"available": true}
- **오류 응답**: 400 아이디 규칙 위반
- **비고**: FNC-U-001. 탈퇴 계정 아이디도 사용 불가

### POST /api/v1/signup — 회원가입

- **설명**: 사용자 계정 생성(PENDING)
- **관련 요구사항 ID**
  auth-001
  perm-002
- **권한**: 공개
- **호출 주체**: 브라우저
- **Request**
  Body
  {"loginId": "hong01", "password": "abcd1234", "passwordConfirm": "abcd1234", "name": "홍길동", "email": "a@b.com", "phone": "010-1234-5678"}
- **Response**
  201
  {"id": 21, "status": "PENDING"}
- **오류 응답**
  400 검증 실패(fieldErrors)
  409 DUPLICATE_LOGIN_ID
- **비고**: FNC-U-002

## 내 정보(공통)

### GET /api/v1/me — 내 정보 조회

- **설명**: 로그인한 계정 정보
- **관련 요구사항 ID**: auth-004
- **권한**: 사용자 이상(두 앱)
- **호출 주체**: 브라우저
- **Request**: -
- **Response**
  200
  {"id": 21, "loginId": "hong01", "name": "홍길동", "email": "a@b.com", "phone": "010-1234-5678", "status": "ACTIVE", "mustChangePassword": false}
  관리자 앱 응답에는 "role": "ADMIN" 또는 "SUPER_ADMIN"이 추가된다(사용자에는 role이 없음)
- **오류 응답**: 401
- **비고**: FNC-C-006

### PATCH /api/v1/me — 내 정보 수정

- **설명**: 이름·메일·연락처 수정
- **관련 요구사항 ID**: auth-004
- **권한**: 사용자 이상(두 앱)
- **호출 주체**: 브라우저
- **Request**
  Body
  {"name": "홍길동", "email": "a@b.com", "phone": "010-1234-5678"}
- **Response**
  200
  수정된 내 정보
- **오류 응답**: 400 검증 실패
- **비고**: FNC-C-006. 보낸 필드만 수정

### PATCH /api/v1/me/password — 비밀번호 변경

- **설명**: 현재 비밀번호 확인 후 변경, 다른 세션 삭제
- **관련 요구사항 ID**
  auth-004
  acman-009
- **권한**: 사용자 이상(두 앱)
- **호출 주체**: 브라우저
- **Request**
  Body
  {"currentPassword": "…", "newPassword": "…", "newPasswordConfirm": "…"}
- **Response**: 204
- **오류 응답**
  400 WRONG_PASSWORD
  400 검증 실패
- **비고**: FNC-C-007. must_change_password=1이어도 호출 가능

### DELETE /api/v1/me — 회원 탈퇴

- **설명**: 비밀번호 확인 후 WITHDRAWN 처리(사용자 앱만)
- **관련 요구사항 ID**: auth-005
- **권한**: 사용자
- **호출 주체**: 브라우저
- **Request**
  Body
  {"password": "…"}
- **Response**: 204 (세션 삭제됨)
- **오류 응답**: 400 WRONG_PASSWORD
- **비고**: FNC-U-004

## 지역·지도(공통)

### GET /api/v1/regions — 하위 지역 목록

- **설명**: 시·도 목록 또는 지역의 바로 아래 지역
- **관련 요구사항 ID**
  map-001
  loca-001
- **권한**: 사용자 이상(두 앱)
- **호출 주체**: 브라우저
- **Request**
  Query
  parentId (없으면 시·도 목록)
- **Response**
  200
  [{"id": 3, "level": "EMD", "code": "25020510", "name": "은행선화동", "centerLat": 36.33, "centerLng": 127.43, "boundary": {GeoJSON}}]
- **오류 응답**: 404 REGION_NOT_FOUND
- **비고**: FNC-C-008

### GET /api/v1/zones — 동의 구역 목록

- **설명**: 동에 속한 구역 또는 전체 구역(삭제 제외)
- **관련 요구사항 ID**
  map-001
  loca-003
- **권한**: 사용자 이상(두 앱)
- **호출 주체**: 브라우저
- **Request**: Query / dongId(선택, 없으면 삭제되지 않은 모든 구역)
- **Response**
  200
  [{"id": 15, "dongId": 3, "name": "궁동 1구역", "areaM2": 2500.0, "centerLat": 36.3621, "centerLng": 127.3449, "boundary": {GeoJSON}, "hasCamera": true}]
- **오류 응답**: 404 REGION_NOT_FOUND
- **비고**: FNC-C-008. 항목마다 `deleted`(boolean)가 있고 이 목록에서는 항상 false(삭제된 구역은 목록에 없음)

### GET /api/v1/zones/{id} — 구역 하나(삭제된 구역 포함)

- **설명**: 번호로 구역 하나를 조회. 삭제 표시된 구역도 준다(`deleted: true`). 지난 통계·다시보기 화면이 삭제된 구역의 이름에 '(삭제됨)'을 붙일 때 쓴다
- **관련 요구사항 ID**: loca-005
- **권한**: 사용자 이상(두 앱)
- **호출 주체**: 브라우저
- **Request**: Path / id
- **Response**
  200
  {"id": 15, "dongId": 3, "name": "궁동 1구역", "areaM2": 2500.0, "centerLat": 36.3621, "centerLng": 127.3449, "boundary": {GeoJSON}, "hasCamera": false, "deleted": true}
- **오류 응답**: 404 ZONE_NOT_FOUND(없는 구역)
- **비고**: FNC-C-008, FNC-A-017 업무 규칙('(삭제됨)' 표시)

### GET /api/v1/map/status — 혼잡 단계 현황

- **설명**: 하위 단위별(또는 대상 아래 모든 구역의) 최근 1분 통계·혼잡 단계·오늘 이벤트 수
- **관련 요구사항 ID**
  map-003
  evthres-001
- **권한**: 사용자 이상(두 앱)
- **호출 주체**: 브라우저
- **Request**
  Query
  regionId, unit(CHILD 기본: 바로 아래 단위, 동이면 구역 / ZONE: 대상 아래 모든 구역)
- **Response**
  200
  {"unitType": "ZONE", "items": [{"id": 15, "name": "궁동 1구역", "centerLat": 36.3621, "centerLng": 127.3449, "countAvg": 120.4, "density": 0.92, "level": 2, "statAt": "2026-10-12T14:03:00+09:00", "todayEventCount": 1, "ongoingEvent": true}]}
  (centerLat·centerLng는 ZONE일 때만)
- **오류 응답**: 404
- **비고**: FNC-C-009·030. 5분 안에 통계 없으면 level=null

### GET /api/v1/map/flows — 이동 흐름

- **설명**: 기간의 구역 간 이동량
- **관련 요구사항 ID**
  stats-006
  map-002
- **권한**: 사용자 이상(두 앱)
- **호출 주체**: 브라우저
- **Request**
  Query
  regionId, from, to
- **Response**
  200
  [{"fromZoneId": 15, "toZoneId": 16, "direction": "E", "count": 340}]
  (toZoneId=null: 관측 범위 밖)
- **오류 응답**: 400 INVALID_RANGE
- **비고**: FNC-C-010

### GET /api/v1/map/heatmap — 시간대별 히트맵

- **설명**: 하위 단위의 시간대(0~23시)별 평균
- **관련 요구사항 ID**: hitm-001~003
- **권한**: 사용자 이상(두 앱)
- **호출 주체**: 브라우저
- **Request**
  Query
  regionId, from, to, item(COUNT/DENSITY/INFLOW/OUTFLOW), dayType(ALL/WEEKDAY/WEEKEND)
- **Response**
  200
  {"units": [15, 16], "values": {"15": [24개, null 가능]}, "min": 0, "max": 310}
- **오류 응답**: 400 기간 1년 초과
- **비고**: FNC-C-011

### GET /api/v1/meta/levels — 혼잡 단계 기준

- **설명**: 단계 이름·색·경계값
- **관련 요구사항 ID**
  evthres-001~002
  map-003
- **권한**: 사용자 이상(두 앱)
- **호출 주체**: 브라우저
- **Request**: -
- **Response**
  200
  [{"level": 1, "name": "정상", "color": "#3BC99B", "minDensity": 0}, {"level": 2, "name": "주의", "color": "#F59E0B", "minDensity": 0.7}, {"level": 3, "name": "위험", "color": "#EF4D55", "minDensity": 1.5}]
- **오류 응답**: -
- **비고**: FNC-C-025

## 통계(공통)

### GET /api/v1/stats/series — 통계 시계열

- **설명**: 구역·지역 통계를 단위별로 조회
- **관련 요구사항 ID**
  stats-001~008
  stagraph-001
  demo-002
- **권한**: 사용자 이상(두 앱)
- **호출 주체**: 브라우저
- **Request**
  Query
  targetType(ZONE/REGION), targetId, interval(1m/1h/1d/1w/1M/1y), from, to
- **Response**
  200
  {"items": [{"at": "…", "countAvg": 120.4, "countMax": 150, "countMin": 90, "density": 0.92, "level": 2, "inflow": {"N": 10, "E": 4, "S": 0, "W": 7}, "outflow": {…}, "dwellAvgSec": 312.5, "sampleSec": 3600, "isDemo": false}]}
- **오류 응답**
  400 RANGE_TOO_LONG
  404 대상 없음
- **비고**: FNC-C-012·024·030, FNC-A-040·047

### GET /api/v1/stats/children — 하위 지역 비교

- **설명**: 하위 단위 계열을 겹쳐 그리기 위한 조회
- **관련 요구사항 ID**: stagraph-002
- **권한**: 사용자 이상(두 앱)
- **호출 주체**: 브라우저
- **Request**
  Query
  regionId, item, interval, from, to
- **Response**
  200
  {"series": [{"id": 15, "name": "궁동 1구역", "points": [{"at": "…", "value": 120.4}]}], "omitted": 2}
- **오류 응답**: 400 RANGE_TOO_LONG
- **비고**: FNC-C-014. 최대 10개

### GET /api/v1/stats/stream — 실시간 통계 스트림

- **설명**: 새 1분 통계를 SSE로 받음
- **관련 요구사항 ID**: stupdate-001
- **권한**: 사용자 이상(두 앱)
- **호출 주체**: 브라우저
- **Request**
  Query
  regionId
- **Response**
  200 text/event-stream
  event: stat
  data: {"statAt": "…", "items": [{"zoneId": 15, "countAvg": 120.4, "density": 0.92, "level": 2}]}
- **오류 응답**: 401
- **비고**: FNC-C-022. retry 5000, 30초마다 주석 줄

### GET /api/v1/stats/export — 통계 엑셀 다운로드

- **설명**: 통계를 xlsx로 받음
- **관련 요구사항 ID**
  xlsx-001~002
  histwr-001
- **권한**: 사용자 이상(두 앱)
- **호출 주체**: 브라우저
- **Request**
  Query
  scope(ZONE/REGION/ALL), targetId, from, to, interval, items(복수), expand(true: 구역별 펼침)
- **Response**
  200 application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
  Content-Disposition: attachment; filename*=UTF-8''stats_….xlsx
- **오류 응답**: 400 RANGE_TOO_LONG / TOO_MANY_ROWS
- **비고**: FNC-C-023. 작업 기록 저장

## 대시보드(공통)

### GET /api/v1/dashboard/summary — 현재 현황 요약

- **설명**: 현재 인원·밀집도·단계·유입/유출·주요 방향·오늘 이벤트 수·캠 수·오늘 최대 인원
- **관련 요구사항 ID**
  das-001
  das-003
- **권한**: 사용자 이상(두 앱)
- **호출 주체**: 브라우저
- **Request**
  Query
  targetType, targetId
- **Response**
  200
  {"statAt": "…", "countAvg": 120.4, "density": 0.92, "level": 2, "inflow": 21, "outflow": 18, "mainDirection": "E", "todayEventCount": 3, "cameraCount": 16, "runningCameraCount": 4, "todayMaxCount": 247}
- **오류 응답**: 404
- **비고**: FNC-C-016·017

### GET /api/v1/dashboard/hourly-levels — 시간대별 혼잡 단계

- **설명**: 날짜의 0~23시 혼잡 단계
- **관련 요구사항 ID**: das-004
- **권한**: 사용자 이상(두 앱)
- **호출 주체**: 브라우저
- **Request**
  Query
  targetType, targetId, date
- **Response**
  200
  [{"hour": 0, "level": 1, "density": 0.05}, … 24개, 없으면 null]
- **오류 응답**: -
- **비고**: FNC-C-018

### GET /api/v1/dashboard/trend — 이용량 증감

- **설명**: 지난주·지난달·지난해 대비 증감률
- **관련 요구사항 ID**: das-005
- **권한**: 사용자 이상(두 앱)
- **호출 주체**: 브라우저
- **Request**
  Query
  targetType, targetId
- **Response**
  200
  {"weekRate": 12.5, "monthRate": -3.1, "yearRate": null}
- **오류 응답**: -
- **비고**: FNC-C-019

### GET /api/v1/dashboard/visit-pattern — 방문 패턴

- **설명**: 요일×시간대 평균 인원
- **관련 요구사항 ID**: das-006
- **권한**: 사용자 이상(두 앱)
- **호출 주체**: 브라우저
- **Request**
  Query
  targetType, targetId, from, to
- **Response**
  200
  {"cells": [{"weekday": 1, "hour": 9, "avgCount": 88.1}], "weekdayAvg": [24개], "weekendAvg": [24개]}
- **오류 응답**: 400 기간 1년 초과
- **비고**: FNC-C-028

### GET /api/v1/dashboard/peak-hours — 피크 타임 TOP 3

- **설명**: 평균 인원 상위 3개 시간대
- **관련 요구사항 ID**: das-010
- **권한**: 사용자 이상(두 앱)
- **호출 주체**: 브라우저
- **Request**
  Query
  targetType, targetId, period(DAY/WEEK/MONTH/YEAR)
- **Response**
  200
  [{"rank": 1, "hour": 18, "avgCount": 240.2}]
- **오류 응답**: -
- **비고**: FNC-C-029

## 기간 비교(공통)

### GET /api/v1/compare — 기간 비교

- **설명**: 같은 요일·시간대끼리 비교, 비정상 변동 표시
- **관련 요구사항 ID**: cmp-001~003
- **권한**: 사용자 이상(두 앱)
- **호출 주체**: 브라우저
- **Request**
  Query
  targetType, targetId, from, to, baseFrom, baseTo 또는 basePreset(LAST_MONTH/LAST_YEAR), thresholdPct(기본 30)
- **Response**
  200
  {"cells": [{"weekday": 1, "hour": 9, "targetAvg": 120, "baseAvg": 80, "rate": 50.0, "abnormal": true}], "totalRate": 8.2}
- **오류 응답**: 400 INVALID_RANGE
- **비고**: FNC-C-020

## 사용자 관리(관리자 앱)

### GET /api/v1/users — 사용자 목록

- **설명**: 사용자 검색·필터·정렬
- **관련 요구사항 ID**
  aclst-001
  aclst-003~004
- **권한**: 관리자 이상
- **호출 주체**: 브라우저
- **Request**
  Query
  keyword, status, joinedFrom, joinedTo, active, sort(createdAt|loginId|lastActiveAt,asc|desc), page, size
  joinedFrom·joinedTo는 날짜이고 둘 다 그날을 포함
- **Response**
  200
  {"items": [{"id": 21, "loginId": "hong01", "name": "홍길동", "email": "…", "phone": "…", "status": "PENDING", "createdAt": "…", "lastActiveAt": "…", "active": false}], "page": 0, "size": 20, "totalElements": 1, "totalPages": 1, "truncated": false}
- **오류 응답**: -
- **비고**: FNC-A-002

### PATCH /api/v1/users/{id} — 사용자 정보 수정

- **설명**: 이름·메일·연락처 수정
- **관련 요구사항 ID**
  acman-001
  histwr-003
- **권한**: 관리자 이상
- **호출 주체**: 브라우저
- **Request**
  Body
  {"name": "…", "email": "…", "phone": "…"}
- **Response**: 200 수정된 사용자
- **오류 응답**: 400 / 404
- **비고**: FNC-A-004

### POST /api/v1/users/{id}/reset-password — 사용자 비밀번호 재설정

- **설명**: 임시 비밀번호 발급
- **관련 요구사항 ID**
  acman-001
  histwr-003
- **권한**: 관리자 이상
- **호출 주체**: 브라우저
- **Request**: -
- **Response**
  200
  {"temporaryPassword": "aB3dE5fG7hJ9"}
- **오류 응답**: 404
- **비고**: FNC-A-005. 한 번만 표시

### POST /api/v1/users/{id}/approve — 사용자 승인

- **설명**: PENDING → ACTIVE
- **관련 요구사항 ID**
  acman-002
  histwr-003
- **권한**: 관리자 이상
- **호출 주체**: 브라우저
- **Request**: -
- **Response**: 204
- **오류 응답**: 409 INVALID_STATUS
- **비고**: FNC-A-006

### POST /api/v1/users/{id}/unapprove — 사용자 승인 취소

- **설명**: ACTIVE → PENDING, 세션 삭제
- **관련 요구사항 ID**
  acman-003
  histwr-003
- **권한**: 관리자 이상
- **호출 주체**: 브라우저
- **Request**: -
- **Response**: 204
- **오류 응답**: 409 INVALID_STATUS
- **비고**: FNC-A-007

### POST /api/v1/users/{id}/logout — 사용자 강제 로그아웃

- **설명**: 세션 모두 삭제
- **관련 요구사항 ID**
  acman-007
  histwr-003
- **권한**: 관리자 이상
- **호출 주체**: 브라우저
- **Request**: -
- **Response**
  200
  {"deletedSessions": 2}
- **오류 응답**: 404
- **비고**: FNC-A-008

## 관리자 관리(관리자 앱)

### GET /api/v1/admins — 관리자 목록

- **설명**: 관리자 검색·최근 활동
- **관련 요구사항 ID**: aclst-002~004
- **권한**: 최고 관리자
- **호출 주체**: 브라우저
- **Request**
  Query
  keyword, status, active, sort, page, size
- **Response**: 200 페이지 응답(사용자 목록과 같은 형식 + role)
- **오류 응답**: 403
- **비고**: FNC-A-003

### POST /api/v1/admins — 관리자 계정 생성

- **설명**: 관리자 계정 생성, 임시 비밀번호 발급
- **관련 요구사항 ID**
  acman-009
  histwr-003
- **권한**: 최고 관리자
- **호출 주체**: 브라우저
- **Request**
  Body
  {"loginId": "admin02", "name": "김관리", "email": "…", "phone": "…"}
- **Response**
  201
  {"id": 5, "temporaryPassword": "…"}
- **오류 응답**: 400 / 409 DUPLICATE_LOGIN_ID
- **비고**: FNC-A-009

### PATCH /api/v1/admins/{id} — 관리자 정보 수정

- **설명**: 이름·메일·연락처 수정
- **관련 요구사항 ID**
  acman-004
  histwr-003
- **권한**: 최고 관리자
- **호출 주체**: 브라우저
- **Request**
  Body
  {"name": "…", "email": "…", "phone": "…"}
- **Response**: 200
- **오류 응답**: 400 / 404
- **비고**: FNC-A-010

### POST /api/v1/admins/{id}/reset-password — 관리자 비밀번호 재설정

- **설명**: 임시 비밀번호 발급
- **관련 요구사항 ID**
  acman-004
  histwr-003
- **권한**: 최고 관리자
- **호출 주체**: 브라우저
- **Request**: -
- **Response**
  200
  {"temporaryPassword": "…"}
- **오류 응답**: 404
- **비고**: FNC-A-010

### POST /api/v1/admins/{id}/disable — 관리자 비활성화

- **설명**: ACTIVE → DISABLED, 세션 삭제
- **관련 요구사항 ID**
  acman-006
  histwr-003
- **권한**: 최고 관리자
- **호출 주체**: 브라우저
- **Request**: -
- **Response**: 204
- **오류 응답**
  400 최고 관리자 대상 불가
  409 INVALID_STATUS
- **비고**: FNC-A-011

### POST /api/v1/admins/{id}/enable — 관리자 활성화

- **설명**: DISABLED → ACTIVE
- **관련 요구사항 ID**
  acman-006
  histwr-003
- **권한**: 최고 관리자
- **호출 주체**: 브라우저
- **Request**: -
- **Response**: 204
- **오류 응답**: 409 INVALID_STATUS
- **비고**: FNC-A-011

### POST /api/v1/admins/{id}/logout — 관리자 강제 로그아웃

- **설명**: 세션 모두 삭제
- **관련 요구사항 ID**
  acman-008
  histwr-003
- **권한**: 최고 관리자
- **호출 주체**: 브라우저
- **Request**: -
- **Response**
  200
  {"deletedSessions": 1}
- **오류 응답**: 400 자기 자신
- **비고**: FNC-A-008

## 구역 관리(관리자 앱)

### POST /api/v1/manage/zones/preview — 구역 미리보기 계산

- **설명**: 면적·소속 동 계산
- **관련 요구사항 ID**: loca-003
- **권한**: 관리자 이상
- **호출 주체**: 브라우저
- **Request**
  Body
  {"boundary": {"type": "Polygon", "coordinates": [[[127.35, 36.36], …]]}}
- **Response**
  200
  {"areaM2": 2481.3, "dongId": 3, "dongName": "궁동"}
- **오류 응답**: 400 INVALID_POLYGON / OUT_OF_SERVICE_AREA
- **비고**: FNC-A-013

### POST /api/v1/manage/zones — 구역 등록

- **설명**: 구역 생성
- **관련 요구사항 ID**
  loca-003
  histwr-006
- **권한**: 관리자 이상
- **호출 주체**: 브라우저
- **Request**
  Body
  {"name": "궁동 1구역", "boundary": {GeoJSON Polygon}}
- **Response**
  201
  {"id": 15, "dongId": 3, "name": "궁동 1구역", "areaM2": 2481.3}
- **오류 응답**: 400 / 409 DUPLICATE_ZONE_NAME
- **비고**: FNC-A-014. 면적·동은 서버가 계산

### PATCH /api/v1/manage/zones/{id} — 구역 수정

- **설명**: 이름·다각형 수정(같은 동 안)
- **관련 요구사항 ID**
  loca-002
  histwr-006
- **권한**: 관리자 이상
- **호출 주체**: 브라우저
- **Request**
  Body
  {"name": "…", "boundary": {…}} (보낸 필드만)
- **Response**: 200 수정된 구역
- **오류 응답**
  400 DONG_CHANGE_NOT_ALLOWED
  404 / 409
- **비고**: FNC-A-015

### DELETE /api/v1/manage/zones/{id} — 구역 삭제

- **설명**: 이력 없으면 실제 삭제, 있으면 삭제 표시
- **관련 요구사항 ID**
  loca-005
  histwr-006
- **권한**: 관리자 이상
- **호출 주체**: 브라우저
- **Request**: -
- **Response**
  200
  {"mode": "SOFT"} (또는 HARD)
- **오류 응답**: 409 CAMERA_RUNNING
- **비고**: FNC-A-017

### GET /api/v1/manage/zones/{id}/neighbors — 구역 이웃 조회

- **설명**: 4방향 이웃
- **관련 요구사항 ID**: loca-004
- **권한**: 관리자 이상
- **호출 주체**: 브라우저
- **Request**: -
- **Response**
  200
  {"N": null, "E": {"id": 16, "name": "궁동 2구역"}, "S": null, "W": null}
- **오류 응답**: 404
- **비고**: FNC-A-016

### PUT /api/v1/manage/zones/{id}/neighbors — 구역 이웃 저장

- **설명**: 4방향 이웃 저장, 반대쪽 자동 반영
- **관련 요구사항 ID**
  loca-004
  histwr-006
- **권한**: 관리자 이상
- **호출 주체**: 브라우저
- **Request**
  Body
  {"N": null, "E": 16, "S": null, "W": 14}
- **Response**: 200 저장된 4방향
- **오류 응답**
  400 자기 자신
  404 없는 구역
- **비고**: FNC-A-016

## 캠 관리(관리자 앱)

### GET /api/v1/manage/cameras — 캠 목록

- **설명**: 모든 캠 상태(삭제 제외)와 대시보드 캠 카드용 구역 통계
- **관련 요구사항 ID**: caman-004~005
- **권한**: 관리자 이상
- **호출 주체**: 브라우저
- **Request**: Query / regionId(선택)
- **Response**
  200 / [{"id": 7, "zoneId": 15, "zoneName": "궁동 1구역", "regionPath": "유성구 · 궁동", "areaM2": 2500.0, "name": "궁동1-캠", "sourceType": "DUMMY", "sourceUri": "dummy/videos/a.mp4", "status": "RUNNING", "progress": null, "errorMessage": null, "runRequested": true, "stat": {"statAt": "…", "countAvg": 120.4, "density": 0.92, "level": 2}, "todayEventCount": 1, "recent10m": [{"at": "…", "countAvg": 118.0}, … 최대 10개]}]
  (stat은 5분 안에 통계가 없으면 null)
- **오류 응답**: -
- **비고**: FNC-A-022

### POST /api/v1/manage/cameras — 캠 등록

- **설명**: 구역에 캠 등록
- **관련 요구사항 ID**
  caman-001
  histwr-006
- **권한**: 관리자 이상
- **호출 주체**: 브라우저
- **Request**
  Body
  {"zoneId": 15, "name": "…", "sourceType": "LIVE", "sourceUri": "rtsp://…"}
- **Response**: 201 캠 정보(status=STOPPED)
- **오류 응답**
  400 주소 규칙
  404 ZONE_NOT_FOUND
  409 ZONE_HAS_CAMERA
- **비고**: FNC-A-018

### PATCH /api/v1/manage/cameras/{id} — 캠 정보 수정

- **설명**: 정지 상태에서 수정
- **관련 요구사항 ID**
  caman-002
  histwr-006
- **권한**: 관리자 이상
- **호출 주체**: 브라우저
- **Request**
  Body
  {"name": "…", "sourceType": "…", "sourceUri": "…"}
- **Response**: 200
- **오류 응답**: 409 CAMERA_NOT_STOPPED
- **비고**: FNC-A-019

### DELETE /api/v1/manage/cameras/{id} — 캠 삭제

- **설명**: 캠 삭제(이력 있으면 삭제 표시)
- **관련 요구사항 ID**
  caman-006
  histwr-006
- **권한**: 관리자 이상
- **호출 주체**: 브라우저
- **Request**: -
- **Response**
  200
  {"mode": "HARD"}
- **오류 응답**: 409 CAMERA_NOT_STOPPED
- **비고**: FNC-A-023

### POST /api/v1/manage/cameras/{id}/start — 캠 가동

- **설명**: 분석 시작 지시
- **관련 요구사항 ID**
  caman-003
  histwr-005
- **권한**: 관리자 이상
- **호출 주체**: 브라우저
- **Request**: -
- **Response**
  200
  {"status": "PREPARING"}
- **오류 응답**: 409 INVALID_STATUS / 409 CAMERA_STOPPING(직전 정지가 아직 끝나지 않음. 캠 상태는 요청 전 그대로) / 422 SOURCE_NOT_FOUND / 502 ANALYZER_UNAVAILABLE
- **비고**: FNC-A-020

### POST /api/v1/manage/cameras/{id}/stop — 캠 정지

- **설명**: 분석 중지 지시
- **관련 요구사항 ID**
  caman-003
  histwr-005
- **권한**: 관리자 이상
- **호출 주체**: 브라우저
- **Request**: -
- **Response**
  200
  {"status": "STOPPED", "warning": null 또는 "분석 서버에 전달 실패"}
- **오류 응답**: 404
- **비고**: FNC-A-021

## 이벤트(관리자 앱)

### GET /api/v1/events — 이벤트 목록

- **설명**: 이벤트 최신순 조회·필터
- **관련 요구사항 ID**: evt-001~002
- **권한**: 관리자 이상
- **호출 주체**: 브라우저
- **Request**
  Query
  from, to, regionId 또는 zoneId, types(복수), statuses(복수), keyword(캠·구역·지역 이름), page, size
- **Response**
  200 페이지 응답
  items: [{"id": 101, "type": "CONGESTION", "zoneId": 15, "zoneName": "궁동 1구역", "regionPath": "유성구 · 궁동", "cameraName": "궁동1-캠", "zoneDeleted": false, "startedAt": "…", "endedAt": null, "ongoing": true, "durationSec": 600, "peakLevel": 3, "peakValue": 1.64, "peakCount": 48, "status": "UNCHECKED"}]
- **오류 응답**: -
- **비고**: FNC-A-036·047. `cameraName`: 캠 이상만 값(이벤트의 캠 이름), 혼잡·급증은 구역 단위 이벤트라 `camera_id`가 없어 null

### GET /api/v1/events/{id} — 이벤트 상세

- **설명**: 상세·처리 이력
- **관련 요구사항 ID**
  evt-003
  histwr-002
- **권한**: 관리자 이상
- **호출 주체**: 브라우저
- **Request**: -
- **Response**
  200
  {…목록 필드, "thresholdSnapshot": {…}, "cameraId": null, "actionCode": null, "actionNote": null, "handledBy": null, "handledAt": null, "histories": [{"at": "…", "loginId": "admin02", "from": "UNCHECKED", "to": "CHECKED", "actionCode": null, "actionNote": null}], "playbackAvailable": true}
- **오류 응답**: 404
- **비고**: FNC-A-037

### PATCH /api/v1/events/{id}/status — 처리 상태 변경

- **설명**: 상태·조치 항목 저장
- **관련 요구사항 ID**
  evt-006~008
  histwr-002
- **권한**: 관리자 이상
- **호출 주체**: 브라우저
- **Request**
  Body
  {"expectedStatus": "UNCHECKED", "status": "RESOLVED", "actionCode": "STAFF", "actionNote": "인력 2명 배치"}
- **Response**: 200 변경된 이벤트
- **오류 응답**
  400 항목 누락
  409 STATUS_CONFLICT
- **비고**: FNC-A-038

### GET /api/v1/events/unchecked-count — 미확인 이벤트 수

- **설명**: 헤더 배지 숫자
- **관련 요구사항 ID**: evt-005
- **권한**: 관리자 이상
- **호출 주체**: 브라우저
- **Request**: -
- **Response**
  200
  {"count": 4}
- **오류 응답**: -
- **비고**: FNC-A-048(첫 화면 표시용)

### GET /api/v1/events/summary — 이벤트 요약

- **설명**: 처리 상태별 건수
- **관련 요구사항 ID**: evt-001
- **권한**: 관리자 이상
- **호출 주체**: 브라우저
- **Request**
  Query
  from, to, regionId 또는 zoneId, types(복수), keyword
- **Response**
  200
  {"total": 4, "unchecked": 3, "checked": 1, "resolved": 0}
- **오류 응답**: -
- **비고**: FNC-A-036, FNC-C-030. 목록과 같은 조건(상태 제외)

### GET /api/v1/events/export — 이벤트 엑셀 다운로드

- **설명**: 현재 필터로 이벤트 xlsx
- **관련 요구사항 ID**
  xlsx-003
  histwr-001
- **권한**: 관리자 이상
- **호출 주체**: 브라우저
- **Request**
  Query
  목록과 같은 필터(page·size 제외)
- **Response**: 200 xlsx 파일 (events_{from}_{to}.xlsx)
- **오류 응답**: 400 TOO_MANY_ROWS
- **비고**: FNC-A-039

### GET /api/v1/notifications/stream — 관리자 알림 스트림

- **설명**: 새 이벤트·미확인 수·캠 상태 SSE
- **관련 요구사항 ID**
  evt-005
  caman-004
- **권한**: 관리자 이상
- **호출 주체**: 브라우저
- **Request**: -
- **Response**
  200 text/event-stream
  event: event-created / unchecked-count / camera-status
  data: JSON(FNC-A-048)
- **오류 응답**: 401
- **비고**: FNC-A-048

## 영상(관리자 앱)

### GET /api/v1/playback — 다시보기 녹화 찾기

- **설명**: 구역·시각의 녹화와 시작 위치
- **관련 요구사항 ID**: repfocus-001~002
- **권한**: 관리자 이상
- **호출 주체**: 브라우저
- **Request**: Query / zoneId, at 또는 latest=true(가장 최근 녹화)
- **Response**
  200
  {"recordingId": 900, "videoUrl": "/admin/api/v1/recordings/900/video", "boxesUrl": "/admin/api/v1/recordings/900/boxes", "seekSec": 37.5, "startedAt": "…", "endedAt": "…"}
  (latest=true면 seekSec=0)
- **오류 응답**
  404 RECORDING_NOT_FOUND('영상 없음')
  404 RECORDING_EXPIRED('보관 기간 지남')
- **비고**: FNC-A-043(FNC-A-040·047에서 호출)

### GET /api/v1/playback/ranges — 다시보기 녹화 구간 조회

- **설명**: 구역의 시간 범위 안에서 녹화가 있는 구간 목록(다시보기 시간축의 '녹화 있음/없음' 띠)
- **관련 요구사항 ID**: repfocus-005
- **권한**: 관리자 이상
- **호출 주체**: 브라우저
- **Request**: Query / zoneId, from, to(ISO-8601, 범위는 24시간 이내)
- **Response**
  200
  {"ranges": [{"from": "…", "to": "…"}]}
  (구간은 시간순, 서로 겹치거나 2초 이하로 떨어진 것은 하나로 합침. 요청 범위를 벗어난 부분은 자름. 녹화가 없으면 빈 목록)
- **오류 응답**
  400 INVALID_INPUT (from ≥ to, 범위가 24시간 초과, 시각 형식 오류)
- **비고**: FNC-A-043(구간 조회)·FNC-A-047에서 호출. 보관 기간(RECORDING_RETENTION_DAYS, 기본 30일)을 넘은 부분은 구간에 넣지 않음

### GET /api/v1/recordings/{id}/next — 다음 녹화

- **설명**: 같은 캠의 이어지는 녹화
- **관련 요구사항 ID**: repfocus-003
- **권한**: 관리자 이상
- **호출 주체**: 브라우저
- **Request**: -
- **Response**: 200 다시보기와 같은 형식(seekSec=0)
- **오류 응답**: 404 이후 영상 없음
- **비고**: FNC-A-045

### GET /api/v1/recordings/{id}/video — 녹화 영상 파일

- **설명**: 권한 확인 후 nginx가 mp4 전송
- **관련 요구사항 ID**
  repfocus-001
  sec-004
- **권한**: 관리자 이상
- **호출 주체**: 브라우저
- **Request**
  Header
  Range(선택)
- **Response**
  200/206 video/mp4
  (앱 응답 헤더 X-Accel-Redirect: /protected/media/{video_path})
- **오류 응답**: 404
- **비고**: FNC-A-044

### GET /api/v1/recordings/{id}/boxes — 좌표 파일

- **설명**: 권한 확인 후 nginx가 좌표 파일 전송
- **관련 요구사항 ID**
  repfocus-004
  sec-004
- **권한**: 관리자 이상
- **호출 주체**: 브라우저
- **Request**: -
- **Response**
  200 application/json (Content-Encoding: gzip)
  형식: 설정·규약 시트 '좌표 파일 형식'
- **오류 응답**: 404
- **비고**: FNC-A-044·046

### GET /api/v1/live/auth — 실시간 화면 권한 확인

- **설명**: nginx auth_request용
- **관련 요구사항 ID**
  live-001~002
  sec-004
- **권한**: 관리자 이상
- **호출 주체**: nginx
- **Request**
  Query
  cameraId
  Cookie
  ADMIN_SESSION
- **Response**: 204
- **오류 응답**: 401 로그인 없음 / 403 권한 없음·가동 중 아님 (nginx auth_request는 2xx·401·403 외 응답을 500으로 처리하므로 404를 쓰지 않음)
- **비고**: FNC-A-041. 브라우저 주소: /admin/live/{cameraId}

## 작업 기록(관리자 앱)

### GET /api/v1/histories — 작업 기록 조회

- **설명**: 작업 기록 최신순 조회
- **관련 요구사항 ID**: histre-001~002
- **권한**: 최고 관리자
- **호출 주체**: 브라우저
- **Request**: Query / from, to, actorType(USER/ADMIN, 선택), loginId, action, page, size
- **Response**
  200 페이지 응답
  items: [{"id": 1, "at": "…", "actorType": "ADMIN", "loginId": "admin02", "action": "EVENT_STATUS", "targetType": "EVENT", "targetId": 101, "targetName": "궁동 1구역 혼잡", "detail": {…}}]
- **오류 응답**: 403
- **비고**: FNC-A-053
