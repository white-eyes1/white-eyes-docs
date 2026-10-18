# 0007. 대시보드 캠 카드는 연속 영상 대신 2초마다 정지 화면을 받음

- 상태: 채택
- 기록: 2026-10-18
- 출처: 2026-10-18 명세 정리 중 결정. '검토한 안' B·C는 결정 당시 비교한 대안으로, 명세 본문에는 채택안(A)만 있다.
- 관련: requirements.md live-002, api/analyzer.md `GET /analyzer/v1/cameras/{id}/snapshot`, conventions.md nginx `/admin/live/{cameraId}/snapshot`·`CARD_SNAPSHOT_INTERVAL_SEC`, features/admin.md FNC-A-041·042, features/analyzer.md FNC-S-011

## 맥락
화면 시안은 관리자 대시보드의 캠 카드(최대 16장)에 실제 영상을 보여준다. 실시간 화면은 MJPEG(끊지 않는 연결)다.

## 검토한 안
| 안 | 내용 | 판단 |
|---|---|---|
| A | 카드는 박스가 그려진 최신 프레임 JPEG를 2초마다 받음. 보이는 카드만, 탭이 숨겨지면 멈춤. 누르면 MJPEG 실시간 창 | 채택 |
| B | 보이는 카드 최대 4장만 MJPEG | 실시간 창 1 + 카드 4 + SSE 1로 연결 6개가 다 참 |
| C | dev에도 TLS를 붙여 HTTP/2로 전체 MJPEG | 인증서 세팅 필요, 분석 서버 인코딩 부하는 그대로 |

## 근거
- 브라우저는 HTTP/1.1에서 같은 서버로 연결을 6개까지만 연다. 카드마다 MJPEG를 열면 나머지 카드·SSE·API 호출이 막힌다. 시연은 local·dev의 http에서 한다(0004).
- '보는 사람이 있을 때만 영상을 만든다'(live-001) 원칙을 유지한다. 스냅샷은 요청이 있을 때만 만들고 같은 캠은 1초 동안 재사용한다.

## 영향
- 권한 확인(`/api/v1/live/auth`)이 2초마다 불리므로 세션 마지막 접근 시각을 갱신하지 않게 한다(FNC-A-041).
- auth_request 응답은 204·401·403만 쓴다(nginx가 그 밖의 응답을 500으로 바꿈).
- 카드 영상은 2초 간격이라 움직임이 끊겨 보인다. 부드러운 영상은 실시간 창에서 본다.
