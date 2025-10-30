from lib.driver import istr, ifam, iper, Istr, Ifam, Iper


def test_type_aliases():
    i: istr = 5
    f: ifam = 10
    p: iper = 15
    assert isinstance(i, int)
    assert isinstance(f, int)
    assert isinstance(p, int)


def test_istr_constants():
    assert Istr.EMPTY == 0
    assert Istr.QUEST == 1


def test_istr_dummy():
    assert Istr.dummy() == -1


def test_istr_is_dummy():
    assert Istr.is_dummy(-1) is True
    assert Istr.is_dummy(0) is False
    assert Istr.is_dummy(1) is False
    assert Istr.is_dummy(100) is False


def test_istr_hash():
    assert Istr.hash_func(0) == 0
    assert Istr.hash_func(1) == 1
    assert Istr.hash_func(42) == 42
    assert Istr.hash_func(-1) == -1


def test_istr_equal():
    assert Istr.equal(0, 0) is True
    assert Istr.equal(1, 1) is True
    assert Istr.equal(42, 42) is True
    assert Istr.equal(0, 1) is False
    assert Istr.equal(42, 43) is False


def test_istr_compare():
    assert Istr.compare(0, 0) == 0
    assert Istr.compare(1, 0) == 1
    assert Istr.compare(0, 1) == -1
    assert Istr.compare(100, 50) == 1
    assert Istr.compare(50, 100) == -1


def test_istr_to_string():
    assert Istr.to_string(0) == "0"
    assert Istr.to_string(1) == "1"
    assert Istr.to_string(42) == "42"
    assert Istr.to_string(-1) == "-1"


def test_istr_of_string():
    assert Istr.of_string("0") == 0
    assert Istr.of_string("1") == 1
    assert Istr.of_string("42") == 42
    assert Istr.of_string("-1") == -1


def test_istr_is_empty():
    assert Istr.is_empty(0) is True
    assert Istr.is_empty(1) is False
    assert Istr.is_empty(42) is False
    assert Istr.is_empty(-1) is False


def test_istr_is_quest():
    assert Istr.is_quest(0) is False
    assert Istr.is_quest(1) is True
    assert Istr.is_quest(42) is False
    assert Istr.is_quest(-1) is False


def test_ifam_dummy():
    assert Ifam.dummy() == -1


def test_ifam_is_dummy():
    assert Ifam.is_dummy(-1) is True
    assert Ifam.is_dummy(0) is False
    assert Ifam.is_dummy(1) is False
    assert Ifam.is_dummy(100) is False


def test_ifam_hash():
    assert Ifam.hash_func(0) == 0
    assert Ifam.hash_func(42) == 42
    assert Ifam.hash_func(-1) == -1


def test_ifam_equal():
    assert Ifam.equal(0, 0) is True
    assert Ifam.equal(42, 42) is True
    assert Ifam.equal(0, 1) is False
    assert Ifam.equal(42, 43) is False


def test_ifam_compare():
    assert Ifam.compare(0, 0) == 0
    assert Ifam.compare(1, 0) == 1
    assert Ifam.compare(0, 1) == -1
    assert Ifam.compare(100, 50) == 1
    assert Ifam.compare(50, 100) == -1


def test_ifam_to_string():
    assert Ifam.to_string(0) == "0"
    assert Ifam.to_string(42) == "42"
    assert Ifam.to_string(-1) == "-1"


def test_ifam_of_string():
    assert Ifam.of_string("0") == 0
    assert Ifam.of_string("42") == 42
    assert Ifam.of_string("-1") == -1


def test_iper_dummy():
    assert Iper.dummy() == -1


def test_iper_is_dummy():
    assert Iper.is_dummy(-1) is True
    assert Iper.is_dummy(0) is False
    assert Iper.is_dummy(1) is False
    assert Iper.is_dummy(100) is False


def test_iper_hash():
    assert Iper.hash_func(0) == 0
    assert Iper.hash_func(42) == 42
    assert Iper.hash_func(-1) == -1


def test_iper_equal():
    assert Iper.equal(0, 0) is True
    assert Iper.equal(42, 42) is True
    assert Iper.equal(0, 1) is False
    assert Iper.equal(42, 43) is False


def test_iper_compare():
    assert Iper.compare(0, 0) == 0
    assert Iper.compare(1, 0) == 1
    assert Iper.compare(0, 1) == -1
    assert Iper.compare(100, 50) == 1
    assert Iper.compare(50, 100) == -1


def test_iper_to_string():
    assert Iper.to_string(0) == "0"
    assert Iper.to_string(42) == "42"
    assert Iper.to_string(-1) == "-1"


def test_iper_of_string():
    assert Iper.of_string("0") == 0
    assert Iper.of_string("42") == 42
    assert Iper.of_string("-1") == -1


def test_poi_and_foi():
    from lib.driver import poi, foi, Person, Family
    from types import SimpleNamespace

    mock_base = SimpleNamespace()
    person = poi(mock_base, 5)
    assert isinstance(person, Person)
    assert person.base == mock_base
    assert person.index == 5

    family = foi(mock_base, 10)
    assert isinstance(family, Family)
    assert family.base == mock_base
    assert family.index == 10


def test_sou():
    from lib.driver import sou
    from types import SimpleNamespace

    mock_strings = SimpleNamespace(get=lambda i: f"string_{i}")
    mock_data = SimpleNamespace(strings=mock_strings)
    mock_base = SimpleNamespace(data=mock_data)

    assert sou(mock_base, 5) == "string_5"
    assert sou(mock_base, 0) == "string_0"


def test_bname():
    from lib.driver import bname
    from types import SimpleNamespace

    mock_data = SimpleNamespace(bdir="/path/to/database.gwb")
    mock_base = SimpleNamespace(data=mock_data)
    assert bname(mock_base) == "database"

    mock_data2 = SimpleNamespace(bdir="/another/path/mybase.gwb")
    mock_base2 = SimpleNamespace(data=mock_data2)
    assert bname(mock_base2) == "mybase"


def test_nb_of_persons():
    from lib.driver import nb_of_persons
    from types import SimpleNamespace

    mock_persons = SimpleNamespace(arr=[None] * 100)
    mock_data = SimpleNamespace(persons=mock_persons)
    mock_base = SimpleNamespace(data=mock_data)
    assert nb_of_persons(mock_base) == 100


def test_nb_of_families():
    from lib.driver import nb_of_families
    from types import SimpleNamespace

    mock_families = SimpleNamespace(arr=[None] * 50)
    mock_data = SimpleNamespace(families=mock_families)
    mock_base = SimpleNamespace(data=mock_data)
    assert nb_of_families(mock_base) == 50


def test_iper_exists():
    from lib.driver import iper_exists
    from types import SimpleNamespace

    mock_persons = SimpleNamespace(arr=[None] * 100)
    mock_data = SimpleNamespace(persons=mock_persons)
    mock_base = SimpleNamespace(data=mock_data)

    assert iper_exists(mock_base, 0) is True
    assert iper_exists(mock_base, 50) is True
    assert iper_exists(mock_base, 99) is True
    assert iper_exists(mock_base, 100) is False
    assert iper_exists(mock_base, -1) is False


def test_ifam_exists():
    from lib.driver import ifam_exists
    from types import SimpleNamespace

    mock_families = SimpleNamespace(arr=[None] * 50)
    mock_data = SimpleNamespace(families=mock_families)
    mock_base = SimpleNamespace(data=mock_data)

    assert ifam_exists(mock_base, 0) is True
    assert ifam_exists(mock_base, 25) is True
    assert ifam_exists(mock_base, 49) is True
    assert ifam_exists(mock_base, 50) is False
    assert ifam_exists(mock_base, -1) is False


