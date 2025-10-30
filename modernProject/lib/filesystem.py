import os
import stat
import shutil
from pathlib import Path
from typing import Callable, TypeVar, Union
from dataclasses import dataclass

class FileError(Exception):
    pass

T = TypeVar('T')

def check_perm(perm: int, path: str) -> bool:
    if os.name == 'nt':
        return True
    st = os.stat(path)
    return (st.st_mode & 0o777) == perm

def check_kind(kind: str, path: str) -> bool:
    st = os.stat(path)
    if kind == 'file':
        return stat.S_ISREG(st.st_mode)
    elif kind == 'dir':
        return stat.S_ISDIR(st.st_mode)
    return False

def create_file(path: str, required_perm: int = None):
    perm = required_perm if required_perm is not None else 0o644

    if os.path.exists(path):
        if not check_kind('file', path):
            raise FileError(f"{path} exists but it is not a regular file")
    else:
        fd = os.open(path, os.O_CREAT | os.O_WRONLY, perm)
        os.close(fd)

    if required_perm is not None and not check_perm(perm, path):
        raise FileError(f"{path} has not the required permissions {oct(perm)}")

def mkdir(perm: int, dir_path: str):
    if os.path.exists(dir_path):
        if not check_kind('dir', dir_path):
            raise FileError(f"{dir_path} exists but it is not a directory")
    else:
        os.mkdir(dir_path, perm)

def iter_path_entries(f: Callable[[str], None], path: str):
    def loop(p):
        dirname = os.path.dirname(p)
        basename = os.path.basename(p)
        if dirname in (".", "/"):
            f(p)
        else:
            loop(dirname)
            f(os.path.join(dirname, basename))
    loop(path)

def create_dir(path: str, parent: bool = False, required_perm: int = None):
    if path == "":
        raise ValueError("create_dir: empty path")

    perm = required_perm if required_perm is not None else 0o755

    if parent:
        iter_path_entries(lambda p: mkdir(perm, p), path)
    else:
        mkdir(perm, path)

    if required_perm is not None and not check_perm(perm, path):
        raise FileError(f"{path} has not the required permissions {oct(perm)}")

@dataclass
class FileEntry:
    path: str

@dataclass
class DirEntry:
    path: str

@dataclass
class ExnEntry:
    path: str
    exn: Exception
    bt: str

Entry = Union[FileEntry, DirEntry, ExnEntry]

def walk_folder(f: Callable[[Entry], T], path: str, acc: T, recursive: bool = False) -> T:
    def walk_siblings(dirs, dir_path, acc_val):
        try:
            entries = os.listdir(dir_path)
        except OSError as e:
            import traceback
            return dirs, f(ExnEntry(dir_path, e, traceback.format_exc()), acc_val)

        new_dirs = []
        for entry in entries:
            if entry in (".", ".."):
                continue

            full_path = os.path.join(dir_path, entry)
            try:
                st = os.stat(full_path)
                if stat.S_ISREG(st.st_mode):
                    acc_val = f(FileEntry(full_path), acc_val)
                elif stat.S_ISDIR(st.st_mode):
                    if recursive:
                        new_dirs.append(full_path)
                    acc_val = f(DirEntry(full_path), acc_val)
            except OSError as e:
                import traceback
                acc_val = f(ExnEntry(full_path, e, traceback.format_exc()), acc_val)

        return dirs + new_dirs, acc_val

    def traverse(stack, acc_val):
        if not stack:
            return acc_val

        current_path = stack.pop(0)
        try:
            stack, acc_val = walk_siblings(stack, current_path, acc_val)
        except Exception as e:
            import traceback
            acc_val = f(ExnEntry(current_path, e, traceback.format_exc()), acc_val)

        return traverse(stack, acc_val)

    return traverse([path], acc)

def copy_file(src: str, dst: str, perm: int = 0o640, overwrite: bool = True):
    if not overwrite and os.path.exists(dst):
        raise FileExistsError(f"{dst} already exists")

    with open(src, 'rb') as src_file:
        with open(dst, 'wb') as dst_file:
            shutil.copyfileobj(src_file, dst_file)

    os.chmod(dst, perm)


def remove_dir(path: str):
    if os.path.exists(path):
        shutil.rmtree(path)
