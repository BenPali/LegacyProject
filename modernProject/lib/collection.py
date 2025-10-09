from typing import TypeVar, Generic, Callable, Optional
from dataclasses import dataclass


T = TypeVar('T')
K = TypeVar('K')
V = TypeVar('V')


@dataclass
class Collection(Generic[T]):
    length: int
    get: Callable[[int], Optional[T]]


def make(length: int, get: Callable[[int], Optional[T]]) -> Collection[T]:
    return Collection(length=length, get=get)


def empty() -> Collection[T]:
    return Collection(length=-1, get=lambda _: None)


def map_collection(fn: Callable[[T], V], c: Collection[T]) -> Collection[V]:
    def mapped_get(i: int) -> Optional[V]:
        result = c.get(i)
        return fn(result) if result is not None else None
    return Collection(length=c.length, get=mapped_get)


def length(c: Collection[T]) -> int:
    return c.length


def iter_collection(fn: Callable[[T], None], c: Collection[T]) -> None:
    for i in range(c.length):
        item = c.get(i)
        if item is not None:
            fn(item)


def iteri(fn: Callable[[int, T], None], c: Collection[T]) -> None:
    for i in range(c.length):
        item = c.get(i)
        if item is not None:
            fn(i, item)


def fold(fn: Callable[[V, T], V], acc: V, c: Collection[T], from_idx: Optional[int] = None, until_idx: Optional[int] = None) -> V:
    start = from_idx if from_idx is not None else 0
    end = (until_idx + 1) if until_idx is not None else c.length

    result = acc
    for i in range(start, end):
        item = c.get(i)
        if item is not None:
            result = fn(result, item)
    return result


def fold_until(continue_fn: Callable[[V], bool], fn: Callable[[V, T], V], acc: V, c: Collection[T]) -> V:
    result = acc
    i = 0
    while continue_fn(result) and i < c.length:
        item = c.get(i)
        if item is not None:
            result = fn(result, item)
        i += 1
    return result


def iterator(c: Collection[T]) -> Callable[[], Optional[T]]:
    cursor = 0

    def next_fn() -> Optional[T]:
        nonlocal cursor
        while cursor < c.length:
            item = c.get(cursor)
            cursor += 1
            if item is not None:
                return item
        return None

    return next_fn


@dataclass
class Marker(Generic[K, V]):
    get: Callable[[K], V]
    set: Callable[[K, V], None]


def make_marker(key_fn: Callable[[K], int], c: Collection, initial: V) -> Marker[K, V]:
    array = [initial] * c.length

    def get_fn(key: K) -> V:
        return array[key_fn(key)]

    def set_fn(key: K, value: V) -> None:
        array[key_fn(key)] = value

    return Marker(get=get_fn, set=set_fn)


def dummy_marker(initial: V) -> Marker[K, V]:
    return Marker(get=lambda _: initial, set=lambda _, __: None)


def marker_get(marker: Marker[K, V], key: K) -> V:
    return marker.get(key)


def marker_set(marker: Marker[K, V], key: K, value: V) -> None:
    marker.set(key, value)