def test_person_getters():
    from lib.driver import (
        Person, get_iper, get_first_name, get_surname, get_occ,
        get_image, get_public_name, get_sex, get_access
    )
    from lib.gwdef import GenPerson, GenAscend, GenUnion, Sex, Access
    from lib.date import cdate_None
    from lib.adef import NO_CONSANG
    from types import SimpleNamespace

    gen_person = GenPerson(
        first_name=10,
        surname=20,
        occ=3,
        image=30,
        public_name=40,
        qualifiers=[],
        aliases=[],
        first_names_aliases=[],
        surnames_aliases=[],
        titles=[],
        rparents=[],
        related=[],
        occupation=50,
        sex=Sex.MALE,
        access=Access.PUBLIC,
        birth=cdate_None,
        birth_place=60,
        birth_note=61,
        birth_src=62,
        baptism=cdate_None,
        baptism_place=70,
        baptism_note=71,
        baptism_src=72,
        death=None,
        death_place=80,
        death_note=81,
        death_src=82,
        burial=None,
        burial_place=90,
        burial_note=91,
        burial_src=92,
        pevents=[],
        notes=100,
        psources=110,
        key_index=5
    )

    person = Person(base=None, index=5)
    person.gen_person = gen_person
    person.gen_ascend = GenAscend(parents=None, consang=NO_CONSANG)
    person.gen_union = GenUnion(family=[])

    assert get_iper(person) == 5
    assert get_first_name(person) == 10
    assert get_surname(person) == 20
    assert get_occ(person) == 3
    assert get_image(person) == 30
    assert get_public_name(person) == 40
    assert get_sex(person) == Sex.MALE
    assert get_access(person) == Access.PUBLIC


def test_family_getters():
    from lib.driver import (
        Family, get_ifam, get_father, get_mother, get_parent_array,
        get_children, get_marriage_place
    )
    from lib.gwdef import GenFamily, GenCouple, GenDescend
    from lib.date import cdate_None
    from types import SimpleNamespace

    gen_family = GenFamily(
        marriage=cdate_None,
        marriage_place=100,
        marriage_note=101,
        marriage_src=102,
        relation=None,
        divorce=None,
        fevents=[],
        witnesses=[],
        comment=110,
        origin_file=120,
        fsources=130,
        fam_index=15
    )
    gen_couple = GenCouple(father=10, mother=20)
    gen_descend = GenDescend(children=[30, 31, 32])

    family = Family(base=None, index=15)
    family.gen_family = gen_family
    family.gen_couple = gen_couple
    family.gen_descend = gen_descend

    assert get_ifam(family) == 15
    assert get_father(family) == 10
    assert get_mother(family) == 20
    assert get_parent_array(family) == (10, 20)
    assert get_children(family) == [30, 31, 32]
    assert get_marriage_place(family) == 100


def test_delete_operations():
    from lib.driver import delete_person, delete_ascend, delete_union
    from lib.driver import delete_family, delete_couple, delete_descend
    from types import SimpleNamespace

    patched_calls = []

    def mock_patch(name):
        def patch_func(*args):
            patched_calls.append((name, args))
        return patch_func

    mock_func = SimpleNamespace(
        patch_person=mock_patch('patch_person'),
        patch_ascend=mock_patch('patch_ascend'),
        patch_union=mock_patch('patch_union'),
        patch_family=mock_patch('patch_family'),
        patch_couple=mock_patch('patch_couple'),
        patch_descend=mock_patch('patch_descend')
    )
    mock_base = SimpleNamespace(func=mock_func)

    delete_person(mock_base, 5)
    assert patched_calls[0][0] == 'patch_person'
    assert patched_calls[0][1][0] == 5

    delete_ascend(mock_base, 6)
    assert patched_calls[1][0] == 'patch_ascend'
    assert patched_calls[1][1][0] == 6

    delete_union(mock_base, 7)
    assert patched_calls[2][0] == 'patch_union'
    assert patched_calls[2][1][0] == 7

    delete_family(mock_base, 8)
    assert patched_calls[3][0] == 'patch_family'
    assert patched_calls[3][1][0] == 8

    delete_couple(mock_base, 9)
    assert patched_calls[4][0] == 'patch_couple'
    assert patched_calls[4][1][0] == 9

    delete_descend(mock_base, 10)
    assert patched_calls[5][0] == 'patch_descend'
    assert patched_calls[5][1][0] == 10


def test_insert_string():
    from lib.driver import insert_string
    from types import SimpleNamespace

    mock_func = SimpleNamespace(insert_string=lambda s: 42)
    mock_base = SimpleNamespace(func=mock_func)

    result = insert_string(mock_base, "test")
    assert result == 42


def test_commit_patches():
    from lib.driver import commit_patches
    from types import SimpleNamespace

    committed = []
    mock_func = SimpleNamespace(commit_patches=lambda: committed.append(True))
    mock_base = SimpleNamespace(func=mock_func)

    commit_patches(mock_base)
    assert len(committed) == 1


def test_commit_notes():
    from lib.driver import commit_notes
    from types import SimpleNamespace

    committed = []
    mock_func = SimpleNamespace(commit_notes=lambda f, c: committed.append((f, c)))
    mock_base = SimpleNamespace(func=mock_func)

    commit_notes(mock_base, "test.txt", "content")
    assert len(committed) == 1
    assert committed[0] == ("test.txt", "content")


def test_commit_wiznotes():
    from lib.driver import commit_wiznotes
    from types import SimpleNamespace

    committed = []
    mock_func = SimpleNamespace(commit_wiznotes=lambda f, c: committed.append((f, c)))
    mock_base = SimpleNamespace(func=mock_func)

    commit_wiznotes(mock_base, "wizard.txt", "notes")
    assert len(committed) == 1
    assert committed[0] == ("wizard.txt", "notes")


def test_person_of_key():
    from lib.driver import person_of_key
    from types import SimpleNamespace

    mock_func = SimpleNamespace(person_of_key=lambda f, s, o: 123 if f == "John" else None)
    mock_base = SimpleNamespace(func=mock_func)

    result = person_of_key(mock_base, "John", "Doe", 0)
    assert result == 123

    result = person_of_key(mock_base, "Jane", "Doe", 0)
    assert result is None


def test_ipers():
    from lib.driver import ipers
    from types import SimpleNamespace

    mock_persons = SimpleNamespace(arr=[None] * 5)
    mock_data = SimpleNamespace(persons=mock_persons)
    mock_base = SimpleNamespace(data=mock_data)

    collection = ipers(mock_base)
    assert collection.length == 5
    assert collection.get(0) == 0
    assert collection.get(4) == 4
    assert collection.get(5) is None


def test_persons():
    from lib.driver import persons, Person
    from types import SimpleNamespace

    mock_persons = SimpleNamespace(arr=[None] * 3)
    mock_data = SimpleNamespace(persons=mock_persons)
    mock_base = SimpleNamespace(data=mock_data)

    collection = persons(mock_base)
    assert collection.length == 3
    person = collection.get(0)
    assert isinstance(person, Person)
    assert person.index == 0


def test_iper_marker():
    from lib.driver import iper_marker, ipers
    from types import SimpleNamespace

    mock_persons = SimpleNamespace(arr=[None] * 10)
    mock_data = SimpleNamespace(persons=mock_persons)
    mock_base = SimpleNamespace(data=mock_data)

    collection = ipers(mock_base)
    marker = iper_marker(collection, False)
    assert marker is not None


