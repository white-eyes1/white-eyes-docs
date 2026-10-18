# 0009. 로깅 구현체를 Log4j2로 통일함

- 상태: 채택
- 기록: 2026-10-19 (INDEX.md·code-conventions.md에는 있었으나 파일이 빠져 있어 보강)
- 출처: code-conventions.md '7. 로깅'에 적힌 결정을 옮김. 결정 당시의 선택 이유는 남아 있지 않다.
- 관련: code-conventions.md '7. 로깅', conventions.md '주요 라이브러리'·`LOG_LEVEL`, overview.md 기술 스택, package-structure.md(`build.gradle` Logback 제외·Log4j2, `common/src/main/resources/log4j2-spring.xml`)

## 결정
- white-eyes-spring의 모든 모듈에서 `spring-boot-starter-logging`(Logback)을 빼고 `spring-boot-starter-log4j2`를 쓴다. 버전은 Spring Boot가 관리하는 버전을 그대로 쓴다.
- 코드는 SLF4J API로만 쓰고 `org.apache.logging.log4j` 클래스를 직접 import하지 않는다.
- 설정 파일은 common의 `log4j2-spring.xml` 한 벌을 두 앱이 함께 쓴다.
- white-eyes-flask는 Log4j2를 쓸 수 없으므로 표준 `logging`을 같은 출력 형식·레벨 기준으로 맞춘다.

## 근거
- 기록 없음. Logback 대신 Log4j2를 고른 이유는 결정한 사람에게 확인해 이 절을 채운다.
- SLF4J API로만 쓰게 한 것은 구현체를 바꿔도 코드가 바뀌지 않게 하려는 것이다(code-conventions.md 7-1).

## 영향
- 출력 형식·위치·레벨 기준·남기지 않는 값은 code-conventions.md 7-2~7-5를 따른다.
