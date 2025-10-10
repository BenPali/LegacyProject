import os
import sys
import struct
from typing import Optional, List, Tuple, Callable, Any, Dict, TypeVar
from dataclasses import dataclass
from lib.dbdisk import (
    DskPerson, DskAscend, DskUnion, DskFamily, DskCouple, DskDescend,
    RecordAccess, StringPersonIndex, BaseData, BaseFunc, BaseVersion, DskBase,
    Perm
)
from lib.gwdef import BaseNotes
from lib import iovalue
from lib import secure
from lib import mutil
from lib import name
from lib import dutil

T = TypeVar('T')

MAGIC_GNWB0020 = b"GnWb0020"
MAGIC_GNWB0021 = b"GnWb0021"
MAGIC_GNWB0022 = b"GnWb0022"
MAGIC_GNWB0023 = b"GnWb0023"
MAGIC_GNWB0024 = b"GnWb0024"
MAGIC_PATCH = b"GnPa0001"

@dataclass
class SynchroPath:
    synch_list: List[Tuple[str, List[int], List[int]]]

@dataclass
class PatchesHt:
    h_person: Tuple[List[int], Dict[int, DskPerson]]
    h_ascend: Tuple[List[int], Dict[int, DskAscend]]
    h_union: Tuple[List[int], Dict[int, DskUnion]]
    h_family: Tuple[List[int], Dict[int, DskFamily]]
    h_couple: Tuple[List[int], Dict[int, DskCouple]]
    h_descend: Tuple[List[int], Dict[int, DskDescend]]
    h_string: Tuple[List[int], Dict[int, str]]
    h_name: Dict[int, List[int]]

def input_binary_int(ic) -> int:
    data = ic.read(4)
    if len(data) < 4:
        raise EOFError("Unexpected end of file")
    return struct.unpack('>I', data)[0]

def output_binary_int(oc, n: int) -> None:
    oc.write(struct.pack('>I', n & 0xFFFFFFFF))

def check_magic(magic: bytes, ic) -> bool:
    pos = ic.tell()
    try:
        read_magic = ic.read(len(magic))
        if read_magic == magic:
            return True
        ic.seek(pos)
        return False
    except:
        ic.seek(pos)
        return False

def move_with_backup(src: str, dst: str) -> None:
    backup = dst + "~"
    if os.path.exists(backup):
        os.remove(backup)
    if os.path.exists(dst):
        os.rename(dst, backup)
    os.rename(src, dst)

def empty_patch_ht() -> PatchesHt:
    return PatchesHt(
        h_person=([0], {}),
        h_ascend=([0], {}),
        h_union=([0], {}),
        h_family=([0], {}),
        h_couple=([0], {}),
        h_descend=([0], {}),
        h_string=([0], {}),
        h_name={}
    )

def input_patches(bname: str) -> Optional[PatchesHt]:
    fname = os.path.join(bname, "patches")
    if not os.path.exists(fname):
        return empty_patch_ht()

    try:
        with secure.open_in_bin(fname) as ic:
            if check_magic(MAGIC_PATCH, ic):
                return iovalue.input_value(ic)
            else:
                ic.seek(0)
                return empty_patch_ht()
    except Exception as e:
        print(f"Warning: Could not load patches: {e}", file=sys.stderr)
        return empty_patch_ht()

def input_synchro(bname: str) -> SynchroPath:
    fname = os.path.join(bname, "synchro_patches")
    if not os.path.exists(fname):
        return SynchroPath(synch_list=[])

    try:
        with secure.open_in_bin(fname) as ic:
            return iovalue.input_value(ic)
    except:
        return SynchroPath(synch_list=[])