def test_ifam_marker():
    from lib.driver import ifam_marker, ifams
    from types import SimpleNamespace

    mock_families = SimpleNamespace(arr=[None] * 5)
    mock_data = SimpleNamespace(families=mock_families)
    mock_base = SimpleNamespace(data=mock_data)

    collection = ifams(mock_base)
    marker = ifam_marker(collection, False)
    assert marker is not None


def test_all_person_getters_coverage():
    from lib.driver import (
        Person, get_aliases, get_first_names_aliases, get_surnames_aliases,
        get_titles, get_related, get_rparents, get_birth_place, get_birth_note,
        get_birth_src, get_baptism, get_baptism_place, get_baptism_note,
        get_baptism_src, get_death, get_death_place, get_death_note, get_death_src,
        get_burial, get_burial_place, get_burial_note, get_burial_src,
        get_pevents, get_notes, get_psources, get_consang, get_parents, get_birth
    )
    from lib.gwdef import GenPerson, GenAscend, GenUnion, Sex, Access
    from lib.date import cdate_None
    from lib.adef import NO_CONSANG

    gen_person = GenPerson(
        first_name=10, surname=20, occ=3, image=30, public_name=40,
        qualifiers=[1, 2], aliases=[3, 4], first_names_aliases=[5, 6],
        surnames_aliases=[7, 8], titles=[9], rparents=[10], related=[11, 12],
        occupation=50, sex=Sex.MALE, access=Access.PUBLIC,
        birth=cdate_None, birth_place=60, birth_note=61, birth_src=62,
        baptism=cdate_None, baptism_place=70, baptism_note=71, baptism_src=72,
        death=None, death_place=80, death_note=81, death_src=82,
        burial=None, burial_place=90, burial_note=91, burial_src=92,
        pevents=[100], notes=110, psources=120, key_index=5
    )

    person = Person(base=None, index=5)
    person.gen_person = gen_person
    person.gen_ascend = GenAscend(parents=15, consang=NO_CONSANG)
    person.gen_union = GenUnion(family=[20, 21])

    assert get_aliases(person) == [3, 4]
    assert get_first_names_aliases(person) == [5, 6]
    assert get_surnames_aliases(person) == [7, 8]
    assert get_titles(person) == [9]
    assert get_related(person) == [11, 12]
    assert get_rparents(person) == [10]
    assert get_birth(person) == cdate_None
    assert get_birth_place(person) == 60
    assert get_birth_note(person) == 61
    assert get_birth_src(person) == 62
    assert get_baptism(person) == cdate_None
    assert get_baptism_place(person) == 70
    assert get_baptism_note(person) == 71
    assert get_baptism_src(person) == 72
    assert get_death(person) is None
    assert get_death_place(person) == 80
    assert get_death_note(person) == 81
    assert get_death_src(person) == 82
    assert get_burial(person) is None
    assert get_burial_place(person) == 90
    assert get_burial_note(person) == 91
    assert get_burial_src(person) == 92
    assert get_pevents(person) == [100]
    assert get_notes(person) == 110
    assert get_psources(person) == 120
    assert get_consang(person) == NO_CONSANG
    assert get_parents(person) == 15


def test_all_family_getters_coverage():
    from lib.driver import (
        Family, get_marriage_note, get_marriage_src, get_divorce,
        get_relation, get_fevents, get_fsources, get_origin_file
    )
    from lib.gwdef import GenFamily, GenCouple, GenDescend, RelationKind, NotDivorced
    from lib.date import cdate_None

    gen_family = GenFamily(
        marriage=cdate_None, marriage_place=100, marriage_note=101, marriage_src=102,
        relation=RelationKind.MARRIED, divorce=NotDivorced(), fevents=[200],
        witnesses=[10, 11], comment=110, origin_file=120, fsources=130, fam_index=15
    )
    gen_couple = GenCouple(father=10, mother=20)
    gen_descend = GenDescend(children=[30, 31, 32])

    family = Family(base=None, index=15)
    family.gen_family = gen_family
    family.gen_couple = gen_couple
    family.gen_descend = gen_descend

    assert get_marriage_note(family) == 101
    assert get_marriage_src(family) == 102
    assert isinstance(get_divorce(family), NotDivorced)
    assert get_relation(family) == RelationKind.MARRIED
    assert get_fevents(family) == [200]
    assert get_fsources(family) == 130
    assert get_origin_file(family) == 120


def test_base_operations_no_func():
    from lib.driver import insert_string, person_of_key, persons_of_name
    from lib.driver import persons_of_first_name, persons_of_surname
    from types import SimpleNamespace

    mock_base = SimpleNamespace()

    assert insert_string(mock_base, "test") == 0
    assert person_of_key(mock_base, "John", "Doe", 0) is None
    assert persons_of_name(mock_base, "John Doe") == []
    assert persons_of_first_name(mock_base) is None
    assert persons_of_surname(mock_base) is None


def test_base_operations_no_data():
    from lib.driver import sou, bname, nb_of_persons, nb_of_families
    from lib.driver import nb_of_real_persons, iper_exists, ifam_exists
    from types import SimpleNamespace

    mock_base = SimpleNamespace()

    assert sou(mock_base, 5) == ""
    assert bname(mock_base) == ""
    assert nb_of_persons(mock_base) == 0
    assert nb_of_families(mock_base) == 0
    assert nb_of_real_persons(mock_base) == 0
    assert iper_exists(mock_base, 0) is False
    assert ifam_exists(mock_base, 0) is False


def test_ifams_with_selection():
    from lib.driver import ifams, foi
    from types import SimpleNamespace

    mock_families = SimpleNamespace(arr=[None] * 5)
    mock_data = SimpleNamespace(families=mock_families)
    mock_base = SimpleNamespace(data=mock_data)

    select_even = lambda i: i % 2 == 0
    collection = ifams(mock_base, select=select_even)
    assert collection.length == 5


def test_families_with_selection():
    from lib.driver import families, Family
    from types import SimpleNamespace

    mock_families = SimpleNamespace(arr=[None] * 5)
    mock_data = SimpleNamespace(families=mock_families)
    mock_base = SimpleNamespace(data=mock_data)

    select_all = lambda f: True
    collection = families(mock_base, select=select_all)
    assert collection.length == 5


def test_load_array_functions():
    from lib.driver import (load_ascends_array, load_unions_array, load_couples_array,
                           load_descends_array, load_strings_array, load_persons_array,
                           load_families_array)
    from types import SimpleNamespace

    loaded = {'ascends': False, 'unions': False, 'couples': False, 'descends': False,
              'strings': False, 'persons': False, 'families': False}

    def make_loadable(name):
        obj = SimpleNamespace()
        obj.load_array = lambda: loaded.update({name: True})
        return obj

    mock_data = SimpleNamespace(
        ascends=make_loadable('ascends'),
        unions=make_loadable('unions'),
        couples=make_loadable('couples'),
        descends=make_loadable('descends'),
        strings=make_loadable('strings'),
        persons=make_loadable('persons'),
        families=make_loadable('families')
    )
    mock_base = SimpleNamespace(data=mock_data)

    load_ascends_array(mock_base)
    assert loaded['ascends'] is True

    load_unions_array(mock_base)
    assert loaded['unions'] is True

    load_couples_array(mock_base)
    assert loaded['couples'] is True

    load_descends_array(mock_base)
    assert loaded['descends'] is True

    load_strings_array(mock_base)
    assert loaded['strings'] is True

    load_persons_array(mock_base)
    assert loaded['persons'] is True

    load_families_array(mock_base)
    assert loaded['families'] is True


