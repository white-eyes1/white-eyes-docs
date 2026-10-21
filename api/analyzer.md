# API 명세 — spring ↔ flask 내부 계약

> 원본: 명세서 시트 'API 명세서'에서 옮김. 이후로는 이 파일이 원본이다.

두 저장소(white-eyes-spring, white-eyes-flask)가 함께 맞춰야 하는 계약. 바꿀 때는 두 저장소를 같이 고친다.

## 내부 API(관리자 앱 8082)

### POST /internal/v1/results — 분석 결과 수신

- **설명**: 1초 결과 묶음 수신
- **관련 요구사항 ID**
  vanly-006
  stagg-001
- **권한**: X-Internal-Token
- **호출 주체**: 분석 서버
- **Request**
  Body
  [{"cameraId": 7, "at": "2026-10-12T14:03:05+09:00", "personCount": 42, "in": {"N": 1, "E": 0, "S": 0, "W": 2}, "out": {…}, "dwellSec": [305.2, 41.0]}]
- **Response**: 204
- **오류 응답**
  400 형식 오류
  401 토큰 불일치
- **비고**: FNC-A-024. 호출하는 기능: FNC-S-006. 최대 2,000건. 분석 서버는 400만 묶음을 버리고, 그 밖의 4xx(401·403·408·429 등)·5xx·연결 실패는 보관 시간(5분) 안에서 다시 보냄

### PATCH /internal/v1/cameras/{id}/status — 캠 상태 보고

- **설명**: 상태·진행률·오류 보고
- **관련 요구사항 ID**
  caman-004~005
  vanly-007
- **권한**: X-Internal-Token
- **호출 주체**: 분석 서버
- **Request**
  Body
  {"status": "PREPARING", "progress": 45, "errorMessage": null}
- **Response**: 204
- **오류 응답**: 401 / 404
- **비고**: FNC-A-025. 호출하는 기능: FNC-S-007·009·012

### POST /internal/v1/recordings — 녹화 등록

- **설명**: 완성된 녹화 등록
- **관련 요구사항 ID**
  rec-001
  rec-003~004
- **권한**: X-Internal-Token
- **호출 주체**: 분석 서버
- **Request**
  Body
  {"cameraId": 7, "startedAt": "2026-10-12T14:03:00.000+09:00", "endedAt": "2026-10-12T14:04:00.000+09:00", "videoPath": "recordings/live/cam7/20261012/cam7_20261012_1403.mp4", "boxPath": "…json.gz"}
- **Response**
  201
  {"id": 900}
- **오류 응답**
  400 경로 규칙
  401 / 404
- **비고**: FNC-A-026. 호출하는 기능: FNC-S-008·010. 더미는 endedAt 없음

### GET /internal/v1/cameras/desired — 가동 대상 캠 목록

- **설명**: run_requested=1인 캠
- **관련 요구사항 ID**: vanly-008
- **권한**: X-Internal-Token
- **호출 주체**: 분석 서버
- **Request**: -
- **Response**
  200
  [{"cameraId": 7, "sourceType": "LIVE", "sourceUri": "rtsp://…"}]
- **오류 응답**: 401
- **비고**: FNC-A-027. 호출하는 기능: FNC-S-012

## 분석 서버(5000)

### POST /analyzer/v1/cameras/{id}/start — 캠 시작

- **설명**: 캠 작업 시작
- **관련 요구사항 ID**
  caman-003
  vanly-005
- **권한**: X-Internal-Token
- **호출 주체**: 관리자 앱
- **Request**
  Body
  {"sourceType": "DUMMY", "sourceUri": "dummy/videos/a.mp4"}
- **Response**
  200
  {"cameraId": 7, "status": "PREPARING"}
- **오류 응답**
  400 SOURCE_NOT_FOUND (DUMMY 파일 없음·경로 규칙 위반·공유 폴더 밖 경로)
  400 INVALID_INPUT (본문 형식 오류. fieldErrors의 field는 sourceType·sourceUri, 본문이 JSON 객체가 아니면 body)
  401
  501 SOURCE_TYPE_NOT_SUPPORTED (LIVE, 2단계 구현 전까지)
  409 CAMERA_STOPPING (정지가 10초 안에 끝나지 않아 같은 캠의 옛 작업 스레드가 아직 살아 있음. 끝나면 다시 시작할 수 있음)
- **비고**: FNC-S-001. 호출하는 기능: FNC-A-020. 타임아웃 5초. 이미 그 캠 작업이 돌고 있으면, 형식이 맞는 요청에 한해 sourceType·sourceUri 값과 상관없이 현재 상태로 200(형식이 틀린 본문은 먼저 400)

### POST /analyzer/v1/cameras/{id}/stop — 캠 정지

- **설명**: 캠 작업 정지
- **관련 요구사항 ID**: caman-003
- **권한**: X-Internal-Token
- **호출 주체**: 관리자 앱
- **Request**: -
- **Response**: 200
- **오류 응답**: 401
- **비고**: FNC-S-002. 호출하는 기능: FNC-A-021·025. 멱등. 응답 본문 없음. 타임아웃 15초(분석 서버가 종료를 최대 10초 기다림). 10초 안에 끝나지 않아도 200을 돌려주고 분석 서버는 WARN 로그만 남김(그 스레드가 끝날 때까지 같은 캠의 시작은 409 CAMERA_STOPPING)

### GET /analyzer/v1/cameras/{id}/live — 실시간 화면

- **설명**: 박스를 그린 MJPEG
- **관련 요구사항 ID**: live-001
- **권한**: X-Internal-Token
- **호출 주체**: nginx
- **Request**: -
- **Response**: 200 multipart/x-mixed-replace; boundary=frame
- **오류 응답**: 401 / 404 작업 없음
- **비고**: FNC-S-011. 호출하는 기능: FNC-A-042(nginx 경유). 외부 노출 금지(nginx만)

### GET /analyzer/v1/cameras/{id}/snapshot — 카드 미리보기

- **설명**: 박스를 그린 최신 프레임 JPEG 1장
- **관련 요구사항 ID**: live-002
- **권한**: X-Internal-Token
- **호출 주체**: nginx
- **Request**: -
- **Response**: 200 image/jpeg (Cache-Control: no-store)
- **오류 응답**: 401 / 404 작업 없음
- **비고**: FNC-S-011. 호출하는 기능: FNC-A-042(nginx 경유). 외부 노출 금지(nginx만)

### GET /analyzer/v1/health — 상태 확인

- **설명**: 분석 서버 상태
- **관련 요구사항 ID**: -
- **권한**: X-Internal-Token
- **호출 주체**: 관리자 앱·운영자
- **Request**: -
- **Response**
  200
  {"status": "UP", "cameras": [{"cameraId": 7, "state": "RUNNING", "lastResultAt": "…"}], "bufferSize": 0}
- **오류 응답**: 401
- **비고**: FNC-S-013
