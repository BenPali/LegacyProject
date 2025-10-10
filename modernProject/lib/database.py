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

        base_data = BaseData(
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
        )

        persons_of_name_fn = persons_of_name(bname, patches.h_name)
        persons_of_surname_fn = persons_of_surname(version, base_data, patches.h_person[1], bname)
        persons_of_first_name_fn = persons_of_first_name(version, base_data, patches.h_person[1], bname)

        def patch_person_fn(i: int, p: DskPerson) -> None:
            if i == -1:
                raise ValueError("Invalid person index -1")
            persons.len = max(persons.len, i + 1)
            pending.h_person[0][0] = persons.len
            pending.h_person[1][i] = p

        def patch_ascend_fn(i: int, a: DskAscend) -> None:
            if i == -1:
                raise ValueError("Invalid ascend index -1")
            ascends.len = max(ascends.len, i + 1)
            pending.h_ascend[0][0] = ascends.len
            pending.h_ascend[1][i] = a

        def patch_union_fn(i: int, u: DskUnion) -> None:
            if i == -1:
                raise ValueError("Invalid union index -1")
            unions.len = max(unions.len, i + 1)
            pending.h_union[0][0] = unions.len
            pending.h_union[1][i] = u

        def patch_family_fn(i: int, f: DskFamily) -> None:
            if i == -1:
                raise ValueError("Invalid family index -1")
            families.len = max(families.len, i + 1)
            pending.h_family[0][0] = families.len
            pending.h_family[1][i] = f

        def patch_couple_fn(i: int, c: DskCouple) -> None:
            if i == -1:
                raise ValueError("Invalid couple index -1")
            couples.len = max(couples.len, i + 1)
            pending.h_couple[0][0] = couples.len
            pending.h_couple[1][i] = c

        def patch_descend_fn(i: int, d: DskDescend) -> None:
            if i == -1:
                raise ValueError("Invalid descend index -1")
            descends.len = max(descends.len, i + 1)
            pending.h_descend[0][0] = descends.len
            pending.h_descend[1][i] = d

        def insert_string_fn(s: str) -> int:
            for i, existing in pending.h_string[1].items():
                if existing == s:
                    return i
            for i, existing in patches.h_string[1].items():
                if existing == s:
                    return i
            for i in range(strings.len):
                try:
                    if strings.get_nopending(i) == s:
                        return i
                except:
                    pass
            i = strings.len
            strings.len = strings.len + 1
            pending.h_string[0][0] = strings.len
            pending.h_string[1][i] = s
            return i

        def patch_name_fn(s: str, ip: int) -> None:
            i = name_index(s)
            if i in patches.h_name:
                ipl = patches.h_name[i]
                if ip not in ipl:
                    patches.h_name[i] = ipl + [ip]
            else:
                patches.h_name[i] = [ip]

        def commit_patches_fn() -> None:
            if perm == Perm.RDONLY:
                raise RuntimeError("Cannot commit patches: database is read-only")

            patches.h_person[0][:] = pending.h_person[0][:]
            for k, v in pending.h_person[1].items():
                patches.h_person[1][k] = v
            pending.h_person[1].clear()

            patches.h_ascend[0][:] = pending.h_ascend[0][:]
            for k, v in pending.h_ascend[1].items():
                patches.h_ascend[1][k] = v
            pending.h_ascend[1].clear()

            patches.h_union[0][:] = pending.h_union[0][:]
            for k, v in pending.h_union[1].items():
                patches.h_union[1][k] = v
            pending.h_union[1].clear()

            patches.h_family[0][:] = pending.h_family[0][:]
            for k, v in pending.h_family[1].items():
                patches.h_family[1][k] = v
            pending.h_family[1].clear()

            patches.h_couple[0][:] = pending.h_couple[0][:]
            for k, v in pending.h_couple[1].items():
                patches.h_couple[1][k] = v
            pending.h_couple[1].clear()

            patches.h_descend[0][:] = pending.h_descend[0][:]
            for k, v in pending.h_descend[1].items():
                patches.h_descend[1][k] = v
            pending.h_descend[1].clear()

            patches.h_string[0][:] = pending.h_string[0][:]
            for k, v in pending.h_string[1].items():
                patches.h_string[1][k] = v
            pending.h_string[1].clear()

            tmp_fname = os.path.join(bname, "1patches")
            fname = os.path.join(bname, "patches")
            with secure.open_out_bin(tmp_fname) as oc:
                oc.write(MAGIC_PATCH)
                iovalue.output(oc, patches)
            move_with_backup(tmp_fname, fname)

        def commit_notes_fn(fnotes: str, s: str) -> None:
            if perm == Perm.RDONLY:
                raise RuntimeError("Cannot commit notes: database is read-only")
            raise NotImplementedError("commit_notes not yet implemented")

        def commit_wiznotes_fn(fnotes: str, s: str) -> None:
            if perm == Perm.RDONLY:
                raise RuntimeError("Cannot commit wiznotes: database is read-only")
            raise NotImplementedError("commit_wiznotes not yet implemented")

        def nb_of_real_persons_fn() -> int:
            nbp_fname = os.path.join(bname, "nb_persons")
            if os.path.exists(nbp_fname):
                with secure.open_in_bin(nbp_fname) as ic:
                    return iovalue.input_value(ic)
            count = 0
            for i in range(persons.len):
                try:
                    p = persons.get(i)
                    if not ((p.surname == 0 or p.surname == 1) and (p.first_name == 0 or p.first_name == 1)):
                        count += 1
                except:
                    pass
            return count

        def iper_exists_fn(i: int) -> bool:
            return iper_exists(patches.h_person[1], pending.h_person[1], persons_len, i)

        def ifam_exists_fn(i: int) -> bool:
            return ifam_exists(patches.h_family[1], pending.h_family[1], families_len, i)

        def person_of_key_fn(first_name: str, surname: str, occ: int) -> Optional[int]:
            return person_of_key(persons, strings, persons_of_name_fn, first_name, surname, occ)

        def strings_of_sname_fn(s: str) -> List[int]:
            return strings_of_fsname(version, bname, strings, patches.h_person, 1, 0, name.split_sname, lambda p: p.surname)(s)

        def strings_of_fname_fn(s: str) -> List[int]:
            return strings_of_fsname(version, bname, strings, patches.h_person, 2, 1, name.split_fname, lambda p: p.first_name)(s)

        base_func = BaseFunc(
            person_of_key=person_of_key_fn,
            persons_of_name=persons_of_name_fn,
            strings_of_sname=strings_of_sname_fn,
            strings_of_fname=strings_of_fname_fn,
            persons_of_surname=persons_of_surname_fn,
            persons_of_first_name=persons_of_first_name_fn,
            patch_person=patch_person_fn,
            patch_ascend=patch_ascend_fn,
            patch_union=patch_union_fn,
            patch_family=patch_family_fn,
            patch_couple=patch_couple_fn,
            patch_descend=patch_descend_fn,
            patch_name=patch_name_fn,
            insert_string=insert_string_fn,
            commit_patches=commit_patches_fn,
            commit_notes=commit_notes_fn,
            commit_wiznotes=commit_wiznotes_fn,
            nb_of_real_persons=nb_of_real_persons_fn,
            iper_exists=iper_exists_fn,
            ifam_exists=ifam_exists_fn
        )

        base = DskBase(
            data=base_data,
            func=base_func,
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

TABLE_SIZE = 0x3FFF
INT_SIZE = 4

def name_index(s: str) -> int:
    return hash(name.crush_lower(s)) % TABLE_SIZE

def binary_search(arr: List[Tuple[Any, Any]], cmp: Callable[[Tuple[Any, Any]], int]) -> int:
    if not arr:
        raise KeyError("Not found")
    low = 0
    high = len(arr) - 1
    while True:
        if high <= low:
            if cmp(arr[low]) == 0:
                return low
            raise KeyError("Not found")
        mid = (low + high) // 2
        c = cmp(arr[mid])
        if c < 0:
            high = mid - 1
        elif c > 0:
            low = mid + 1
        else:
            return mid

def binary_search_key_after(arr: List[Tuple[Any, Any]], cmp: Callable[[Tuple[Any, Any]], int]) -> int:
    if not arr:
        raise KeyError("Not found")
    acc = None
    low = 0
    high = len(arr) - 1
    while True:
        if high <= low:
            if cmp(arr[low]) <= 0:
                return low
            if acc is not None:
                return acc
            raise KeyError("Not found")
        mid = (low + high) // 2
        c = cmp(arr[mid])
        if c < 0:
            acc = mid
            high = mid - 1
        elif c > 0:
            low = mid + 1
        else:
            return mid

def binary_search_next(arr: List[Tuple[Any, Any]], cmp: Callable[[Tuple[Any, Any]], int]) -> int:
    if not arr:
        raise KeyError("Not found")
    acc = None
    low = 0
    high = len(arr) - 1
    while True:
        if high <= low:
            if cmp(arr[low]) < 0:
                return low
            if acc is not None:
                return acc
            raise KeyError("Not found")
        mid = (low + high) // 2
        c = cmp(arr[mid])
        if c < 0:
            acc = mid
            high = mid - 1
        else:
            low = mid + 1

def compare_after_particle(particles: List[str], s1: str, s2: str) -> int:
    def skip_particles(s: str) -> str:
        words = s.split()
        if not words:
            return s
        for particle in particles:
            if words[0].lower() == particle.lower() and len(words) > 1:
                return ' '.join(words[1:])
        return s

    s1_stripped = skip_particles(s1)
    s2_stripped = skip_particles(s2)

    if s1_stripped < s2_stripped:
        return -1
    elif s1_stripped > s2_stripped:
        return 1
    return 0

def compare_snames(base_data: BaseData, s1: str, s2: str) -> int:
    particles = base_data.particles_txt if base_data.particles_txt else []
    return compare_after_particle(particles, s1, s2)

def compare_snames_i(base_data: BaseData, is1: int, is2: int) -> int:
    if is1 == is2:
        return 0
    return compare_snames(base_data, base_data.strings.get(is1), base_data.strings.get(is2))

def compare_fnames(base_data: BaseData, s1: str, s2: str) -> int:
    if s1 < s2:
        return -1
    elif s1 > s2:
        return 1
    return 0

def compare_fnames_i(base_data: BaseData, is1: int, is2: int) -> int:
    if is1 == is2:
        return 0
    s1 = base_data.strings.get(is1)
    s2 = base_data.strings.get(is2)
    return compare_fnames(base_data, s1, s2)

def persons_of_name(bname: str, patches_h_name: Dict[int, List[int]]) -> Callable[[str], List[int]]:
    cached_table = [None]

    def lookup(s: str) -> List[int]:
        i = name_index(s)
        names_inx_file = os.path.join(bname, "names.inx")
        names_acc_file = os.path.join(bname, "names.acc")

        with secure.open_in_bin(names_inx_file) as ic_inx:
            if os.path.exists(names_acc_file):
                with secure.open_in_bin(names_acc_file) as ic_inx_acc:
                    ic_inx_acc.seek(iovalue.SIZEOF_LONG * i)
                    pos = input_binary_int(ic_inx_acc)
                ic_inx.seek(pos)
                ai = iovalue.input_value(ic_inx)
            else:
                if cached_table[0] is None:
                    ic_inx.seek(INT_SIZE)
                    cached_table[0] = iovalue.input_value(ic_inx)
                ai = cached_table[0][i]

        result = list(ai) if isinstance(ai, (list, tuple)) else []

        if i in patches_h_name:
            patch_list = patches_h_name[i]
            for ip in patch_list:
                if ip not in result:
                    result.append(ip)

        return result

    return lookup

def new_persons_of_first_name_or_surname(cmp_str: Callable[[BaseData, str, str], int],
                                          cmp_istr: Callable[[BaseData, int, int], int],
                                          base_data: BaseData, proj: Callable[[DskPerson], int],
                                          person_patches: Dict[int, DskPerson], names_inx: str,
                                          names_dat: str, bname: str) -> StringPersonIndex:
    fname_dat = os.path.join(bname, names_dat)
    bt_cache = [None]
    patched_cache = [None]

    def load_bt() -> List[Tuple[int, int]]:
        if bt_cache[0] is None:
            fname_inx = os.path.join(bname, names_inx)
            with secure.open_in_bin(fname_inx) as ic_inx:
                bt_cache[0] = iovalue.input_value(ic_inx)
        return bt_cache[0]

    def load_patched() -> List[Tuple[int, List[int]]]:
        if patched_cache[0] is None:
            ht = {}
            for iper, p in person_patches.items():
                k = proj(p)
                if k not in ht:
                    ht[k] = []
            a = [(k, v) for k, v in ht.items()]
            a.sort(key=lambda x: (cmp_istr(base_data, x[0], x[0]), x[0]))
            patched_cache[0] = a
        return patched_cache[0]

    def find(istr: int) -> List[int]:
        ipera = []
        try:
            bt = load_bt()
            s = base_data.strings.get(istr)

            def cmp_entry(entry):
                k, _ = entry
                if k == istr:
                    return 0
                return cmp_str(base_data, s, base_data.strings.get(k))

            pos = bt[binary_search(bt, cmp_entry)][1]
            with secure.open_in_bin(fname_dat) as ic_dat:
                ic_dat.seek(pos)
                length = input_binary_int(ic_dat)
                for _ in range(length):
                    iper = input_binary_int(ic_dat)
                    ipera.append(iper)
        except (KeyError, FileNotFoundError):
            pass

        patched_ipers = [i for i in person_patches.keys()]
        ipera = [i for i in ipera if i not in patched_ipers]

        for i, p in person_patches.items():
            istr1 = proj(p)
            if istr1 == istr and i not in ipera:
                ipera.append(i)

        return ipera

    def cursor(s: str) -> int:
        bt = load_bt()
        patched = load_patched()

        def cmp_bt(entry):
            k, _ = entry
            return cmp_str(base_data, s, base_data.strings.get(k))

        istr1 = -1
        try:
            istr1 = bt[binary_search_key_after(bt, cmp_bt)][0]
        except (KeyError, IndexError):
            pass

        istr2 = -1
        try:
            istr2 = patched[binary_search_key_after(patched, cmp_bt)][0]
        except (KeyError, IndexError):
            pass

        if istr2 == -1:
            if istr1 == -1:
                raise KeyError("Not found")
            return istr1
        elif istr1 == -1:
            return istr2
        elif istr1 == istr2:
            return istr1
        else:
            c = cmp_str(base_data, base_data.strings.get(istr1), base_data.strings.get(istr2))
            return istr1 if c < 0 else istr2

    def next_istr(istr: int) -> int:
        bt = load_bt()
        patched = load_patched()
        s = base_data.strings.get(istr)

        def cmp_bt(entry):
            k, _ = entry
            if k == istr:
                return 0
            return cmp_str(base_data, s, base_data.strings.get(k))

        istr1 = -1
        try:
            istr1 = bt[binary_search_next(bt, cmp_bt)][0]
        except (KeyError, IndexError):
            pass

        istr2 = -1
        try:
            istr2 = patched[binary_search_next(patched, cmp_bt)][0]
        except (KeyError, IndexError):
            pass

        if istr2 == -1:
            if istr1 == -1:
                raise KeyError("Not found")
            return istr1
        elif istr1 == -1:
            return istr2
        elif istr1 == istr2:
            return istr1
        else:
            c = cmp_str(base_data, base_data.strings.get(istr1), base_data.strings.get(istr2))
            return istr1 if c < 0 else istr2

    return StringPersonIndex(find=find, cursor=cursor, next=next_istr)

def persons_of_surname(version: BaseVersion, base_data: BaseData, person_patches: Dict[int, DskPerson],
                       bname: str) -> StringPersonIndex:
    if version == BaseVersion.GNWB0024 or version == BaseVersion.GNWB0023 or version == BaseVersion.GNWB0022 or version == BaseVersion.GNWB0021:
        return new_persons_of_first_name_or_surname(
            compare_snames, compare_snames_i, base_data,
            lambda p: p.surname, person_patches, "snames.inx", "snames.dat", bname
        )
    else:
        raise NotImplementedError("GnWb0020 surname index not implemented")

def persons_of_first_name(version: BaseVersion, base_data: BaseData, person_patches: Dict[int, DskPerson],
                           bname: str) -> StringPersonIndex:
    if version == BaseVersion.GNWB0024:
        return new_persons_of_first_name_or_surname(
            lambda bd, s1, s2: compare_fnames(bd, s1, s2), compare_fnames_i, base_data,
            lambda p: p.first_name, person_patches, "fnames.inx", "fnames.dat", bname
        )
    elif version == BaseVersion.GNWB0023 or version == BaseVersion.GNWB0022 or version == BaseVersion.GNWB0021:
        return new_persons_of_first_name_or_surname(
            compare_snames, compare_snames_i, base_data,
            lambda p: p.first_name, person_patches, "fnames.inx", "fnames.dat", bname
        )
    else:
        raise NotImplementedError("GnWb0020 firstname index not implemented")

def person_of_key(persons: RecordAccess, strings: RecordAccess,
                  persons_of_name_fn: Callable[[str], List[int]],
                  first_name: str, surname: str, occ: int) -> Optional[int]:
    first_name_lower = name.lower(first_name)
    surname_lower = name.lower(surname)
    ipl = persons_of_name_fn(first_name + " " + surname)

    for ip in ipl:
        p = persons.get(ip)
        p_first = name.lower(strings.get(p.first_name))
        p_surname = name.lower(strings.get(p.surname))
        if occ == p.occ and first_name_lower == p_first and surname_lower == p_surname:
            return ip
    return None

def iper_exists(patches: Dict[int, DskPerson], pending: Dict[int, DskPerson],
                len_val: int, i: int) -> bool:
    return i in pending or i in patches or (0 <= i < len_val)

def ifam_exists(patches: Dict[int, DskFamily], pending: Dict[int, DskFamily],
                len_val: int, i: int) -> bool:
    return i in pending or i in patches or (0 <= i < len_val)

def strings_of_fsname(version: BaseVersion, bname: str, strings: RecordAccess,
                      patches_h_person: Tuple[List[int], Dict[int, DskPerson]],
                      offset_acc: int, offset_inx: int,
                      split_fn: Callable[[str], List[str]],
                      get_fn: Callable[[DskPerson], int]) -> Callable[[str], List[int]]:
    if version == BaseVersion.GNWB0024 or version == BaseVersion.GNWB0023:
        cached_table = [None]

        def lookup(s: str) -> List[int]:
            i = name_index(s)
            names_inx_file = os.path.join(bname, "names.inx")
            names_acc_file = os.path.join(bname, "names.acc")

            with secure.open_in_bin(names_inx_file) as ic_inx:
                if os.path.exists(names_acc_file):
                    with secure.open_in_bin(names_acc_file) as ic_inx_acc:
                        ic_inx_acc.seek(iovalue.SIZEOF_LONG * ((offset_acc * TABLE_SIZE) + i))
                        pos = input_binary_int(ic_inx_acc)
                    ic_inx.seek(pos)
                    ai = iovalue.input_value(ic_inx)
                else:
                    if cached_table[0] is None:
                        ic_inx.seek(offset_inx)
                        pos = input_binary_int(ic_inx)
                        ic_inx.seek(pos)
                        cached_table[0] = iovalue.input_value(ic_inx)
                    ai = cached_table[0][i]

            result = list(ai) if isinstance(ai, (list, tuple)) else []

            _, person_patches = patches_h_person
            for ip, p in person_patches.items():
                istr = get_fn(p)
                str_val = strings.get(istr)
                if istr not in result:
                    parts = split_fn(str_val)
                    if len(parts) == 1:
                        if i == name_index(parts[0]):
                            result.append(istr)
                    else:
                        for part in parts:
                            if i == name_index(part):
                                result.append(istr)
                                break
                        if str_val not in [strings.get(r) for r in result]:
                            if i == name_index(str_val):
                                result.append(istr)

            return result

        return lookup
    else:
        cached_table = [None]

        def lookup_old(s: str) -> List[int]:
            i = name_index(s)
            names_inx_file = os.path.join(bname, "names.inx")
            names_acc_file = os.path.join(bname, "names.acc")

            with secure.open_in_bin(names_inx_file) as ic_inx:
                if os.path.exists(names_acc_file):
                    with secure.open_in_bin(names_acc_file) as ic_inx_acc:
                        ic_inx_acc.seek(iovalue.SIZEOF_LONG * (TABLE_SIZE + i))
                        pos = input_binary_int(ic_inx_acc)
                    ic_inx.seek(pos)
                    ai = iovalue.input_value(ic_inx)
                else:
                    if cached_table[0] is None:
                        pos = input_binary_int(ic_inx)
                        ic_inx.seek(pos)
                        cached_table[0] = iovalue.input_value(ic_inx)
                    ai = cached_table[0][i]

            result = list(ai) if isinstance(ai, (list, tuple)) else []

            _, person_patches = patches_h_person
            for ip, p in person_patches.items():
                istr = get_fn(p)
                str_val = strings.get(istr)
                if istr not in result:
                    parts = split_fn(str_val)
                    if len(parts) == 1:
                        if i == name_index(parts[0]):
                            result.append(istr)
                    else:
                        for part in parts:
                            if i == name_index(part):
                                result.append(istr)
                                break

            return result

        return lookup_old

def make(bname: str, particles: List[str], arrays: Tuple[Any, Any, Any, BaseNotes],
         k: Callable[[DskBase], T]) -> T:
    raise NotImplementedError("make() not yet implemented")