def test_load_array_functions_no_data():
    from lib.driver import (load_ascends_array, load_unions_array, load_couples_array,
                           load_descends_array, load_strings_array, load_persons_array,
                           load_families_array)
    from types import SimpleNamespace

    mock_base = SimpleNamespace()

    load_ascends_array(mock_base)
    load_unions_array(mock_base)
    load_couples_array(mock_base)
    load_descends_array(mock_base)
    load_strings_array(mock_base)
    load_persons_array(mock_base)
    load_families_array(mock_base)


def test_clear_array_functions():
    from lib.driver import (clear_ascends_array, clear_unions_array, clear_couples_array,
                           clear_descends_array, clear_strings_array, clear_persons_array,
                           clear_families_array)
    from types import SimpleNamespace

    cleared = {'ascends': False, 'unions': False, 'couples': False, 'descends': False,
               'strings': False, 'persons': False, 'families': False}

    def make_clearable(name):
        obj = SimpleNamespace()
        obj.clear_array = lambda: cleared.update({name: True})
        return obj

    mock_data = SimpleNamespace(
        ascends=make_clearable('ascends'),
        unions=make_clearable('unions'),
        couples=make_clearable('couples'),
        descends=make_clearable('descends'),
        strings=make_clearable('strings'),
        persons=make_clearable('persons'),
        families=make_clearable('families')
    )
    mock_base = SimpleNamespace(data=mock_data)

    clear_ascends_array(mock_base)
    assert cleared['ascends'] is True

    clear_unions_array(mock_base)
    assert cleared['unions'] is True

    clear_couples_array(mock_base)
    assert cleared['couples'] is True

    clear_descends_array(mock_base)
    assert cleared['descends'] is True

    clear_strings_array(mock_base)
    assert cleared['strings'] is True

    clear_persons_array(mock_base)
    assert cleared['persons'] is True

    clear_families_array(mock_base)
    assert cleared['families'] is True


def test_clear_array_functions_no_data():
    from lib.driver import (clear_ascends_array, clear_unions_array, clear_couples_array,
                           clear_descends_array, clear_strings_array, clear_persons_array,
                           clear_families_array)
    from types import SimpleNamespace

    mock_base = SimpleNamespace()

    clear_ascends_array(mock_base)
    clear_unions_array(mock_base)
    clear_couples_array(mock_base)
    clear_descends_array(mock_base)
    clear_strings_array(mock_base)
    clear_persons_array(mock_base)
    clear_families_array(mock_base)


def test_gen_person_of_person():
    from lib.driver import gen_person_of_person, Person
    from lib.gwdef import GenPerson, Sex
    from types import SimpleNamespace

    mock_gen_person = GenPerson(
        first_name=1,
        surname=2,
        occ=0,
        image=0,
        public_name=0,
        qualifiers=[],
        aliases=[],
        first_names_aliases=[],
        surnames_aliases=[],
        titles=[],
        rparents=[],
        related=[],
        occupation=0,
        sex=Sex.MALE,
        access=0,
        birth=None,
        birth_place=0,
        birth_note=0,
        birth_src=0,
        baptism=None,
        baptism_place=0,
        baptism_note=0,
        baptism_src=0,
        death=None,
        death_place=0,
        death_note=0,
        death_src=0,
        burial=None,
        burial_place=0,
        burial_note=0,
        burial_src=0,
        pevents=[],
        notes=0,
        psources=0,
        key_index=0
    )

    mock_base = SimpleNamespace()
    mock_persons = SimpleNamespace(arr=[None])
    mock_base.data = SimpleNamespace(persons=mock_persons)

    person = Person(mock_base, 0)
    person.gen_person = mock_gen_person
    person.loaded = True

    result = gen_person_of_person(person)
    assert result == mock_gen_person
    assert result.first_name == 1
    assert result.surname == 2


def test_gen_ascend_of_person():
    from lib.driver import gen_ascend_of_person, Person
    from lib.gwdef import GenAscend
    from lib.adef import Fix
    from types import SimpleNamespace

    mock_gen_ascend = GenAscend(parents=None, consang=Fix.from_float(0.0))

    mock_base = SimpleNamespace()
    mock_persons = SimpleNamespace(arr=[None], get=lambda i: None)
    mock_base.data = SimpleNamespace(persons=mock_persons)

    person = Person(mock_base, 0)
    person.gen_ascend = mock_gen_ascend
    person.gen_person = SimpleNamespace()

    result = gen_ascend_of_person(person)
    assert result == mock_gen_ascend
    assert result.parents is None
    assert result.consang.to_float() == 0.0


def test_gen_union_of_person():
    from lib.driver import gen_union_of_person, Person
    from lib.gwdef import GenUnion
    from types import SimpleNamespace

    mock_gen_union = GenUnion(family=[])

    mock_base = SimpleNamespace()
    mock_persons = SimpleNamespace(arr=[None], get=lambda i: None)
    mock_base.data = SimpleNamespace(persons=mock_persons)

    person = Person(mock_base, 0)
    person.gen_union = mock_gen_union
    person.gen_person = SimpleNamespace()

    result = gen_union_of_person(person)
    assert result == mock_gen_union
    assert result.family == []


def test_new_iper():
    from lib.driver import new_iper
    from types import SimpleNamespace

    mock_persons = SimpleNamespace(arr=[None] * 42)
    mock_data = SimpleNamespace(persons=mock_persons)
    mock_base = SimpleNamespace(data=mock_data)

    result = new_iper(mock_base)
    assert result == 42


def test_new_ifam():
    from lib.driver import new_ifam
    from types import SimpleNamespace

    mock_families = SimpleNamespace(arr=[None] * 13)
    mock_data = SimpleNamespace(families=mock_families)
    mock_base = SimpleNamespace(data=mock_data)

    result = new_ifam(mock_base)
    assert result == 13


def test_gen_couple_of_family():
    from lib.driver import gen_couple_of_family, Family
    from lib.gwdef import GenCouple
    from types import SimpleNamespace

    mock_gen_couple = GenCouple(father=0, mother=1)

    mock_base = SimpleNamespace()
    mock_families = SimpleNamespace(arr=[None], get=lambda i: None)
    mock_base.data = SimpleNamespace(families=mock_families)

    family = Family(mock_base, 0)
    family.gen_couple = mock_gen_couple
    family.gen_family = SimpleNamespace()

    result = gen_couple_of_family(family)
    assert result == mock_gen_couple
    assert result.father == 0
    assert result.mother == 1


def test_gen_descend_of_family():
    from lib.driver import gen_descend_of_family, Family
    from lib.gwdef import GenDescend
    from types import SimpleNamespace

    mock_gen_descend = GenDescend(children=[0, 1, 2])

    mock_base = SimpleNamespace()
    mock_families = SimpleNamespace(arr=[None], get=lambda i: None)
    mock_base.data = SimpleNamespace(families=mock_families)

    family = Family(mock_base, 0)
    family.gen_descend = mock_gen_descend
    family.gen_family = SimpleNamespace()

    result = gen_descend_of_family(family)
    assert result == mock_gen_descend
    assert result.children == [0, 1, 2]


