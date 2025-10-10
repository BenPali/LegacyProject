from typing import Any, List
from lib import iovalue
from lib import name
from lib import mutil


def array_forall(f, arr):
    return all(f(x) for x in arr)


def array_exists(f, arr):
    return any(f(x) for x in arr)


def array_associ(f, arr):
    for i, x in enumerate(arr):
        if f(x):
            return i
    raise ValueError("Not found")


def array_find_all(f, arr):
    return [x for x in arr if f(x)]


def sort_uniq(cmp, lst):
    if not lst:
        return []
    sorted_list = sorted(lst, key=lambda x: (x, id(x)))
    result = [sorted_list[0]]
    for item in sorted_list[1:]:
        if item != result[-1]:
            result.append(item)
    return result


def output_value_no_sharing(oc, v: Any) -> None:
    iovalue.output(oc, v)


def name_index(s: str) -> int:
    from lib.database import TABLE_SIZE
    return hash(name.crush_lower(s)) % TABLE_SIZE


def compare_snames(base_data, s1: str, s2: str) -> int:
    particles = base_data.particles if base_data.particles else []
    return mutil.compare_after_particle(particles, s1, s2)


def compare_snames_i(base_data, is1: int, is2: int) -> int:
    if is1 == is2:
        return 0
    return compare_snames(base_data, base_data.strings.get(is1), base_data.strings.get(is2))


def compare_fnames(s1: str, s2: str) -> int:
    if s1 < s2:
        return -1
    elif s1 > s2:
        return 1
    return 0


def compare_fnames_i(base_data, is1: int, is2: int) -> int:
    if is1 == is2:
        return 0
    return compare_fnames(base_data.strings.get(is1), base_data.strings.get(is2))
