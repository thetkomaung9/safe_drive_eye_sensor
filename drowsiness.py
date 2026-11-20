"""졸음 판단: 눈이 안 보이거나 얼굴이 벗어난 시간을 잰다"""
import time


class DrowsinessJudge:
    WARNING = "WARNING"
    PULL_OVER = "PULL_OVER"

    def __init__(self, limit_sec=1.0, pull_over_sec=2.5, repeat_event_limit=3):
        self.limit_sec = limit_sec
        self.pull_over_sec = pull_over_sec
        self.repeat_event_limit = repeat_event_limit
        self.closed_since = None

    def update(self, face_found, eyes_found, now=None):
        """반환: (졸음 여부, 눈/얼굴이 안 보인 시간(초))"""
        now = time.time() if now is None else now
        # 얼굴이 보이고 눈도 보일 때만 정상 상태로 초기화
        # (얼굴이 돌아가거나 안 보이면 head turn / gaze away로 간주하고 시간 누적)
        if face_found and eyes_found:
            self.closed_since = None
            return False, 0.0
        if self.closed_since is None:
            self.closed_since = now
        closed = now - self.closed_since
        return closed >= self.limit_sec, closed

    def alert_level(self, drowsy, closed, repeated_events=0):
        if not drowsy:
            return None
        if closed >= self.pull_over_sec or repeated_events >= self.repeat_event_limit:
            return self.PULL_OVER
        return self.WARNING