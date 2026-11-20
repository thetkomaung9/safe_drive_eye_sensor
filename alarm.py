"""Non-blocking warning and voice alerts."""
import queue
import shutil
import subprocess
import threading
import time


class Alarm:
    WARNING = "WARNING"
    PULL_OVER = "PULL_OVER"

    def __init__(self, cooldown=6.0):
        self.cooldown = cooldown
        self._last_alert = {}
        self._queue = queue.Queue(maxsize=1)
        self._worker = threading.Thread(target=self._run, daemon=True)
        self._worker.start()

    def _beep(self, urgent=False):
        try:
            import winsound

            winsound.Beep(1400 if urgent else 1000, 900 if urgent else 350)
        except (ImportError, OSError):
            print("\a\a" if urgent else "\a", end="", flush=True)

    def _speak(self, text):
        command = next(
            (
                cmd
                for cmd in ("say", "spd-say", "espeak")
                if shutil.which(cmd)
            ),
            None,
        )
        if command is None:
            return
        try:
            subprocess.run([command, text], check=False, timeout=10)
        except (OSError, subprocess.SubprocessError):
            pass

    def _run(self):
        while True:
            alert = self._queue.get()
            try:
                if alert == self.WARNING:
                    self._beep()
                elif alert == self.PULL_OVER:
                    self._beep(urgent=True)
                    self._speak(
                        "Drowsiness detected. Please safely pull over to the side "
                        "of the road and rest."
                    )
            finally:
                self._queue.task_done()

    def alert(self, level):
        if level not in (self.WARNING, self.PULL_OVER):
            return False
        now = time.time()
        if now - self._last_alert.get(level, 0.0) < self.cooldown:
            return False
        self._last_alert[level] = now

        # Queue ထဲမှာ ကျန်နေတဲ့ alert အဟောင်းကို ဖယ်ပြီး နောက်ဆုံး alert ကိုသာ ထည့်မည်
        while not self._queue.empty():
            try:
                self._queue.get_nowait()
                self._queue.task_done()
            except queue.Empty:
                break

        try:
            self._queue.put_nowait(level)
        except queue.Full:
            pass
        return True

    def ring(self):
        """Backward-compatible alias for the standard warning alert."""
        return self.alert(self.WARNING)
