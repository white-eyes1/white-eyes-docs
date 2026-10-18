# 0010. 공통 모듈(common)에는 두 앱이 모두 쓰는 것만 둠

- 상태: 채택
- 기록: 2026-10-19 (INDEX.md에는 있었으나 파일이 빠져 있어 보강)
- 출처: package-structure.md 1장 '원칙'·4장 '무엇을 common에 두는가'에 적힌 결정을 옮김
- 관련: package-structure.md 1·4장, conventions.md '모듈·포트'·'DB 계정', tables.md

## 결정
- white-eyes-spring은 common / user / admin 멀티모듈로 나누고, common에는 **두 앱이 모두 쓰는 것만** 둔다.
- common에 둔다: 두 앱이 함께 읽거나 쓰는 테이블의 엔티티·리포지토리(user_account, region, zone, zone_neighbor, camera, zone_stat_minute·hourly·daily, event, work_history), 두 앱의 공통 화면(통계·대시보드·기간 비교·내 정보·로그인)과 그 API, 보안·세션·예외·응답 형식·요청 ID 같은 공통 설정.
- common에 두지 않는다: 관리자 앱만 쓰는 테이블의 엔티티(admin_account, recording → admin), 한 앱에서만 쓰는 화면·API(가입·탈퇴는 user, 운영 화면은 admin), 예약 작업과 Flyway 마이그레이션(관리자 앱만).
- 공유 엔티티가 admin 전용 테이블을 가리키는 칼럼은 연관관계가 아니라 id 값으로 둔다: `Event.handledBy`, `WorkHistory.actorId`.

## 근거
- common을 아무 코드나 넣는 곳으로 쓰면 한 앱 전용 코드가 다른 앱에도 실리고 모듈 경계가 흐려진다.
- 사용자 앱 DB 계정에는 admin_account 권한이 없다. 그 엔티티가 common에 있으면 사용자 앱 시작 때 JPA 검증(`ddl-auto=validate`)이 테이블을 확인하다 실패한다.

## 영향
- 공통 모듈 범위가 바뀌면 package-structure.md 4장과 conventions.md '모듈·포트'의 공통 모듈 설명을 함께 고친다(CLAUDE.md '고칠 때 함께 바꿀 문서').