def test_gen_family_of_family():
    from lib.driver import gen_family_of_family, Family
    from lib.gwdef import GenFamily, RelationKind, NotDivorced
    from lib.date import cdate_None
    from types import SimpleNamespace

    mock_gen_family = GenFamily(
        marriage=cdate_None,
        marriage_place=0,
        marriage_note=0,
        marriage_src=0,
        relation=RelationKind.MARRIED,
        divorce=NotDivorced(),
        fevents=[],
        witnesses=[],
        comment=0,
        origin_file=0,
        fsources=0,
        fam_index=5
    )

    mock_base = SimpleNamespace()
    mock_families = SimpleNamespace(arr=[None], get=lambda i: None)
    mock_base.data = SimpleNamespace(families=mock_families)

    family = Family(mock_base, 5)
    family.gen_family = mock_gen_family

    result = gen_family_of_family(family)
    assert result == mock_gen_family
    assert result.fam_index == 5


def test_person_of_gen_person():
    from lib.driver import person_of_gen_person, Person
    from lib.gwdef import GenPerson, GenAscend, GenUnion, Sex, Access, DontKnowIfDead, UnknownBurial
    from lib.date import cdate_None
    from lib.adef import NO_CONSANG
    from types import SimpleNamespace

    mock_base = SimpleNamespace()

    mock_gen_person = GenPerson(
        first_name=1, surname=2, occ=0, image=0,
        first_names_aliases=[], surnames_aliases=[], public_name=0,
        qualifiers=[], titles=[], rparents=[], related=[], aliases=[],
        occupation=0, sex=Sex.MALE, access=Access.PUBLIC,
        birth=cdate_None, birth_place=0, birth_note=0, birth_src=0,
        baptism=cdate_None, baptism_place=0, baptism_note=0, baptism_src=0,
        death=DontKnowIfDead(), death_place=0, death_note=0, death_src=0,
        burial=UnknownBurial(), burial_place=0, burial_note=0, burial_src=0,
        pevents=[], notes=0, psources=0, key_index=42
    )
    mock_gen_ascend = GenAscend(parents=None, consang=NO_CONSANG)
    mock_gen_union = GenUnion(family=[])

    result = person_of_gen_person(mock_base, (mock_gen_person, mock_gen_ascend, mock_gen_union))
    assert isinstance(result, Person)
    assert result.index == 42
    assert result.gen_person == mock_gen_person
    assert result.gen_ascend == mock_gen_ascend
    assert result.gen_union == mock_gen_union


def test_family_of_gen_family():
    from lib.driver import family_of_gen_family, Family
    from lib.gwdef import GenFamily, GenCouple, GenDescend, RelationKind, NotDivorced
    from lib.date import cdate_None
    from types import SimpleNamespace

    mock_base = SimpleNamespace()

    mock_gen_family = GenFamily(
        marriage=cdate_None, marriage_place=0, marriage_note=0, marriage_src=0,
        relation=RelationKind.MARRIED, divorce=NotDivorced(),
        fevents=[], witnesses=[], comment=0, origin_file=0, fsources=0,
        fam_index=10
    )
    mock_gen_couple = GenCouple(father=0, mother=1)
    mock_gen_descend = GenDescend(children=[2, 3])

    result = family_of_gen_family(mock_base, (mock_gen_family, mock_gen_couple, mock_gen_descend))
    assert isinstance(result, Family)
    assert result.index == 10
    assert result.gen_family == mock_gen_family
    assert result.gen_couple == mock_gen_couple
    assert result.gen_descend == mock_gen_descend


def test_no_person():
    from lib.driver import no_person, Istr
    from lib.gwdef import Sex, Access

    result = no_person(42)
    assert result.key_index == 42
    assert result.first_name == Istr.QUEST
    assert result.surname == Istr.QUEST
    assert result.sex == Sex.NEUTER
    assert result.access == Access.PRIVATE
    assert result.first_names_aliases == []
    assert result.surnames_aliases == []
    assert result.qualifiers == []
    assert result.titles == []


def test_no_ascend():
    from lib.driver import no_ascend
    from lib.adef import NO_CONSANG

    result = no_ascend()
    assert result.parents is None
    assert result.consang == NO_CONSANG


def test_no_union():
    from lib.driver import no_union

    result = no_union()
    assert result.family == []


def test_no_family():
    from lib.driver import no_family, Istr
    from lib.gwdef import RelationKind

    result = no_family(99)
    assert result.fam_index == 99
    assert result.marriage_place == Istr.EMPTY
    assert result.relation == RelationKind.MARRIED
    assert result.fevents == []
    assert result.witnesses == []


def test_no_descend():
    from lib.driver import no_descend

    result = no_descend()
    assert result.children == []


def test_no_couple():
    from lib.driver import no_couple, Iper

    result = no_couple()
    assert result.father == Iper.dummy()
    assert result.mother == Iper.dummy()


def test_p_first_name():
    from lib.driver import p_first_name, Person
    from lib.gwdef import GenPerson, Sex, Access, DontKnowIfDead, UnknownBurial
    from lib.date import cdate_None
    from types import SimpleNamespace

    mock_gen_person = GenPerson(
        first_name=5, surname=2, occ=0, image=0,
        first_names_aliases=[], surnames_aliases=[], public_name=0,
        qualifiers=[], titles=[], rparents=[], related=[], aliases=[],
        occupation=0, sex=Sex.MALE, access=Access.PUBLIC,
        birth=cdate_None, birth_place=0, birth_note=0, birth_src=0,
        baptism=cdate_None, baptism_place=0, baptism_note=0, baptism_src=0,
        death=DontKnowIfDead(), death_place=0, death_note=0, death_src=0,
        burial=UnknownBurial(), burial_place=0, burial_note=0, burial_src=0,
        pevents=[], notes=0, psources=0, key_index=0
    )

    strings = ["", "?", "surname", "", "", "John"]
    mock_strings = SimpleNamespace(get=lambda i: strings[i] if 0 <= i < len(strings) else "")
    mock_base = SimpleNamespace(data=SimpleNamespace(strings=mock_strings))

    person = Person(mock_base, 0)
    person.gen_person = mock_gen_person

    result = p_first_name(mock_base, person)
    assert result == "John"


def test_p_surname():
    from lib.driver import p_surname, Person
    from lib.gwdef import GenPerson, Sex, Access, DontKnowIfDead, UnknownBurial
    from lib.date import cdate_None
    from types import SimpleNamespace

    mock_gen_person = GenPerson(
        first_name=1, surname=7, occ=0, image=0,
        first_names_aliases=[], surnames_aliases=[], public_name=0,
        qualifiers=[], titles=[], rparents=[], related=[], aliases=[],
        occupation=0, sex=Sex.MALE, access=Access.PUBLIC,
        birth=cdate_None, birth_place=0, birth_note=0, birth_src=0,
        baptism=cdate_None, baptism_place=0, baptism_note=0, baptism_src=0,
        death=DontKnowIfDead(), death_place=0, death_note=0, death_src=0,
        burial=UnknownBurial(), burial_place=0, burial_note=0, burial_src=0,
        pevents=[], notes=0, psources=0, key_index=0
    )

    strings = ["", "?", "", "", "", "", "", "Smith"]
    mock_strings = SimpleNamespace(get=lambda i: strings[i] if 0 <= i < len(strings) else "")
    mock_base = SimpleNamespace(data=SimpleNamespace(strings=mock_strings))

    person = Person(mock_base, 0)
    person.gen_person = mock_gen_person

    result = p_surname(mock_base, person)
    assert result == "Smith"


