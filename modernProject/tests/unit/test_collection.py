import pytest
from lib import collection


class TestCollectionBasics:
    def test_make_collection(self):
        c = collection.make(5, lambda i: i * 2)
        assert collection.length(c) == 5
        assert c.get(0) == 0
        assert c.get(2) == 4

    def test_empty_collection(self):
        c = collection.empty()
        assert collection.length(c) == -1
        assert c.get(0) is None

    def test_get_with_none(self):
        c = collection.make(3, lambda i: i if i % 2 == 0 else None)
        assert c.get(0) == 0
        assert c.get(1) is None
        assert c.get(2) == 2


class TestCollectionMap:
    def test_map_collection(self):
        c = collection.make(3, lambda i: i)
        mapped = collection.map_collection(lambda x: x * 10, c)
        assert mapped.get(0) == 0
        assert mapped.get(1) == 10
        assert mapped.get(2) == 20

    def test_map_preserves_none(self):
        c = collection.make(3, lambda i: i if i != 1 else None)
        mapped = collection.map_collection(lambda x: x * 2, c)
        assert mapped.get(0) == 0
        assert mapped.get(1) is None
        assert mapped.get(2) == 4


class TestCollectionIter:
    def test_iter_collection(self):
        results = []
        c = collection.make(4, lambda i: i * 3)
        collection.iter_collection(lambda x: results.append(x), c)
        assert results == [0, 3, 6, 9]

    def test_iter_skips_none(self):
        results = []
        c = collection.make(4, lambda i: i if i % 2 == 0 else None)
        collection.iter_collection(lambda x: results.append(x), c)
        assert results == [0, 2]

    def test_iteri(self):
        results = []
        c = collection.make(3, lambda i: i * 2)
        collection.iteri(lambda idx, val: results.append((idx, val)), c)
        assert results == [(0, 0), (1, 2), (2, 4)]


class TestCollectionFold:
    def test_fold_sum(self):
        c = collection.make(5, lambda i: i)
        result = collection.fold(lambda acc, x: acc + x, 0, c)
        assert result == 10

    def test_fold_with_range(self):
        c = collection.make(10, lambda i: i)
        result = collection.fold(lambda acc, x: acc + x, 0, c, from_idx=2, until_idx=5)
        assert result == 2 + 3 + 4 + 5

    def test_fold_skips_none(self):
        c = collection.make(5, lambda i: i if i != 2 else None)
        result = collection.fold(lambda acc, x: acc + x, 0, c)
        assert result == 8

    def test_fold_until(self):
        c = collection.make(10, lambda i: i)
        result = collection.fold_until(
            lambda acc: acc < 10,
            lambda acc, x: acc + x,
            0,
            c
        )
        assert result == 10


class TestCollectionIterator:
    def test_iterator(self):
        c = collection.make(3, lambda i: i * 5)
        next_fn = collection.iterator(c)
        assert next_fn() == 0
        assert next_fn() == 5
        assert next_fn() == 10
        assert next_fn() is None

    def test_iterator_skips_none(self):
        c = collection.make(5, lambda i: i if i % 2 == 0 else None)
        next_fn = collection.iterator(c)
        assert next_fn() == 0
        assert next_fn() == 2
        assert next_fn() == 4
        assert next_fn() is None


class TestMarker:
    def test_make_marker(self):
        c = collection.make(5, lambda i: i)
        marker = collection.make_marker(lambda k: k, c, 0)

        collection.marker_set(marker, 2, 42)
        assert collection.marker_get(marker, 2) == 42
        assert collection.marker_get(marker, 3) == 0

    def test_marker_operations(self):
        c = collection.make(3, lambda i: i)
        marker = collection.make_marker(lambda k: k, c, -1)

        for i in range(3):
            collection.marker_set(marker, i, i * 10)

        assert collection.marker_get(marker, 0) == 0
        assert collection.marker_get(marker, 1) == 10
        assert collection.marker_get(marker, 2) == 20

    def test_dummy_marker(self):
        marker = collection.dummy_marker(99)
        assert collection.marker_get(marker, "any") == 99
        assert collection.marker_get(marker, 123) == 99
        collection.marker_set(marker, "key", 100)
        assert collection.marker_get(marker, "key") == 99
