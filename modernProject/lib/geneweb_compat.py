from typing import TypeVar, Callable, List, BinaryIO, TextIO

T = TypeVar('T')

class InChannel:
    @staticmethod
    def with_open_bin(filename: str, f: Callable[[BinaryIO], T]) -> T:
        with open(filename, 'rb') as ic:
            return f(ic)

    @staticmethod
    def with_open_text(filename: str, f: Callable[[TextIO], T]) -> T:
        with open(filename, 'r') as ic:
            return f(ic)

    @staticmethod
    def with_open_gen(mode: str, perm: int, filename: str, f: Callable[[object], T]) -> T:
        import os
        flags = os.O_RDONLY
        if 'w' in mode:
            flags = os.O_WRONLY | os.O_CREAT
        if 'a' in mode:
            flags |= os.O_APPEND

        fd = os.open(filename, flags, perm)
        file_obj = os.fdopen(fd, mode)
        try:
            return f(file_obj)
        finally:
            file_obj.close()

    @staticmethod
    def input(ic: BinaryIO, buf: bytearray, pos: int, length: int) -> int:
        data = ic.read(length)
        n = len(data)
        buf[pos:pos+n] = data
        return n

class OutChannel:
    @staticmethod
    def with_open_bin(filename: str, f: Callable[[BinaryIO], T]) -> T:
        with open(filename, 'wb') as oc:
            return f(oc)

    @staticmethod
    def with_open_text(filename: str, f: Callable[[TextIO], T]) -> T:
        with open(filename, 'w') as oc:
            return f(oc)

    @staticmethod
    def with_open_gen(mode: str, perm: int, filename: str, f: Callable[[object], T]) -> T:
        import os
        flags = os.O_WRONLY | os.O_CREAT
        if 'a' in mode:
            flags |= os.O_APPEND
        if 'x' in mode:
            flags |= os.O_EXCL

        fd = os.open(filename, flags, perm)
        file_obj = os.fdopen(fd, mode)
        try:
            return f(file_obj)
        finally:
            file_obj.close()

    @staticmethod
    def flush(oc):
        oc.flush()

    @staticmethod
    def output(oc: BinaryIO, buf: bytes, pos: int, length: int):
        oc.write(buf[pos:pos+length])

class ListCompat:
    @staticmethod
    def equal(eq: Callable[[T, T], bool], l1: List[T], l2: List[T]) -> bool:
        if len(l1) != len(l2):
            return False
        for a1, a2 in zip(l1, l2):
            if not eq(a1, a2):
                return False
        return True
