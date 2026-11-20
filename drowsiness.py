"""졸음 판단: 눈이 안 보이는 시간을 잰다"""
import time


class DrowsinessJudge:
    def __init__(self, limit_sec=2.0):
        self.limit_sec = limit_sec   # 이 시간(초)보다 오래 눈이 안 보이면 졸음
        self.closed_since = None     # 눈이 안 보이기 시작한 시각

    def update(self, face_found, eyes_found, now=None):
        """반환: (졸음 여부, 눈이 안 보인 시간(초))"""
        now = time.time() if now is None else now
        if face_found and eyes_found:        # 눈이 보임 -> 초기화
            self.closed_since = None
            return False, 0.0
        if self.closed_since is None:        # 눈이 안 보이기 시작함
            self.closed_since = now
        closed = now - self.closed_since     # 얼굴이 사라진 경우(고개 숙임)도 포함
        return closed >= self.limit_sec, closed
