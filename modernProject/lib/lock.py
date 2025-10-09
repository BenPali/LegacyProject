import os
import fcntl
import traceback
from typing import Callable, TypeVar, Any


T = TypeVar('T')


no_lock_flag = False


def pp_exception(exn: Exception) -> str:
    tb_str = ''.join(traceback.format_exception(type(exn), exn, exn.__traceback__))
    return f"Raised exception {type(exn).__name__}: {str(exn)}\n{tb_str}"


def _close_noerr(fd: int) -> None:
    try:
        os.close(fd)
    except:
        pass


def _chmod_noerr(fl: str, perm: int) -> None:
    try:
        os.chmod(fl, perm)
    except:
        pass


def _acquire_lock(wait: bool, lock_file: str) -> int:
    fd = os.open(lock_file, os.O_RDWR | os.O_CREAT, 0o666)
    _chmod_noerr(lock_file, 0o666)
    if wait:
        fcntl.lockf(fd, fcntl.LOCK_EX)
    else:
        fcntl.lockf(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    return fd


def _release_lock_noerr(fd: int) -> None:
    try:
        fcntl.lockf(fd, fcntl.LOCK_UN)
    except:
        pass


def control(
    on_exn: Callable[[Exception], T],
    wait: bool,
    lock_file: str,
    k: Callable[[], T]
) -> T:
    global no_lock_flag
    if no_lock_flag or os.path.basename(lock_file) == ".lck":
        return k()
    try:
        fd = _acquire_lock(wait, lock_file)
    except Exception as exn:
        return on_exn(exn)
    try:
        return k()
    finally:
        _release_lock_noerr(fd)
        _close_noerr(fd)
