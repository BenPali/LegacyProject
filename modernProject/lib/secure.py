import os
from typing import List, Callable, TypeVar
from contextlib import contextmanager

T = TypeVar('T')

_ok_r: List[List[str]] = []
_assets_r: List[str] = ["gw"]
_bd_r: str = os.path.join(os.curdir, "bases")

def decompose(path: str) -> List[str]:
    result = []
    current = path

    while True:
        basename = os.path.basename(current)

        if basename == "" or basename == os.curdir or basename == os.sep:
            dirname = os.path.dirname(current)
            if dirname == "" or dirname == os.curdir:
                break
            elif dirname == current:
                result.insert(0, dirname)
                break
            else:
                current = dirname
        elif basename == current:
            result.insert(0, basename)
            break
        else:
            result.insert(0, basename)
            current = os.path.dirname(current)

    return result

def add_assets(d: str):
    global _assets_r, _ok_r
    if d not in _assets_r:
        _assets_r.append(d)
        _ok_r.append(decompose(d))

def set_base_dir(d: str):
    global _bd_r, _ok_r
    ok = decompose(d)
    _bd_r = d
    _ok_r = [ok] + [x for x in _ok_r if x != ok]

def assets() -> List[str]:
    return _assets_r.copy()

def base_dir() -> str:
    return _bd_r

def list_check_prefix(d: List[str], df: List[str]) -> List[str]:
    i = 0
    while i < len(d) and i < len(df):
        if d[i] != df[i]:
            return None
        i += 1

    if i == len(d):
        return df[i:]
    return None

def check(fname: str) -> bool:
    if '\0' in fname:
        return False

    df = decompose(fname)

    for d in _ok_r:
        bf = list_check_prefix(d, df)
        if bf is not None and os.pardir not in bf:
            return True

    if not os.path.isabs(fname):
        return os.pardir not in df

    return False

def check_open(fname: str):
    if not check(fname):
        import sys
        if sys.platform != 'win32':
            import sys
            print(f"*** secure rejects open {repr(fname)}", file=sys.stderr)
            sys.stderr.flush()
        raise OSError(f"invalid access: {fname}")

def open_in(fname: str):
    check_open(fname)
    return open(fname, 'r')

def with_open_in_text(fname: str, f: Callable[[object], T]) -> T:
    check_open(fname)
    with open(fname, 'r') as ic:
        return f(ic)

def open_in_bin(fname: str):
    check_open(fname)
    return open(fname, 'rb')

def with_open_in_bin(fname: str, f: Callable[[object], T]) -> T:
    check_open(fname)
    with open(fname, 'rb') as ic:
        return f(ic)

def open_out(fname: str):
    check_open(fname)
    return open(fname, 'w')

def with_open_out_text(fname: str, f: Callable[[object], T]) -> T:
    check_open(fname)
    with open(fname, 'w') as oc:
        return f(oc)

def open_out_bin(fname: str):
    check_open(fname)
    return open(fname, 'wb')

def with_open_out_bin(fname: str, f: Callable[[object], T]) -> T:
    check_open(fname)
    with open(fname, 'wb') as oc:
        return f(oc)

def open_out_gen(mode: str, perm: int, fname: str):
    check_open(fname)
    flags = os.O_WRONLY | os.O_CREAT
    if 'a' in mode:
        flags |= os.O_APPEND
    if 'x' in mode:
        flags |= os.O_EXCL
    if 't' not in mode:
        flags |= os.O_TRUNC

    fd = os.open(fname, flags, perm)
    return os.fdopen(fd, mode)

def with_open_out_gen(mode: str, perm: int, fname: str, f: Callable[[object], T]) -> T:
    check_open(fname)
    with open_out_gen(mode, perm, fname) as oc:
        return f(oc)
