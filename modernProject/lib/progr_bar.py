import sys
import time


class ProgressBar:
    def __init__(self, width: int = 60, empty: str = '.', full: str = '#', disabled: bool = False):
        self.width = width
        self.empty = empty
        self.full = full
        self.disabled = disabled
        self.last_output = 0.0

    def progress(self, current: int, total: int) -> None:
        if self.disabled:
            return
        now = time.time()
        if now - self.last_output < 0.2:
            return
        self.last_output = now
        filled = current * self.width // total
        bar = self.full * filled + self.empty * (self.width - filled)
        percentage = current * 100 // total
        sys.stderr.write(f"\r[{bar}] {percentage}%")
        sys.stderr.flush()

    def finish(self) -> None:
        if not self.disabled:
            bar = self.full * self.width
            sys.stderr.write(f"\r[{bar}] 100%\n")
            sys.stderr.flush()


def with_bar(width: int = 60, empty: str = '.', full: str = '#', disabled: bool = False):
    def decorator(func):
        def wrapper(*args, **kwargs):
            bar = ProgressBar(width, empty, full, disabled)
            try:
                return func(bar, *args, **kwargs)
            finally:
                bar.finish()
        return wrapper
    return decorator
