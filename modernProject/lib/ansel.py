ISO_8859_1_UNKNOWN = chr(129)
ANSEL_UNKNOWN = 129


def no_accent(c: str) -> str:
    if not c:
        return c
    code = ord(c)
    if 224 <= code <= 229:
        return 'a'
    if code in (162, 231):
        return 'c'
    if 232 <= code <= 235:
        return 'e'
    if 236 <= code <= 239:
        return 'i'
    if code == 241:
        return 'n'
    if 242 <= code <= 246:
        return 'o'
    if 249 <= code <= 252:
        return 'u'
    if code in (253, 255):
        return 'y'
    if 192 <= code <= 197:
        return 'A'
    if code == 199:
        return 'C'
    if 200 <= code <= 203:
        return 'E'
    if 204 <= code <= 207:
        return 'I'
    if code == 209:
        return 'N'
    if 210 <= code <= 214:
        return 'O'
    if 217 <= code <= 220:
        return 'U'
    if code == 221:
        return 'Y'
    if code in (168, 176, 180, 184, 186):
        return ' '
    if code == 171:
        return '<'
    if code == 187:
        return '>'
    return c


def accent_code(c: str) -> int:
    if not c:
        return 0
    code = ord(c)
    if code in (192, 200, 204, 210, 217, 224, 232, 236, 242, 249):
        return 225
    if code in (193, 201, 205, 211, 218, 221, 180, 225, 233, 237, 243, 250, 253):
        return 226
    if code in (194, 202, 206, 212, 219, 226, 234, 238, 244, 251):
        return 227
    if code in (195, 209, 213, 227, 241, 245):
        return 228
    if code in (196, 203, 207, 214, 220, 168, 228, 235, 239, 246, 252, 255):
        return 232
    if code in (197, 229, 176, 186):
        return 234
    if code in (199, 231, 184):
        return 240
    if code == 161:
        return 198
    if code == 162:
        return 252
    if code == 163:
        return 185
    if code == 164:
        return 0x6f
    if code == 165:
        return 0x59
    if code == 166:
        return 0x7c
    if code == 169:
        return 195
    if code == 170:
        return 0x61
    if code == 171:
        return 0x3c
    if code == 173:
        return 0x2d
    if code == 174:
        return 170
    if code == 177:
        return 171
    if code == 178:
        return 0x32
    if code == 179:
        return 0x33
    if code == 183:
        return 168
    if code == 185:
        return 0x31
    if code == 187:
        return 0x3e
    if code == 191:
        return 197
    if code == 198:
        return 165
    if code == 230:
        return 181
    if code == 208:
        return 163
    if code == 240:
        return 179
    if code == 216:
        return 162
    if code == 248:
        return 178
    if code == 222:
        return 164
    if code == 254:
        return 180
    if code == 223:
        return 207
    if code >= 161:
        return ANSEL_UNKNOWN
    return 0


def of_iso_8859_1(s: str) -> str:
    length = 0
    identical = True
    for c in s:
        a = accent_code(c)
        if a == 0:
            length += 1
        else:
            n = no_accent(c)
            if n == c:
                length += 1
                identical = False
            else:
                length += 2
                identical = False
    if identical:
        return s
    result = []
    for c in s:
        a = accent_code(c)
        if a > 0:
            result.append(chr(a))
            n = no_accent(c)
            if n != c:
                result.append(n)
        else:
            result.append(c)
    return ''.join(result)


def grave(c: str) -> str:
    mapping = {
        'a': '\u00e0', 'e': '\u00e8', 'i': '\u00ec', 'o': '\u00f2', 'u': '\u00f9',
        'A': '\u00c0', 'E': '\u00c8', 'I': '\u00cc', 'O': '\u00d2', 'U': '\u00d9',
        ' ': '`'
    }
    return mapping.get(c, c)


def acute(c: str) -> str:
    mapping = {
        'a': '\u00e1', 'e': '\u00e9', 'i': '\u00ed', 'o': '\u00f3', 'u': '\u00fa', 'y': '\u00fd',
        'A': '\u00c1', 'E': '\u00c9', 'I': '\u00cd', 'O': '\u00d3', 'U': '\u00da', 'Y': '\u00dd',
        ' ': '\u00b4'
    }
    return mapping.get(c, c)


