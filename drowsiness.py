"""졸음 판단: 눈이 안 보이는 시간을 잰다"""
import time


class DrowsinessJudge:
    WARNING = "WARNING"
    PULL_OVER = "PULL_OVER"

    def __init__(
        self,
        limit_sec=2.0,
        pull_over_sec=None,
        repeat_event_limit=3,
        event_window_sec=60.0,
    ):
        self.limit_sec = limit_sec
        self.pull_over_sec = (
            pull_over_sec if pull_over_sec is not None else limit_sec * 2
        )
        self.repeat_event_limit = repeat_event_limit
        self.event_window_sec = event_window_sec

        self.closed_since = None
        self._was_drowsy = False
        self._event_timestamps = []

    def _prune_old_events(self, now):
        cutoff = now - self.event_window_sec
        self._event_timestamps = [t for t in self._event_timestamps if t >= cutoff]

    def update(self, face_found, eyes_found, now=None):
        """반환: (졸음 여부, 눈이 안 보인 시간(초))"""
        now = time.time() if now is None else now
        self._prune_old_events(now)

        if face_found and eyes_found:
            self.closed_since = None
            self._was_drowsy = False
            return False, 0.0

        if self.closed_since is None:
            self.closed_since = now

        closed = now - self.closed_since
        is_drowsy = closed >= self.limit_sec

        # 졸음 상태로 새로 진입할 때만 이벤트 횟수로 기록
        if is_drowsy and not self._was_drowsy:
            self._event_timestamps.append(now)
        self._was_drowsy = is_drowsy

        return is_drowsy, closed

    def recent_event_count(self, now=None):
        now = time.time() if now is None else now
        self._prune_old_events(now)
        return len(self._event_timestamps)

    def alert_level(self, drowsy, closed, repeated_events=None, now=None):
        """반환: None | 'WARNING' | 'PULL_OVER'"""
        if not drowsy:
            return None

        events = (
            self.recent_event_count(now=now)
            if repeated_events is None
            else repeated_events
        )

        if closed >= self.pull_over_sec or events >= self.repeat_event_limit:
            return self.PULL_OVER
        return self.WARNING