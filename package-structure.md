# 패키지(모듈) 구조

> 노션 '코딩 프롬프트 > 코드 작성 원칙 > 패키지(모듈) 구조'의 원칙(도메인 중심, 도메인 안에서 계층 분리)을 이 프로젝트의 멀티모듈 구성에 맞게 정리했다.
> 프로젝트 이름은 white-eyes. Java 패키지 이름에는 '-'를 쓸 수 없어 기본 패키지는 `com.whiteeyes`로 한다.

## 1. 원칙
- 패키지는 도메인(기능) 단위로 묶고, 계층(controller·service·repository…)은 도메인 안에서 나눈다. 프로젝트 전체를 `controller/`, `service/`로 먼저 나누지 않는다.
- 한 도메인 패키지는 다른 도메인에 대한 의존을 최소로 한다.
- 공통 코드는 공통 모듈로 빼되, common을 아무 코드나 넣는 곳으로 쓰지 않는다. **두 앱이 모두 쓰는 것만** common에 둔다(4장).

## 2. 저장소와 모듈
| 저장소 | 모듈 | 실행 | 역할 |
|---|---|---|---|
| white-eyes-spring | `common` | 단독 실행 없음(java-library, bootJar 없음) | 두 앱이 함께 쓰는 엔티티·리포지토리·통계 조회·공통 화면·보안·예외 처리·작업 기록 저장 |
| white-eyes-spring | `user` | 사용자 앱(8080) | 회원가입·탈퇴 등 사용자 앱 전용 기능 + common |
| white-eyes-spring | `admin` | 관리자 앱(8081, 내부 8082) | 계정·구역·캠·집계·이벤트·영상·알림 등 운영 기능 + common |
| white-eyes-flask | `analyzer` | 분석 서버(5000) | 탐지·추적·집계용 1초 결과·녹화·실시간 화면 |

### 2-1. 모듈 의존 방향
```
user ──▶ common ◀── admin
```
- `user`와 `admin`은 `common`에만 의존한다. `user` ↔ `admin`은 서로 의존하지 않는다.
- `common`은 `user`·`admin`을 참조하지 않는다.
- 명세는 white-eyes-docs(이 저장소)에 있고, 코드 저장소는 white-eyes-spring·white-eyes-flask 두 개다.
- white-eyes-spring ↔ white-eyes-flask는 HTTP 계약(api/analyzer.md)으로만 연결한다. 서로의 코드를 가져다 쓰지 않는다.