def with_database(bname: str, k: Callable[[DskBase], T], read_only: bool = False) -> T:
    if not bname.endswith(".gwb"):
        bname = bname + ".gwb"

    base_file = os.path.join(bname, "base")
    if not os.path.exists(base_file):
        raise FileNotFoundError(f"Database not found: {base_file}")

    patches = input_patches(bname)
    pending = empty_patch_ht()

    tm_fname = os.path.join(bname, "commit_timestamp")
    perm = Perm.RDONLY if os.path.exists(tm_fname) or read_only else Perm.RDRW

    if patches:
        pending.h_person[0][:] = patches.h_person[0][:]
        pending.h_ascend[0][:] = patches.h_ascend[0][:]
        pending.h_union[0][:] = patches.h_union[0][:]
        pending.h_family[0][:] = patches.h_family[0][:]
        pending.h_couple[0][:] = patches.h_couple[0][:]
        pending.h_descend[0][:] = patches.h_descend[0][:]
        pending.h_string[0][:] = patches.h_string[0][:]

    synchro = input_synchro(bname)

    particles_file = os.path.join(bname, "particles.txt")
    particles_txt = []
    if os.path.exists(particles_file):
        try:
            with open(particles_file, 'r', encoding='utf-8') as f:
                particles_txt = [line.strip() for line in f if line.strip()]
        except:
            pass

    with secure.open_in_bin(base_file) as ic:
        version = None
        if check_magic(MAGIC_GNWB0024, ic):
            version = BaseVersion.GNWB0024
        elif check_magic(MAGIC_GNWB0023, ic):
            version = BaseVersion.GNWB0023
        elif check_magic(MAGIC_GNWB0022, ic):
            version = BaseVersion.GNWB0022
        elif check_magic(MAGIC_GNWB0021, ic):
            version = BaseVersion.GNWB0021
        elif check_magic(MAGIC_GNWB0020, ic):
            version = BaseVersion.GNWB0020
        else:
            magic_start = ic.read(4)
            if magic_start == b"GnWb":
                raise ValueError("This is a GeneWeb base, but not compatible version")
            raise ValueError("This is not a GeneWeb base, or it is a very old version")

        persons_len = input_binary_int(ic)
        families_len = input_binary_int(ic)
        strings_len = input_binary_int(ic)
        persons_array_pos = input_binary_int(ic)
        ascends_array_pos = input_binary_int(ic)
        unions_array_pos = input_binary_int(ic)
        families_array_pos = input_binary_int(ic)
        couples_array_pos = input_binary_int(ic)
        descends_array_pos = input_binary_int(ic)
        strings_array_pos = input_binary_int(ic)
        norigin_file = iovalue.input_value(ic)

        base_acc_file = os.path.join(bname, "base.acc")
        ic_acc = None
        if os.path.exists(base_acc_file):
            ic_acc = open(base_acc_file, 'rb')

        bnotes = BaseNotes(norigin_file=norigin_file)

        shift = 0
        im_persons = make_immut_record_access(
            read_only, ic, ic_acc, shift, persons_array_pos, persons_len, "persons"
        )
        shift += persons_len * iovalue.SIZEOF_LONG

        im_ascends = make_immut_record_access(
            read_only, ic, ic_acc, shift, ascends_array_pos, persons_len, "ascends"
        )
        shift += persons_len * iovalue.SIZEOF_LONG

        im_unions = make_immut_record_access(
            read_only, ic, ic_acc, shift, unions_array_pos, persons_len, "unions"
        )
        shift += persons_len * iovalue.SIZEOF_LONG

        im_families = make_immut_record_access(
            read_only, ic, ic_acc, shift, families_array_pos, families_len, "families"
        )
        shift += families_len * iovalue.SIZEOF_LONG

        im_couples = make_immut_record_access(
            read_only, ic, ic_acc, shift, couples_array_pos, families_len, "couples"
        )
        shift += families_len * iovalue.SIZEOF_LONG

        im_descends = make_immut_record_access(
            read_only, ic, ic_acc, shift, descends_array_pos, families_len, "descends"
        )
        shift += families_len * iovalue.SIZEOF_LONG

        im_strings = make_immut_record_access(
            read_only, ic, ic_acc, shift, strings_array_pos, strings_len, "strings"
        )

        persons = make_record_access(im_persons, patches.h_person, pending.h_person, persons_len)
        ascends = make_record_access(im_ascends, patches.h_ascend, pending.h_ascend, persons_len)
        unions = make_record_access(im_unions, patches.h_union, pending.h_union, persons_len)
        families = make_record_access(im_families, patches.h_family, pending.h_family, families_len)
        couples = make_record_access(im_couples, patches.h_couple, pending.h_couple, families_len)
        descends = make_record_access(im_descends, patches.h_descend, pending.h_descend, families_len)
        strings = make_record_access(im_strings, patches.h_string, pending.h_string, strings_len)

        base = DskBase(
            data=BaseData(
                persons=persons,
                ascends=ascends,
                unions=unions,
                visible=None,
                families=families,
                couples=couples,
                descends=descends,
                strings=strings,
                particles_txt=particles_txt,
                particles=None,
                bnotes=bnotes,
                bdir=bname,
                perm=perm
            ),
            func=None,
            version=version
        )

        try:
            result = k(base)
            return result
        finally:
            if ic_acc:
                ic_acc.close()

