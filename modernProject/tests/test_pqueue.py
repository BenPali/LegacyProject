import pytest
from lib.pqueue import PQueue, OrderedType, create_min_heap, create_max_heap


class IntComparator(OrderedType[int]):
    def leq(self, a: int, b: int) -> bool:
        return a <= b


class TestPQueueBasics:
    def test_empty_queue(self):
        pq = PQueue(IntComparator())
        assert pq.is_empty()

    def test_add_single_element(self):
        pq = PQueue(IntComparator())
        pq = pq.add(5)
        assert not pq.is_empty()

    def test_take_from_empty_raises(self):
        pq = PQueue(IntComparator())
        with pytest.raises(ValueError):
            pq.take()

    def test_add_and_take_single(self):
        pq = PQueue(IntComparator())
        pq = pq.add(42)
        value, pq = pq.take()
        assert value == 42
        assert pq.is_empty()


class TestPQueueOrdering:
    def test_min_heap_order(self):
        pq = PQueue(IntComparator())
        pq = pq.add(5)
        pq = pq.add(3)
        pq = pq.add(7)
        pq = pq.add(1)

        value, pq = pq.take()
        assert value == 1
        value, pq = pq.take()
        assert value == 3
        value, pq = pq.take()
        assert value == 5
        value, pq = pq.take()
        assert value == 7
        assert pq.is_empty()

    def test_many_elements(self):
        pq = PQueue(IntComparator())
        elements = [15, 3, 9, 1, 12, 7, 20, 4, 18, 6]
        for elem in elements:
            pq = pq.add(elem)

        sorted_elements = sorted(elements)
        for expected in sorted_elements:
            value, pq = pq.take()
            assert value == expected
        assert pq.is_empty()

    def test_duplicate_elements(self):
        pq = PQueue(IntComparator())
        pq = pq.add(5)
        pq = pq.add(5)
        pq = pq.add(3)
        pq = pq.add(5)

        value, pq = pq.take()
        assert value == 3
        value, pq = pq.take()
        assert value == 5
        value, pq = pq.take()
        assert value == 5
        value, pq = pq.take()
        assert value == 5


class TestPQueueUnion:
    def test_union_two_queues(self):
        pq1 = PQueue(IntComparator())
        pq1 = pq1.add(1).add(5).add(9)

        pq2 = PQueue(IntComparator())
        pq2 = pq2.add(2).add(6).add(10)

        pq_merged = pq1.union(pq2)

        expected = [1, 2, 5, 6, 9, 10]
        for exp in expected:
            value, pq_merged = pq_merged.take()
            assert value == exp
        assert pq_merged.is_empty()

    def test_union_with_empty(self):
        pq1 = PQueue(IntComparator())
        pq1 = pq1.add(5).add(3)

        pq2 = PQueue(IntComparator())

        pq_merged = pq1.union(pq2)
        value, pq_merged = pq_merged.take()
        assert value == 3
        value, pq_merged = pq_merged.take()
        assert value == 5
        assert pq_merged.is_empty()

    def test_union_empty_with_nonempty(self):
        pq1 = PQueue(IntComparator())
        pq2 = PQueue(IntComparator())
        pq2 = pq2.add(7).add(2)

        pq_merged = pq1.union(pq2)
        value, pq_merged = pq_merged.take()
        assert value == 2
        value, pq_merged = pq_merged.take()
        assert value == 7

    def test_union_multiple_times(self):
        pq1 = PQueue(IntComparator()).add(10)
        pq2 = PQueue(IntComparator()).add(5)
        pq3 = PQueue(IntComparator()).add(15)

        pq_merged = pq1.union(pq2).union(pq3)

        value, pq_merged = pq_merged.take()
        assert value == 5
        value, pq_merged = pq_merged.take()
        assert value == 10
        value, pq_merged = pq_merged.take()
        assert value == 15


class TestPQueueImmutability:
    def test_add_preserves_original(self):
        pq1 = PQueue(IntComparator())
        pq1 = pq1.add(5)
        pq2 = pq1.add(3)

        assert not pq1.is_empty()
        assert not pq2.is_empty()

        value, _ = pq1.take()
        assert value == 5

        value, _ = pq2.take()
        assert value == 3

    def test_take_preserves_structure(self):
        pq1 = PQueue(IntComparator())
        pq1 = pq1.add(5).add(3).add(7)

        value, pq2 = pq1.take()
        assert value == 3

        value, pq3 = pq1.take()
        assert value == 3

        value, _ = pq2.take()
        assert value == 5


class TestHelperFunctions:
    def test_create_min_heap(self):
        pq = create_min_heap()
        pq = pq.add(10).add(5).add(15)

        value, pq = pq.take()
        assert value == 5
        value, pq = pq.take()
        assert value == 10
        value, pq = pq.take()
        assert value == 15

    def test_create_max_heap(self):
        pq = create_max_heap()
        pq = pq.add(10).add(5).add(15)

        value, pq = pq.take()
        assert value == 15
        value, pq = pq.take()
        assert value == 10
        value, pq = pq.take()
        assert value == 5


class TestCustomComparator:
    def test_string_comparator(self):
        class StrComparator(OrderedType[str]):
            def leq(self, a: str, b: str) -> bool:
                return a <= b

        pq = PQueue(StrComparator())
        pq = pq.add("zebra").add("apple").add("mango").add("banana")

        value, pq = pq.take()
        assert value == "apple"
        value, pq = pq.take()
        assert value == "banana"
        value, pq = pq.take()
        assert value == "mango"
        value, pq = pq.take()
        assert value == "zebra"

    def test_reverse_string_comparator(self):
        class ReverseStrComparator(OrderedType[str]):
            def leq(self, a: str, b: str) -> bool:
                return a >= b

        pq = PQueue(ReverseStrComparator())
        pq = pq.add("apple").add("zebra").add("mango")

        value, pq = pq.take()
        assert value == "zebra"
        value, pq = pq.take()
        assert value == "mango"
        value, pq = pq.take()
        assert value == "apple"


class TestLargeDatasets:
    def test_large_ascending_sequence(self):
        pq = PQueue(IntComparator())
        for i in range(100):
            pq = pq.add(i)

        for i in range(100):
            value, pq = pq.take()
            assert value == i

    def test_large_descending_sequence(self):
        pq = PQueue(IntComparator())
        for i in range(99, -1, -1):
            pq = pq.add(i)

        for i in range(100):
            value, pq = pq.take()
            assert value == i

    def test_large_random_like_sequence(self):
        pq = PQueue(IntComparator())
        elements = [i * 7 % 100 for i in range(100)]
        for elem in elements:
            pq = pq.add(elem)

        prev = -1
        for _ in range(100):
            value, pq = pq.take()
            assert value >= prev
            prev = value
