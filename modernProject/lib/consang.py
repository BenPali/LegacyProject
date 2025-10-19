from enum import Enum
from dataclasses import dataclass, field
from typing import List, Tuple, Callable, Optional
from lib import adef
from lib.database import Driver
from lib.collection import Marker


class AncStat(Enum):
    MAYBE_ANC = 0
    IS_ANC = 1


class Visit(Enum):
    NOT_VISITED = 0
    BEING_VISITED = 1
    VISITED = 2


@dataclass
class Relationship:
    weight1: float = 0.0
    weight2: float = 0.0
    relationship: float = 0.0
    lens1: List[Tuple[int, int, List[int]]] = field(default_factory=list)
    lens2: List[Tuple[int, int, List[int]]] = field(default_factory=list)
    inserted: int = 0
    elim_ancestors: bool = False
    anc_stat1: AncStat = AncStat.MAYBE_ANC
    anc_stat2: AncStat = AncStat.MAYBE_ANC


@dataclass
class RelationshipInfo:
    tstab: Marker
    reltab: Marker
    queue: List[List[int]] = field(default_factory=lambda: [])


class TopologicalSortError(Exception):
    def __init__(self, person):
        self.person = person
        super().__init__(f"Topological sort error: person is their own ancestor")


def half(x: float) -> float:
    return x * 0.5


_mark_counter = 0


def new_mark() -> int:
    global _mark_counter
    _mark_counter += 1
    return _mark_counter


def _noloop_aux(base, error: Callable, tab: Marker, i: int):
    visit_state = tab.get(i)
    if visit_state == Visit.NOT_VISITED:
        person = Driver.poi(base, i)
        parents_opt = Driver.get_parents(person)
        if parents_opt is not None:
            fam = Driver.foi(base, parents_opt)
            fath = Driver.get_father(fam)
            moth = Driver.get_mother(fam)
            tab.set(i, Visit.BEING_VISITED)
            _noloop_aux(base, error, tab, fath)
            _noloop_aux(base, error, tab, moth)
        tab.set(i, Visit.VISITED)
    elif visit_state == Visit.BEING_VISITED:
        from lib.gwdef import OwnAncestor
        person = Driver.poi(base, i)
        error(OwnAncestor(person))


def check_noloop(base, error: Callable):
    ipers = Driver.ipers(base)
    tab = Driver.iper_marker(ipers, Visit.NOT_VISITED)
    for i in ipers:
        _noloop_aux(base, error, tab, i)


def check_noloop_for_person_list(base, error: Callable, person_list: List[int]):
    ipers = Driver.ipers(base)
    tab = Driver.iper_marker(ipers, Visit.NOT_VISITED)
    for i in person_list:
        _noloop_aux(base, error, tab, i)


def topological_sort(base, poi: Callable):
    persons = Driver.ipers(base)
    tab = Driver.iper_marker(persons, 0)
    cnt = 0

    for i in persons:
        a = poi(base, i)
        parents_opt = Driver.get_parents(a)
        if parents_opt is not None:
            cpl = Driver.foi(base, parents_opt)
            ifath = Driver.get_father(cpl)
            imoth = Driver.get_mother(cpl)
            tab.set(ifath, tab.get(ifath) + 1)
            tab.set(imoth, tab.get(imoth) + 1)

    todo = []
    for i in persons:
        if tab.get(i) == 0:
            todo.append(i)

    def loop(tval: int, lst: List[int]) -> int:
        nonlocal cnt
        if not lst:
            return cnt

        new_list = []
        for i in lst:
            a = poi(base, i)
            tab.set(i, tval)
            cnt += 1
            parents_opt = Driver.get_parents(a)
            if parents_opt is not None:
                cpl = Driver.foi(base, parents_opt)
                ifath = Driver.get_father(cpl)
                imoth = Driver.get_mother(cpl)
                tab.set(ifath, tab.get(ifath) - 1)
                tab.set(imoth, tab.get(imoth) - 1)
                if tab.get(ifath) == 0:
                    new_list.append(ifath)
                if tab.get(imoth) == 0:
                    new_list.append(imoth)

        return loop(tval + 1, new_list)

    loop(0, todo)

    if cnt != Driver.nb_of_persons(base):
        def error_handler(err):
            from lib.gwdef import OwnAncestor
            if isinstance(err, OwnAncestor):
                raise TopologicalSortError(err.person)
            raise AssertionError("Unexpected error type")

        check_noloop(base, error_handler)

    return tab


PHONY_REL = Relationship()


def make_relationship_info(base, tstab: Marker) -> RelationshipInfo:
    ipers = Driver.ipers(base)
    tab = Driver.iper_marker(ipers, PHONY_REL)
    return RelationshipInfo(tstab=tstab, reltab=tab, queue=[])


def _insert_branch_len_rec(x: Tuple[int, int, int], lens: List[Tuple[int, int, List[int]]]) -> List[Tuple[int, int, List[int]]]:
    len_val, n, ip = x
    if not lens:
        return [(len_val, n, [ip])]

    result = []
    found = False
    for len1, n1, ipl1 in lens:
        if len_val == len1 and not found:
            n2 = n + n1
            if n < 0 or n1 < 0 or n2 < 0:
                n2 = -1
            result.append((len1, n2, [ip] + ipl1))
            found = True
        else:
            result.append((len1, n1, ipl1))

    if not found:
        result.append((len_val, n, [ip]))

    return result


