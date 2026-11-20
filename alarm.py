"""경고음 클래스 (영상이 멈추지 않도록 별도 스레드에서 소리 재생)"""
import threading
import time


class Alarm:
    def __init__(self, cooldown=2.0):
        self.cooldown = cooldown   # 경고음 사이의 최소 간격(초)
        self.last = 0.0

    def _beep(self):
        try:
            import winsound                      # Windows
            winsound.Beep(1000, 500)
        except ImportError:                      # Mac / Linux
            print("\a", end="", flush=True)

    def ring(self):
        now = time.time()
        if now - self.last < self.cooldown:
            return False
        self.last = now
        threading.Thread(target=self._beep, daemon=True).start()
        return True
