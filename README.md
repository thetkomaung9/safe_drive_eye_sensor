# 실시간 운전자 졸음 감지 시스템 (OpenCV)

## 파일 구조 (클래스 1개 = 파일 1개)
| 파일 | 클래스 | 역할 |
|---|---|---|
| camera.py | Camera | 웹캠 영상 읽기 |
| detector.py | FaceEyeDetector | 전처리, 얼굴·눈 검출 (Haar Cascade) |
| drowsiness.py | DrowsinessJudge | 눈이 안 보이는 시간으로 졸음 판단 |
| alarm.py | Alarm | 경고음 |
| database.py | EventDB | SQLite에 졸음 기록 저장 |
| main.py | - | 실행 파일 |
| report.py | - | 저장된 기록 보기 |

## 실행 방법
```
pip install -r requirements.txt   # OpenCV 4.x 필요 (5.x에는 CascadeClassifier가 없음)
python main.py      # 종료: q 또는 ESC
python report.py    # 졸음 기록 보기
```
- 졸음 기준 시간은 `main.py`의 `LIMIT_SEC`에서 바꿉니다 (기본 2초).
- 기록은 `drowsiness.db` 파일에 저장됩니다.
