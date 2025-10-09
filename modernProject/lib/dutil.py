from typing import Any


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
