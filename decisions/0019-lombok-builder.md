# 0019. Lombok `@Builder`를 생성자·record에 한해 허용하고, Lombok 정리는 포매터와 나눠 진행함

- 상태: 채택
- 기록: 2026-11-04
- 관련: code-conventions.md 3-3·3-6, 0017(일부 대체), spring#364, spring#367

## 맥락
- 0017은 Lombok 허용 목록에서 `@Builder`를 뺐고, 영향에 `ZoneStatMinute`의 `@Builder` 변환을 적었다. 다른 금지 어노테이션과 달리 `@Builder`를 금지한 이유는 기록이 없다.
- spring#364에서 변환을 검토해 보니 `ZoneStatMinute`(1분 통계 엔티티)의 생성자는 인자가 17개이고 그중 13개가 `int`(최대·최소 인원, 방향별 유입·유출 8개, 체류 합·건수 등)다. `@Builder`를 지우면 같은 타입 인자를 순서로만 넘기게 되어, 순서를 바꿔 넣어도 컴파일이 통과한다.
- 이 `@Builder`는 `private` 생성자에 붙어 있고, 운영 코드에서 만드는 곳은 1분 마감 계산 한 곳이며 모든 칸을 채운다.

## 결정
- `@Builder`는 **생성자**(주로 `private`) 또는 **record 선언**에 붙여 쓸 수 있다. record가 아닌 클래스 선언에는 붙이지 않는다.
- 시험 데이터는 생성자에 `@Builder`가 있으면 빌더로 만들어도 된다(3-3).
- `lombok.config`에서 `@Builder`를 막지 않는다. 붙인 위치는 `lombok.config`·아키텍처 테스트로 구분할 수 없어 리뷰에서 본다.
- 0017 영향의 "기존 코드 변환과 `lombok.config` 추가는 포매터 도입과 같은 시점에 한 PR로 한다"는 따르지 않는다. Lombok 변환·`lombok.config`·아키텍처 테스트는 spring#364, 포매터는 spring#367(#364 다음)로 나눠 진행한다.

## 이유
- PM 결정(2026-11-04): `@Builder`를 허용한다.
- 빌더는 값을 이름으로 넣으므로, 같은 타입 인자가 많은 생성자에서 순서 실수를 막는다. 인자가 많은 DTO record(2026-11-04 기준 10개 이상 7개, 최대 23개)도 같다.
- 클래스 선언에 붙이면 Lombok이 전체 인자 생성자를 요구하는데, 엔티티에는 `@NoArgsConstructor(access = PROTECTED)`가 있어 `@AllArgsConstructor`를 더 붙이게 되고, 이는 3-6(복합키 ID 클래스 밖 `@AllArgsConstructor` 금지)과 부딪힌다. 생성자에 붙이면 이 문제가 없다. record는 정식 생성자가 있어 선언에 붙여도 이 문제가 없다.
- 포매터와 PR을 나눈 이유: 기록 없음(이슈를 나눌 때 정함).

## 영향
- `ZoneStatMinute`의 `@Builder`는 그대로 둔다.
- spring#364 이슈 본문의 `lombok.config` 금지 목록에서 `@Builder`를 뺀다.
- 빌더는 필수 칸을 빠뜨려도 컴파일되므로(빠진 칸은 0·null), 운영 코드에서 엔티티를 만들 때 모든 칸을 채우는지는 리뷰와 시험으로 확인한다.
