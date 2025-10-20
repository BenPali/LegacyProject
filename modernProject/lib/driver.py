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
        return len(base.data.persons.arr)
    return 0


def nb_of_real_persons(base) -> int:
    if hasattr(base, 'func') and hasattr(base.func, 'nb_of_real_persons'):
        return base.func.nb_of_real_persons()
    return 0


def nb_of_families(base) -> int:
    if hasattr(base, 'data') and hasattr(base.data, 'families'):
        return len(base.data.families.arr)
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