## 3. white-eyes-spring 저장소 구조
```
white-eyes-spring/
├── settings.gradle                 rootProject.name = 'white-eyes-spring', include 'common', 'user', 'admin'
├── build.gradle                    공통 설정(Java 17, Logback 제외·Log4j2, Spotless)
├── .editorconfig · .prettierrc · eslint 설정
│
├── common/
│   └── src/main/
│       ├── java/com/whiteeyes/common/
│       │   ├── account/        UserAccount 엔티티·리포지토리, 내 정보·비밀번호 변경(FNC-C-006·007)
│       │   ├── region/         Region·Zone·ZoneNeighbor 엔티티·리포지토리, 지역·구역 목록(FNC-C-008)
│       │   ├── camera/         Camera 엔티티·리포지토리(조회용)
│       │   ├── stat/           ZoneStatMinute·Hourly·Daily 엔티티·리포지토리, 지도 현황·흐름·히트맵,
│       │   │                   그래프·대시보드·기간 비교, 실시간 통계 SSE, 통계 엑셀, 시연용 표시
│       │   │                   (FNC-C-009~014·016·018~020·022~024·028·029)
│       │   ├── level/          혼잡 단계 판정·/meta/levels(FNC-C-025)
│       │   ├── event/          Event 엔티티·리포지토리, 오늘 이벤트 수(FNC-C-017)
│       │   ├── history/        WorkHistory 엔티티·리포지토리, 작업 기록 저장(FNC-C-026)
│       │   ├── security/       Spring Security 공통 설정: 로그인·로그아웃·접근 권한·세션 만료·비밀번호 암호화(FNC-C-001~005)
│       │   ├── config/         Session JDBC, Jackson, Web, 요청 ID(MDC) 필터
│       │   ├── exception/      ErrorCode, BusinessException, 전역 예외 처리(FNC-C-027)
│       │   ├── web/            ErrorResponse, PageResponse 등 공통 응답
│       │   ├── util/
│       │   └── constant/
│       └── resources/
│           ├── templates/      공통 화면(통계 메인·그래프·기간 비교·내 정보·로그인 등)
│           ├── static/js/      common/(api·sse·format), map/(Leaflet), chart/(Chart.js), pages/
│           ├── static/css/
│           └── log4j2-spring.xml
│
├── user/
│   └── src/main/
│       ├── java/com/whiteeyes/user/
│       │   ├── UserApplication.java
│       │   ├── account/        아이디 중복 확인·회원가입·승인 대기·탈퇴(FNC-U-001~004)
│       │   └── config/         사용자 앱 보안 설정, 세션 테이블 SPRING_SESSION_USER, 쿠키 USER_SESSION
│       └── resources/
│           ├── application.yml (+ application-local.yml, -dev, -prod)
│           └── templates/user/ 가입·승인 대기·탈퇴 화면
│
└── admin/
    └── src/main/
        ├── java/com/whiteeyes/admin/
        │   ├── AdminApplication.java
        │   ├── account/        AdminAccount 엔티티·리포지토리, 최고 관리자 초기 등록,
        │   │                   사용자·관리자 관리, 강제 로그아웃(FNC-A-001~011)
        │   ├── region/         행정구역 적재, 구역 미리보기·등록·수정·이웃·삭제(FNC-A-012~017)
        │   ├── camera/         캠 등록·수정·가동·정지·상태·삭제, 분석 서버 호출(client/),
        │   │                   상태 보고·가동 대상 목록 내부 API(FNC-A-018~023·025·027)
        │   ├── stat/           분석 결과 수신, 1분·시간별·일별 집계, 보충, 정리(FNC-A-024·028~032)
        │   ├── event/          혼잡·급증·캠 이상 판정, 목록·상세·처리·엑셀·다시보기 이동(FNC-A-033~040)
        │   ├── media/          Recording 엔티티·리포지토리, 녹화 등록 내부 API, 실시간 권한 확인,
        │   │                   카드 미리보기, 다시보기·파일 전송(FNC-A-026·041~047)
        │   ├── notification/   관리자 알림 SSE(FNC-A-048)
        │   ├── demo/           시연용 통계 생성·삭제(FNC-A-051·052) — local·dev 프로필에서만 등록
        │   ├── history/        작업 기록 조회(FNC-A-053)
        │   └── config/         관리자 앱 보안, 세션 테이블 SPRING_SESSION_ADMIN, 쿠키 ADMIN_SESSION,
        │                       내부 포트(8082) 연결, 스케줄러
        └── resources/
            ├── application.yml (+ application-local.yml, -dev, -prod)
            ├── templates/admin/ 운영 화면(사용자·관리자·구역·캠·이벤트·다시보기·작업 기록)
            ├── static/js/admin/ 관리자 화면 전용 JS
            └── db/migration/   Flyway 마이그레이션(관리자 앱만 실행)
```
- 같은 도메인 이름이 여러 모듈에 있을 수 있다(예: common의 `camera`는 엔티티·조회, admin의 `camera`는 관리 기능). 같은 도메인끼리는 모듈이 달라도 한 기능 영역으로 본다.
- 앱 이름(`spring.application.name`): 사용자 앱 `white-eyes-user`, 관리자 앱 `white-eyes-admin`. 로그·컨테이너 이름에 그대로 쓴다.
- 앱 시작 클래스는 `common`과 자기 패키지만 스캔한다: `@SpringBootApplication(scanBasePackages = {"com.whiteeyes.common", "com.whiteeyes.admin"})`, `@EntityScan`·`@EnableJpaRepositories`도 같은 두 패키지.

