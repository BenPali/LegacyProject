import gzip
from typing import TextIO
from contextlib import contextmanager

class InChannel:
    def __init__(self, path: str):
        self._file = gzip.open(path, 'rt', encoding='utf-8')

    def close(self):
        if self._file:
            self._file.close()

    def close_noerr(self):
        try:
            self.close()
        except:
            pass

    def input_line(self) -> str:
        line = self._file.readline()
        if not line:
            raise EOFError
        return line.rstrip('\n')

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_noerr()
        return False

def open_in(path: str) -> InChannel:
    return InChannel(path)

def close_in(ic: InChannel):
    ic.close()

def close_in_noerr(ic: InChannel):
    ic.close_noerr()

def input_line(ic: InChannel) -> str:
    return ic.input_line()

@contextmanager
def with_open(path: str):
    ic = open_in(path)
    try:
        yield ic
    finally:
        close_in_noerr(ic)
