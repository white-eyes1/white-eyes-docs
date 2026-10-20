# 0001. 사람 탐지 모델로 YOLO-CROWD 사용

- 상태: 채택
- 기록: 2026-10-18 (명세서 시트에서 옮김)
- 관련: overview.md '기술 스택·외부 연동 사양 > 분석 모델', 알려진 한계 16~18, conventions.md `DETECT_CONF / DETECT_IMGSZ / YOLO_WEIGHTS`

## 맥락
높은 고도의 드론·CCTV 영상은 사람이 작고 빽빽하다. CPU 추론으로 초당 5프레임(ANALYZE_FPS)을 지켜야 한다.

## 결정
YOLO-CROWD(YOLOv5s 기반 머리 탐지, 클래스 'people' 1개)를 입력 960, 신뢰도 0.3으로 시작한다. 추적은 ByteTrack을 탐지와 따로 호출한다.

## 근거 (overview.md '분석 모델'에서 인용)
- VisDrone 드론 사진 120장(사람 4,074명) 비교
  - YOLOv8n(COCO), 입력 960: 실제의 약 18%, 상관계수 0.51
  - YOLO-CROWD, 입력 960: 약 30%, 상관계수 0.70
  - YOLO-CROWD, 입력 1280: 약 43%, 상관계수 0.73
- "이 PC에서 입력 960은 이미지당 약 0.33초, 1280은 약 0.5초라 초당 5프레임을 지키려면 960 이하만 쓸 수 있다."

## 영향
- 센 수는 실제의 일부이므로 '추정 인원'과 상대 혼잡 지표로만 쓴다. 혼잡 단계 경계 밀도는 이 센 값 기준으로 실제 영상에서 맞춘다.
- Ultralytics `model.track()`으로 불러올 수 없어 YOLOv5 저장소 코드와 `yolo-crowd.pt`가 필요하다. torch 2.6 이상은 `torch.load(weights_only=False)`.
- 라이선스: YOLO-CROWD는 MIT 표기지만 YOLOv5 기반이라 사용 전에 원 라이선스를 확인한다.

## 갱신 (2026-10-20): 코드·가중치 입수 경로와 라이선스 현황
- 코드: white-eyes-flask `vendor/yolo_crowd/`는 zaki1003/YOLO-CROWD 커밋 `fbe4f63`(2025-11-04)의 `models/`·`utils/` 40개 파일과 내용이 같다(git 객체 해시 비교로 확인). 수정하지 않았다.
- 가중치: 원 저장소 README의 'Postweight'(Google Drive 링크)로 받는다. 원 저장소는 Release·체크섬을 제공하지 않는다. 팀은 비공개 저장소 white-eyes1/white-eyes-assets의 Release `yolo-crowd-v1`로 공유한다(37,220,901바이트, SHA-256 `22aea94cad4eb181e94ea600b0013cf7307b1a4dd8788cc8454dc5ca5f573c39`, 받은 파일의 수정 시각 2026-10-15). 공개 저장소에는 올리지 않는다.
- 라이선스 현황(확인한 범위): 원 저장소는 MIT로 표기한다. 그러나 학습 시작 가중치가 Ultralytics `yolov5s.pt`(v5.0)이고 코드도 YOLOv5 파생이다. YOLOv5 v5.0은 GPL-3.0이었고 현재는 AGPL-3.0이다. 학습 데이터셋(Roboflow `crowd-counting-dataset-w3o7w`)의 라이선스는 확인하지 못했다. 가중치 파일에 대한 별도 라이선스 문구는 없다. 추적기(Ultralytics `BYTETracker`)도 AGPL-3.0이다.
- 현재는 팀 안의 시연·학습 목적으로 쓴다. 배포하거나 저장소·가중치를 공개하기 전에 위 항목을 다시 확인한다.