def test_person_misc_names():
    from lib.driver import person_misc_names, Person, Istr
    from lib.gwdef import GenPerson, Sex, Access, DontKnowIfDead, UnknownBurial
    from lib.date import cdate_None
    from types import SimpleNamespace

    mock_gen_person = GenPerson(
        first_name=2, surname=3, occ=0, image=0,
        first_names_aliases=[4], surnames_aliases=[5], public_name=6,
        qualifiers=[7], titles=[], rparents=[], related=[], aliases=[8],
        occupation=0, sex=Sex.MALE, access=Access.PUBLIC,
        birth=cdate_None, birth_place=0, birth_note=0, birth_src=0,
        baptism=cdate_None, baptism_place=0, baptism_note=0, baptism_src=0,
        death=DontKnowIfDead(), death_place=0, death_note=0, death_src=0,
        burial=UnknownBurial(), burial_place=0, burial_note=0, burial_src=0,
        pevents=[], notes=0, psources=0, key_index=0
    )

    strings = ["", "?", "John", "Doe", "Johnny", "Smith", "J.D.", "Jr", "John D."]
    mock_strings = SimpleNamespace(get=lambda i: strings[i] if 0 <= i < len(strings) else "")
    mock_base = SimpleNamespace(data=SimpleNamespace(strings=mock_strings))

    person = Person(mock_base, 0)
    person.gen_person = mock_gen_person

    def nobtit(p):
        return []

    result = person_misc_names(mock_base, person, nobtit)
    assert "John Doe" in result
    assert "J.D. Doe" in result
    assert "John D." in result
    assert "John Jr Doe" in result
    assert "Johnny Doe" in result
    assert "John Smith" in result


def test_insert_person_with_union_and_ascendants():
    from lib.driver import insert_person_with_union_and_ascendants, Istr
    from lib.gwdef import GenPerson, GenAscend, GenUnion, Sex, Access, DontKnowIfDead, UnknownBurial
    from lib.date import cdate_None
    from lib.adef import NO_CONSANG
    from types import SimpleNamespace

    patched = {'person': None, 'ascend': None, 'union': None}

    def patch_person(ip, p):
        patched['person'] = (ip, p)

    def patch_ascend(ip, a):
        patched['ascend'] = (ip, a)

    def patch_union(ip, u):
        patched['union'] = (ip, u)

    mock_func = SimpleNamespace(
        patch_person=patch_person,
        patch_ascend=patch_ascend,
        patch_union=patch_union
    )
    mock_persons = SimpleNamespace(arr=[None] * 5)
    mock_data = SimpleNamespace(persons=mock_persons)
    mock_base = SimpleNamespace(func=mock_func, data=mock_data)

    gen_person = GenPerson(
        first_name=Istr.QUEST, surname=Istr.QUEST, occ=0, image=0,
        first_names_aliases=[], surnames_aliases=[], public_name=0,
        qualifiers=[], titles=[], rparents=[], related=[], aliases=[],
        occupation=0, sex=Sex.MALE, access=Access.PUBLIC,
        birth=cdate_None, birth_place=0, birth_note=0, birth_src=0,
        baptism=cdate_None, baptism_place=0, baptism_note=0, baptism_src=0,
        death=DontKnowIfDead(), death_place=0, death_note=0, death_src=0,
        burial=UnknownBurial(), burial_place=0, burial_note=0, burial_src=0,
        pevents=[], notes=0, psources=0, key_index=-1
    )
    gen_ascend = GenAscend(parents=None, consang=NO_CONSANG)
    gen_union = GenUnion(family=[])

    result = insert_person_with_union_and_ascendants(mock_base, gen_person, gen_ascend, gen_union)
    assert result == 5
    assert patched['person'] is not None
    assert patched['person'][0] == 5
    assert patched['person'][1].key_index == 5
    assert patched['ascend'] is not None
    assert patched['union'] is not None


def test_insert_family_with_couple_and_descendants():
    from lib.driver import insert_family_with_couple_and_descendants, Istr
    from lib.gwdef import GenFamily, GenCouple, GenDescend, RelationKind, NotDivorced
    from lib.date import cdate_None
    from types import SimpleNamespace

    patched = {'family': None, 'couple': None, 'descend': None}

    def patch_family(ifam, f):
        patched['family'] = (ifam, f)

    def patch_couple(ifam, c):
        patched['couple'] = (ifam, c)

    def patch_descend(ifam, d):
        patched['descend'] = (ifam, d)

    mock_func = SimpleNamespace(
        patch_family=patch_family,
        patch_couple=patch_couple,
        patch_descend=patch_descend
    )
    mock_families = SimpleNamespace(arr=[None] * 3)
    mock_data = SimpleNamespace(families=mock_families)
    mock_base = SimpleNamespace(func=mock_func, data=mock_data)

    gen_family = GenFamily(
        marriage=cdate_None, marriage_place=Istr.EMPTY, marriage_note=Istr.EMPTY,
        marriage_src=Istr.EMPTY, relation=RelationKind.MARRIED, divorce=NotDivorced(),
        fevents=[], witnesses=[], comment=Istr.EMPTY, origin_file=Istr.EMPTY,
        fsources=Istr.EMPTY, fam_index=-1
    )
    gen_couple = GenCouple(father=0, mother=1)
    gen_descend = GenDescend(children=[2, 3])

    result = insert_family_with_couple_and_descendants(mock_base, gen_family, gen_couple, gen_descend)
    assert result == 3
    assert patched['family'] is not None
    assert patched['family'][0] == 3
    assert patched['family'][1].fam_index == 3
    assert patched['couple'] is not None
    assert patched['descend'] is not None


def test_delete_person_rec():
    import lib.driver
    from lib.gwdef import GenUnion
    from types import SimpleNamespace

    deleted = {'person': [], 'ascend': [], 'union': [], 'descend': []}

    original_delete_person = lib.driver.delete_person
    original_delete_ascend = lib.driver.delete_ascend
    original_delete_union = lib.driver.delete_union
    original_delete_descend = lib.driver.delete_descend
    original_delete_family_rec = lib.driver.delete_family_rec

    def mock_delete_person(base, ip):
        deleted['person'].append(ip)

    def mock_delete_ascend(base, ip):
        deleted['ascend'].append(ip)

    def mock_delete_union(base, ip):
        deleted['union'].append(ip)

    def mock_delete_descend(base, ifam):
        deleted['descend'].append(ifam)

    def mock_delete_family_rec(base, ifam):
        pass

    lib.driver.delete_person = mock_delete_person
    lib.driver.delete_ascend = mock_delete_ascend
    lib.driver.delete_union = mock_delete_union
    lib.driver.delete_descend = mock_delete_descend
    lib.driver.delete_family_rec = mock_delete_family_rec

    try:
        person = lib.driver.Person(None, 0)
        person.gen_person = SimpleNamespace()
        person.gen_ascend = SimpleNamespace(parents=5)
        person.gen_union = GenUnion(family=[1, 2])

        family1 = lib.driver.Family(None, 1)
        family1.gen_couple = SimpleNamespace(father=0, mother=10)
        family1.gen_family = SimpleNamespace()

        family2 = lib.driver.Family(None, 2)
        family2.gen_couple = SimpleNamespace(father=0, mother=11)
        family2.gen_family = SimpleNamespace()

        original_poi = lib.driver.poi
        original_foi = lib.driver.foi

        def mock_poi(base, ip):
            return person

        def mock_foi(base, ifam):
            if ifam == 1:
                return family1
            elif ifam == 2:
                return family2
            return None

        lib.driver.poi = mock_poi
        lib.driver.foi = mock_foi

        lib.driver.delete_person_rec(None, 0)
        assert 0 in deleted['person']
        assert 0 in deleted['ascend']
        assert 0 in deleted['union']
        assert 5 in deleted['descend']

        lib.driver.poi = original_poi
        lib.driver.foi = original_foi
    finally:
        lib.driver.delete_person = original_delete_person
        lib.driver.delete_ascend = original_delete_ascend
        lib.driver.delete_union = original_delete_union
        lib.driver.delete_descend = original_delete_descend
        lib.driver.delete_family_rec = original_delete_family_rec


