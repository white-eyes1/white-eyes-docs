# 0017. Lombok은 허용 목록만 쓰고, 로거는 @Slf4j로 통일함

- 상태: 채택
- 기록: 2026-10-28
- 관련: code-conventions.md 3-3·3-6·7-1, 0009(로깅 Log4j2)

## 맥락
2026-10-28 white-eyes-spring dev를 점검해 보니 Lombok 사용이 섞여 있었다.
- 스프링 빈 182개 중 생성자를 `@RequiredArgsConstructor`로 만든 것 71개, 직접 쓴 것 87개(그중 78개는 단순 주입).
- 로거는 `LoggerFactory.getLogger(...)` 직접 선언 30개, `@Slf4j` 4개, `@Log4j2` 4개. `@Log4j2`는 7-1의 'Log4j2 API를 직접 쓰지 않음'에 어긋난다.
- 코드 컨벤션에 Lombok 규칙이 없었다.

## 결정
- Lombok은 code-conventions.md 3-6 표의 어노테이션만 쓴다: `@RequiredArgsConstructor`, `@Slf4j`, 엔티티의 `@Getter`·`@NoArgsConstructor(access = PROTECTED)`, 복합키 ID 클래스의 `@EqualsAndHashCode`·`@AllArgsConstructor`.
- 생성자 주입은 `@RequiredArgsConstructor`로 통일한다. 생성자 매개변수에 `@Value`·`@Qualifier`가 필요하거나 생성자에 로직이 있을 때만 직접 쓴다.
- 로거는 `@Slf4j`로 통일한다.
- 엔티티 setter·`@Data`는 쓰지 않는다.
- 허용 목록은 저장소 루트 `lombok.config`로 빌드에서 막는다.

## 근거
- PM 결정(2026-10-28): Lombok을 쓰는 쪽으로 통일, 로거는 `@Slf4j`.
- `@RequiredArgsConstructor`는 3-3의 '생성자 주입 + `private final`'을 그대로 만들어, 필드를 추가하고 생성자에 빠뜨리는 실수를 막는다.
- `@Slf4j`가 만드는 로거는 직접 선언과 같은 SLF4J 로거라 0009와 충돌하지 않고, 다른 클래스 이름을 복사해 넣는 실수를 막는다.
- 목록 방식으로 정한 이유: 'Lombok을 쓴다'만 정하면 엔티티에 `@Data`·`@Builder`·`@ToString`이 들어온다. 엔티티의 setter는 함께 바뀌어야 할 값을 일부만 바꾸게 하고, `@ToString`·`@EqualsAndHashCode`는 지연 로딩·순환 참조·민감 값 로그(7-4)·저장 전후 hashCode 변경 문제를 만든다.

## 영향
- 기존 코드 변환(생성자 78개, 로거 34개, `ZoneStatMinute`의 `@Builder`)과 `lombok.config` 추가는 white-eyes-spring 포매터 도입과 같은 시점에 한 PR로 한다.
- `@RequiredArgsConstructor`는 `final` 필드만 주입하므로 빈 필드의 `final` 규칙을 아키텍처 테스트로 확인한다.