### 3-1. 도메인 안의 계층
```
admin/.../event/
├── controller/   EventPageController, EventApiController
├── service/      EventService, CongestionEventDetector …
├── repository/   (admin 전용 엔티티가 있을 때만. 공유 엔티티의 리포지토리는 common의 같은 도메인에 있음)
├── dto/          EventStatusUpdateRequest, EventResponse …
├── entity/       (admin 전용 테이블만)
├── exception/    EventStatusConflictException …
├── client/       외부 호출이 있을 때만(예: camera/client/AnalyzerClient)
└── scheduler/    예약 작업이 있을 때만(예: stat/scheduler/StatAggregationScheduler)
```
| 계층 | 하는 일 | 하지 않는 일 |
|---|---|---|
| controller | 요청 받기, 입력 형식 검증(`@Valid`), service 호출, 응답·화면 반환 | 비즈니스 판단, DB 접근 |
| service | 비즈니스 로직, 트랜잭션(`@Transactional`), 다른 도메인 service 호출, DTO ↔ 엔티티 변환 | HTTP 요청·응답 객체 사용 |
| repository | 데이터 조회·저장·수정·삭제(Spring Data JPA) | 비즈니스 판단 |
| client | 다른 서버 호출(분석 서버 HTTP) | 비즈니스 판단 |
| scheduler | 정해진 시각에 service 호출 | 로직 직접 구현 |

### 3-2. 의존 규칙
- 계층 의존은 `controller → service → repository` 한 방향. controller가 repository를 직접 부르지 않는다.
- 같은 도메인이면 모듈이 달라도 그 도메인의 repository를 쓸 수 있다(admin `camera` service → common `camera` repository).
- 다른 도메인이 필요하면 그 도메인의 **service**만 부른다. 다른 도메인의 repository·엔티티를 직접 쓰지 않는다(예: admin `event`가 1분 통계를 볼 때 common `stat`의 service를 부름).
- 두 도메인이 서로를 부르는 순환이 생기면 설계를 다시 보거나, 둘 다 쓰는 부분을 아래 쪽(common의 해당 도메인)으로 내린다.
- 작업 기록 저장(FNC-C-026)은 common `history`의 service 하나로만 한다.

### 3-3. DTO·엔티티
- 엔티티는 controller 밖으로 내보내지 않는다. 요청·응답은 항상 DTO.
- DTO ↔ 엔티티 변환은 service에서 한다.
- 요청 DTO와 응답 DTO를 나눈다(`CameraCreateRequest` / `CameraResponse`). 한 DTO를 여러 API에 억지로 같이 쓰지 않는다.
- JSON 필드 이름은 camelCase(conventions.md '데이터 형식').

## 4. 무엇을 common에 두는가
| 둔다 | 두지 않는다 |
|---|---|
| 두 앱이 함께 읽거나 쓰는 테이블의 엔티티·리포지토리: user_account, region, zone, zone_neighbor, camera, zone_stat_minute·hourly·daily, event, work_history | 관리자 앱만 쓰는 테이블의 엔티티: **admin_account, recording** → admin 모듈 |
| 두 앱의 공통 화면(통계·대시보드·기간 비교·내 정보·로그인)과 그 API | 한 앱에서만 쓰는 화면·API(가입·탈퇴는 user, 운영 화면은 admin) |
| 보안·세션·예외·응답 형식·요청 ID 같은 공통 설정 | 예약 작업(관리자 앱에서만 실행), Flyway 마이그레이션(관리자 앱만) |

