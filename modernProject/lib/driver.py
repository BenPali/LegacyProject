from typing import Optional, List, Callable, Any, Tuple
from dataclasses import dataclass
from lib import dutil
from lib.gwdef import GenPerson, GenFamily, GenAscend, GenUnion, GenCouple, GenDescend


istr = int
ifam = int
iper = int


class Istr:
    EMPTY = 0
    QUEST = 1

    @staticmethod
    def dummy() -> istr:
        return -1

    @staticmethod
    def is_dummy(i: istr) -> bool:
        return i == -1

    @staticmethod
    def hash_func(i: istr) -> int:
        return i

    @staticmethod
    def equal(i1: istr, i2: istr) -> bool:
        return i1 == i2

    @staticmethod
    def compare(i1: istr, i2: istr) -> int:
        if i1 < i2:
            return -1
        elif i1 > i2:
            return 1
        return 0

    @staticmethod
    def to_string(i: istr) -> str:
        return str(i)

    @staticmethod
    def of_string(s: str) -> istr:
        return int(s)

    @staticmethod
    def is_empty(i: istr) -> bool:
        return i == 0

    @staticmethod
    def is_quest(i: istr) -> bool:
        return i == 1


class Ifam:
    @staticmethod
    def dummy() -> ifam:
        return -1

    @staticmethod
    def is_dummy(i: ifam) -> bool:
        return i == -1

    @staticmethod
    def hash_func(i: ifam) -> int:
        return i

    @staticmethod
    def equal(i1: ifam, i2: ifam) -> bool:
        return i1 == i2

    @staticmethod
    def compare(i1: ifam, i2: ifam) -> int:
        if i1 < i2:
            return -1
        elif i1 > i2:
            return 1
        return 0

    @staticmethod
    def to_string(i: ifam) -> str:
        return str(i)

    @staticmethod
    def of_string(s: str) -> ifam:
        return int(s)


class Iper:
    @staticmethod
    def dummy() -> iper:
        return -1

    @staticmethod
    def is_dummy(i: iper) -> bool:
        return i == -1

    @staticmethod
    def hash_func(i: iper) -> int:
        return i

    @staticmethod
    def equal(i1: iper, i2: iper) -> bool:
        return i1 == i2

    @staticmethod
    def compare(i1: iper, i2: iper) -> int:
        if i1 < i2:
            return -1
        elif i1 > i2:
            return 1
        return 0

    @staticmethod
    def to_string(i: iper) -> str:
        return str(i)

    @staticmethod
    def of_string(s: str) -> iper:
        return int(s)


@dataclass
class Person:
    base: Any
    index: iper
    gen_person: Optional[GenPerson] = None
    gen_ascend: Optional[GenAscend] = None
    gen_union: Optional[GenUnion] = None

    def _ensure_loaded(self):
        if self.gen_person is None:
            persons_get = self.base.data.persons.get
            ascends_get = self.base.data.ascends.get
            unions_get = self.base.data.unions.get
            strings_get = self.base.data.strings.get

            dsk_person = persons_get(self.index)
            dsk_ascend = ascends_get(self.index)
            dsk_union = unions_get(self.index)

            self.gen_person = dutil.person_to_gen_person(dsk_person, strings_get, self.index)
            self.gen_ascend = dutil.ascend_to_gen_ascend(dsk_ascend)
            self.gen_union = dutil.union_to_gen_union(dsk_union)


@dataclass
class Family:
    base: Any
    index: ifam
    gen_family: Optional[GenFamily] = None
    gen_couple: Optional[GenCouple] = None
    gen_descend: Optional[GenDescend] = None

    def _ensure_loaded(self):
        if self.gen_family is None:
            families_get = self.base.data.families.get
            couples_get = self.base.data.couples.get
            descends_get = self.base.data.descends.get
            strings_get = self.base.data.strings.get

            dsk_family = families_get(self.index)
            dsk_couple = couples_get(self.index)
            dsk_descend = descends_get(self.index)

            self.gen_family = dutil.family_to_gen_family(dsk_family, strings_get, self.index)
            self.gen_couple = dutil.couple_to_gen_couple(dsk_couple)
            self.gen_descend = dutil.descend_to_gen_descend(dsk_descend)


def poi(base, i: iper) -> Person:
    return Person(base=base, index=i)


def foi(base, i: ifam) -> Family:
    return Family(base=base, index=i)


def sou(base, i: istr) -> str:
    if hasattr(base, 'data') and hasattr(base.data, 'strings'):
        return base.data.strings.get(i)
    return ""


