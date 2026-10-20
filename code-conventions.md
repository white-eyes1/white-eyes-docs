# 코드 컨벤션

> 노션 '코딩 프롬프트 > 코드 작성 원칙 > 코드 컨벤션'을 바탕으로 이 프로젝트에 맞게 정리했다. JavaScript 규칙과 로깅 규칙은 이 문서에서 새로 정했다.
> 패키지·모듈 배치는 package-structure.md, API 경로·오류 응답 형식은 conventions.md를 따른다.

## 1. 기본 원칙
- 가독성을 가장 먼저 본다. 이름만 보고 역할과 의도를 알 수 있게 쓴다.
- 언어별 공식 스타일 가이드를 기본으로 하고, 이 문서에 따로 정한 것은 이 문서를 따른다.
- 포매터는 개인 IDE 설정이 아니라 저장소에 둔 설정으로 통일한다. 커밋 전에 포매터를 돌리고, CI에서 형식 검사를 한다.
- 한 파일 안에서는 같은 스타일을 유지한다.
- 주석으로 코드를 설명하기보다 코드가 의도를 드러내게 쓴다.

## 2. 공통 규칙 (Java·Python·JavaScript)

### 2-1. 이름
| 대상 | Java | Python | JavaScript |
|---|---|---|---|
| 변수·함수(메서드) | camelCase | snake_case | camelCase |
| 클래스·인터페이스·Enum | PascalCase | PascalCase | PascalCase |
| 상수 | UPPER_SNAKE_CASE (`static final`) | UPPER_SNAKE_CASE (모듈 최상위) | UPPER_SNAKE_CASE (모듈 최상위 `const`) |
| 패키지·모듈·파일 | 패키지 소문자 (`com.whiteeyes.admin.camera`) | 소문자 snake_case (`camera_service.py`) | 소문자 kebab-case (`map-view.js`) |

- 의미 없는 축약어와 지나치게 짧은 이름을 쓰지 않는다(`cnt`, `tmp`, `data2` 금지). 반복문 인덱스 `i`, 좌표 `x`·`y`처럼 관례가 굳은 것은 예외.
- Boolean은 상태나 조건이 드러나게 쓴다: `isRunning`, `hasCamera`, `canDelete` / `is_running`.
- 명세의 용어를 그대로 쓴다. 코드 값(`RUNNING`, `CONGESTION` 등)과 칼럼 이름은 conventions.md·tables.md와 같은 철자.

### 2-2. 형식
- 들여쓰기는 공백 4칸. Tab과 Space를 섞지 않는다. 예외: YAML은 2칸.
- 파일 인코딩 UTF-8, 줄바꿈 LF, 파일 끝 줄바꿈 1개, 줄 끝 공백 없음. 각 저장소 루트의 `.editorconfig`로 강제한다.
- 논리적으로 다른 영역은 빈 줄로 나눈다. 클래스 안에서는 필드·생성자·메서드 영역을 빈 줄로 나눈다.

### 2-3. Import
- 쓰지 않는 import는 지운다.
- 표준 라이브러리 → 외부 라이브러리 → 프로젝트 내부 순서로 묶는다.
- 와일드카드 import(`import x.*`, `from x import *`)는 쓰지 않는다.

### 2-4. 주석
- '왜 이렇게 했는지'를 쓴다. 코드만으로 알 수 없는 비즈니스 규칙·주의사항을 남긴다.
- 명세에서 온 규칙은 ID를 함께 적는다. 예: `// 주의 미만 5분 유지 시 종료(FNC-A-033)`
- 기능(FNC)을 구현하는 진입점(컨트롤러·서비스·작업 클래스, flask는 모듈·클래스)과 그 테스트 클래스의 JavaDoc/docstring에 기능 ID를 적는다. 예: `/** 아이디 중복 확인(FNC-U-001) */`. 여러 기능이 같이 쓰는 공통 코드는 쓰는 기능 ID를 모두 적지 않고, 규칙의 출처 ID 하나만 적는다.
- 주석 처리한 옛 코드를 남기지 않는다(기록은 git이 한다).

### 2-5. 가독성
- 함수·메서드 하나가 여러 책임을 지지 않게 한다.
- 같은 코드가 반복되면 공통 로직으로 빼는 것을 고려하되, 중복 제거를 위해 복잡한 추상화를 만들지 않는다.
- 매직 넘버·매직 문자열은 상수로 뺀다. 운영 중 바꿀 수 있는 값은 상수가 아니라 환경변수(conventions.md '설정값')로 읽는다.
- 변수는 쓰는 곳 가까이에서 선언한다.

