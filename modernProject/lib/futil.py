from typing import Callable, Optional, TypeVar, List, Tuple
from dataclasses import replace
from lib.adef import Cdate, Date, Couple
from lib.gwdef import (
    GenTitle, GenTitleName, Tmain, Tname, Tnone,
    GenPersEvent, GenPersEventName, EpersName,
    GenFamEvent, GenFamEventName, EfamName,
    GenRelation, GenPerson, GenAscend, GenUnion, GenFamily, GenDescend,
    Death, NotDead, DeadYoung, DeadDontKnowWhen, DontKnowIfDead, OfCourseDead, DeathWithReason,
    Burial, UnknownBurial, Buried, Cremated,
    Divorce, NotDivorced, SeparatedOld, NotSeparated, DivorceWithDate, Separated
)
from lib.date import od_of_cdate, cdate_of_date
from lib.adef import parent_array


T = TypeVar('T')
U = TypeVar('U')
V = TypeVar('V')
W = TypeVar('W')
X = TypeVar('X')
Y = TypeVar('Y')


def identity(x: T) -> T:
    return x


def map_cdate(fd: Callable[[Date], Date], cd: Cdate) -> Cdate:
    d_opt = od_of_cdate(cd)
    if d_opt is not None:
        return cdate_of_date(fd(d_opt))
    return cd


def map_title_strings(f: Callable[[T], U], t: GenTitle[T], fd: Optional[Callable[[Date], Date]] = None) -> GenTitle[U]:
    if fd is None:
        fd = identity

    if isinstance(t.t_name, Tmain):
        t_name = Tmain[U]()
    elif isinstance(t.t_name, Tname):
        t_name = Tname[U](name=f(t.t_name.name))
    elif isinstance(t.t_name, Tnone):
        t_name = Tnone[U]()
    else:
        t_name = t.t_name

    return GenTitle[U](
        t_name=t_name,
        t_ident=f(t.t_ident),
        t_place=f(t.t_place),
        t_date_start=map_cdate(fd, t.t_date_start),
        t_date_end=map_cdate(fd, t.t_date_end),
        t_nth=t.t_nth
    )


def map_pers_event(
    fp: Callable[[T], X],
    fs: Callable[[U], Y],
    e: GenPersEvent[T, U],
    fd: Optional[Callable[[Date], Date]] = None
) -> GenPersEvent[X, Y]:
    if fd is None:
        fd = identity

    if isinstance(e.epers_name, GenPersEventName):
        epers_name = e.epers_name
    elif isinstance(e.epers_name, EpersName):
        epers_name = EpersName[Y](name=fs(e.epers_name.name))
    else:
        epers_name = e.epers_name

    return GenPersEvent[X, Y](
        epers_name=epers_name,
        epers_date=map_cdate(fd, e.epers_date),
        epers_place=fs(e.epers_place),
        epers_reason=fs(e.epers_reason),
        epers_note=fs(e.epers_note),
        epers_src=fs(e.epers_src),
        epers_witnesses=[(fp(p), w) for p, w in e.epers_witnesses]
    )


def map_fam_event(
    fp: Callable[[T], X],
    fs: Callable[[U], Y],
    e: GenFamEvent[T, U],
    fd: Optional[Callable[[Date], Date]] = None
) -> GenFamEvent[X, Y]:
    if fd is None:
        fd = identity

    if isinstance(e.efam_name, GenFamEventName):
        efam_name = e.efam_name
    elif isinstance(e.efam_name, EfamName):
        efam_name = EfamName[Y](name=fs(e.efam_name.name))
    else:
        efam_name = e.efam_name

    return GenFamEvent[X, Y](
        efam_name=efam_name,
        efam_date=map_cdate(fd, e.efam_date),
        efam_place=fs(e.efam_place),
        efam_reason=fs(e.efam_reason),
        efam_note=fs(e.efam_note),
        efam_src=fs(e.efam_src),
        efam_witnesses=[(fp(p), w) for p, w in e.efam_witnesses]
    )


def map_relation_ps(fp: Callable[[T], X], fs: Callable[[U], Y], r: GenRelation[T, U]) -> GenRelation[X, Y]:
    return GenRelation[X, Y](
        r_type=r.r_type,
        r_fath=fp(r.r_fath) if r.r_fath is not None else None,
        r_moth=fp(r.r_moth) if r.r_moth is not None else None,
        r_sources=fs(r.r_sources)
    )