def bname(base) -> str:
    import os
    if hasattr(base, 'data') and hasattr(base.data, 'bdir'):
        return os.path.splitext(os.path.basename(base.data.bdir))[0]
    return ""


def nb_of_persons(base) -> int:
    if hasattr(base, 'data') and hasattr(base.data, 'persons'):
        return base.data.persons.len
    return 0


def nb_of_real_persons(base) -> int:
    if hasattr(base, 'func') and hasattr(base.func, 'nb_of_real_persons'):
        return base.func.nb_of_real_persons()
    return 0


def nb_of_families(base) -> int:
    if hasattr(base, 'data') and hasattr(base.data, 'families'):
        return base.data.families.len
    return 0


def iper_exists(base, i: iper) -> bool:
    if hasattr(base, 'func') and hasattr(base.func, 'iper_exists'):
        return base.func.iper_exists(i)
    return 0 <= i < nb_of_persons(base)


def ifam_exists(base, i: ifam) -> bool:
    if hasattr(base, 'func') and hasattr(base.func, 'ifam_exists'):
        return base.func.ifam_exists(i)
    return 0 <= i < nb_of_families(base)


def get_iper(person: Person) -> iper:
    return person.index


def get_first_name(person: Person) -> istr:
    person._ensure_loaded()
    return person.gen_person.first_name


def get_surname(person: Person) -> istr:
    person._ensure_loaded()
    return person.gen_person.surname


def get_occ(person: Person) -> int:
    person._ensure_loaded()
    return person.gen_person.occ


def get_image(person: Person) -> istr:
    person._ensure_loaded()
    return person.gen_person.image


def get_public_name(person: Person) -> istr:
    person._ensure_loaded()
    return person.gen_person.public_name


def get_qualifiers(person: Person) -> List[istr]:
    person._ensure_loaded()
    return person.gen_person.qualifiers


def get_aliases(person: Person) -> List[istr]:
    person._ensure_loaded()
    return person.gen_person.aliases


def get_first_names_aliases(person: Person) -> List[istr]:
    person._ensure_loaded()
    return person.gen_person.first_names_aliases


def get_surnames_aliases(person: Person) -> List[istr]:
    person._ensure_loaded()
    return person.gen_person.surnames_aliases


def get_titles(person: Person) -> List[Any]:
    person._ensure_loaded()
    return person.gen_person.titles


def get_related(person: Person) -> List[iper]:
    person._ensure_loaded()
    return person.gen_person.related


def get_rparents(person: Person) -> List[Any]:
    person._ensure_loaded()
    return person.gen_person.rparents


def get_occupation(person: Person) -> istr:
    person._ensure_loaded()
    return person.gen_person.occupation


def get_sex(person: Person) -> Any:
    person._ensure_loaded()
    return person.gen_person.sex


def get_access(person: Person) -> Any:
    person._ensure_loaded()
    return person.gen_person.access


def get_birth(person: Person) -> Any:
    person._ensure_loaded()
    return person.gen_person.birth


def get_birth_place(person: Person) -> istr:
    person._ensure_loaded()
    return person.gen_person.birth_place


def get_birth_note(person: Person) -> istr:
    person._ensure_loaded()
    return person.gen_person.birth_note


def get_birth_src(person: Person) -> istr:
    person._ensure_loaded()
    return person.gen_person.birth_src


def get_baptism(person: Person) -> Any:
    person._ensure_loaded()
    return person.gen_person.baptism


def get_baptism_place(person: Person) -> istr:
    person._ensure_loaded()
    return person.gen_person.baptism_place


def get_baptism_note(person: Person) -> istr:
    person._ensure_loaded()
    return person.gen_person.baptism_note


def get_baptism_src(person: Person) -> istr:
    person._ensure_loaded()
    return person.gen_person.baptism_src


def get_death(person: Person) -> Any:
    person._ensure_loaded()
    return person.gen_person.death


def get_death_place(person: Person) -> istr:
    person._ensure_loaded()
    return person.gen_person.death_place


def get_death_note(person: Person) -> istr:
    person._ensure_loaded()
    return person.gen_person.death_note


def get_death_src(person: Person) -> istr:
    person._ensure_loaded()
    return person.gen_person.death_src


def get_burial(person: Person) -> Any:
    person._ensure_loaded()
    return person.gen_person.burial


def get_burial_place(person: Person) -> istr:
    person._ensure_loaded()
    return person.gen_person.burial_place


def get_burial_note(person: Person) -> istr:
    person._ensure_loaded()
    return person.gen_person.burial_note