def apply_patches(arr: List[T], patches: Dict[int, T], new_len: int) -> List[T]:
    if new_len <= len(arr):
        result = arr.copy()
    else:
        result = arr + [None] * (new_len - len(arr))

    for i, val in patches.items():
        if i < len(result):
            result[i] = val
        else:
            while len(result) <= i:
                result.append(None)
            result[i] = val

    return result

class ImmutRecord:
    def __init__(self, read_only: bool, ic, ic_acc, shift: int, array_pos: int,
                 len_val: int, name: str):
        self.read_only = read_only
        self.ic = ic
        self.ic_acc = ic_acc
        self.shift = shift
        self.array_pos = array_pos
        self.len = len_val
        self.name = name
        self.cached_array = None
        self.cleared = False

    def im_get(self, i: int) -> Any:
        if self.cached_array is not None:
            return self.cached_array[i]

        if i < 0 or i >= self.len:
            raise IndexError(f"access {self.name} out of bounds; i = {i}")

        if self.ic_acc is not None:
            self.ic_acc.seek(self.shift + (iovalue.SIZEOF_LONG * i))
            pos = input_binary_int(self.ic_acc)
            self.ic.seek(pos)
            return iovalue.input_value(self.ic)
        else:
            raise RuntimeError("Sorry; I really need base.acc")

    def im_array(self) -> List[Any]:
        if self.cached_array is not None:
            return self.cached_array

        self.ic.seek(self.array_pos)
        self.cached_array = iovalue.input_value(self.ic)
        return self.cached_array

    def im_clear_array(self) -> None:
        self.cleared = True
        self.cached_array = None

def make_immut_record_access(read_only: bool, ic, ic_acc, shift: int,
                              array_pos: int, len_val: int, name: str) -> ImmutRecord:
    return ImmutRecord(read_only, ic, ic_acc, shift, array_pos, len_val, name)

def make_record_access(immut_record: ImmutRecord,
                       patches: Tuple[List[int], Dict[int, Any]],
                       pending: Tuple[List[int], Dict[int, Any]],
                       base_len: int) -> RecordAccess:
    plenr, patches_dict = patches
    _, pending_dict = pending

    def get_nopending(i: int) -> Any:
        if i in patches_dict:
            return patches_dict[i]
        return immut_record.im_get(i)

    def get(i: int) -> Any:
        if i in pending_dict:
            return pending_dict[i]
        return get_nopending(i)

    current_len = max(base_len, plenr[0] if plenr else 0)

    def load_array() -> None:
        immut_record.im_array()

    def output_array(oc) -> None:
        arr = immut_record.im_array()
        if immut_record.read_only:
            raise RuntimeError("cannot modify read-only data")
        patched_arr = apply_patches(arr, patches_dict, current_len)
        dutil.output_value_no_sharing(oc, patched_arr)

    def clear_array() -> None:
        immut_record.im_clear_array()

    return RecordAccess(
        load_array=load_array,
        get=get,
        get_nopending=get_nopending,
        len=current_len,
        output_array=output_array,
        clear_array=clear_array
    )

def make(bname: str, particles: List[str], arrays: Tuple[Any, Any, Any, BaseNotes],
         k: Callable[[DskBase], T]) -> T:
    raise NotImplementedError("make() not yet implemented")
