import time


class FPSLimiter:
    def __init__(self, fps: float):
        self._period = 1.0 / max(1e-6, fps)
        self._last = time.perf_counter()

    def sleep(self) -> None:
        now = time.perf_counter()
        elapsed = now - self._last
        remaining = self._period - elapsed
        if remaining > 0:
            time.sleep(remaining)
        self._last = time.perf_counter()