def get_burial_src(person: Person) -> istr:
    person._ensure_loaded()
    return person.gen_person.burial_src


def get_pevents(person: Person) -> List[Any]:
    person._ensure_loaded()
    return person.gen_person.pevents


def get_notes(person: Person) -> istr:
    person._ensure_loaded()
    return person.gen_person.notes


def get_psources(person: Person) -> istr:
    person._ensure_loaded()
    return person.gen_person.psources


def get_consang(person: Person) -> Any:
    person._ensure_loaded()
    return person.gen_ascend.consang


def get_parents(person: Person) -> Optional[ifam]:
    person._ensure_loaded()
    return person.gen_ascend.parents


def get_family(person: Person) -> List[ifam]:
    person._ensure_loaded()
    return person.gen_union.family


def get_ifam(family: Family) -> ifam:
    return family.index


def get_father(family: Family) -> iper:
    family._ensure_loaded()
    return family.gen_couple.father


def get_mother(family: Family) -> iper:
    family._ensure_loaded()
    return family.gen_couple.mother


def get_parent_array(family: Family) -> Tuple[iper, iper]:
    family._ensure_loaded()
    return (family.gen_couple.father, family.gen_couple.mother)


def get_children(family: Family) -> List[iper]:
    family._ensure_loaded()
    return family.gen_descend.children


def get_marriage(family: Family) -> Any:
    family._ensure_loaded()
    return family.gen_family.marriage


def get_marriage_place(family: Family) -> istr:
    family._ensure_loaded()
    return family.gen_family.marriage_place


def get_marriage_note(family: Family) -> istr:
    family._ensure_loaded()
    return family.gen_family.marriage_note


def get_marriage_src(family: Family) -> istr:
    family._ensure_loaded()
    return family.gen_family.marriage_src


def get_divorce(family: Family) -> Any:
    family._ensure_loaded()
    return family.gen_family.divorce


def get_witnesses(family: Family) -> List[iper]:
    family._ensure_loaded()
    return family.gen_family.witnesses


def get_relation(family: Family) -> Any:
    family._ensure_loaded()
    return family.gen_family.relation


def get_fevents(family: Family) -> List[Any]:
    family._ensure_loaded()
    return family.gen_family.fevents


def get_comment(family: Family) -> istr:
    family._ensure_loaded()
    return family.gen_family.comment


def get_fsources(family: Family) -> istr:
    family._ensure_loaded()
    return family.gen_family.fsources


def get_origin_file(family: Family) -> istr:
    family._ensure_loaded()
    return family.gen_family.origin_file


def patch_person(base, ip: iper, p: GenPerson):
    if hasattr(base, 'func') and hasattr(base.func, 'patch_person'):
        base.func.patch_person(ip, p)


def patch_ascend(base, ip: iper, a: GenAscend):
    if hasattr(base, 'func') and hasattr(base.func, 'patch_ascend'):
        base.func.patch_ascend(ip, a)


def patch_union(base, ip: iper, u: GenUnion):
    if hasattr(base, 'func') and hasattr(base.func, 'patch_union'):
        base.func.patch_union(ip, u)


def patch_family(base, ifam: ifam, f: GenFamily):
    if hasattr(base, 'func') and hasattr(base.func, 'patch_family'):
        base.func.patch_family(ifam, f)


def patch_couple(base, ifam: ifam, c: GenCouple):
    if hasattr(base, 'func') and hasattr(base.func, 'patch_couple'):
        base.func.patch_couple(ifam, c)


def patch_descend(base, ifam: ifam, d: GenDescend):
    if hasattr(base, 'func') and hasattr(base.func, 'patch_descend'):
        base.func.patch_descend(ifam, d)


insert_person = patch_person
insert_ascend = patch_ascend
insert_union = patch_union
insert_family = patch_family
insert_couple = patch_couple
insert_descend = patch_descend