### 2-6. 예외·오류
- 오류 응답 형식은 conventions.md '공통 API 규칙 > 오류 응답', 상태 코드 매핑은 FNC-C-027을 따른다.
- 예외를 잡아서 아무것도 하지 않는 코드(빈 catch / `except: pass`)를 쓰지 않는다.
- 예외는 한 곳에서만 로그로 남긴다(로그를 남기고 다시 던지지 않는다). 자세한 기준은 7장.

## 3. Java 규칙 (white-eyes-spring)

### 3-1. 기준·도구
- Java 17, Spring Boot 4.1.1. 일반적인 Java 코딩 관례를 기본으로 한다.
- 포매터: Spotless + palantir-java-format(4칸 들여쓰기, 줄 길이 120). `./gradlew spotlessApply`로 정리하고 CI에서 `spotlessCheck`.
- IntelliJ IDEA 사용 시 저장소의 코드 스타일 설정을 그대로 쓴다.

### 3-2. 이름
- 메서드는 동사 + 목적어: `findZoneById()`, `createCamera()`, `startCamera()`, `validateBoundary()`.
- Boolean을 반환하는 메서드는 `is`·`has`·`can`으로 시작한다.
- 클래스 이름 접미사

| 역할 | 접미사 | 예 |
|---|---|---|
| 화면(Thymeleaf) 컨트롤러 | `PageController` | `EventPageController` |
| REST API 컨트롤러 | `ApiController` | `EventApiController` |
| 내부 API(8082) 컨트롤러 | `InternalController` | `CameraInternalController` |
| 서비스 | `Service` | `EventService` |
| JPA 리포지토리 | `Repository` | `EventRepository` |
| 외부 호출 클라이언트 | `Client` | `AnalyzerClient` |
| 예약 작업 | `Scheduler` | `StatAggregationScheduler` |
| 요청 DTO | `{동작}Request` | `CameraCreateRequest`, `EventStatusUpdateRequest` |
| 응답 DTO | `Response` | `CameraResponse` |
| 예외 | `Exception` | `ZoneNotFoundException` |

### 3-3. 작성 규칙
- 중괄호는 선언문과 같은 줄에 쓴다. 한 줄짜리 `if`에도 중괄호를 쓴다.
- 의존성은 생성자 주입 + `private final` 필드로 받는다. 필드 주입(`@Autowired` 필드)은 쓰지 않는다.
- 값이 바뀌지 않는 지역 변수·필드는 `final`을 고려한다.
- DTO는 Java `record`를 기본으로 한다. 엔티티는 `record`로 만들지 않는다.
- 엔티티에 public setter를 열지 않는다. 상태 변경은 의미 있는 메서드로: `camera.start()`, `event.resolve(actionCode, note, adminId)`.
- 날짜·시각은 `java.time`을 쓴다. 저장은 `LocalDateTime`(KST), API 응답은 `OffsetDateTime`(+09:00)으로 바꿔 내보낸다(conventions.md '시각 형식').
- `Optional`은 반환값에만 쓴다(필드·매개변수에 쓰지 않음).
- 문자열 비교는 `"RUNNING".equals(status)`처럼 상수 쪽에서 하거나 Enum으로 비교한다.
- `System.out.println`, `e.printStackTrace()`를 쓰지 않는다(7장 로거 사용).

### 3-4. 파일 구조
Package → Import → 클래스 선언 → 상수 → 필드 → 생성자 → public 메서드 → protected·package-private 메서드 → private 메서드.

### 3-5. JavaDoc
- 다른 모듈에서 쓰는 public 클래스·메서드(특히 common 모듈)에 쓴다. 단순 getter·private 메서드에는 쓰지 않는다.

## 4. Python 규칙 (white-eyes-flask)

### 4-1. 기준·도구
- Python 3.12, PEP 8 기준.
- 포매터: Black(기본 줄 길이 88). import 정렬: isort(`profile = "black"`). 설정은 `pyproject.toml`에 둔다. CI에서 `black --check`, `isort --check-only`.
- IDE(PyCharm 등)의 정적 검사를 켠다.

### 4-2. 이름
- 변수·함수·모듈·패키지: snake_case / 클래스·Enum: PascalCase / 상수: UPPER_SNAKE_CASE.
- 모듈 파일 이름은 `{도메인}_{역할}.py`: `camera_controller.py`, `camera_service.py`, `admin_client.py`.
- 모듈 안에서만 쓰는 함수·변수는 이름 앞에 `_`를 붙인다.