def test_delete_family_rec():
    import lib.driver
    from lib.gwdef import GenUnion
    from types import SimpleNamespace

    deleted = {'family': [], 'couple': [], 'descend': [], 'ascend': []}
    patched_unions = {}

    original_delete_family = lib.driver.delete_family
    original_delete_couple = lib.driver.delete_couple
    original_delete_descend = lib.driver.delete_descend
    original_delete_ascend = lib.driver.delete_ascend
    original_patch_union = lib.driver.patch_union

    def mock_delete_family(base, ifam):
        deleted['family'].append(ifam)

    def mock_delete_couple(base, ifam):
        deleted['couple'].append(ifam)

    def mock_delete_descend(base, ifam):
        deleted['descend'].append(ifam)

    def mock_delete_ascend(base, ip):
        deleted['ascend'].append(ip)

    def mock_patch_union(base, ip, u):
        patched_unions[ip] = u

    lib.driver.delete_family = mock_delete_family
    lib.driver.delete_couple = mock_delete_couple
    lib.driver.delete_descend = mock_delete_descend
    lib.driver.delete_ascend = mock_delete_ascend
    lib.driver.patch_union = mock_patch_union

    try:
        father = lib.driver.Person(None, 0)
        father.gen_person = SimpleNamespace()
        father.gen_ascend = SimpleNamespace(parents=5)
        father.gen_union = GenUnion(family=[5, 6])

        mother = lib.driver.Person(None, 1)
        mother.gen_person = SimpleNamespace()
        mother.gen_ascend = SimpleNamespace(parents=5)
        mother.gen_union = GenUnion(family=[5, 7])

        child1 = lib.driver.Person(None, 2)
        child1.gen_person = SimpleNamespace()
        child1.gen_ascend = SimpleNamespace(parents=5)

        child2 = lib.driver.Person(None, 3)
        child2.gen_person = SimpleNamespace()
        child2.gen_ascend = SimpleNamespace(parents=5)

        family = lib.driver.Family(None, 5)
        family.gen_couple = SimpleNamespace(father=0, mother=1)
        family.gen_descend = SimpleNamespace(children=[2, 3])
        family.gen_family = SimpleNamespace()

        original_poi = lib.driver.poi
        original_foi = lib.driver.foi

        def mock_poi(base, ip):
            if ip == 0:
                return father
            elif ip == 1:
                return mother
            elif ip == 2:
                return child1
            elif ip == 3:
                return child2
            return None

        def mock_foi(base, ifam):
            if ifam == 5:
                return family
            return None

        lib.driver.poi = mock_poi
        lib.driver.foi = mock_foi

        lib.driver.delete_family_rec(None, 5)
        assert 5 in deleted['family']
        assert 5 in deleted['couple']
        assert 5 in deleted['descend']
        assert 2 in deleted['ascend']
        assert 3 in deleted['ascend']
        assert 0 in patched_unions
        assert 1 in patched_unions

        lib.driver.poi = original_poi
        lib.driver.foi = original_foi
    finally:
        lib.driver.delete_family = original_delete_family
        lib.driver.delete_couple = original_delete_couple
        lib.driver.delete_descend = original_delete_descend
        lib.driver.delete_ascend = original_delete_ascend
        lib.driver.patch_union = original_patch_union


def test_empty_person():
    from lib.driver import empty_person, Person
    from types import SimpleNamespace

    mock_base = SimpleNamespace()
    result = empty_person(mock_base, 42)
    assert isinstance(result, Person)
    assert result.index == 42
    assert result.base == mock_base


def test_empty_family():
    from lib.driver import empty_family, Family
    from types import SimpleNamespace

    mock_base = SimpleNamespace()
    result = empty_family(mock_base, 10)
    assert isinstance(result, Family)
    assert result.index == 10
    assert result.base == mock_base


def test_get_separation():
    from lib.driver import get_separation, Family
    from lib.gwdef import NotDivorced
    from types import SimpleNamespace

    mock_base = SimpleNamespace()
    family = Family(mock_base, 0)
    family.gen_family = SimpleNamespace(divorce=NotDivorced())

    result = get_separation(family)
    assert isinstance(result, NotDivorced)


def test_children_of_p():
    from lib.driver import children_of_p, Person, Family
    from lib.gwdef import GenUnion
    from types import SimpleNamespace

    mock_base = SimpleNamespace()

    person = Person(mock_base, 0)
    person.gen_union = GenUnion(family=[1, 2])
    person.gen_person = SimpleNamespace()

    fam1 = Family(mock_base, 1)
    fam1.gen_descend = SimpleNamespace(children=[10, 11])
    fam1.gen_family = SimpleNamespace()

    fam2 = Family(mock_base, 2)
    fam2.gen_descend = SimpleNamespace(children=[12])
    fam2.gen_family = SimpleNamespace()

    import lib.driver
    original_foi = lib.driver.foi

    def mock_foi(base, ifam):
        if ifam == 1:
            return fam1
        elif ifam == 2:
            return fam2
        return None

    lib.driver.foi = mock_foi
    try:
        result = children_of_p(mock_base, person)
        assert result == [10, 11, 12]
    finally:
        lib.driver.foi = original_foi


def test_nobtitles():
    from lib.driver import nobtitles, Person, Istr
    from lib.gwdef import GenPerson, Sex, Access, DontKnowIfDead, UnknownBurial
    from lib.date import cdate_None
    from types import SimpleNamespace

    mock_title1 = SimpleNamespace(name=5)
    mock_title2 = SimpleNamespace(name=6)
    mock_title3 = SimpleNamespace(name=7)

    mock_gen_person = GenPerson(
        first_name=1, surname=2, occ=0, image=0,
        first_names_aliases=[], surnames_aliases=[], public_name=0,
        qualifiers=[], titles=[mock_title1, mock_title2, mock_title3],
        rparents=[], related=[], aliases=[],
        occupation=0, sex=Sex.MALE, access=Access.PUBLIC,
        birth=cdate_None, birth_place=0, birth_note=0, birth_src=0,
        baptism=cdate_None, baptism_place=0, baptism_note=0, baptism_src=0,
        death=DontKnowIfDead(), death_place=0, death_note=0, death_src=0,
        burial=UnknownBurial(), burial_place=0, burial_note=0, burial_src=0,
        pevents=[], notes=0, psources=0, key_index=0
    )

    strings = ["", "?", "", "", "", "Duke", "Earl", "Baron"]
    mock_strings = SimpleNamespace(get=lambda i: strings[i] if 0 <= i < len(strings) else "")
    mock_base = SimpleNamespace(data=SimpleNamespace(strings=mock_strings))

    person = Person(mock_base, 0)
    person.gen_person = mock_gen_person

    result = nobtitles(mock_base, ["Duke", "Earl"], [], person)
    assert len(result) == 2

    result = nobtitles(mock_base, [], ["Baron"], person)
    assert len(result) == 2


def test_make():
    from lib.driver import make
    import pytest

    with pytest.raises(NotImplementedError):
        make("test", [], None, None, lambda x: x)