def map_death(fd: Callable[[Date], Date], death: Death) -> Death:
    if isinstance(death, (NotDead, DeadYoung, DeadDontKnowWhen, DontKnowIfDead, OfCourseDead)):
        return death
    elif isinstance(death, DeathWithReason):
        return DeathWithReason(reason=death.reason, date=map_cdate(fd, death.date))
    return death


def map_burial(fd: Callable[[Date], Date], burial: Burial) -> Burial:
    if isinstance(burial, UnknownBurial):
        return burial
    elif isinstance(burial, Buried):
        return Buried(date=map_cdate(fd, burial.date))
    elif isinstance(burial, Cremated):
        return Cremated(date=map_cdate(fd, burial.date))
    return burial


def map_person_ps(
    fp: Callable[[U], X],
    fs: Callable[[V], Y],
    p: GenPerson[T, U, V],
    fd: Optional[Callable[[Date], Date]] = None
) -> GenPerson[T, X, Y]:
    if fd is None:
        fd = identity

    return GenPerson[T, X, Y](
        first_name=fs(p.first_name),
        surname=fs(p.surname),
        occ=p.occ,
        image=fs(p.image),
        public_name=fs(p.public_name),
        qualifiers=[fs(q) for q in p.qualifiers],
        aliases=[fs(a) for a in p.aliases],
        first_names_aliases=[fs(fn) for fn in p.first_names_aliases],
        surnames_aliases=[fs(sn) for sn in p.surnames_aliases],
        titles=[map_title_strings(fs, t, fd) for t in p.titles],
        rparents=[map_relation_ps(fp, fs, r) for r in p.rparents],
        related=[fp(r) for r in p.related],
        occupation=fs(p.occupation),
        sex=p.sex,
        access=p.access,
        birth=map_cdate(fd, p.birth),
        birth_place=fs(p.birth_place),
        birth_note=fs(p.birth_note),
        birth_src=fs(p.birth_src),
        baptism=map_cdate(fd, p.baptism),
        baptism_place=fs(p.baptism_place),
        baptism_note=fs(p.baptism_note),
        baptism_src=fs(p.baptism_src),
        death=map_death(fd, p.death),
        death_place=fs(p.death_place),
        death_note=fs(p.death_note),
        death_src=fs(p.death_src),
        burial=map_burial(fd, p.burial),
        burial_place=fs(p.burial_place),
        burial_note=fs(p.burial_note),
        burial_src=fs(p.burial_src),
        pevents=[map_pers_event(fp, fs, pe, fd) for pe in p.pevents],
        notes=fs(p.notes),
        psources=fs(p.psources),
        key_index=p.key_index
    )


def map_ascend_f(ff: Callable[[T], U], a: GenAscend[T]) -> GenAscend[U]:
    return GenAscend[U](
        parents=ff(a.parents) if a.parents is not None else None,
        consang=a.consang
    )


def map_union_f(ff: Callable[[T], U], u: GenUnion[T]) -> GenUnion[U]:
    return GenUnion[U](family=[ff(f) for f in u.family])


def map_divorce(fd: Callable[[Date], Date], divorce: Divorce) -> Divorce:
    if isinstance(divorce, (NotDivorced, NotSeparated, SeparatedOld)):
        return divorce
    elif isinstance(divorce, DivorceWithDate):
        return DivorceWithDate(date=map_cdate(fd, divorce.date))
    elif isinstance(divorce, Separated):
        return Separated(date=map_cdate(fd, divorce.date))
    return divorce


def map_family_ps(
    fp: Callable[[T], X],
    ff: Callable[[U], Y],
    fs: Callable[[V], W],
    fam: GenFamily[T, U, V],
    fd: Optional[Callable[[Date], Date]] = None
) -> GenFamily[X, Y, W]:
    if fd is None:
        fd = identity

    return GenFamily[X, Y, W](
        marriage=map_cdate(fd, fam.marriage),
        marriage_place=fs(fam.marriage_place),
        marriage_note=fs(fam.marriage_note),
        marriage_src=fs(fam.marriage_src),
        witnesses=[fp(w) for w in fam.witnesses],
        relation=fam.relation,
        divorce=map_divorce(fd, fam.divorce),
        fevents=[map_fam_event(fp, fs, fe, fd) for fe in fam.fevents],
        comment=fs(fam.comment),
        origin_file=fs(fam.origin_file),
        fsources=fs(fam.fsources),
        fam_index=ff(fam.fam_index)
    )