### 4-3. 작성 규칙
- 빈 줄: 최상위 함수·클래스 사이 2줄, 클래스 안 메서드 사이 1줄(PEP 8).
- 문자열에 값을 넣을 때는 f-string. 단, 로그 메시지는 7-3의 지연 포매팅(`%s`)을 쓴다.
- 함수의 매개변수와 반환값에 타입 힌트를 쓴다. 관리자 앱과 주고받는 JSON 구조는 `dataclass`(또는 `TypedDict`)로 정의한다. 필드 이름은 API 계약(api/analyzer.md)의 camelCase를 그대로 쓰고, 변환은 그 정의 한 곳에서만 한다.
- 시각은 timezone이 있는 `datetime`(Asia/Seoul)으로 다룬다. 계약 형식은 ISO-8601 +09:00.
- 캠 작업 스레드 사이에서 공유하는 값은 잠금(`threading.Lock`) 또는 큐로만 주고받는다.
- `print()`를 쓰지 않는다(7장 로거 사용).
- `third_party/yolov5/`(외부 모델 코드)는 수정하지 않고 포매터·검사 대상에서 뺀다.

## 5. JavaScript 규칙 (화면 정적 파일)

### 5-1. 기준·도구
- 대상: Thymeleaf 화면의 정적 JS(빌드 도구·프레임워크 없음). 브라우저 ES2020 이상, 모듈은 `<script type="module">`로 불러온다.
- 포매터: Prettier(`tabWidth: 4`, `printWidth: 100`, `singleQuote: true`, `semi: true`). 검사: ESLint(`eslint:recommended`). 설정은 white-eyes-spring 저장소 루트에 두고 CI에서 `prettier --check`, `eslint`.

### 5-2. 이름·파일
- 변수·함수 camelCase, 클래스 PascalCase, 상수 UPPER_SNAKE_CASE, 파일 kebab-case(`event-log.js`, `map-view.js`).
- 페이지마다 진입 파일 하나(`pages/dashboard.js`), 공용 기능은 모듈로 나눠 `import`한다. 전역 변수를 만들지 않는다.

### 5-3. 작성 규칙
- `var`를 쓰지 않는다. 기본은 `const`, 다시 대입할 때만 `let`.
- 비교는 `===`·`!==`.
- 비동기는 `async`/`await` + `fetch`. 콜백을 겹쳐 쓰지 않는다.
- API 호출은 공용 모듈 `common/api.js` 한 곳을 거친다. 이 모듈이 CSRF 헤더(`X-CSRF-TOKEN`, conventions.md 'CSRF') 추가, JSON 변환, 오류 응답(`code`·`message`·`fieldErrors`) 처리, 401 시 로그인 화면 이동을 맡는다.
- 서버에서 받은 값을 화면에 넣을 때는 `textContent`를 쓴다. `innerHTML`에 서버 값이나 사용자 입력을 넣지 않는다(XSS).
- 템플릿에 인라인 이벤트 속성(`onclick="..."`)을 쓰지 않는다. JS에서 `addEventListener`로 연결한다.
- Leaflet 코드는 지도 모듈(`map/`)에만 둔다(overview.md '화면 라이브러리'). 그래프(Chart.js)도 `chart/` 모듈에만 둔다.
- SSE(`EventSource`)는 `common/sse.js`로 연결·재연결·끊김 표시를 한 곳에서 처리한다.
- 날짜 표시 형식은 `yyyy-MM-dd HH:mm`(conventions.md '시각 형식'), 변환 함수는 `common/format.js` 한 곳에 둔다.
- 화면 갱신 주기·간격 같은 값은 서버가 내려준 설정을 쓴다(예: `CARD_SNAPSHOT_INTERVAL_SEC`). JS에 숫자를 따로 박지 않는다.
- `console.log`를 남기지 않는다. 오류 보고가 필요하면 `console.error`만.

## 6. 테스트 이름
- Java: JUnit 5, 테스트 클래스는 `{대상}Test`, 메서드 이름은 한국어 `@DisplayName`으로 무엇을 확인하는지 쓴다. 명세의 '완료/검수 기준'을 테스트로 옮길 때는 기능 ID를 적는다(`@DisplayName("FNC-A-033 주의 미만 5분 유지 시 이벤트 종료")`).
- Python: pytest, 파일 `test_{대상}.py`, 함수 `test_{조건}_{결과}`.

## 7. 로깅

로깅 구현체는 Log4j2로 통일한다(decisions/0009). 분석 서버(Python)는 Log4j2를 쓸 수 없으므로 표준 `logging`을 같은 형식·레벨 기준으로 맞춘다.