def test_load_database():
    from lib.driver import load_database
    import pytest

    if hasattr(load_database, '_loaded_bases'):
        load_database._loaded_bases.clear()

    with pytest.raises(Exception):
        load_database("nonexistent_db")


def test_with_database():
    from lib.driver import with_database
    import pytest

    with pytest.raises(Exception):
        with_database("nonexistent_db", lambda base: 42)


def test_sync():
    from lib.driver import sync
    from types import SimpleNamespace

    synced = {'called': False}

    def mock_sync(scratch):
        synced['called'] = True

    mock_func = SimpleNamespace(sync=mock_sync)
    mock_base = SimpleNamespace(func=mock_func)

    sync(mock_base)
    assert synced['called'] is True


def test_spi_functions():
    from lib.driver import spi_find, spi_first, spi_next, Istr
    from types import SimpleNamespace

    mock_spi = SimpleNamespace(
        find=lambda i: [1, 2, 3],
        first=lambda s: 5,
        next=lambda i: i + 1
    )

    assert spi_find(mock_spi, 10) == [1, 2, 3]
    assert spi_first(mock_spi, "test") == 5
    assert spi_next(mock_spi, 10) == 11

    empty_spi = SimpleNamespace()
    assert spi_find(empty_spi, 10) == []
    assert spi_first(empty_spi, "test") == Istr.EMPTY
    assert spi_next(empty_spi, 10) == Istr.EMPTY


def test_base_visible_get():
    from lib.driver import base_visible_get, Person
    from types import SimpleNamespace

    called = {'value': False}

    def fct(person):
        called['value'] = True
        return True

    mock_base = SimpleNamespace()
    result = base_visible_get(mock_base, fct, 0)
    assert result is True
    assert called['value'] is True


def test_base_visible_write():
    from lib.driver import base_visible_write
    from types import SimpleNamespace

    written = {'called': False}

    mock_func = SimpleNamespace(base_visible_write=lambda: written.update({'called': True}))
    mock_base = SimpleNamespace(func=mock_func)

    base_visible_write(mock_base)
    assert written['called'] is True


def test_base_particles():
    from lib.driver import base_particles
    from types import SimpleNamespace
    import re

    mock_base = SimpleNamespace()
    result = base_particles(mock_base)
    assert isinstance(result, type(re.compile('')))


def test_base_strings_of_first_name():
    from lib.driver import base_strings_of_first_name
    from types import SimpleNamespace

    mock_func = SimpleNamespace(base_strings_of_first_name=lambda s: [1, 2, 3])
    mock_base = SimpleNamespace(func=mock_func)

    result = base_strings_of_first_name(mock_base, "John")
    assert result == [1, 2, 3]

    empty_base = SimpleNamespace()
    assert base_strings_of_first_name(empty_base, "John") == []


def test_base_strings_of_surname():
    from lib.driver import base_strings_of_surname
    from types import SimpleNamespace

    mock_func = SimpleNamespace(base_strings_of_surname=lambda s: [4, 5, 6])
    mock_base = SimpleNamespace(func=mock_func)

    result = base_strings_of_surname(mock_base, "Smith")
    assert result == [4, 5, 6]

    empty_base = SimpleNamespace()
    assert base_strings_of_surname(empty_base, "Smith") == []


def test_base_notes_read():
    from lib.driver import base_notes_read
    from types import SimpleNamespace

    mock_func = SimpleNamespace(base_notes_read=lambda fname: "Test note content")
    mock_base = SimpleNamespace(func=mock_func)

    result = base_notes_read(mock_base, "test.txt")
    assert result == "Test note content"

    empty_base = SimpleNamespace()
    assert base_notes_read(empty_base, "test.txt") == ""


def test_base_wiznotes_read():
    from lib.driver import base_wiznotes_read
    from types import SimpleNamespace

    mock_func = SimpleNamespace(base_wiznotes_read=lambda fname: "Wizard note")
    mock_base = SimpleNamespace(func=mock_func)

    result = base_wiznotes_read(mock_base, "wiz.txt")
    assert result == "Wizard note"

    empty_base = SimpleNamespace()
    assert base_wiznotes_read(empty_base, "wiz.txt") == ""


def test_base_notes_read_first_line():
    from lib.driver import base_notes_read_first_line
    from types import SimpleNamespace

    mock_func = SimpleNamespace(base_notes_read=lambda fname: "First line\nSecond line\nThird line")
    mock_base = SimpleNamespace(func=mock_func)

    result = base_notes_read_first_line(mock_base, "test.txt")
    assert result == "First line"


def test_base_notes_are_empty():
    from lib.driver import base_notes_are_empty
    from types import SimpleNamespace

    mock_func = SimpleNamespace(base_notes_read=lambda fname: "")
    mock_base = SimpleNamespace(func=mock_func)

    assert base_notes_are_empty(mock_base, "empty.txt") is True

    mock_func2 = SimpleNamespace(base_notes_read=lambda fname: "Not empty")
    mock_base2 = SimpleNamespace(func=mock_func2)

    assert base_notes_are_empty(mock_base2, "notempty.txt") is False


def test_base_notes_origin_file():
    from lib.driver import base_notes_origin_file
    from types import SimpleNamespace

    mock_func = SimpleNamespace(base_notes_origin_file=lambda: "origin.gw")
    mock_base = SimpleNamespace(func=mock_func)

    result = base_notes_origin_file(mock_base)
    assert result == "origin.gw"

    empty_base = SimpleNamespace()
    assert base_notes_origin_file(empty_base) == ""


def test_base_notes_dir():
    from lib.driver import base_notes_dir
    from types import SimpleNamespace

    mock_data = SimpleNamespace(bdir="/path/to/base")
    mock_base = SimpleNamespace(data=mock_data)

    result = base_notes_dir(mock_base)
    assert result == "/path/to/base/notes"

    empty_base = SimpleNamespace()
    assert base_notes_dir(empty_base) == ""


def test_base_wiznotes_dir():
    from lib.driver import base_wiznotes_dir
    from types import SimpleNamespace

    mock_data = SimpleNamespace(bdir="/path/to/base")
    mock_base = SimpleNamespace(data=mock_data)

    result = base_wiznotes_dir(mock_base)
    assert result == "/path/to/base/wiznotes"

    empty_base = SimpleNamespace()
    assert base_wiznotes_dir(empty_base) == ""


def test_read_nldb():
    from lib.driver import read_nldb
    from types import SimpleNamespace

    mock_func = SimpleNamespace(read_nldb=lambda: {'key': 'value'})
    mock_base = SimpleNamespace(func=mock_func)

    result = read_nldb(mock_base)
    assert result == {'key': 'value'}

    empty_base = SimpleNamespace()
    assert read_nldb(empty_base) == {}


def test_write_nldb():
    from lib.driver import write_nldb
    from types import SimpleNamespace

    written = {'data': None}

    def mock_write(nldb):
        written['data'] = nldb

    mock_func = SimpleNamespace(write_nldb=mock_write)
    mock_base = SimpleNamespace(func=mock_func)

    write_nldb(mock_base, {'test': 'data'})
    assert written['data'] == {'test': 'data'}


def test_date_of_last_change():
    from lib.driver import date_of_last_change
    from types import SimpleNamespace

    mock_func = SimpleNamespace(date_of_last_change=lambda: 1234567890.0)
    mock_base = SimpleNamespace(func=mock_func)

    result = date_of_last_change(mock_base)
    assert result == 1234567890.0

    empty_base = SimpleNamespace()
    assert date_of_last_change(empty_base) == 0.0
