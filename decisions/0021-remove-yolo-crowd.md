# 0021. YOLO-CROWD 코드와 DETECTOR=yolo-crowd 선택지를 제거함

- 상태: 채택
- 기록: 2026-11-17
- 관련: FNC-S-003, 0001(YOLO-CROWD 사용, 대체됨), 0015(VisDrone YOLOv8m + PointTracker), white-eyes1/white-eyes-flask#71

## 맥락
- 사람 탐지는 0015에서 VisDrone YOLOv8m으로 바뀌었고, YOLO-CROWD는 `DETECTOR=yolo-crowd`로 고를 수 있는 선택지로만 코드에 남아 있었다(white-eyes-flask `vendor/yolo_crowd/`, `YoloCrowdDetector`).
- `vendor/yolo_crowd/`는 YOLOv5 파생 코드이고, 학습 데이터셋의 라이선스는 확인하지 못했다(0001).

## 결정
1. white-eyes-flask에서 `vendor/yolo_crowd/`(`LICENSE.yolov5` 포함)와 `YoloCrowdDetector`, `DETECTOR=yolo-crowd` 선택지를 제거한다.
2. `DETECTOR`는 `visdrone`만 받는다. 다른 값이면 시작할 때 오류가 난다.
3. 0001·0015의 기록은 당시 판단 그대로 두고, 제거했다는 사실만 덧붙인다.

## 이유
- PM 결정(2026-11-17).
- YOLOv5 파생 코드와 라이선스를 확인하지 못한 학습 데이터셋을 저장소에 두지 않는다. 기본 탐지기는 이미 0015에서 VisDrone YOLOv8m으로 바뀌어 이 코드는 쓰지 않는다.
- 그 밖의 이유는 기록 없음.

## 검토한 다른 방법
- 기록 없음.

## 영향
- 코드: `vendor/yolo_crowd/`, `analysis/detector.py`의 YOLO-CROWD 탐지기, `detector_provider.py`의 `yolo-crowd` 분기, 관련 테스트가 없어진다. 기본 탐지기 동작은 같다.
- 명세: conventions.md `DETECTOR` 표, overview.md '분석 모델', package-structure.md에서 YOLO-CROWD 설명을 뺐다.
- Ultralytics YOLOv8(AGPL-3.0)과 VisDrone 가중치의 라이선스 문제는 이 결정으로 해결되지 않는다(0015 열린 질문 1).
