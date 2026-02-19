# backend/app/utils/metrics.py
# 성능 측정을 위한 유틸리티 클래스 정의

import time

class Timer:
    def __enter__(self):
        self.start = time.perf_counter()
        return self

    def __exit__(self, *args):
        self.end = time.perf_counter()
        self.elapsed_ms = (self.end - self.start) * 1000
