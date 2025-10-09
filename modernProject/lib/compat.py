from typing import TypeVar, Callable, List


T = TypeVar('T')


def list_equal(eq: Callable[[T, T], bool], l1: List[T], l2: List[T]) -> bool:
    if len(l1) != len(l2):
        return False
    for a1, a2 in zip(l1, l2):
        if not eq(a1, a2):
            return False
    return True
