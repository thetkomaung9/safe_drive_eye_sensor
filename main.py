"""실시간 운전자 졸음 감지 - 실행 파일  (종료: q 또는 ESC)"""
import time
from collections import deque

import cv2
from camera import Camera
from detector import FaceEyeDetector
from drowsiness import DrowsinessJudge
from alarm import Alarm
from database import EventDB

LIMIT_SEC = 2.0   # 눈이 이 시간 이상 안 보이면 졸음으로 판단 (실험으로 조정)
PULL_OVER_SEC = 5.0
REPEAT_WINDOW_SEC = 60.0
REPEAT_EVENT_LIMIT = 3


def draw(frame, face, eyes, drowsy, closed, fps, alert_level=None):
    color = (
        (0, 0, 255) if alert_level == "PULL_OVER"
        else (0, 165, 255) if alert_level == "WARNING"
        else (0, 200, 0)
    )
    if face is not None:
        x, y, w, h = face
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 120, 0), 2)
    for (x, y, w, h) in eyes:
        cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
    status = "DROWSY! WAKE UP" if drowsy else "OK"
    cv2.putText(frame, f"{status}  closed: {closed:.1f}s", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
    cv2.putText(frame, f"FPS: {fps:.0f}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    if alert_level == "WARNING":
        cv2.rectangle(frame, (0, 75), (frame.shape[1] - 1, 125), (0, 165, 255), -1)
        cv2.putText(frame, "WARNING: PLEASE STAY ALERT", (15, 108),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
    elif alert_level == "PULL_OVER":
        cv2.rectangle(frame, (0, 0), (frame.shape[1] - 1, frame.shape[0] - 1), (0, 0, 255), 6)
        cv2.rectangle(frame, (0, 75), (frame.shape[1] - 1, 145), (0, 0, 180), -1)
        cv2.putText(frame, "PULL OVER SAFELY AND REST", (15, 110),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.85, (255, 255, 255), 2)
        cv2.putText(frame, "DROWSINESS DETECTED", (15, 137),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)


def main():
    cam, detector = Camera(), FaceEyeDetector()
    judge = DrowsinessJudge(LIMIT_SEC, PULL_OVER_SEC, REPEAT_EVENT_LIMIT)
    alarm, db = Alarm(), EventDB()
    session_id = db.start_session()
    was_drowsy, episode_max, episode_alert = False, 0.0, None
    drowsy_events = deque()
    prev = time.time()
    try:
        while True:
            frame = cam.read()
            if frame is None:
                break
            frame = cv2.flip(frame, 1)                      # 거울처럼 보이게
            face, eyes = detector.detect(frame)
            drowsy, closed = judge.update(face is not None, len(eyes) > 0)
            t = time.time(); fps = 1 / max(t - prev, 1e-6); prev = t

            if drowsy:
                while drowsy_events and t - drowsy_events[0] > REPEAT_WINDOW_SEC:
                    drowsy_events.popleft()
                repeated_events = len(drowsy_events) + (0 if was_drowsy else 1)
                alert_level = judge.alert_level(drowsy, closed, repeated_events)
                alarm.alert(alert_level)
                episode_max = max(episode_max, closed)
                episode_alert = (
                    "PULL_OVER"
                    if alert_level == "PULL_OVER" or episode_alert == "PULL_OVER"
                    else "WARNING"
                )
            elif was_drowsy:                                # 졸음 상태가 끝남 -> DB에 기록
                db.log_event(session_id, "DROWSY", episode_max, episode_alert)
                drowsy_events.append(t)
                episode_max, episode_alert = 0.0, None
            was_drowsy = drowsy

            draw(frame, face, eyes, drowsy, closed, fps, episode_alert if drowsy else None)
            cv2.imshow("Driver Drowsiness Detection", frame)
            if cv2.waitKey(1) & 0xFF in (ord("q"), 27):
                break
    finally:
        if was_drowsy:
            db.log_event(session_id, "DROWSY", episode_max, episode_alert)
        cam.release()
        cv2.destroyAllWindows()
        db.end_session(session_id)
        db.close()


if __name__ == "__main__":
    main()
