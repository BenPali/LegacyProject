from dataclasses import dataclass
from typing import List, Tuple, Optional, Union
from . import loc
from . import geneweb_compat


@dataclass(frozen=True)
class Atext:
    value: str


@dataclass(frozen=True)
class Avar:
    name: str
    attrs: List[str]


@dataclass(frozen=True)
class Atransl:
    decline: bool
    key: str
    context: str


@dataclass(frozen=True)
class AwidHei:
    value: str


@dataclass(frozen=True)
class Aif:
    condition: 'AST'
    then_branch: List['AST']
    else_branch: List['AST']


@dataclass(frozen=True)
class Aforeach:
    var: Tuple[str, List[str]]
    items: List[List['AST']]
    body: List['AST']


@dataclass(frozen=True)
class Afor:
    var: str
    start: 'AST'
    end: 'AST'
    body: List['AST']


@dataclass(frozen=True)
class Adefine:
    name: str
    params: List[Tuple[str, Optional['AST']]]
    body: List['AST']
    continuation: List['AST']


@dataclass(frozen=True)
class Aapply:
    name: str
    args: List[Tuple[Optional[str], List['AST']]]


@dataclass(frozen=True)
class Alet:
    var: str
    value: List['AST']
    body: List['AST']


@dataclass(frozen=True)
class Aop1:
    op: str
    operand: 'AST'


@dataclass(frozen=True)
class Aop2:
    op: str
    left: 'AST'
    right: 'AST'


@dataclass(frozen=True)
class Aint:
    value: str


@dataclass(frozen=True)
class Ainclude:
    source: Union[loc.SourceFile, loc.SourceRaw]


@dataclass(frozen=True)
class Apack:
    items: List['AST']


Desc = Union[Atext, Avar, Atransl, AwidHei, Aif, Aforeach, Afor, Adefine,
              Aapply, Alet, Aop1, Aop2, Aint, Ainclude, Apack]


@dataclass(frozen=True)
class AST:
    desc: Desc
    location: loc.Loc


def mk(desc: Desc, location: loc.Loc = loc.DUMMY) -> AST:
    return AST(desc=desc, location=location)


def mk_text(value: str, location: loc.Loc = loc.DUMMY) -> AST:
    return mk(Atext(value), location)


def mk_var(name: str, attrs: List[str], location: loc.Loc = loc.DUMMY) -> AST:
    return mk(Avar(name, attrs), location)


def mk_transl(decline: bool, key: str, context: str, location: loc.Loc = loc.DUMMY) -> AST:
    return mk(Atransl(decline, key, context), location)


def mk_wid_hei(value: str, location: loc.Loc = loc.DUMMY) -> AST:
    return mk(AwidHei(value), location)


def mk_foreach(var: Tuple[str, List[str]], items: List[List[AST]], body: List[AST],
               location: loc.Loc = loc.DUMMY) -> AST:
    return mk(Aforeach(var, items, body), location)


def mk_for(var: str, start: AST, end: AST, body: List[AST],
           location: loc.Loc = loc.DUMMY) -> AST:
    return mk(Afor(var, start, end, body), location)


def mk_if(condition: AST, then_branch: List[AST], else_branch: List[AST],
          location: loc.Loc = loc.DUMMY) -> AST:
    return mk(Aif(condition, then_branch, else_branch), location)


def mk_define(name: str, params: List[Tuple[str, Optional[AST]]], body: List[AST],
              continuation: List[AST], location: loc.Loc = loc.DUMMY) -> AST:
    return mk(Adefine(name, params, body, continuation), location)


def mk_apply(name: str, args: List[Tuple[Optional[str], List[AST]]],
             location: loc.Loc = loc.DUMMY) -> AST:
    return mk(Aapply(name, args), location)


def mk_let(var: str, value: List[AST], body: List[AST],
           location: loc.Loc = loc.DUMMY) -> AST:
    return mk(Alet(var, value, body), location)


def mk_op1(op: str, operand: AST, location: loc.Loc = loc.DUMMY) -> AST:
    return mk(Aop1(op, operand), location)


def mk_op2(op: str, left: AST, right: AST, location: loc.Loc = loc.DUMMY) -> AST:
    return mk(Aop2(op, left, right), location)


def mk_int(value: str, location: loc.Loc = loc.DUMMY) -> AST:
    return mk(Aint(value), location)


def mk_include(source: Union[loc.SourceFile, loc.SourceRaw],
               location: loc.Loc = loc.DUMMY) -> AST:
    return mk(Ainclude(source), location)


def mk_pack(items: List[AST], location: loc.Loc = loc.DUMMY) -> AST:
    return mk(Apack(items), location)


def subst(sf, ast: AST) -> AST:
    return AST(desc=subst_desc(sf, ast.desc), location=ast.location)


def subst_list(sf, asts: List[AST]) -> List[AST]:
    return [subst(sf, a) for a in asts]


def subst_desc(sf, desc: Desc) -> Desc:
    if isinstance(desc, Atext):
        return Atext(sf(desc.value))
    elif isinstance(desc, Avar):
        s1 = sf(desc.name)
        sl1 = [sf(s) for s in desc.attrs]
        if not desc.attrs:
            try:
                int(s1)
                return Aint(s1)
            except ValueError:
                pass
        parts = s1.split('.')
        if len(parts) == 1:
            return Avar(s1, sl1)
        else:
            return Avar(parts[0], parts[1:] + sl1)
    elif isinstance(desc, Atransl):
        return Atransl(desc.decline, sf(desc.key), desc.context)
    elif isinstance(desc, AwidHei):
        return AwidHei(sf(desc.value))
    elif isinstance(desc, Aif):
        return Aif(subst(sf, desc.condition), subst_list(sf, desc.then_branch),
                   subst_list(sf, desc.else_branch))
    elif isinstance(desc, Aforeach):
        s1 = sf(desc.var[0])
        sl1 = [sf(s) for s in desc.var[1]]
        parts = s1.split('.')
        if len(parts) == 1:
            var = (s1, sl1)
        else:
            var = (parts[0], list(reversed([sf(p) for p in reversed(parts[1:])])) + sl1)
        items = [[subst(sf, a) for a in item] for item in desc.items]
        body = subst_list(sf, desc.body)
        return Aforeach(var, items, body)
    elif isinstance(desc, Afor):
        return Afor(sf(desc.var), subst(sf, desc.start), subst(sf, desc.end),
                    subst_list(sf, desc.body))
    elif isinstance(desc, Adefine):
        params = [(sf(x), subst(sf, a) if a is not None else None) for x, a in desc.params]
        return Adefine(sf(desc.name), params, subst_list(sf, desc.body),
                       subst_list(sf, desc.continuation))
    elif isinstance(desc, Aapply):
        args = [(sf(x) if x is not None else None, subst_list(sf, asts))
                for x, asts in desc.args]
        return Aapply(sf(desc.name), args)
    elif isinstance(desc, Alet):
        return Alet(sf(desc.var), subst_list(sf, desc.value), subst_list(sf, desc.body))
    elif isinstance(desc, Ainclude):
        return desc
    elif isinstance(desc, Aint):
        return desc
    elif isinstance(desc, Aop1):
        return Aop1(desc.op, subst(sf, desc.operand))
    elif isinstance(desc, Aop2):
        return Aop2(sf(desc.op), subst(sf, desc.left), subst(sf, desc.right))
    elif isinstance(desc, Apack):
        return Apack(subst_list(sf, desc.items))
    else:
        raise ValueError(f"Unknown desc type: {type(desc)}")