def delete_person(base, ip: iper):
    from lib.gwdef import Sex, Access, DontKnowIfDead, UnknownBurial
    from lib.date import cdate_None
    empty_person = GenPerson(
        first_name=Istr.QUEST,
        surname=Istr.QUEST,
        occ=0,
        image=Istr.EMPTY,
        first_names_aliases=[],
        surnames_aliases=[],
        public_name=Istr.EMPTY,
        qualifiers=[],
        titles=[],
        rparents=[],
        related=[],
        aliases=[],
        occupation=Istr.EMPTY,
        sex=Sex.NEUTER,
        access=Access.PRIVATE,
        birth=cdate_None,
        birth_place=Istr.EMPTY,
        birth_note=Istr.EMPTY,
        birth_src=Istr.EMPTY,
        baptism=cdate_None,
        baptism_place=Istr.EMPTY,
        baptism_note=Istr.EMPTY,
        baptism_src=Istr.EMPTY,
        death=DontKnowIfDead(),
        death_place=Istr.EMPTY,
        death_note=Istr.EMPTY,
        death_src=Istr.EMPTY,
        burial=UnknownBurial(),
        burial_place=Istr.EMPTY,
        burial_note=Istr.EMPTY,
        burial_src=Istr.EMPTY,
        pevents=[],
        notes=Istr.EMPTY,
        psources=Istr.EMPTY,
        key_index=ip
    )
    patch_person(base, ip, empty_person)


def delete_ascend(base, ip: iper):
    from lib.adef import NO_CONSANG
    empty_ascend = GenAscend(parents=None, consang=NO_CONSANG)
    patch_ascend(base, ip, empty_ascend)


def delete_union(base, ip: iper):
    empty_union = GenUnion(family=[])
    patch_union(base, ip, empty_union)


def delete_family(base, ifam_val: ifam):
    from lib.gwdef import RelationKind, NotDivorced
    from lib.date import cdate_None
    empty_family = GenFamily(
        marriage=cdate_None,
        marriage_place=Istr.EMPTY,
        marriage_note=Istr.EMPTY,
        marriage_src=Istr.EMPTY,
        relation=RelationKind.MARRIED,
        divorce=NotDivorced(),
        fevents=[],
        witnesses=[],
        comment=Istr.EMPTY,
        origin_file=Istr.EMPTY,
        fsources=Istr.EMPTY,
        fam_index=Ifam.dummy()
    )
    patch_family(base, ifam_val, empty_family)


def delete_couple(base, ifam_val: ifam):
    empty_couple = GenCouple(father=Iper.dummy(), mother=Iper.dummy())
    patch_couple(base, ifam_val, empty_couple)


def delete_descend(base, ifam_val: ifam):
    empty_descend = GenDescend(children=[])
    patch_descend(base, ifam_val, empty_descend)


def insert_string(base, s: str) -> istr:
    if hasattr(base, 'func') and hasattr(base.func, 'insert_string'):
        return base.func.insert_string(s)
    return Istr.EMPTY


def commit_patches(base):
    if hasattr(base, 'func') and hasattr(base.func, 'commit_patches'):
        base.func.commit_patches()


def commit_notes(base, fname: str, content: str):
    if hasattr(base, 'func') and hasattr(base.func, 'commit_notes'):
        base.func.commit_notes(fname, content)


def commit_wiznotes(base, fname: str, content: str):
    if hasattr(base, 'func') and hasattr(base.func, 'commit_wiznotes'):
        base.func.commit_wiznotes(fname, content)


def person_of_key(base, first: str, surname: str, occ: int) -> Optional[iper]:
    if hasattr(base, 'func') and hasattr(base.func, 'person_of_key'):
        return base.func.person_of_key(first, surname, occ)
    return None


def persons_of_name(base, name: str):
    if hasattr(base, 'func') and hasattr(base.func, 'persons_of_name'):
        return base.func.persons_of_name(name)
    return []


def persons_of_first_name(base):
    if hasattr(base, 'func') and hasattr(base.func, 'persons_of_first_name'):
        return base.func.persons_of_first_name()
    return None


def persons_of_surname(base):
    if hasattr(base, 'func') and hasattr(base.func, 'persons_of_surname'):
        return base.func.persons_of_surname()
    return None


def ipers(base):
    from lib.collection import Collection
    length = nb_of_persons(base)
    return Collection(length=length, get=lambda i: i if 0 <= i < length else None)


def persons(base):
    from lib.collection import Collection
    length = nb_of_persons(base)
    return Collection(length=length, get=lambda i: poi(base, i) if 0 <= i < length else None)


def ifams(base, select: Optional[Callable[[ifam], bool]] = None):
    from lib.collection import Collection
    length = nb_of_families(base)
    if select is None:
        select = lambda _: True
    def get_ifam_at(i: int) -> Optional[ifam]:
        if 0 <= i < length and select(i):
            fam = foi(base, i)
            fam_idx = fam.index
            if fam_idx != Ifam.dummy():
                return i
        return None
    return Collection(length=length, get=get_ifam_at)


