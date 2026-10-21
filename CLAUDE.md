# white-eyes-docs 수정 규칙

white-eyes 프로젝트의 명세 저장소(white-eyes-docs)이고, 이 저장소가 명세의 원본이다. 2026-10-18에 구글 시트 '명세서 목록'에서 옮겼고, 시트는 그 뒤로 고치지 않는다(동결).
코드 저장소 white-eyes-spring(사용자·관리자 앱)과 white-eyes-flask(분석 서버)는 이 문서를 기준으로 구현한다. 명세와 코드가 다르면 명세를 먼저 고치고 PR로 남긴다.

## 문서 위치
- 어떤 내용이 어느 파일에 있는지는 INDEX.md를 먼저 본다.
- 코드를 쓸 때는 code-conventions.md(코드 컨벤션·로깅)와 package-structure.md(모듈·패키지 배치)를 따른다. 커밋 메시지는 commit-convention.md.
- 결정의 이유는 decisions/에 남긴다. 명세 본문에는 결과만 쓰고 긴 근거는 결정 기록으로 링크한다.

## ID 규칙
| 종류 | 형식 | 예 | 위치 |
|---|---|---|---|
| 요구사항 | `{영역}-{3자리}` 소문자 | `evtdet-001` | requirements.md |
| 기능 | `FNC-{C/U/A/S}-{3자리}` | `FNC-A-020` | features/ |
| 화면 | `SCR-{C/U/A}-{3자리}` | `SCR-A-008` | screens.md |
| 결정 | `{4자리}-{짧은-영문}.md` | `0001-yolo-crowd.md` | decisions/ |

- 기능·화면 접두사: C = 두 앱 공용(common), U = 사용자 앱, A = 관리자 앱, S = 분석 서버·운영.
- ID는 한 번 쓰면 바꾸거나 다시 쓰지 않는다. 지운 ID는 빈 번호로 남긴다.
  - 기능: FNC-C-015, FNC-C-021, FNC-A-049, FNC-A-050(날씨 2순위로 빠짐)
  - 요구사항: stats-002, acman-005, vanly-003, das-002·008·009, histwr-004(비어 있는 번호. 일부는 비고에 '기존 …'으로만 남음), sec-002(2순위로 이동)
- 원본에 있던 범위 표기 `stats-001~008`은 빈 번호 stats-002를 포함한다. 새로 쓸 때는 범위 안에 없는 ID를 넣지 않는다.
- 새 ID는 같은 접두사의 가장 큰 번호 + 1.
- 2순위 항목을 1순위로 올릴 때 요구사항 ID는 그대로 쓴다.
- 범위 표기 `caman-004~005`, 묶음 표기 `FNC-A-020·021`은 그대로 써도 된다.

## 고칠 때 함께 바꿀 문서
| 바꾸는 것 | 함께 확인·수정할 곳 |
|---|---|
| 요구사항 추가·변경 | requirements.md → features/index.md의 관련 요구사항 ID → 해당 features/*.md → screens.md의 관련 요구사항 ID |
| 기능 추가·변경 | features/index.md와 상세 파일 둘 다(기능명 일치) → 이 기능을 부르는 screens.md·api/*.md 비고의 FNC ID |
| 브라우저 API 변경 | api/public.md → 이 API를 쓰는 features 처리 순서 → screens.md 처리 규칙 |
| spring ↔ flask API 변경 | api/analyzer.md → features/admin.md·features/analyzer.md. **white-eyes-spring·white-eyes-flask 두 저장소를 같은 시점에 고친다** |
| nginx 경로 | conventions.md 'nginx 경로 규칙' → overview.md '서비스 구성 > nginx' |
| 테이블·칼럼 | tables.md → 이 칼럼을 쓰는 features·api 예시 → conventions.md 코드 값 |
| 코드 값·환경변수 | conventions.md를 먼저 고치고 → tables.md 설명 → features·api 예시 |
| 혼잡 단계 기준 | conventions.md(코드 값 '혼잡 단계', 설정값, '혼잡 단계 판정') → api/public.md `/meta/levels` 예시 → overview.md '이벤트' |
| 알려진 한계 | overview.md 맨 끝 목록. 번호를 바꾸면 `알려진 한계 N` 참조를 모두 찾아 고친다 |
| 2순위 → 1순위 | backlog-p2.md에서 항목과 테이블 초안을 빼서 1순위 문서로 옮긴다. 테이블 초안의 `account.id`는 `user_account.id` 또는 `admin_account.id`로 고친다 |
| 패키지·모듈 배치 | package-structure.md → (공통 모듈 범위가 바뀌면) conventions.md '모듈·포트'의 공통 모듈 설명 |
| 로깅 규칙 | code-conventions.md '7. 로깅' → conventions.md '주요 라이브러리'·`LOG_LEVEL` → overview.md 기술 스택 |
| 화면 모양 | design/src → design/screens·png 다시 만들기(design/README.md) → 요소가 바뀌면 screens.md |
| 결정이 바뀜 | 기존 결정 기록은 지우지 않고 상태를 '대체됨(→ 새 번호)'으로 바꾼 뒤 새 기록을 추가 |

변경 뒤에는 바꾼 ID·경로·칼럼 이름으로 `grep -rn`을 돌려 남은 참조가 없는지 확인한다.

## 쓰는 방식
- 2026-10-18 이관 때 시트에 없던 문장은 각 파일의 H1 제목, `> 원본: …` 줄, features/index.md·api/*.md 머리의 안내 한 줄뿐이었다. 이후 변경은 git 기록과 decisions/로 본다.
- 기능 명세는 `### {ID} {기능명}` + 항목 목록. 요구 명세·기능 목록·화면 명세·테이블은 표.
- 표 칸 안의 줄바꿈은 `<br>`, 칸 안의 `|`는 `\|`.
- 요구 명세에 '출처'·'수용 기준' 열을 추가하지 않는다.
- 비밀번호·키·토큰 값은 쓰지 않는다. 환경변수 이름만 쓴다.
- prod에는 코드만 올린다. 더미 영상·시연용 데이터는 local·dev에만 있다는 전제를 바꾸지 않는다(decisions/0004).
