import os
import sys
from typing import List, Tuple, Callable, Any, Set
from lib.dbdisk import DskBase, DskPerson
from lib import iovalue
from lib import dutil
from lib import name
from lib import mutil
from lib import secure
from lib import filesystem

verbose = False

def trace(s: str) -> None:
    if verbose:
        print(f"*** {s}", file=sys.stderr)
        sys.stderr.flush()

def count_error(computed: int, found: int) -> None:
    print(f"Count error. Computed {computed}. Found {found}.", file=sys.stderr)
    sys.stderr.flush()
    sys.exit(2)

def output_binary_int(oc, n: int) -> None:
    oc.write(n.to_bytes(4, byteorder='big', signed=False))

def input_binary_int(ic) -> int:
    b = ic.read(4)
    if len(b) < 4:
        raise EOFError("Unexpected end of file")
    return int.from_bytes(b, byteorder='big', signed=False)

def output_index_aux(oc_inx, oc_inx_acc, ni):
    bpos = oc_inx.tell()
    dutil.output_value_no_sharing(oc_inx, ni)
    output_array_access(oc_inx_acc, lambda i: ni[i], len(ni), bpos)

def output_array_access(oc, get_fn, length, shift):
    for i in range(length):
        pos = oc.tell()
        output_binary_int(oc, pos + shift)

def make_name_index(base: DskBase):
    from lib.database import TABLE_SIZE
    t = [[] for _ in range(TABLE_SIZE)]
    for i in range(base.data.persons.len):
        p = base.data.persons.get(i)
        if hasattr(p, 'first_name'):
            if p.first_name != 1 and p.surname != 1:
                key_index = p.key_index if hasattr(p, 'key_index') else i
                misc_names = dsk_person_misc_names(base, p)
                indices = []
                for n in misc_names:
                    idx = dutil.name_index(n)
                    if idx not in indices:
                        indices.append(idx)
                indices.sort()
                for idx in indices:
                    if key_index not in t[idx]:
                        t[idx].append(key_index)
    return [list(x) for x in t]

def dsk_person_misc_names(base: DskBase, p: DskPerson) -> List[str]:
    result = []
    if hasattr(p, 'first_name'):
        fn = base.data.strings.get(p.first_name)
        sn = base.data.strings.get(p.surname)
        result.append(f"{fn} {sn}")
    return result

def create_name_index(oc_inx, oc_inx_acc, base: DskBase) -> None:
    output_index_aux(oc_inx, oc_inx_acc, make_name_index(base))

def make_strings_of_fsname_aux(split_fn: Callable, get_fn: Callable, base: DskBase):
    from lib.database import TABLE_SIZE
    t = [set() for _ in range(TABLE_SIZE)]

    def add_name(key: str, value: int):
        idx = dutil.name_index(key)
        t[idx].add(value)

    for i in range(base.data.persons.len):
        p = base.data.persons.get(i)
        istr = get_fn(p)
        if istr != 1:
            s = base.data.strings.get(istr)
            add_name(s, istr)
            split_fn(lambda start, length: add_name(s[start:start+length], istr), s)

    result = []
    for s in t:
        arr = sorted(list(s))
        result.append(arr)
    return result

def make_strings_of_fname(base: DskBase):
    return make_strings_of_fsname_aux(
        name.split_fname_callback,
        lambda p: p.first_name if hasattr(p, 'first_name') else p['first_name'],
        base
    )

def make_strings_of_sname(base: DskBase):
    return make_strings_of_fsname_aux(
        name.split_sname_callback,
        lambda p: p.surname if hasattr(p, 'surname') else p['surname'],
        base
    )

def create_strings_of_sname(oc_inx, oc_inx_acc, base: DskBase) -> None:
    output_index_aux(oc_inx, oc_inx_acc, make_strings_of_sname(base))

def create_strings_of_fname(oc_inx, oc_inx_acc, base: DskBase) -> None:
    output_index_aux(oc_inx, oc_inx_acc, make_strings_of_fname(base))

def is_prime(a: int) -> bool:
    if a < 2:
        return False
    b = 2
    while True:
        if a // b < b:
            return True
        if a % b == 0:
            return False
        b += 1

def prime_after(n: int) -> int:
    while not is_prime(n):
        n += 1
    return n

def output_strings_hash(tmp_strings_inx: str, base: DskBase) -> None:
    with secure.open_out_bin(tmp_strings_inx) as oc:
        base.data.strings.load_array()
        strings_array = base.data.strings
        taba_size = min(sys.maxsize, prime_after(max(2, 10 * strings_array.len)))
        taba = [-1] * taba_size
        tabl = [-1] * strings_array.len
        for i in range(strings_array.len):
            ia = hash(base.data.strings.get(i)) % len(taba)
            tabl[i] = taba[ia]
            taba[ia] = i
        output_binary_int(oc, len(taba))
        for i in range(len(taba)):
            output_binary_int(oc, taba[i])
        for i in range(len(tabl)):
            output_binary_int(oc, tabl[i])

