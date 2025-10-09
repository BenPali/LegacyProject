from typing import TypeVar, Generic, Callable, Optional
from dataclasses import dataclass


K = TypeVar('K')
V = TypeVar('V')


@dataclass
class Node(Generic[K, V]):
    left: 'Tree[K, V]'
    key: K
    data: V
    right: 'Tree[K, V]'
    height: int


Tree = Optional[Node[K, V]]


class AVL(Generic[K, V]):
    def __init__(self, compare: Callable[[K, K], int]):
        self.compare = compare
        self.root: Tree[K, V] = None

    @staticmethod
    def _height(node: Tree[K, V]) -> int:
        return 0 if node is None else node.height

    @staticmethod
    def _create(left: Tree[K, V], key: K, data: V, right: Tree[K, V]) -> Node[K, V]:
        hl = AVL._height(left)
        hr = AVL._height(right)
        return Node(left, key, data, right, (hl if hl >= hr else hr) + 1)

    def _bal(self, left: Tree[K, V], key: K, data: V, right: Tree[K, V]) -> Node[K, V]:
        hl = self._height(left)
        hr = self._height(right)

        if hl > hr + 2:
            if left is None:
                raise ValueError("AVL.bal: invalid left")
            ll, lv, ld, lr = left.left, left.key, left.data, left.right
            if self._height(ll) >= self._height(lr):
                return self._create(ll, lv, ld, self._create(lr, key, data, right))
            else:
                if lr is None:
                    raise ValueError("AVL.bal: invalid left-right")
                lrl, lrv, lrd, lrr = lr.left, lr.key, lr.data, lr.right
                return self._create(self._create(ll, lv, ld, lrl), lrv, lrd, self._create(lrr, key, data, right))
        elif hr > hl + 2:
            if right is None:
                raise ValueError("AVL.bal: invalid right")
            rl, rv, rd, rr = right.left, right.key, right.data, right.right
            if self._height(rr) >= self._height(rl):
                return self._create(self._create(left, key, data, rl), rv, rd, rr)
            else:
                if rl is None:
                    raise ValueError("AVL.bal: invalid right-left")
                rll, rlv, rld, rlr = rl.left, rl.key, rl.data, rl.right
                return self._create(self._create(left, key, data, rll), rlv, rld, self._create(rlr, rv, rd, rr))
        else:
            return Node(left, key, data, right, (hl if hl >= hr else hr) + 1)

    def add(self, key: K, data: V) -> None:
        self.root = self._add(self.root, key, data)

    def _add(self, node: Tree[K, V], key: K, data: V) -> Node[K, V]:
        if node is None:
            return Node(None, key, data, None, 1)

        c = self.compare(key, node.key)
        if c == 0:
            if node.data is data:
                return node
            return Node(node.left, key, data, node.right, node.height)
        elif c < 0:
            new_left = self._add(node.left, key, data)
            if node.left is new_left:
                return node
            return self._bal(new_left, node.key, node.data, node.right)
        else:
            new_right = self._add(node.right, key, data)
            if node.right is new_right:
                return node
            return self._bal(node.left, node.key, node.data, new_right)

    def find(self, key: K) -> V:
        result = self._find(self.root, key)
        if result is None:
            raise KeyError(f"Key not found: {key}")
        return result

    def _find(self, node: Tree[K, V], key: K) -> Optional[V]:
        if node is None:
            return None
        c = self.compare(key, node.key)
        if c == 0:
            return node.data
        return self._find(node.left if c < 0 else node.right, key)

    def mem(self, key: K) -> bool:
        return self._mem(self.root, key)

    def _mem(self, node: Tree[K, V], key: K) -> bool:
        if node is None:
            return False
        c = self.compare(key, node.key)
        if c == 0:
            return True
        return self._mem(node.left if c < 0 else node.right, key)

    def key_after(self, f_compare: Callable[[K], int]) -> K:
        result = self._key_after(self.root, f_compare)
        if result is None:
            raise KeyError("No key found matching criteria")
        return result

    def _key_after(self, node: Tree[K, V], f_compare: Callable[[K], int]) -> Optional[K]:
        if node is None:
            return None
        c = f_compare(node.key)
        if c < 0:
            result = self._key_after(node.left, f_compare)
            return result if result is not None else node.key
        elif c > 0:
            return self._key_after(node.right, f_compare)
        else:
            return node.key

    def next(self, key: K) -> K:
        result = self._next(self.root, key)
        if result is None:
            raise KeyError(f"No next key after: {key}")
        return result

    def _next(self, node: Tree[K, V], key: K) -> Optional[K]:
        if node is None:
            return None
        c = self.compare(key, node.key)
        if c < 0:
            result = self._next(node.left, key)
            return result if result is not None else node.key
        else:
            return self._next(node.right, key)
