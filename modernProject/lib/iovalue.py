import struct
import sys
from typing import Any, BinaryIO, Callable
from dataclasses import dataclass

SIZEOF_LONG = 4

SIGN_EXTEND_SHIFT = (((sys.maxsize.bit_length() + 1) // 8 - 1) * 8) - 1

PREFIX_SMALL_BLOCK = 0x80
PREFIX_SMALL_INT = 0x40
PREFIX_SMALL_STRING = 0x20

CODE_INT8 = 0x0
CODE_INT16 = 0x1
CODE_INT32 = 0x2
CODE_INT64 = 0x3
CODE_BLOCK32 = 0x8
CODE_BLOCK64 = 0x13
CODE_STRING8 = 0x9
CODE_STRING32 = 0xA

OUTPUT_VALUE_HEADER_SIZE = 20

@dataclass
class InFuns:
    input_byte: Callable[[BinaryIO], int]
    input_binary_int: Callable[[BinaryIO], int]
    input_data: Callable[[BinaryIO, int], bytes]

@dataclass
class OutFuns:
    output_byte: Callable[[BinaryIO, int], None]
    output_binary_int: Callable[[BinaryIO, int], None]
    output_data: Callable[[BinaryIO, bytes], None]

def sign_extend(x: int) -> int:
    if SIGN_EXTEND_SHIFT <= 0:
        return x
    return (x << SIGN_EXTEND_SHIFT) >> SIGN_EXTEND_SHIFT

def default_input_byte(ic: BinaryIO) -> int:
    b = ic.read(1)
    if not b:
        raise EOFError("Unexpected end of file")
    return b[0]

def default_input_binary_int(ic: BinaryIO) -> int:
    data = ic.read(4)
    if len(data) < 4:
        raise EOFError("Unexpected end of file")
    return struct.unpack('>I', data)[0]

def default_input_data(ic: BinaryIO, length: int) -> bytes:
    data = ic.read(length)
    if len(data) < length:
        raise EOFError("Unexpected end of file")
    return data

def default_output_byte(oc: BinaryIO, b: int) -> None:
    oc.write(bytes([b & 0xFF]))

def default_output_binary_int(oc: BinaryIO, n: int) -> None:
    oc.write(struct.pack('>I', n & 0xFFFFFFFF))

def default_output_data(oc: BinaryIO, data: bytes) -> None:
    oc.write(data)

in_channel_funs = InFuns(
    input_byte=default_input_byte,
    input_binary_int=default_input_binary_int,
    input_data=default_input_data
)

out_channel_funs = OutFuns(
    output_byte=default_output_byte,
    output_binary_int=default_output_binary_int,
    output_data=default_output_data
)

def input_binary_int64(ifuns: InFuns, ic: BinaryIO) -> int:
    result = 0
    for _ in range(8):
        result = (result << 8) + ifuns.input_byte(ic)
    return result

def input_block(ifuns: InFuns, ic: BinaryIO, tag: int, size: int) -> Any:
    if tag == 0:
        result = [None] * size
        for i in range(size):
            result[i] = input_loop(ifuns, ic)
        return result
    else:
        block = {'tag': tag, 'fields': []}
        for _ in range(size):
            block['fields'].append(input_loop(ifuns, ic))
        return block

def input_loop(ifuns: InFuns, ic: BinaryIO) -> Any:
    code = ifuns.input_byte(ic)

    if code >= PREFIX_SMALL_INT:
        if code >= PREFIX_SMALL_BLOCK:
            tag = code & 0xF
            size = (code >> 4) & 0x7
            return input_block(ifuns, ic, tag, size)
        else:
            return code & 0x3F

    elif code >= PREFIX_SMALL_STRING:
        length = code & 0x1F
        return ifuns.input_data(ic, length)

    elif code == CODE_INT8:
        b = ifuns.input_byte(ic)
        return struct.unpack('b', bytes([b]))[0]

    elif code == CODE_INT16:
        h = ifuns.input_byte(ic)
        l = ifuns.input_byte(ic)
        val = (h << 8) + l
        return struct.unpack('>h', struct.pack('>H', val))[0]

    elif code == CODE_INT32:
        x1 = ifuns.input_byte(ic)
        x2 = ifuns.input_byte(ic)
        x3 = ifuns.input_byte(ic)
        x4 = ifuns.input_byte(ic)
        val = (x1 << 24) + (x2 << 16) + (x3 << 8) + x4
        return struct.unpack('>i', struct.pack('>I', val))[0]

    elif code == CODE_INT64:
        if sys.maxsize <= 2**31:
            raise ValueError("64-bit integers not supported on 32-bit systems")
        return input_binary_int64(ifuns, ic)

    elif code == CODE_BLOCK32:
        header = ifuns.input_binary_int(ic)
        tag = header & 0xFF
        size = header >> 10
        return input_block(ifuns, ic, tag, size)

    elif code == CODE_BLOCK64:
        if sys.maxsize <= 2**31:
            raise ValueError("64-bit blocks not supported on 32-bit systems")
        header = input_binary_int64(ifuns, ic)
        tag = header & 0xFF
        size = header >> 10
        return input_block(ifuns, ic, tag, size)

    elif code == CODE_STRING8:
        length = ifuns.input_byte(ic)
        return ifuns.input_data(ic, length)

    elif code == CODE_STRING32:
        length = ifuns.input_binary_int(ic)
        return ifuns.input_data(ic, length)

    else:
        raise ValueError(f"Invalid code: 0x{code:02x}")

def input_value(ic: BinaryIO) -> Any:
    return input_loop(in_channel_funs, ic)

def output_binary_int64(ofuns: OutFuns, oc: BinaryIO, x: int) -> None:
    for i in range(1, 9):
        ofuns.output_byte(oc, (x >> (64 - 8 * i)) & 0xFF)

def output_block_header(ofuns: OutFuns, oc: BinaryIO, tag: int, size: int) -> None:
    hd = (size << 10) + tag

    if tag < 16 and size < 8:
        ofuns.output_byte(oc, PREFIX_SMALL_BLOCK + tag + (size << 4))
    elif sys.maxsize > 2**31 and hd >= (1 << 32):
        ofuns.output_byte(oc, CODE_BLOCK64)
        output_binary_int64(ofuns, oc, hd)
    else:
        ofuns.output_byte(oc, CODE_BLOCK32)
        ofuns.output_byte(oc, (size >> 14) & 0xFF)
        ofuns.output_byte(oc, (size >> 6) & 0xFF)
        ofuns.output_byte(oc, (size << 2) & 0xFF)
        ofuns.output_byte(oc, ((size << 10) & 0xFF) + tag)

def output_loop(ofuns: OutFuns, oc: BinaryIO, x: Any) -> None:
    if isinstance(x, int):
        if 0 <= x < 0x40:
            ofuns.output_byte(oc, PREFIX_SMALL_INT + x)
        elif -128 <= x < 128:
            ofuns.output_byte(oc, CODE_INT8)
            b = struct.pack('b', x)[0]
            ofuns.output_byte(oc, b)
        elif -32768 <= x <= 32767:
            ofuns.output_byte(oc, CODE_INT16)
            data = struct.pack('>h', x)
            ofuns.output_byte(oc, data[0])
            ofuns.output_byte(oc, data[1])
        elif -1073741824 <= x <= 1073741823:
            ofuns.output_byte(oc, CODE_INT32)
            data = struct.pack('>i', x)
            for b in data:
                ofuns.output_byte(oc, b)
        else:
            ofuns.output_byte(oc, CODE_INT64)
            output_binary_int64(ofuns, oc, x)

    elif isinstance(x, (bytes, bytearray)):
        length = len(x)
        if length < 0x20:
            ofuns.output_byte(oc, PREFIX_SMALL_STRING + length)
        elif length < 0x100:
            ofuns.output_byte(oc, CODE_STRING8)
            ofuns.output_byte(oc, length)
        else:
            ofuns.output_byte(oc, CODE_STRING32)
            ofuns.output_binary_int(oc, length)
        ofuns.output_data(oc, bytes(x))

    elif isinstance(x, str):
        data = x.encode('utf-8')
        output_loop(ofuns, oc, data)

    elif isinstance(x, list):
        size = len(x)
        output_block_header(ofuns, oc, 0, size)
        for item in x:
            output_loop(ofuns, oc, item)

    elif isinstance(x, dict) and 'tag' in x and 'fields' in x:
        tag = x['tag']
        fields = x['fields']
        output_block_header(ofuns, oc, tag, len(fields))
        for field in fields:
            output_loop(ofuns, oc, field)

    elif x is None:
        output_block_header(ofuns, oc, 0, 0)

    else:
        raise TypeError(f"Unsupported type for output: {type(x)}")

def output(oc: BinaryIO, value: Any) -> None:
    output_loop(out_channel_funs, oc, value)

def calculate_size(ofuns: OutFuns, value: Any) -> int:
    size_counter = [0]

    def count_byte(_, __):
        size_counter[0] += 1

    def count_binary_int(_, __):
        size_counter[0] += 4

    def count_data(_, data):
        size_counter[0] += len(data)

    size_funs = OutFuns(
        output_byte=count_byte,
        output_binary_int=count_binary_int,
        output_data=count_data
    )

    output_loop(size_funs, None, value)
    return size_counter[0]

def size(value: Any) -> int:
    return calculate_size(out_channel_funs, value)

def array_header_size(arr_len: int) -> int:
    if arr_len < 8:
        return 1
    elif sys.maxsize > 2**31 and (arr_len << 10) >= (1 << 32):
        return 9
    else:
        return 5

def output_array_access(oc: BinaryIO, arr_get: Callable[[int], Any], arr_len: int, pos: int) -> int:
    current_pos = pos + OUTPUT_VALUE_HEADER_SIZE + array_header_size(arr_len)

    for i in range(arr_len):
        default_output_binary_int(oc, current_pos)
        current_pos += size(arr_get(i))

    return current_pos