def output_name_index_aux(cmp_fn: Callable, get_fn: Callable, base: DskBase,
                          names_inx: str, names_dat: str) -> None:
    ht = {}
    for i in range(base.data.persons.len):
        p = base.data.persons.get(i)
        k = get_fn(p)
        key_index = p.key_index if hasattr(p, 'key_index') else i
        if k in ht:
            ht[k].append(key_index)
        else:
            ht[k] = [key_index]

    a = [(k, v) for k, v in ht.items()]
    a.sort(key=lambda x: (cmp_fn(x[0], x[0]), x[0]))

    with secure.open_out_bin(names_dat) as oc_n_dat:
        bt2 = []
        for k, ipl in a:
            off = oc_n_dat.tell()
            output_binary_int(oc_n_dat, len(ipl))
            for ip in ipl:
                output_binary_int(oc_n_dat, ip)
            bt2.append((k, off))

    with secure.open_out_bin(names_inx) as oc_n_inx:
        dutil.output_value_no_sharing(oc_n_inx, bt2)

def output_surname_index(base: DskBase, tmp_snames_inx: str, tmp_snames_dat: str) -> None:
    output_name_index_aux(
        lambda k1, k2: dutil.compare_snames_i(base.data, k1, k2),
        lambda p: p.surname if hasattr(p, 'surname') else p['surname'],
        base, tmp_snames_inx, tmp_snames_dat
    )

def output_first_name_index(base: DskBase, tmp_fnames_inx: str, tmp_fnames_dat: str) -> None:
    output_name_index_aux(
        lambda k1, k2: dutil.compare_fnames_i(base.data, k1, k2),
        lambda p: p.first_name if hasattr(p, 'first_name') else p['first_name'],
        base, tmp_fnames_inx, tmp_fnames_dat
    )

def output_particles_file(particles: List[str], fname: str) -> None:
    with open(fname, 'w') as oc:
        for s in particles:
            oc.write(mutil.tr(' ', '_', s) + '\n')

def output_notes(base: DskBase, dst: str) -> None:
    from lib.adef import RnAll
    content = base.data.bnotes.nread("", RnAll)
    with open(dst, 'w') as oc:
        oc.write(content)

def output_notes_d(base: DskBase, dst_dir: str) -> None:
    from lib.adef import RnAll
    l = base.data.bnotes.efiles()
    for f in l:
        dst = os.path.join(dst_dir, f + ".txt")
        filesystem.create_dir(os.path.dirname(dst), parent=True)
        content = base.data.bnotes.nread(f, RnAll)
        with open(dst, 'w') as oc:
            oc.write(content)

def safe_rename(src: str, dst: str) -> None:
    try:
        if os.path.exists(dst):
            os.remove(dst)
        os.rename(src, dst)
    except:
        filesystem.copy_file(src, dst)
        os.remove(src)

