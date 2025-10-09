class Buff:
    def __init__(self):
        self._buff = bytearray(80)
        self._capacity = 80

    def store(self, pos: int, char: str) -> int:
        if len(char) != 1:
            raise ValueError("char must be a single character")
        if pos >= self._capacity:
            self._extend()
        self._buff[pos] = ord(char)
        return pos + 1

    def mstore(self, pos: int, s: str) -> int:
        return self.gstore(pos, s, 0, len(s))

    def gstore(self, pos: int, s: str, si: int, slen: int) -> int:
        actual_len = min(slen, len(s) - si)
        newlen = pos + actual_len
        while newlen > self._capacity:
            self._extend()
        encoded = s[si:si + actual_len].encode('utf-8')
        self._buff[pos:pos + len(encoded)] = encoded
        return pos + len(encoded)

    def get(self, length: int) -> str:
        return self._buff[:length].decode('utf-8')

    def _extend(self):
        self._capacity *= 2
        new_buff = bytearray(self._capacity)
        new_buff[:len(self._buff)] = self._buff
        self._buff = new_buff


_global_buff = Buff()


def store(pos: int, char: str) -> int:
    return _global_buff.store(pos, char)


def mstore(pos: int, s: str) -> int:
    return _global_buff.mstore(pos, s)


def gstore(pos: int, s: str, si: int, slen: int) -> int:
    return _global_buff.gstore(pos, s, si, slen)


def get(length: int) -> str:
    return _global_buff.get(length)