def families(base, select: Optional[Callable[[Family], bool]] = None):
    from lib.collection import Collection
    length = nb_of_families(base)
    if select is None:
        select = lambda _: True
    def get_family_at(i: int) -> Optional[Family]:
        if 0 <= i < length:
            fam = foi(base, i)
            if fam.index != Ifam.dummy() and select(fam):
                return fam
        return None
    return Collection(length=length, get=get_family_at)


def iper_marker(collection, default_value: Any):
    from lib.collection import make_marker
    return make_marker(key_fn=lambda i: i, c=collection, initial=default_value)


def ifam_marker(collection, default_value: Any):
    from lib.collection import make_marker
    return make_marker(key_fn=lambda i: i, c=collection, initial=default_value)


def load_ascends_array(base):
    if hasattr(base, 'data') and hasattr(base.data, 'ascends') and hasattr(base.data.ascends, 'load_array'):
        base.data.ascends.load_array()


def load_unions_array(base):
    if hasattr(base, 'data') and hasattr(base.data, 'unions') and hasattr(base.data.unions, 'load_array'):
        base.data.unions.load_array()


def load_couples_array(base):
    if hasattr(base, 'data') and hasattr(base.data, 'couples') and hasattr(base.data.couples, 'load_array'):
        base.data.couples.load_array()


def load_descends_array(base):
    if hasattr(base, 'data') and hasattr(base.data, 'descends') and hasattr(base.data.descends, 'load_array'):
        base.data.descends.load_array()


def load_strings_array(base):
    if hasattr(base, 'data') and hasattr(base.data, 'strings') and hasattr(base.data.strings, 'load_array'):
        base.data.strings.load_array()


def load_persons_array(base):
    if hasattr(base, 'data') and hasattr(base.data, 'persons') and hasattr(base.data.persons, 'load_array'):
        base.data.persons.load_array()


def load_families_array(base):
    if hasattr(base, 'data') and hasattr(base.data, 'families') and hasattr(base.data.families, 'load_array'):
        base.data.families.load_array()


def clear_ascends_array(base):
    if hasattr(base, 'data') and hasattr(base.data, 'ascends') and hasattr(base.data.ascends, 'clear_array'):
        base.data.ascends.clear_array()


def clear_unions_array(base):
    if hasattr(base, 'data') and hasattr(base.data, 'unions') and hasattr(base.data.unions, 'clear_array'):
        base.data.unions.clear_array()


def clear_couples_array(base):
    if hasattr(base, 'data') and hasattr(base.data, 'couples') and hasattr(base.data.couples, 'clear_array'):
        base.data.couples.clear_array()


def clear_descends_array(base):
    if hasattr(base, 'data') and hasattr(base.data, 'descends') and hasattr(base.data.descends, 'clear_array'):
        base.data.descends.clear_array()


def clear_strings_array(base):
    if hasattr(base, 'data') and hasattr(base.data, 'strings') and hasattr(base.data.strings, 'clear_array'):
        base.data.strings.clear_array()


def clear_persons_array(base):
    if hasattr(base, 'data') and hasattr(base.data, 'persons') and hasattr(base.data.persons, 'clear_array'):
        base.data.persons.clear_array()


def clear_families_array(base):
    if hasattr(base, 'data') and hasattr(base.data, 'families') and hasattr(base.data.families, 'clear_array'):
        base.data.families.clear_array()


def gen_person_of_person(person: Person) -> GenPerson:
    person._ensure_loaded()
    return person.gen_person


def gen_ascend_of_person(person: Person) -> GenAscend:
    person._ensure_loaded()
    return person.gen_ascend


def gen_union_of_person(person: Person) -> GenUnion:
    person._ensure_loaded()
    return person.gen_union


def new_iper(base) -> iper:
    return nb_of_persons(base)


def new_ifam(base) -> ifam:
    return nb_of_families(base)


def gen_couple_of_family(family: Family) -> GenCouple:
    family._ensure_loaded()
    return family.gen_couple


def gen_descend_of_family(family: Family) -> GenDescend:
    family._ensure_loaded()
    return family.gen_descend


def gen_family_of_family(family: Family) -> GenFamily:
    family._ensure_loaded()
    return family.gen_family


def person_of_gen_person(base, gen_data: Tuple[GenPerson, GenAscend, GenUnion]) -> Person:
    gen_person, gen_ascend, gen_union = gen_data
    person = Person(base=base, index=gen_person.key_index)
    person.gen_person = gen_person
    person.gen_ascend = gen_ascend
    person.gen_union = gen_union
    return person