### 7-1. Spring(Java)
- 의존성: 모든 모듈에서 `spring-boot-starter-logging`(Logback)을 빼고 `spring-boot-starter-log4j2`를 넣는다. Log4j2 버전은 Spring Boot가 관리하는 버전을 그대로 쓴다(직접 올리거나 내리지 않음).
- 코드에서는 SLF4J API로 쓴다: `private static final Logger log = LoggerFactory.getLogger(EventService.class);` — 실제 출력은 Log4j2가 한다. `org.apache.logging.log4j` 클래스를 코드에서 직접 import하지 않는다.
- 설정 파일: `common/src/main/resources/log4j2-spring.xml` 한 벌을 두 앱이 함께 쓴다. 앱 이름은 `${spring:spring.application.name}`(`white-eyes-user` / `white-eyes-admin`)으로 넣는다.
- 레벨: 프로젝트 패키지(`com.whiteeyes`)는 환경변수 `LOG_LEVEL`(local·dev `DEBUG`, prod `INFO`), 그 밖의 라이브러리는 `WARN`(Hibernate SQL은 local에서만 `DEBUG`).

### 7-2. 출력 형식·위치
- 형식(white-eyes-spring·white-eyes-flask 공통): `시각 레벨 [스레드] 요청ID 로거 - 메시지`
  - Log4j2 패턴: `%d{yyyy-MM-dd HH:mm:ss.SSS}{Asia/Seoul} %-5level [%t] %X{requestId} %logger{36} - %msg%n%throwable`
  - Python 형식: `%(asctime)s.%(msecs)03d %(levelname)-5s [%(threadName)s] %(request_id)s %(name)s - %(message)s` (`datefmt="%Y-%m-%d %H:%M:%S"`, 시간대 KST)
- 출력은 콘솔(표준 출력)만 쓴다. 컨테이너 로그로 모으고, 회전은 Docker 로그 설정(`json-file`, `max-size: 10m`, `max-file: 5`)으로 한다. 앱이 파일을 직접 쓰지 않는다.
- 요청 ID: common의 필터가 요청마다 `requestId`를 만들어 MDC에 넣고 응답 헤더 `X-Request-Id`로 돌려준다. 관리자 앱이 분석 서버를 부를 때 같은 헤더를 넘기고, 분석 서버는 그 값을 로그에 남긴다. 분석 서버가 먼저 보내는 요청(결과 전송 등)은 분석 서버가 ID를 만든다.

### 7-3. 레벨 기준
| 레벨 | 쓰는 경우 | 예 |
|---|---|---|
| ERROR | 요청·작업이 실패해 사람이 봐야 함, 데이터 손실 가능 | 500 응답, 1분 통계 저장 실패, 녹화 등록 최종 실패 |
| WARN | 실패했지만 재시도·복구 중이거나 기능이 줄어든 상태 | 분석 서버 연결 실패(502), 결과 재전송, 라이브 재연결, 탐지 오류 프레임 건너뜀 |
| INFO | 운영에 의미 있는 상태 변화(1회성) | 앱 시작·종료, 캠 가동·정지·상태 변경, 이벤트 생성·종료, 집계·정리 작업 완료 요약(건수) |
| DEBUG | 개발 중 흐름 확인용 상세 | 요청 파라미터, 프레임 처리 시간, 판정 중간값 |

- 1초마다·프레임마다 도는 반복 처리는 INFO로 남기지 않는다(DEBUG 또는 1분 요약).
- 메시지는 파라미터 방식으로 쓴다: Java `log.info("캠 가동 cameraId={}", id)`, Python `logger.info("캠 가동 cameraId=%s", camera_id)`. 문자열 더하기·f-string으로 만들지 않는다.
- 예외는 처리하는 한 곳에서 스택과 함께 남긴다: Java `log.error("…", e)`, Python `logger.exception("…")`. 4xx 같은 예상된 업무 예외는 스택 없이 WARN 또는 남기지 않음, 500만 ERROR.

### 7-4. 남기지 않는 것
- 비밀번호(평문·해시)·임시 비밀번호, 세션 ID·쿠키, `X-Internal-Token` 값, 환경변수의 비밀값.
- 개인 정보(메일·연락처·이름)는 남기지 않는다. 계정은 `loginId` 또는 id만.
- 요청·응답 본문 전체, 영상 프레임·좌표 파일 내용.

### 7-5. Python(분석 서버)
- `logging.getLogger(__name__)`로 모듈마다 로거를 만든다. 로그에 쓰는 앱 이름은 `white-eyes-analyzer`.
- 설정은 `create_app()`에서 `logging.config.dictConfig`로 한 번만 한다. 레벨은 환경변수 `LOG_LEVEL`.
- 요청 ID는 요청 처리 중이면 Flask `g`에서, 캠 작업 스레드면 `"cam-{cameraId}"`를 넣는 `logging.Filter`로 채운다.