def circum(c: str) -> str:
    mapping = {
        'a': '\u00e2', 'e': '\u00ea', 'i': '\u00ee', 'o': '\u00f4', 'u': '\u00fb',
        'A': '\u00c2', 'E': '\u00ca', 'I': '\u00ce', 'O': '\u00d4', 'U': '\u00db',
        ' ': '^'
    }
    return mapping.get(c, c)


def uml(c: str) -> str:
    mapping = {
        'a': '\u00e4', 'e': '\u00eb', 'i': '\u00ef', 'o': '\u00f6', 'u': '\u00fc', 'y': '\u00ff',
        'A': '\u00c4', 'E': '\u00cb', 'I': '\u00cf', 'O': '\u00d6', 'U': '\u00dc',
        ' ': '\u00a8'
    }
    return mapping.get(c, c)


def circle(c: str) -> str:
    mapping = {'a': '\u00e5', 'A': '\u00c5', ' ': '\u00b0'}
    return mapping.get(c, c)


def tilde(c: str) -> str:
    mapping = {
        'a': '\u00e3', 'n': '\u00f1', 'o': '\u00f5',
        'A': '\u00c3', 'N': '\u00d1', 'O': '\u00d5',
        ' ': '~'
    }
    return mapping.get(c, c)


def cedil(c: str) -> str:
    mapping = {'c': '\u00e7', 'C': '\u00c7', ' ': '\u00b8'}
    return mapping.get(c, c)


def slash(c: str) -> str:
    mapping = {'C': '\u00a2', 'c': '\u00a2', 'O': '\u00d8', 'o': '\u00f8', ' ': '/'}
    return mapping.get(c, c)


def to_iso_8859_1(s: str) -> str:
    length = 0
    identical = True
    i = 0
    while i < len(s):
        if i == len(s) - 1:
            length += 1
        else:
            code = ord(s[i])
            if code in (166, 172, 173, 182, 188, 189):
                length += 2
                identical = False
            elif code >= 224:
                length += 1
                identical = False
                i += 1
            elif code >= 161:
                length += 1
                identical = False
            else:
                length += 1
        i += 1
    if identical:
        return s
    result = []
    i = 0
    while i < len(s):
        if i == len(s) - 1:
            result.append(s[i])
            break
        code = ord(s[i])
        if code in (166, 172, 173, 182, 188, 189):
            pairs = {
                166: ('O', 'E'), 172: ('O', '\u00b4'), 173: ('U', '\u00b4'),
                182: ('o', 'e'), 188: ('o', '\u00b4'), 189: ('u', '\u00b4')
            }
            c1, c2 = pairs.get(code, (ISO_8859_1_UNKNOWN, ISO_8859_1_UNKNOWN))
            result.extend([c1, c2])
        elif code >= 224:
            c_next = s[i + 1]
            if code in (224, 226, 235, 237, 254):
                c_next = acute(c_next)
            elif code in (225, 236):
                c_next = grave(c_next)
            elif code in (227, 250):
                c_next = circum(c_next)
            elif code in (228, 230, 233):
                c_next = tilde(c_next)
            elif code in (232, 238):
                c_next = uml(c_next)
            elif code in (231, 234):
                c_next = circle(c_next)
            elif code in (240, 241, 242, 243, 244, 247, 248, 249):
                c_next = cedil(c_next)
            elif code == 252:
                c_next = slash(c_next)
            result.append(c_next)
            i += 1
        else:
            mapping = {
                161: 'L', 162: '\u00d8', 163: '\u00d0', 164: '\u00de', 165: '\u00c6',
                167: '\u00b4', 168: '\u00b7', 169: 'b', 170: '\u00ae', 171: '\u00b1',
                174: '\u00b4', 176: '\u00b4', 177: 'l', 178: '\u00f8', 179: '\u00f0',
                180: '\u00fe', 181: '\u00e6', 183: '"', 184: 'i', 185: '\u00a3',
                186: '\u00f0', 190: ISO_8859_1_UNKNOWN, 191: ISO_8859_1_UNKNOWN,
                192: '\u00b0', 194: 'P', 195: '\u00a9', 196: '#', 197: '\u00bf',
                198: '\u00a1', 205: 'e', 206: 'o', 207: '\u00df'
            }
            result.append(mapping.get(code, chr(code)))
        i += 1
    return ''.join(result)