def family_of_gen_family(base, gen_data: Tuple[GenFamily, GenCouple, GenDescend]) -> Family:
    gen_family, gen_couple, gen_descend = gen_data
    family = Family(base=base, index=gen_family.fam_index)
    family.gen_family = gen_family
    family.gen_couple = gen_couple
    family.gen_descend = gen_descend
    return family


def no_person(ip: iper) -> GenPerson:
    from lib.gwdef import Sex, Access, DontKnowIfDead, UnknownBurial
    from lib.date import cdate_None
    return GenPerson(
        first_name=Istr.QUEST,
        surname=Istr.QUEST,
        occ=0,
        image=Istr.EMPTY,
        first_names_aliases=[],
        surnames_aliases=[],
        public_name=Istr.EMPTY,
        qualifiers=[],
        titles=[],
        rparents=[],
        related=[],
        aliases=[],
        occupation=Istr.EMPTY,
        sex=Sex.NEUTER,
        access=Access.PRIVATE,
        birth=cdate_None,
        birth_place=Istr.EMPTY,
        birth_note=Istr.EMPTY,
        birth_src=Istr.EMPTY,
        baptism=cdate_None,
        baptism_place=Istr.EMPTY,
        baptism_note=Istr.EMPTY,
        baptism_src=Istr.EMPTY,
        death=DontKnowIfDead(),
        death_place=Istr.EMPTY,
        death_note=Istr.EMPTY,
        death_src=Istr.EMPTY,
        burial=UnknownBurial(),
        burial_place=Istr.EMPTY,
        burial_note=Istr.EMPTY,
        burial_src=Istr.EMPTY,
        pevents=[],
        notes=Istr.EMPTY,
        psources=Istr.EMPTY,
        key_index=ip
    )


def no_ascend() -> GenAscend:
    from lib.adef import NO_CONSANG
    return GenAscend(parents=None, consang=NO_CONSANG)


def no_union() -> GenUnion:
    return GenUnion(family=[])


def no_family(ifam_val: ifam) -> GenFamily:
    from lib.gwdef import RelationKind, NotDivorced
    from lib.date import cdate_None
    return GenFamily(
        marriage=cdate_None,
        marriage_place=Istr.EMPTY,
        marriage_note=Istr.EMPTY,
        marriage_src=Istr.EMPTY,
        relation=RelationKind.MARRIED,
        divorce=NotDivorced(),
        fevents=[],
        witnesses=[],
        comment=Istr.EMPTY,
        origin_file=Istr.EMPTY,
        fsources=Istr.EMPTY,
        fam_index=ifam_val
    )


def no_descend() -> GenDescend:
    return GenDescend(children=[])


def no_couple() -> GenCouple:
    return GenCouple(father=Iper.dummy(), mother=Iper.dummy())


def p_first_name(base, person: Person) -> str:
    return sou(base, get_first_name(person))


def p_surname(base, person: Person) -> str:
    return sou(base, get_surname(person))


def person_misc_names(base, person: Person, nobtit: Callable[[Person], List[Any]]) -> List[str]:
    result = []

    first = p_first_name(base, person)
    surname = p_surname(base, person)

    result.append(first + " " + surname)

    if get_public_name(person) != Istr.EMPTY:
        public = sou(base, get_public_name(person))
        result.append(public + " " + surname)

    for alias in get_aliases(person):
        if alias != Istr.EMPTY:
            result.append(sou(base, alias))

    for qualifier in get_qualifiers(person):
        if qualifier != Istr.EMPTY:
            result.append(first + " " + sou(base, qualifier) + " " + surname)

    for fn_alias in get_first_names_aliases(person):
        if fn_alias != Istr.EMPTY:
            result.append(sou(base, fn_alias) + " " + surname)

    for sn_alias in get_surnames_aliases(person):
        if sn_alias != Istr.EMPTY:
            result.append(first + " " + sou(base, sn_alias))

    titles = nobtit(person)
    for title in titles:
        if hasattr(title, 'name') and title.name != Istr.EMPTY:
            title_name = sou(base, title.name)
            result.append(title_name)
        if hasattr(title, 'place') and title.place != Istr.EMPTY:
            place = sou(base, title.place)
            result.append(first + " " + surname + " " + place)

    return result