- **admin_account를 common에 두지 않는 이유**: 사용자 앱 DB 계정에는 admin_account 권한이 없다(conventions.md 'DB 계정'). 엔티티가 common에 있으면 사용자 앱이 시작할 때 JPA 검증(`ddl-auto=validate`)이 그 테이블을 확인하다 실패한다.
- 공유 엔티티가 admin 전용 테이블을 가리키는 칼럼은 연관관계가 아니라 id 값으로 둔다: `Event.handledBy`(Long, admin_account.id), `WorkHistory.actorId`(Long, FK 없음).
- 두 앱 설정: 두 앱 모두 `spring.jpa.hibernate.ddl-auto=validate`, `spring.jpa.open-in-view=false`. 사용자 앱은 `spring.flyway.enabled=false`.

## 5. white-eyes-flask 저장소 구조
```
white-eyes-flask/
├── pyproject.toml                  Black·isort 설정, 의존성
├── .editorconfig
├── analyzer/
│   ├── __init__.py                 create_app(): 설정·로깅·Blueprint 등록, 시작 시 재가동 복구(FNC-S-012)
│   ├── config.py                   환경변수 읽기(conventions.md '설정값')
│   ├── common/                     내부 토큰 검사, 오류 응답, 로깅 설정(요청 ID 필터), 시각·경로 유틸
│   ├── camera/                     camera_controller.py(/analyzer/v1/cameras/*), camera_service.py(캠 작업 시작·정지·상태),
│   │                               camera_job.py(캠마다 스레드 1개)(FNC-S-001·002·012)
│   ├── analysis/                   detector.py(YOLO-CROWD), tracker.py(ByteTrack), edge_counter.py(유입/유출),
│   │                               dwell.py(체류 시간)(FNC-S-003~005)
│   ├── live/                       RTSP 읽기·재연결(FNC-S-007)
│   ├── recording/                  1분 파일 녹화(ffmpeg)·좌표 파일·녹화 등록(FNC-S-008)
│   ├── dummy/                      분석 준비(캐시 생성)·재생·반복 등록(FNC-S-009·010)
│   ├── stream/                     MJPEG·스냅샷(FNC-S-011)
│   ├── report/                     admin_client.py(관리자 앱 내부 API 호출), 1초 결과 전송·재전송 버퍼(FNC-S-006)
│   └── health/                     상태 확인(FNC-S-013)
├── third_party/yolov5/             YOLO-CROWD 모델 코드(외부 코드, 수정 금지)
├── ops/                            녹화 파일 정리·DB 백업 스크립트(FNC-S-014·015, 분석 서버 앱과 따로 실행)
├── tests/                          analyzer/와 같은 도메인 구조
└── run.py
```
- 가중치 파일(`yolo-crowd.pt`)·더미 영상·캐시는 저장소에 올리지 않는다. 경로는 환경변수(`YOLO_WEIGHTS`)와 공유 폴더 규칙(conventions.md '공유 폴더 구조')을 따른다.
- 도메인 안 파일 이름은 `{도메인}_{역할}.py`를 기본으로 한다. 계층이 하나뿐인 작은 도메인(health 등)은 파일 하나로 둔다.
- 계층 규칙은 3-1·3-2와 같다: controller(Blueprint 라우트)는 요청 검증과 service 호출만, 관리자 앱 호출은 `report/admin_client.py` 한 곳.
- 다른 도메인은 그 도메인 service의 공개 함수로만 부른다(`_`로 시작하는 함수·모듈 내부 상태를 가져다 쓰지 않는다).

## 6. 화면 정적 파일(JS)
```
common/src/main/resources/static/js/
├── common/   api.js(fetch·CSRF·오류 처리), sse.js(EventSource 연결·재연결), format.js(날짜·숫자 표시)
├── map/      map-view.js 등 Leaflet 코드(이 폴더 밖에서 Leaflet을 직접 쓰지 않음)
├── chart/    Chart.js 코드
└── pages/    화면별 진입 파일(dashboard.js, stats-graph.js, compare.js …)
admin/src/main/resources/static/js/admin/
├── pages/    운영 화면 진입 파일(camera-manage.js, event-log.js, playback.js …)
└── …         관리자 전용 모듈(구역 그리기 등)
```
- pages/는 화면 조립만 하고, 공용 기능은 common/·map/·chart/ 모듈을 import한다.