def parent(multi: bool, parent_arr: List[T]) -> Couple:
    from lib.adef import parent as adef_parent, multi_parent
    if not multi:
        return adef_parent(parent_arr)
    else:
        return multi_parent(parent_arr)


def map_couple_p(multi_parents: bool, fp: Callable[[T], U], cpl: Couple) -> Couple:
    arr = parent_array(cpl)
    mapped_arr = [fp(p) for p in arr]
    return parent(multi_parents, mapped_arr)


def map_descend_p(fp: Callable[[T], U], des: GenDescend[T]) -> GenDescend[U]:
    return GenDescend[U](children=[fp(c) for c in des.children])


def eq_lists(eq: Callable[[T, U], bool], l1: List[T], l2: List[U]) -> bool:
    if len(l1) != len(l2):
        return False
    for x1, x2 in zip(l1, l2):
        if not eq(x1, x2):
            return False
    return True


def eq_title_names(eq: Callable[[T, U], bool], tn1: GenTitleName[T], tn2: GenTitleName[U]) -> bool:
    if isinstance(tn1, Tname) and isinstance(tn2, Tname):
        return eq(tn1.name, tn2.name)
    elif isinstance(tn1, Tmain) and isinstance(tn2, Tmain):
        return True
    elif isinstance(tn1, Tnone) and isinstance(tn2, Tnone):
        return True
    return False


def eq_titles(eq: Callable[[T, U], bool], t1: GenTitle[T], t2: GenTitle[U]) -> bool:
    return (eq_title_names(eq, t1.t_name, t2.t_name) and
            eq(t1.t_ident, t2.t_ident) and
            eq(t1.t_place, t2.t_place) and
            t1.t_date_start == t2.t_date_start and
            t1.t_date_end == t2.t_date_end and
            t1.t_nth == t2.t_nth)


def gen_person_misc_names(
    sou: Callable[[T], str],
    empty_string: T,
    quest_string: T,
    first_name: T,
    surname: T,
    public_name: T,
    qualifiers: List[T],
    aliases: List[T],
    first_names_aliases: List[T],
    surnames_aliases: List[T],
    titles: List[GenTitle[T]],
    husbands: List[Tuple[T, List[T]]],
    father_titles_places: List[GenTitle[T]]
) -> List[str]:
    from lib.mutil import surnames_pieces
    from lib.name import concat

    def nominative(s: str) -> str:
        idx = s.rfind(':')
        if idx != -1:
            parts = s[idx+1:].split('.')
            return parts[0] if parts else s
        return s

    if first_name == quest_string or surname == quest_string:
        return []

    s_first_name = nominative(sou(first_name))
    s_surname = nominative(sou(surname))

    s_titles_names = []
    for t in titles:
        if isinstance(t.t_name, Tname):
            s_titles_names.append(sou(t.t_name.name))

    if public_name == empty_string:
        s_public_names = s_titles_names
    else:
        s_public_names = [sou(public_name)] + s_titles_names

    s_first_names = [s_first_name] + [sou(fn) for fn in first_names_aliases]

    s_surnames = [s_surname]
    for sn in surnames_aliases:
        s_surnames.append(sou(sn))
    for q in qualifiers:
        s_surnames.append(sou(q))
    for piece in surnames_pieces(s_surname):
        s_surnames.append(piece)

    for husband_surname, husband_surnames_aliases in husbands:
        if husband_surname == quest_string:
            for hsn in husband_surnames_aliases:
                s_surnames.append(sou(hsn))
        else:
            s_husband_surname = nominative(sou(husband_surname))
            s_surnames.append(s_husband_surname)
            for hsn in husband_surnames_aliases:
                s_surnames.append(sou(hsn))
            for piece in surnames_pieces(s_husband_surname):
                s_surnames.append(piece)

    s_list = list(s_public_names)

    for f in s_first_names:
        for s in s_surnames:
            s_list.append(concat(f, s))

    for t in titles:
        s = t.t_place
        if s != empty_string:
            s_str = sou(s)
            s_first_names_extended = list(s_first_names)
            if isinstance(t.t_name, Tname):
                s_first_names_extended.append(sou(t.t_name.name))
            elif public_name != empty_string:
                s_first_names_extended.append(sou(public_name))

            for f in s_first_names_extended:
                s_list.append(concat(f, s_str))

    if father_titles_places:
        for t in father_titles_places:
            s = t.t_place
            if s != empty_string:
                s_str = sou(s)
                for f in s_first_names:
                    s_list.append(concat(f, s_str))

    for alias in aliases:
        s_list.append(sou(alias))

    return s_list
