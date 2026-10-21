# INDEX — white-eyes-docs

수정 규칙은 CLAUDE.md. 명세의 원본은 이 저장소다.
본문의 옛 시트 이름 참조: 설정·규약 시트 → conventions.md, 공용 기능 명세서 → features/common.md, 기능 명세서(관리자) → features/admin.md, 2순위 기능 시트 → backlog-p2.md, 테이블 명세서 → tables.md, 요구 명세서 → requirements.md, 프로젝트 개요 → overview.md

## 문서
| 파일 | 내용 |
|---|---|
| overview.md | 프로젝트 개요, 서비스 구성, 기술 스택, 실행 흐름, 이벤트 규칙, 더미 데이터, 알려진 한계(맨 끝) |
| conventions.md | 포트, nginx 경로, 공통 API 규칙, 세션, 입력값 규칙, 코드 값, 환경변수, 공유 폴더, 혼잡 단계 판정 |
| requirements.md | 요구 명세(영역별 표) |
| features/index.md | 기능 목록(전체 표) |
| features/common.md · user.md · admin.md · analyzer.md | 기능 상세(FNC-C / U / A / S) |
| api/public.md | 브라우저 → 사용자·관리자 앱 API (nginx auth_request용 포함) |
| api/analyzer.md | white-eyes-spring ↔ white-eyes-flask 계약: `/internal/v1/*`, `/analyzer/v1/*` |
| screens.md | 화면 기능 명세(화면 ID별 표) |
| tables.md | 테이블 명세(공통 규칙 + 테이블별 칼럼 표) |
| backlog-p2.md | 2순위 기능과 테이블 초안 |
| code-conventions.md | Java·Python·JavaScript 코드 컨벤션, 로깅(Log4j2) |
| package-structure.md | spring 멀티모듈(common/user/admin)·flask 패키지 구조, 계층·의존 규칙 |
| commit-convention.md | 커밋 메시지 규칙(세 저장소 공통) |
| design/ | 화면 시안: 화면마다 정적 HTML·PNG, 공통 CSS(we.css). 모양의 기준(동작·데이터는 명세) |
| decisions/ | 결정 기록 |
| test-reports/ | 시험 보고서(날짜별 폴더의 README.md) |

## ID 접두사 → 파일
| 접두사 | 파일 |
|---|---|
| FNC-C-* | features/common.md |
| FNC-U-* | features/user.md |
| FNC-A-* | features/admin.md |
| FNC-S-* | features/analyzer.md |
| SCR-C-* · SCR-U-* · SCR-A-* | screens.md |
| 1순위 요구사항 ID | requirements.md |
| 2순위 요구사항(perm-006, fest-001·002, sec-002·005·006, das-007, wthr-001·002, stagraph-004, cmp-004) | backlog-p2.md |

## 요구사항 접두사 → requirements.md 영역
| 영역 | 접두사 |
|---|---|
| 회원 | perm, auth, aclst, acman |
| 운영 관리 | loca, caman |
| 영상 분석 | vanly, rec |
| 통계 데이터 | stats, stagg, demo |
| 통계 화면 | map, hitm, stagraph, das, cmp, stupdate |
| 영상 화면 | live, repfocus |
| 이벤트 | evtdet, evthres, evt |
| 내려받기(엑셀) | xlsx |
| 작업 기록 | histre, histwr |
| 보안·운영 | sec, ops |

## 결정 기록
0001 YOLO-CROWD(대체됨 → 0015) · 0002 날씨 2순위 · 0003 VM 방화벽 2순위 · 0004 prod는 코드만 · 0005 계정 테이블 분리 · 0006 혼잡 3단계 · 0007 카드 미리보기 스냅샷 · 0008 명세 원본을 md로 · 0009 로깅 Log4j2 · 0010 공통 모듈 배치 기준 · 0011 개발 단계(1·2·3단계) · 0014 행정구역 계층(시·도/시·군·구/읍·면·동) · 0015 VisDrone YOLOv8m + PointTracker
