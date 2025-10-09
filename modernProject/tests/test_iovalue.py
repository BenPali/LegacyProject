import pytest
import io
from modernProject.lib.iovalue import (
    input_value,
    output,
    size,
    array_header_size,
    output_array_access,
    SIZEOF_LONG,
    OUTPUT_VALUE_HEADER_SIZE,
    sign_extend,
    PREFIX_SMALL_INT,
    PREFIX_SMALL_STRING,
    PREFIX_SMALL_BLOCK,
    CODE_INT8,
    CODE_INT16,
    CODE_INT32,
    CODE_STRING8,
    CODE_STRING32,
)

def test_sizeof_long():
    assert SIZEOF_LONG == 4

def test_sign_extend_positive():
    result = sign_extend(42)
    assert isinstance(result, int)

def test_sign_extend_negative():
    result = sign_extend(0xFF)
    assert isinstance(result, int)

def test_small_int_roundtrip():
    for val in [0, 1, 10, 42, 63]:
        buf = io.BytesIO()
        output(buf, val)
        buf.seek(0)
        result = input_value(buf)
        assert result == val

def test_int8_roundtrip():
    for val in [-128, -1, 64, 127]:
        buf = io.BytesIO()
        output(buf, val)
        buf.seek(0)
        result = input_value(buf)
        assert result == val

def test_int16_roundtrip():
    for val in [-32768, -129, 128, 1000, 32767]:
        buf = io.BytesIO()
        output(buf, val)
        buf.seek(0)
        result = input_value(buf)
        assert result == val

def test_int32_roundtrip():
    for val in [-1073741824, -32769, 32768, 1000000, 1073741823]:
        buf = io.BytesIO()
        output(buf, val)
        buf.seek(0)
        result = input_value(buf)
        assert result == val

def test_small_string_roundtrip():
    data = b"hello"
    buf = io.BytesIO()
    output(buf, data)
    buf.seek(0)
    result = input_value(buf)
    assert result == data

def test_string8_roundtrip():
    data = b"a" * 50
    buf = io.BytesIO()
    output(buf, data)
    buf.seek(0)
    result = input_value(buf)
    assert result == data

def test_string32_roundtrip():
    data = b"x" * 300
    buf = io.BytesIO()
    output(buf, data)
    buf.seek(0)
    result = input_value(buf)
    assert result == data

def test_utf8_string_roundtrip():
    text = "hello world"
    buf = io.BytesIO()
    output(buf, text)
    buf.seek(0)
    result = input_value(buf)
    assert result == text.encode('utf-8')

def test_empty_list_roundtrip():
    data = []
    buf = io.BytesIO()
    output(buf, data)
    buf.seek(0)
    result = input_value(buf)
    assert result == data

def test_list_roundtrip():
    data = [1, 2, 3, 4, 5]
    buf = io.BytesIO()
    output(buf, data)
    buf.seek(0)
    result = input_value(buf)
    assert result == data

def test_nested_list_roundtrip():
    data = [1, [2, 3], [4, [5, 6]]]
    buf = io.BytesIO()
    output(buf, data)
    buf.seek(0)
    result = input_value(buf)
    assert result == data

def test_mixed_list_roundtrip():
    data = [42, b"test", 100]
    buf = io.BytesIO()
    output(buf, data)
    buf.seek(0)
    result = input_value(buf)
    assert result == data

def test_tagged_block_roundtrip():
    block = {'tag': 5, 'fields': [1, 2, 3]}
    buf = io.BytesIO()
    output(buf, block)
    buf.seek(0)
    result = input_value(buf)
    assert result == block

def test_size_small_int():
    assert size(0) == 1
    assert size(42) == 1
    assert size(63) == 1

def test_size_int8():
    assert size(64) == 2
    assert size(127) == 2
    assert size(-128) == 2

def test_size_int16():
    assert size(128) == 3
    assert size(32767) == 3
    assert size(-32768) == 3

def test_size_int32():
    s = size(32768)
    assert s == 5

def test_size_small_string():
    assert size(b"hi") == 1 + 2
    assert size(b"hello") == 1 + 5

def test_size_string8():
    s = size(b"a" * 50)
    assert s == 2 + 50

def test_size_string32():
    s = size(b"x" * 300)
    assert s == 5 + 300

def test_size_list():
    s = size([1, 2, 3])
    assert s > 3

def test_array_header_size_small():
    assert array_header_size(0) == 1
    assert array_header_size(7) == 1

def test_array_header_size_medium():
    assert array_header_size(8) in [1, 5]
    assert array_header_size(100) in [5, 9]

def test_output_array_access():
    buf = io.BytesIO()

    def arr_get(i):
        return i * 10

    arr_len = 5
    pos = 0

    final_pos = output_array_access(buf, arr_get, arr_len, pos)

    assert final_pos > pos
    buf.seek(0)
    data = buf.read()
    assert len(data) == arr_len * 4

def test_output_header_size_constant():
    assert OUTPUT_VALUE_HEADER_SIZE == 20

def test_prefix_constants():
    assert PREFIX_SMALL_INT == 0x40
    assert PREFIX_SMALL_STRING == 0x20
    assert PREFIX_SMALL_BLOCK == 0x80

def test_code_constants():
    assert CODE_INT8 == 0x0
    assert CODE_INT16 == 0x1
    assert CODE_INT32 == 0x2
    assert CODE_STRING8 == 0x9
    assert CODE_STRING32 == 0xA

def test_empty_string_roundtrip():
    data = b""
    buf = io.BytesIO()
    output(buf, data)
    buf.seek(0)
    result = input_value(buf)
    assert result == data

def test_large_list_roundtrip():
    data = list(range(100))
    buf = io.BytesIO()
    output(buf, data)
    buf.seek(0)
    result = input_value(buf)
    assert result == data

def test_bytearray_roundtrip():
    data = bytearray(b"test data")
    buf = io.BytesIO()
    output(buf, data)
    buf.seek(0)
    result = input_value(buf)
    assert result == bytes(data)

def test_invalid_input_raises_error():
    buf = io.BytesIO(b"\xFF\xFF")
    with pytest.raises((ValueError, EOFError)):
        input_value(buf)

def test_eof_raises_error():
    buf = io.BytesIO(b"")
    with pytest.raises(EOFError):
        input_value(buf)

def test_unsupported_type_raises_error():
    buf = io.BytesIO()
    with pytest.raises(TypeError):
        output(buf, 3.14)

def test_complex_nested_structure():
    data = [
        1,
        b"string",
        [2, 3, [4, 5]],
        {'tag': 1, 'fields': [6, b"inner"]},
        [7, 8, 9]
    ]
    buf = io.BytesIO()
    output(buf, data)
    buf.seek(0)
    result = input_value(buf)
    assert result == data

def test_negative_int_roundtrip():
    for val in [-1, -100, -1000, -10000]:
        buf = io.BytesIO()
        output(buf, val)
        buf.seek(0)
        result = input_value(buf)
        assert result == val

def test_boundary_values():
    boundaries = [
        -1073741824,
        -32769,
        -32768,
        -129,
        -128,
        -1,
        0,
        1,
        63,
        64,
        127,
        128,
        32767,
        32768,
        1073741823
    ]

    for val in boundaries:
        buf = io.BytesIO()
        output(buf, val)
        buf.seek(0)
        result = input_value(buf)
        assert result == val, f"Failed for value {val}"