def output(base: DskBase) -> None:
    bname = base.data.bdir
    if not os.path.exists(bname):
        os.makedirs(bname, 0o755)

    tmp_particles = os.path.join(bname, "1particles.txt")
    tmp_base = os.path.join(bname, "1base")
    tmp_base_acc = os.path.join(bname, "1base.acc")
    tmp_names_inx = os.path.join(bname, "1names.inx")
    tmp_names_acc = os.path.join(bname, "1names.acc")
    tmp_snames_inx = os.path.join(bname, "1snames.inx")
    tmp_snames_dat = os.path.join(bname, "1snames.dat")
    tmp_fnames_inx = os.path.join(bname, "1fnames.inx")
    tmp_fnames_dat = os.path.join(bname, "1fnames.dat")
    tmp_strings_inx = os.path.join(bname, "1strings.inx")
    tmp_notes = os.path.join(bname, "1notes")
    tmp_notes_d = os.path.join(bname, "1notes_d")

    base.data.ascends.load_array()
    base.data.unions.load_array()
    base.data.couples.load_array()
    base.data.descends.load_array()
    base.data.strings.load_array()

    oc = None
    oc_acc = None
    try:
        oc = secure.open_out_bin(tmp_base)
        oc_acc = secure.open_out_bin(tmp_base_acc)

        def output_array(arrname: str, arr):
            bpos = oc.tell()
            if verbose:
                print(f"*** saving {arrname} array", file=sys.stderr)
                sys.stderr.flush()
            arr.output_array(oc)
            output_array_access(oc_acc, arr.get, arr.len, bpos)

        oc.write(b"GnWb0024")
        output_binary_int(oc, base.data.persons.len)
        output_binary_int(oc, base.data.families.len)
        output_binary_int(oc, base.data.strings.len)
        array_start_indexes = oc.tell()
        for _ in range(7):
            output_binary_int(oc, 0)
        dutil.output_value_no_sharing(oc, base.data.bnotes.norigin_file)

        persons_array_pos = oc.tell()
        output_array("persons", base.data.persons)
        ascends_array_pos = oc.tell()
        output_array("ascends", base.data.ascends)
        unions_array_pos = oc.tell()
        output_array("unions", base.data.unions)
        families_array_pos = oc.tell()
        output_array("families", base.data.families)
        couples_array_pos = oc.tell()
        output_array("couples", base.data.couples)
        descends_array_pos = oc.tell()
        output_array("descends", base.data.descends)
        strings_array_pos = oc.tell()
        output_array("strings", base.data.strings)

        oc.seek(array_start_indexes)
        output_binary_int(oc, persons_array_pos)
        output_binary_int(oc, ascends_array_pos)
        output_binary_int(oc, unions_array_pos)
        output_binary_int(oc, families_array_pos)
        output_binary_int(oc, couples_array_pos)
        output_binary_int(oc, descends_array_pos)
        output_binary_int(oc, strings_array_pos)

        base.data.families.clear_array()
        base.data.descends.clear_array()
        oc.close()
        oc_acc.close()

        with secure.open_out_bin(tmp_names_inx) as oc_inx:
            with secure.open_out_bin(tmp_names_acc) as oc_inx_acc:
                trace("create name index")
                output_binary_int(oc_inx, 0)
                output_binary_int(oc_inx, 0)
                create_name_index(oc_inx, oc_inx_acc, base)
                base.data.ascends.clear_array()
                base.data.unions.clear_array()
                base.data.couples.clear_array()

                surname_pos = oc_inx.tell()
                trace("create strings of sname")
                create_strings_of_sname(oc_inx, oc_inx_acc, base)
                first_name_pos = oc_inx.tell()
                trace("create strings of fname")
                create_strings_of_fname(oc_inx, oc_inx_acc, base)
                oc_inx.seek(0)
                output_binary_int(oc_inx, surname_pos)
                oc_inx.seek(4)
                output_binary_int(oc_inx, first_name_pos)

        trace("create string index")
        output_strings_hash(tmp_strings_inx, base)
        trace("create surname index")
        output_surname_index(base, tmp_snames_inx, tmp_snames_dat)
        trace("create first name index")
        output_first_name_index(base, tmp_fnames_inx, tmp_fnames_dat)
        output_notes(base, tmp_notes)
        output_notes_d(base, tmp_notes_d)
        output_particles_file(base.data.particles_txt, tmp_particles)

        trace("ok")

        nbp = 0
        for i in range(base.data.persons.len):
            p = base.data.persons.get(i)
            key_index = p.key_index if hasattr(p, 'key_index') else -1
            surname = p.surname if hasattr(p, 'surname') else 0
            first_name = p.first_name if hasattr(p, 'first_name') else 0
            if key_index != -1 and not ((surname == 0 or surname == 1) and (first_name == 0 or first_name == 1)):
                nbp += 1

        with secure.open_out_bin(os.path.join(bname, "nb_persons")) as oc_nbp:
            iovalue.output(oc_nbp, nbp)

    except Exception as e:
        if oc:
            try:
                oc.close()
            except:
                pass
        if oc_acc:
            try:
                oc_acc.close()
            except:
                pass
        for f in [tmp_base, tmp_base_acc, tmp_names_inx, tmp_names_acc, tmp_strings_inx]:
            if os.path.exists(f):
                os.remove(f)
        if os.path.exists(tmp_notes_d):
            filesystem.remove_dir(tmp_notes_d)
        raise e

    safe_rename(tmp_base, os.path.join(bname, "base"))
    safe_rename(tmp_base_acc, os.path.join(bname, "base.acc"))
    safe_rename(tmp_names_inx, os.path.join(bname, "names.inx"))
    safe_rename(tmp_names_acc, os.path.join(bname, "names.acc"))
    safe_rename(tmp_snames_dat, os.path.join(bname, "snames.dat"))
    safe_rename(tmp_snames_inx, os.path.join(bname, "snames.inx"))
    safe_rename(tmp_fnames_dat, os.path.join(bname, "fnames.dat"))
    safe_rename(tmp_fnames_inx, os.path.join(bname, "fnames.inx"))
    safe_rename(tmp_strings_inx, os.path.join(bname, "strings.inx"))
    safe_rename(tmp_particles, os.path.join(bname, "particles.txt"))

    notes_file = os.path.join(bname, "notes")
    if os.path.exists(notes_file):
        os.remove(notes_file)
    if os.path.exists(tmp_notes):
        os.rename(tmp_notes, notes_file)

    if os.path.exists(tmp_notes_d):
        notes_d = os.path.join(bname, "notes_d")
        if os.path.exists(notes_d):
            filesystem.remove_dir(notes_d)
        try:
            os.rename(tmp_notes_d, notes_d)
        except Exception as e:
            trace(f"Error renaming {tmp_notes_d} to {notes_d}: {str(e)}. Retrying once.")
            import time
            time.sleep(0.5)
            os.rename(tmp_notes_d, notes_d)

    for f in ["patches", "patches~", "synchro_patches", "notes_link", "restrict",
              "tstab_visitor", "nb_persons", "tstab"]:
        fpath = os.path.join(bname, f)
        if os.path.exists(fpath):
            os.remove(fpath)
