import pytest
from lib.buff import Buff, store, mstore, gstore, get


class TestBuffInstance:
    def test_buff_creation(self):
        b = Buff()
        assert b._capacity == 80

    def test_store_single_char(self):
        b = Buff()
        pos = b.store(0, 'a')
        assert pos == 1
        assert b.get(1) == 'a'

    def test_store_multiple_chars(self):
        b = Buff()
        pos = b.store(0, 'h')
        pos = b.store(pos, 'i')
        assert pos == 2
        assert b.get(2) == 'hi'

    def test_store_invalid_char(self):
        b = Buff()
        with pytest.raises(ValueError):
            b.store(0, 'ab')

    def test_mstore_string(self):
        b = Buff()
        pos = b.mstore(0, "hello")
        assert pos == 5
        assert b.get(5) == "hello"

    def test_mstore_empty_string(self):
        b = Buff()
        pos = b.mstore(0, "")
        assert pos == 0
        assert b.get(0) == ""

    def test_mstore_concatenate(self):
        b = Buff()
        pos = b.mstore(0, "hello")
        pos = b.mstore(pos, " world")
        assert pos == 11
        assert b.get(11) == "hello world"

    def test_gstore_substring(self):
        b = Buff()
        pos = b.gstore(0, "hello world", 0, 5)
        assert pos == 5
        assert b.get(5) == "hello"

    def test_gstore_with_offset(self):
        b = Buff()
        pos = b.gstore(0, "hello world", 6, 5)
        assert pos == 5
        assert b.get(5) == "world"

    def test_gstore_exceeds_string_length(self):
        b = Buff()
        pos = b.gstore(0, "hello", 0, 100)
        assert pos == 5
        assert b.get(5) == "hello"

    def test_buffer_auto_extend(self):
        b = Buff()
        long_string = "a" * 100
        pos = b.mstore(0, long_string)
        assert pos == 100
        assert b.get(100) == long_string
        assert b._capacity >= 100

    def test_buffer_extend_preserves_content(self):
        b = Buff()
        pos = b.mstore(0, "start")
        long_string = "x" * 100
        pos = b.mstore(pos, long_string)
        result = b.get(pos)
        assert result.startswith("start")
        assert result.endswith("x" * 100)

    def test_get_partial(self):
        b = Buff()
        b.mstore(0, "hello world")
        assert b.get(5) == "hello"

    def test_store_at_different_positions(self):
        b = Buff()
        b.store(0, 'a')
        b.store(5, 'b')
        result = b.get(6)
        assert result[0] == 'a'
        assert result[5] == 'b'


class TestGlobalBuffFunctions:
    def test_global_store(self):
        pos = store(0, 'x')
        assert pos == 1

    def test_global_mstore(self):
        pos = mstore(0, "test")
        assert pos == 4

    def test_global_gstore(self):
        pos = gstore(0, "hello world", 0, 5)
        assert pos == 5

    def test_global_get(self):
        mstore(0, "global")
        result = get(6)
        assert result == "global"

    def test_global_buffer_persistence(self):
        pos = mstore(0, "first")
        pos = mstore(pos, "second")
        result = get(11)
        assert result == "firstsecond"


class TestBuffEdgeCases:
    def test_store_triggers_extend(self):
        b = Buff()
        pos = 0
        for i in range(100):
            pos = b.store(pos, 'a')
        assert b._capacity >= 100
        assert b.get(100) == "a" * 100

    def test_mstore_large_string(self):
        b = Buff()
        large = "x" * 1000
        pos = b.mstore(0, large)
        assert pos == 1000
        assert b.get(1000) == large

    def test_gstore_zero_length(self):
        b = Buff()
        pos = b.gstore(0, "hello", 0, 0)
        assert pos == 0
        assert b.get(0) == ""

    def test_multiple_extends(self):
        b = Buff()
        initial_capacity = b._capacity
        text = "a" * (initial_capacity * 3)
        pos = b.mstore(0, text)
        assert b._capacity >= initial_capacity * 3
        assert b.get(pos) == text

    def test_unicode_support(self):
        b = Buff()
        pos = b.mstore(0, "héllo wörld")
        result = b.get(pos)
        assert "héllo" in result
        assert "wörld" in result
