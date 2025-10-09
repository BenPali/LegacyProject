from abc import ABC, abstractmethod
from typing import TypeVar, Generic, List, Tuple, Optional
from dataclasses import dataclass


T = TypeVar('T')


class OrderedType(ABC, Generic[T]):
    @abstractmethod
    def leq(self, a: T, b: T) -> bool:
        pass


@dataclass
class _Tree(Generic[T]):
    node: T
    rank: int
    children: List['_Tree[T]']


class PQueue(Generic[T]):
    def __init__(self, comparator: OrderedType[T]):
        self._comparator = comparator
        self._trees: List[_Tree[T]] = []

    @staticmethod
    def create(comparator: OrderedType[T]) -> 'PQueue[T]':
        return PQueue(comparator)

    def is_empty(self) -> bool:
        return len(self._trees) == 0

    def _link(self, t1: _Tree[T], t2: _Tree[T]) -> _Tree[T]:
        if self._comparator.leq(t1.node, t2.node):
            return _Tree(node=t1.node, rank=t1.rank + 1, children=[t2] + t1.children)
        else:
            return _Tree(node=t2.node, rank=t2.rank + 1, children=[t1] + t2.children)

    def _ins(self, t: _Tree[T], ts: List[_Tree[T]]) -> List[_Tree[T]]:
        if not ts:
            return [t]
        t_prime = ts[0]
        rest = ts[1:]
        if t.rank < t_prime.rank:
            return [t] + ts
        else:
            return self._ins(self._link(t, t_prime), rest)

    def _union(self, ts1: List[_Tree[T]], ts2: List[_Tree[T]]) -> List[_Tree[T]]:
        if not ts1:
            return ts2
        if not ts2:
            return ts1
        t1, rest1 = ts1[0], ts1[1:]
        t2, rest2 = ts2[0], ts2[1:]
        if t1.rank < t2.rank:
            return [t1] + self._union(rest1, ts2)
        elif t2.rank < t1.rank:
            return [t2] + self._union(ts1, rest2)
        else:
            return self._ins(self._link(t1, t2), self._union(rest1, rest2))

    def add(self, x: T) -> 'PQueue[T]':
        new_pq = PQueue(self._comparator)
        new_pq._trees = self._ins(_Tree(node=x, rank=0, children=[]), self._trees)
        return new_pq

    def _get_min(self, ts: List[_Tree[T]]) -> Tuple[_Tree[T], List[_Tree[T]]]:
        if not ts:
            raise ValueError("Priority queue is empty")
        if len(ts) == 1:
            return ts[0], []
        t = ts[0]
        rest = ts[1:]
        t_prime, rest_prime = self._get_min(rest)
        if self._comparator.leq(t.node, t_prime.node):
            return t, rest
        else:
            return t_prime, [t] + rest_prime

    def take(self) -> Tuple[T, 'PQueue[T]']:
        t, ts = self._get_min(self._trees)
        new_pq = PQueue(self._comparator)
        new_pq._trees = self._union(list(reversed(t.children)), ts)
        return t.node, new_pq

    def union(self, other: 'PQueue[T]') -> 'PQueue[T]':
        new_pq = PQueue(self._comparator)
        new_pq._trees = self._union(self._trees, other._trees)
        return new_pq


def create_min_heap() -> PQueue[int]:
    class IntComparator(OrderedType[int]):
        def leq(self, a: int, b: int) -> bool:
            return a <= b
    return PQueue(IntComparator())


def create_max_heap() -> PQueue[int]:
    class IntComparator(OrderedType[int]):
        def leq(self, a: int, b: int) -> bool:
            return a >= b
    return PQueue(IntComparator())
