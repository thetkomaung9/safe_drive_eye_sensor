"""실시간 운전자 졸음 감지 - 실행 파일  (종료: q 또는 ESC)"""
import time
import cv2
from camera import Camera
from detector import FaceEyeDetector
from drowsiness import DrowsinessJudge
from alarm import Alarm
from database import EventDB

LIMIT_SEC = 2.0   # 눈이 이 시간 이상 안 보이면 졸음으로 판단 (실험으로 조정)


def draw(frame, face, eyes, drowsy, closed, fps):
    color = (0, 0, 255) if drowsy else (0, 200, 0)
    if face is not None:
        x, y, w, h = face
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 120, 0), 2)
    for (x, y, w, h) in eyes:
        cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
    status = "DROWSY! WAKE UP" if drowsy else "OK"
    cv2.putText(frame, f"{status}  closed: {closed:.1f}s", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
    cv2.putText(frame, f"FPS: {fps:.0f}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    if drowsy:
        cv2.rectangle(frame, (0, 0), (frame.shape[1] - 1, frame.shape[0] - 1), (0, 0, 255), 6)


def main():
    cam, detector = Camera(), FaceEyeDetector()
    judge, alarm, db = DrowsinessJudge(LIMIT_SEC), Alarm(), EventDB()
    session_id = db.start_session()
    was_drowsy, episode_max, prev = False, 0.0, time.time()
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
                alarm.ring()
                episode_max = max(episode_max, closed)
            elif was_drowsy:                                # 졸음 상태가 끝남 -> DB에 기록
                db.log_event(session_id, "DROWSY", episode_max)
                episode_max = 0.0
            was_drowsy = drowsy

            draw(frame, face, eyes, drowsy, closed, fps)
            cv2.imshow("Driver Drowsiness Detection", frame)
            if cv2.waitKey(1) & 0xFF in (ord("q"), 27):
                break
    finally:
        if was_drowsy:
            db.log_event(session_id, "DROWSY", episode_max)
        cam.release()
        cv2.destroyAllWindows()
        db.end_session(session_id)
        db.close()


if __name__ == "__main__":
    main()