def insert_branch_len(ip: int, lens: List[Tuple[int, int, List[int]]], branch: Tuple[int, int, List[int]]) -> List[Tuple[int, int, List[int]]]:
    len_val, n, _ipl = branch
    return _insert_branch_len_rec((len_val + 1, n, ip), lens)


def consang_of(p) -> float:
    consang = Driver.get_consang(p)
    if consang == adef.NO_CONSANG:
        return 0.0
    return consang.to_float()


def relationship_and_links(base, ri: RelationshipInfo, b: bool, ip1: int, ip2: int) -> Tuple[float, List[int]]:
    i1 = ip1
    i2 = ip2

    if i1 == i2:
        return (1.0, [])

    reltab = ri.reltab
    tstab = ri.tstab
    yes_inserted = new_mark()

    def reset(u: int):
        tu = reltab.get(u)
        if tu is PHONY_REL:
            reltab.set(u, Relationship(
                weight1=0.0,
                weight2=0.0,
                relationship=0.0,
                lens1=[],
                lens2=[],
                inserted=yes_inserted,
                elim_ancestors=False,
                anc_stat1=AncStat.MAYBE_ANC,
                anc_stat2=AncStat.MAYBE_ANC
            ))
        else:
            tu.weight1 = 0.0
            tu.weight2 = 0.0
            tu.relationship = 0.0
            tu.lens1 = []
            tu.lens2 = []
            tu.inserted = yes_inserted
            tu.elim_ancestors = False
            tu.anc_stat1 = AncStat.MAYBE_ANC
            tu.anc_stat2 = AncStat.MAYBE_ANC

    qi = min(tstab.get(i1), tstab.get(i2))
    qmax = -1

    def insert(u: int):
        nonlocal qmax
        v = tstab.get(u)
        reset(u)

        if v >= len(ri.queue):
            old_len = len(ri.queue)
            ri.queue.extend([[] for _ in range(v + 1 - old_len)])

        if qmax < 0:
            for i in range(qi, v):
                if i < len(ri.queue):
                    ri.queue[i] = []
                else:
                    ri.queue.append([])
            qmax = v
            if v < len(ri.queue):
                ri.queue[v] = [u]
            else:
                ri.queue.append([u])
        else:
            if v > qmax:
                for i in range(qmax + 1, v + 1):
                    if i < len(ri.queue):
                        ri.queue[i] = []
                    else:
                        ri.queue.append([])
                qmax = v
            ri.queue[v] = [u] + ri.queue[v]

    relationship_val = 0.0
    nb_anc1 = 1
    nb_anc2 = 1
    tops = []

    def treat_parent(ip_from: int, u: Relationship, y: int):
        nonlocal nb_anc1, nb_anc2
        if reltab.get(y).inserted != yes_inserted:
            insert(y)

        ty = reltab.get(y)
        p1 = half(u.weight1)
        p2 = half(u.weight2)

        if u.anc_stat1 == AncStat.IS_ANC and ty.anc_stat1 != AncStat.IS_ANC:
            ty.anc_stat1 = AncStat.IS_ANC
            nb_anc1 += 1

        if u.anc_stat2 == AncStat.IS_ANC and ty.anc_stat2 != AncStat.IS_ANC:
            ty.anc_stat2 = AncStat.IS_ANC
            nb_anc2 += 1

        ty.weight1 += p1
        ty.weight2 += p2
        ty.relationship += (p1 * p2)

        if u.elim_ancestors:
            ty.elim_ancestors = True

        if b and not ty.elim_ancestors:
            for branch in u.lens1:
                ty.lens1 = insert_branch_len(ip_from, ty.lens1, branch)
            for branch in u.lens2:
                ty.lens2 = insert_branch_len(ip_from, ty.lens2, branch)

    def treat_ancestor(u: int):
        nonlocal relationship_val, nb_anc1, nb_anc2
        tu = reltab.get(u)
        a = Driver.poi(base, u)
        contribution = (tu.weight1 * tu.weight2) - (tu.relationship * (1.0 + consang_of(a)))

        if tu.anc_stat1 == AncStat.IS_ANC:
            nb_anc1 -= 1
        if tu.anc_stat2 == AncStat.IS_ANC:
            nb_anc2 -= 1

        relationship_val += contribution

        if b and contribution != 0.0 and not tu.elim_ancestors:
            tops.append(u)
            tu.elim_ancestors = True

        parents_opt = Driver.get_parents(a)
        if parents_opt is not None:
            cpl = Driver.foi(base, parents_opt)
            treat_parent(u, tu, Driver.get_father(cpl))
            treat_parent(u, tu, Driver.get_mother(cpl))

    insert(i1)
    insert(i2)
    reltab.get(i1).weight1 = 1.0
    reltab.get(i2).weight2 = 1.0
    reltab.get(i1).lens1 = [(0, 1, [])]
    reltab.get(i2).lens2 = [(0, 1, [])]
    reltab.get(i1).anc_stat1 = AncStat.IS_ANC
    reltab.get(i2).anc_stat2 = AncStat.IS_ANC

    while qi <= qmax and nb_anc1 > 0 and nb_anc2 > 0:
        for ancestor in ri.queue[qi]:
            treat_ancestor(ancestor)
        qi += 1

    return (half(relationship_val), tops)
