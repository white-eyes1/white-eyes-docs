# 0005. 사용자 계정과 관리자 계정 테이블을 나눔

- 상태: 채택
- 기록: 2026-10-18
- 관련: tables.md 공통 규칙·user_account·admin_account·work_history, conventions.md '세션·로그인'·'코드 값'·DB 계정

## 결정
- 계정을 user_account(사용자 앱)와 admin_account(관리자 앱)로 나눈다.
- 세션 테이블도 앱마다 따로 둔다: SPRING_SESSION_USER, SPRING_SESSION_ADMIN(+ 각 _ATTRIBUTES).
- 앱마다 DB 계정을 따로 두고, 사용자 앱 DB 계정에는 admin_account·SPRING_SESSION_ADMIN 권한을 주지 않는다.
- 작업 기록(work_history)은 actor_type + actor_id(FK 없음) + actor_login_id로 행위자를 남긴다.

## 근거
- 두 계정은 상태와 역할이 다르다: 사용자 PENDING / ACTIVE / WITHDRAWN, 관리자 role ADMIN / SUPER_ADMIN + status ACTIVE / DISABLED(conventions.md '코드 값').
- 사용자 앱이 뚫려도 관리자 계정·세션에 닿지 않게 DB 권한으로 막을 수 있다(tables.md 공통 규칙).
- 사용자와 관리자는 같은 아이디를 가질 수 있지만 세션 테이블이 달라 섞이지 않는다(conventions.md '세션 주인 이름').

## 영향
- 같은 아이디가 두 종류에 있을 수 있으므로 작업 기록 조회는 actorType과 아이디를 함께 거른다(FNC-A-053).
- backlog-p2.md의 테이블 초안은 아직 `account.id`를 가리킨다. 1순위로 옮길 때 고친다(CLAUDE.md).