def insert_person_with_union_and_ascendants(base, p: GenPerson, a: GenAscend, u: GenUnion) -> iper:
    ip = new_iper(base)
    new_p = GenPerson(
        first_name=p.first_name,
        surname=p.surname,
        occ=p.occ,
        image=p.image,
        first_names_aliases=p.first_names_aliases,
        surnames_aliases=p.surnames_aliases,
        public_name=p.public_name,
        qualifiers=p.qualifiers,
        titles=p.titles,
        rparents=p.rparents,
        related=p.related,
        aliases=p.aliases,
        occupation=p.occupation,
        sex=p.sex,
        access=p.access,
        birth=p.birth,
        birth_place=p.birth_place,
        birth_note=p.birth_note,
        birth_src=p.birth_src,
        baptism=p.baptism,
        baptism_place=p.baptism_place,
        baptism_note=p.baptism_note,
        baptism_src=p.baptism_src,
        death=p.death,
        death_place=p.death_place,
        death_note=p.death_note,
        death_src=p.death_src,
        burial=p.burial,
        burial_place=p.burial_place,
        burial_note=p.burial_note,
        burial_src=p.burial_src,
        pevents=p.pevents,
        notes=p.notes,
        psources=p.psources,
        key_index=ip
    )
    patch_person(base, ip, new_p)
    patch_ascend(base, ip, a)
    patch_union(base, ip, u)
    return ip


def insert_family_with_couple_and_descendants(base, f: GenFamily, c: GenCouple, d: GenDescend) -> ifam:
    ifam_val = new_ifam(base)
    new_f = GenFamily(
        marriage=f.marriage,
        marriage_place=f.marriage_place,
        marriage_note=f.marriage_note,
        marriage_src=f.marriage_src,
        relation=f.relation,
        divorce=f.divorce,
        fevents=f.fevents,
        witnesses=f.witnesses,
        comment=f.comment,
        origin_file=f.origin_file,
        fsources=f.fsources,
        fam_index=ifam_val
    )
    patch_family(base, ifam_val, new_f)
    patch_couple(base, ifam_val, c)
    patch_descend(base, ifam_val, d)
    return ifam_val


def delete_person_rec(base, ip: iper):
    person = poi(base, ip)
    person._ensure_loaded()

    families = get_family(person)
    for ifam_val in families:
        family = foi(base, ifam_val)
        family._ensure_loaded()
        if get_father(family) == ip or get_mother(family) == ip:
            delete_family_rec(base, ifam_val)

    parent_fam = get_parents(person)
    if parent_fam is not None:
        delete_descend(base, parent_fam)

    delete_person(base, ip)
    delete_ascend(base, ip)
    delete_union(base, ip)


def delete_family_rec(base, ifam_val: ifam):
    family = foi(base, ifam_val)
    family._ensure_loaded()

    father_ip = get_father(family)
    mother_ip = get_mother(family)

    if not Iper.is_dummy(father_ip):
        father = poi(base, father_ip)
        father._ensure_loaded()
        union = get_family(father)
        new_union = GenUnion(family=[f for f in union if f != ifam_val])
        patch_union(base, father_ip, new_union)

    if not Iper.is_dummy(mother_ip):
        mother = poi(base, mother_ip)
        mother._ensure_loaded()
        union = get_family(mother)
        new_union = GenUnion(family=[f for f in union if f != ifam_val])
        patch_union(base, mother_ip, new_union)

    children = get_children(family)
    for child_ip in children:
        child = poi(base, child_ip)
        child._ensure_loaded()
        if get_parents(child) == ifam_val:
            delete_ascend(base, child_ip)

    delete_family(base, ifam_val)
    delete_couple(base, ifam_val)
    delete_descend(base, ifam_val)


def empty_person(base, ip: iper) -> Person:
    return Person(base=base, index=ip)


def empty_family(base, ifam_val: ifam) -> Family:
    return Family(base=base, index=ifam_val)


def get_separation(family: Family):
    return get_divorce(family)


def children_of_p(base, person: Person) -> List[iper]:
    result = []
    for ifam_val in get_family(person):
        fam = foi(base, ifam_val)
        result.extend(get_children(fam))
    return result


def nobtitles(base, allowed_titles, denied_titles, person: Person) -> List[Any]:
    titles = get_titles(person)
    allowed = allowed_titles.value if hasattr(allowed_titles, 'value') else (allowed_titles if isinstance(allowed_titles, list) else [])
    denied = denied_titles.value if hasattr(denied_titles, 'value') else (denied_titles if isinstance(denied_titles, list) else [])

    if not allowed:
        if not denied:
            return titles
        return [t for t in titles if hasattr(t, 'name') and sou(base, t.name) not in denied]

    result = []
    for title in titles:
        if hasattr(title, 'name'):
            title_name = sou(base, title.name)
            if title_name in allowed and title_name not in denied:
                result.append(title)
    return result


