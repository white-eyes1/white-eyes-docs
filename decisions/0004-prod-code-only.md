# 0004. prod에는 코드만 올리고 시연은 local·dev에서 함

- 상태: 채택
- 기록: 2026-10-18
- 관련: overview.md '기술 스택·외부 연동 사양 > 결정 필요 항목 요약', '더미데이터 사용 방식', requirements.md demo-002

## 결정
prod에는 코드만 배포한다. 더미 캠 영상과 시연용 통계 데이터는 local·dev에만 넣고, 시연은 local·dev에서 한다.

## 근거 (인용)
- overview.md: "prod는 코드만(더미 캠 영상·시연용 데이터는 local·dev에만, 시연은 local·dev)"
- requirements.md demo-002 비고: "local·dev에만 넣음. prod는 코드만 올리고 시연용 데이터는 넣지 않음"
- overview.md '서버 환경': PC 한 대로는 dev·prod VM을 동시에 띄울 수 없다.

## 영향
- 시연 데이터 생성 스크립트·더미 영상 적재는 prod 프로필에서 실행되지 않게 막는다.
- 시연용 데이터 표시·일괄 삭제(demo-002)는 local·dev 기준으로 검수한다.