def make(bname: str, particles: List[str], arrays, base_notes, continuation: Callable):
    raise NotImplementedError("make() is not implemented - use database.Database instead")


def load_database(bname: str):
    if hasattr(load_database, '_loaded_bases'):
        if bname in load_database._loaded_bases:
            raise RuntimeError(f"Database {bname} already loaded")
    else:
        load_database._loaded_bases = {}

    from lib import database
    base = database.Database(bname)
    load_database._loaded_bases[bname] = base
    return base


def with_database(bname: str, continuation: Callable):
    if hasattr(load_database, '_loaded_bases') and bname in load_database._loaded_bases:
        return continuation(load_database._loaded_bases[bname])

    from lib import database
    base = database.Database(bname)
    try:
        return continuation(base)
    finally:
        if hasattr(base, 'close'):
            base.close()


def sync(base, scratch: bool = False):
    if hasattr(base, 'func') and hasattr(base.func, 'sync'):
        base.func.sync(scratch)


def spi_find(spi, istr_val: istr) -> List[iper]:
    if hasattr(spi, 'find'):
        return spi.find(istr_val)
    return []


def spi_first(spi, s: str) -> istr:
    if hasattr(spi, 'first'):
        return spi.first(s)
    return Istr.EMPTY


def spi_next(spi, istr_val: istr) -> istr:
    if hasattr(spi, 'next'):
        return spi.next(istr_val)
    return Istr.EMPTY


def base_visible_get(base, fct: Callable[[Person], bool], ip: iper) -> bool:
    if hasattr(base, 'func') and hasattr(base.func, 'base_visible_get'):
        return base.func.base_visible_get(fct, ip)
    return fct(poi(base, ip))


def base_visible_write(base):
    if hasattr(base, 'func') and hasattr(base.func, 'base_visible_write'):
        base.func.base_visible_write()


def base_particles(base):
    if hasattr(base, 'func') and hasattr(base.func, 'base_particles'):
        return base.func.base_particles()
    import re
    return re.compile(r'(?!)')


def base_strings_of_first_name(base, s: str) -> List[istr]:
    if hasattr(base, 'func') and hasattr(base.func, 'base_strings_of_first_name'):
        return base.func.base_strings_of_first_name(s)
    return []


def base_strings_of_surname(base, s: str) -> List[istr]:
    if hasattr(base, 'func') and hasattr(base.func, 'base_strings_of_surname'):
        return base.func.base_strings_of_surname(s)
    return []


def base_notes_read(base, fname: str) -> str:
    if hasattr(base, 'func') and hasattr(base.func, 'base_notes_read'):
        return base.func.base_notes_read(fname)
    return ""


def base_wiznotes_read(base, fname: str) -> str:
    if hasattr(base, 'func') and hasattr(base.func, 'base_wiznotes_read'):
        return base.func.base_wiznotes_read(fname)
    return ""


def base_notes_read_first_line(base, fname: str) -> str:
    content = base_notes_read(base, fname)
    if content:
        return content.split('\n')[0] if '\n' in content else content
    return ""


def base_notes_are_empty(base, fname: str) -> bool:
    return base_notes_read(base, fname) == ""


def base_notes_origin_file(base) -> str:
    if hasattr(base, 'func') and hasattr(base.func, 'base_notes_origin_file'):
        return base.func.base_notes_origin_file()
    return ""


def base_notes_dir(base) -> str:
    if hasattr(base, 'func') and hasattr(base.func, 'base_notes_dir'):
        return base.func.base_notes_dir()
    import os
    if hasattr(base, 'data') and hasattr(base.data, 'bdir'):
        return os.path.join(base.data.bdir, 'notes')
    return ""


def base_wiznotes_dir(base) -> str:
    if hasattr(base, 'func') and hasattr(base.func, 'base_wiznotes_dir'):
        return base.func.base_wiznotes_dir()
    import os
    if hasattr(base, 'data') and hasattr(base.data, 'bdir'):
        return os.path.join(base.data.bdir, 'wiznotes')
    return ""


def read_nldb(base):
    if hasattr(base, 'func') and hasattr(base.func, 'read_nldb'):
        return base.func.read_nldb()
    return {}


def write_nldb(base, nldb):
    if hasattr(base, 'func') and hasattr(base.func, 'write_nldb'):
        base.func.write_nldb(nldb)


def date_of_last_change(base) -> float:
    if hasattr(base, 'func') and hasattr(base.func, 'date_of_last_change'):
        return base.func.date_of_last_change()
    return 0.0
