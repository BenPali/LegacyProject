import pytest
from types import SimpleNamespace
from lib import change_children


def test_digest_children(monkeypatch):
    def mock_poi(base, ip):
        if ip == 0:
            return SimpleNamespace(iper=0)
        return SimpleNamespace(iper=1)

    def mock_get_first_name(p):
        return 10 if p.iper == 0 else 11

    def mock_get_surname(p):
        return 20 if p.iper == 0 else 21

    def mock_get_occ(p):
        return 0 if p.iper == 0 else 1

    def mock_sou(base, istr):
        if istr == 10:
            return "John"
        elif istr == 11:
            return "Jane"
        elif istr == 20:
            return "Doe"
        elif istr == 21:
            return "Smith"
        return ""

    monkeypatch.setattr("lib.change_children.driver.poi", mock_poi)
    monkeypatch.setattr("lib.change_children.driver.get_first_name", mock_get_first_name)
    monkeypatch.setattr("lib.change_children.driver.get_surname", mock_get_surname)
    monkeypatch.setattr("lib.change_children.driver.get_occ", mock_get_occ)
    monkeypatch.setattr("lib.change_children.driver.sou", mock_sou)

    base = SimpleNamespace()
    ipl = [0, 1]

    result = change_children.digest_children(base, ipl)
    assert isinstance(result, str)
    assert len(result) == 32


def test_digest_children_empty():
    base = SimpleNamespace()
    result = change_children.digest_children(base, [])
    assert isinstance(result, str)
    assert len(result) == 32


def test_check_digest_match():
    conf = SimpleNamespace(env={"digest": "abc123"})
    change_children.check_digest(conf, "abc123")


def test_check_digest_mismatch():
    conf = SimpleNamespace(env={"digest": "abc123"})
    with pytest.raises(ValueError):
        change_children.check_digest(conf, "xyz789")


def test_check_digest_no_env_digest():
    conf = SimpleNamespace(env={})
    change_children.check_digest(conf, "any_digest")


def test_check_conflict_no_conflict(monkeypatch):
    def mock_poi(base, ip):
        return SimpleNamespace(iper=ip)

    def mock_get_iper(p):
        return p.iper

    def mock_p_first_name(base, p):
        return "John" if p.iper == 1 else "Jane"

    def mock_p_surname(base, p):
        return "Doe" if p.iper == 1 else "Smith"

    def mock_get_occ(p):
        return 0

    monkeypatch.setattr("lib.change_children.driver.poi", mock_poi)
    monkeypatch.setattr("lib.change_children.driver.get_iper", mock_get_iper)
    monkeypatch.setattr("lib.change_children.driver.p_first_name", mock_p_first_name)
    monkeypatch.setattr("lib.change_children.driver.p_surname", mock_p_surname)
    monkeypatch.setattr("lib.change_children.driver.get_occ", mock_get_occ)

    base = SimpleNamespace()
    p = SimpleNamespace(iper=0)
    ipl = [1, 2]

    change_children.check_conflict(base, p, "Robert Jones", 0, ipl)


def test_check_conflict_with_conflict(monkeypatch):
    def mock_poi(base, ip):
        return SimpleNamespace(iper=ip)

    def mock_get_iper(p):
        return p.iper

    def mock_p_first_name(base, p):
        return "John"

    def mock_p_surname(base, p):
        return "Doe"

    def mock_get_occ(p):
        return 0

    monkeypatch.setattr("lib.change_children.driver.poi", mock_poi)
    monkeypatch.setattr("lib.change_children.driver.get_iper", mock_get_iper)
    monkeypatch.setattr("lib.change_children.driver.p_first_name", mock_p_first_name)
    monkeypatch.setattr("lib.change_children.driver.p_surname", mock_p_surname)
    monkeypatch.setattr("lib.change_children.driver.get_occ", mock_get_occ)

    base = SimpleNamespace()
    p = SimpleNamespace(iper=0)
    ipl = [1]

    with pytest.raises(change_children.ChangeChildrenConflict):
        change_children.check_conflict(base, p, "John Doe", 0, ipl)


def test_change_child_no_change(monkeypatch):
    def mock_poi(base, ip):
        return SimpleNamespace(iper=ip)

    def mock_get_iper(p):
        return p.iper

    def mock_p_first_name(base, p):
        return "John"

    def mock_p_surname(base, p):
        return "Doe"

    def mock_get_occ(p):
        return 0

    monkeypatch.setattr("lib.change_children.driver.poi", mock_poi)
    monkeypatch.setattr("lib.change_children.driver.get_iper", mock_get_iper)
    monkeypatch.setattr("lib.change_children.driver.p_first_name", mock_p_first_name)
    monkeypatch.setattr("lib.change_children.driver.p_surname", mock_p_surname)
    monkeypatch.setattr("lib.change_children.driver.get_occ", mock_get_occ)

    conf = SimpleNamespace(env={})
    base = SimpleNamespace()
    changed = []

    result = change_children.change_child(conf, base, "Smith", changed, 5)
    assert result == []


def test_change_child_with_change(monkeypatch):
    def mock_poi(base, ip):
        return SimpleNamespace(iper=ip)

    def mock_get_iper(p):
        return p.iper

    def mock_p_first_name(base, p):
        return "John"

    def mock_p_surname(base, p):
        return "Doe"

    def mock_get_occ(p):
        return 0

    def mock_person_ht_find_all(base, key):
        return []

    def mock_insert_string(base, s):
        return hash(s)

    def mock_gen_person_of_person(p):
        return SimpleNamespace(first_name=None, surname=None, occ=None)

    patched = []
    def mock_patch_person(base, ip, gen_p):
        patched.append((ip, gen_p))

    monkeypatch.setattr("lib.change_children.driver.poi", mock_poi)
    monkeypatch.setattr("lib.change_children.driver.get_iper", mock_get_iper)
    monkeypatch.setattr("lib.change_children.driver.p_first_name", mock_p_first_name)
    monkeypatch.setattr("lib.change_children.driver.p_surname", mock_p_surname)
    monkeypatch.setattr("lib.change_children.driver.get_occ", mock_get_occ)
    monkeypatch.setattr("lib.change_children.gutil.person_ht_find_all", mock_person_ht_find_all)
    monkeypatch.setattr("lib.change_children.driver.insert_string", mock_insert_string)
    monkeypatch.setattr("lib.change_children.driver.gen_person_of_person", mock_gen_person_of_person)
    monkeypatch.setattr("lib.change_children.driver.patch_person", mock_patch_person)

    conf = SimpleNamespace(env={"c5_first_name": "Jane"})
    base = SimpleNamespace()
    changed = []

    result = change_children.change_child(conf, base, "Smith", changed, 5)
    assert len(result) == 1
    assert result[0][0] == ("John", "Doe", 0, 5)
    assert result[0][1] == ("Jane", "Doe", 0, 5)
    assert len(patched) == 1


def test_change_child_first_name_missing(monkeypatch):
    def mock_poi(base, ip):
        return SimpleNamespace(iper=ip)

    def mock_get_iper(p):
        return p.iper

    def mock_p_first_name(base, p):
        return "John"

    def mock_p_surname(base, p):
        return "Doe"

    def mock_get_occ(p):
        return 0

    monkeypatch.setattr("lib.change_children.driver.poi", mock_poi)
    monkeypatch.setattr("lib.change_children.driver.get_iper", mock_get_iper)
    monkeypatch.setattr("lib.change_children.driver.p_first_name", mock_p_first_name)
    monkeypatch.setattr("lib.change_children.driver.p_surname", mock_p_surname)
    monkeypatch.setattr("lib.change_children.driver.get_occ", mock_get_occ)

    conf = SimpleNamespace(env={"c5_first_name": ""})
    base = SimpleNamespace()
    changed = []

    with pytest.raises(change_children.FirstNameMissing):
        change_children.change_child(conf, base, "Smith", changed, 5)


def test_change_child_surname_change(monkeypatch):
    def mock_poi(base, ip):
        return SimpleNamespace(iper=ip)

    def mock_get_iper(p):
        return p.iper

    def mock_p_first_name(base, p):
        return "John"

    def mock_p_surname(base, p):
        return "Doe"

    def mock_get_occ(p):
        return 0

    def mock_person_ht_find_all(base, key):
        return []

    def mock_insert_string(base, s):
        return hash(s)

    def mock_gen_person_of_person(p):
        return SimpleNamespace(first_name=None, surname=None, occ=None)

    patched = []
    def mock_patch_person(base, ip, gen_p):
        patched.append((ip, gen_p))

    monkeypatch.setattr("lib.change_children.driver.poi", mock_poi)
    monkeypatch.setattr("lib.change_children.driver.get_iper", mock_get_iper)
    monkeypatch.setattr("lib.change_children.driver.p_first_name", mock_p_first_name)
    monkeypatch.setattr("lib.change_children.driver.p_surname", mock_p_surname)
    monkeypatch.setattr("lib.change_children.driver.get_occ", mock_get_occ)
    monkeypatch.setattr("lib.change_children.gutil.person_ht_find_all", mock_person_ht_find_all)
    monkeypatch.setattr("lib.change_children.driver.insert_string", mock_insert_string)
    monkeypatch.setattr("lib.change_children.driver.gen_person_of_person", mock_gen_person_of_person)
    monkeypatch.setattr("lib.change_children.driver.patch_person", mock_patch_person)

    conf = SimpleNamespace(env={"c5_surname": "Smith"})
    base = SimpleNamespace()
    changed = []

    result = change_children.change_child(conf, base, "Jones", changed, 5)
    assert len(result) == 1
    assert result[0][1] == ("John", "Smith", 0, 5)


def test_change_child_surname_empty_uses_parent(monkeypatch):
    def mock_poi(base, ip):
        return SimpleNamespace(iper=ip)

    def mock_get_iper(p):
        return p.iper

    def mock_p_first_name(base, p):
        return "John"

    def mock_p_surname(base, p):
        return "Doe"

    def mock_get_occ(p):
        return 0

    def mock_person_ht_find_all(base, key):
        return []

    def mock_insert_string(base, s):
        return hash(s)

    def mock_gen_person_of_person(p):
        return SimpleNamespace(first_name=None, surname=None, occ=None)

    patched = []
    def mock_patch_person(base, ip, gen_p):
        patched.append((ip, gen_p))

    monkeypatch.setattr("lib.change_children.driver.poi", mock_poi)
    monkeypatch.setattr("lib.change_children.driver.get_iper", mock_get_iper)
    monkeypatch.setattr("lib.change_children.driver.p_first_name", mock_p_first_name)
    monkeypatch.setattr("lib.change_children.driver.p_surname", mock_p_surname)
    monkeypatch.setattr("lib.change_children.driver.get_occ", mock_get_occ)
    monkeypatch.setattr("lib.change_children.gutil.person_ht_find_all", mock_person_ht_find_all)
    monkeypatch.setattr("lib.change_children.driver.insert_string", mock_insert_string)
    monkeypatch.setattr("lib.change_children.driver.gen_person_of_person", mock_gen_person_of_person)
    monkeypatch.setattr("lib.change_children.driver.patch_person", mock_patch_person)

    conf = SimpleNamespace(env={"c5_surname": ""})
    base = SimpleNamespace()
    changed = []

    result = change_children.change_child(conf, base, "ParentName", changed, 5)
    assert len(result) == 1
    assert result[0][1] == ("John", "ParentName", 0, 5)


def test_change_child_occ_change(monkeypatch):
    def mock_poi(base, ip):
        return SimpleNamespace(iper=ip)

    def mock_get_iper(p):
        return p.iper

    def mock_p_first_name(base, p):
        return "John"

    def mock_p_surname(base, p):
        return "Doe"

    def mock_get_occ(p):
        return 0

    def mock_person_ht_find_all(base, key):
        return []

    def mock_insert_string(base, s):
        return hash(s)

    def mock_gen_person_of_person(p):
        return SimpleNamespace(first_name=None, surname=None, occ=None)

    patched = []
    def mock_patch_person(base, ip, gen_p):
        patched.append((ip, gen_p))

    monkeypatch.setattr("lib.change_children.driver.poi", mock_poi)
    monkeypatch.setattr("lib.change_children.driver.get_iper", mock_get_iper)
    monkeypatch.setattr("lib.change_children.driver.p_first_name", mock_p_first_name)
    monkeypatch.setattr("lib.change_children.driver.p_surname", mock_p_surname)
    monkeypatch.setattr("lib.change_children.driver.get_occ", mock_get_occ)
    monkeypatch.setattr("lib.change_children.gutil.person_ht_find_all", mock_person_ht_find_all)
    monkeypatch.setattr("lib.change_children.driver.insert_string", mock_insert_string)
    monkeypatch.setattr("lib.change_children.driver.gen_person_of_person", mock_gen_person_of_person)
    monkeypatch.setattr("lib.change_children.driver.patch_person", mock_patch_person)

    conf = SimpleNamespace(env={"c5_occ": "2"})
    base = SimpleNamespace()
    changed = []

    result = change_children.change_child(conf, base, "Smith", changed, 5)
    assert len(result) == 1
    assert result[0][1] == ("John", "Doe", 2, 5)


def test_change_children_multiple(monkeypatch):
    def mock_poi(base, ip):
        return SimpleNamespace(iper=ip)

    def mock_get_iper(p):
        return p.iper

    def mock_p_first_name(base, p):
        return "Child" + str(p.iper)

    def mock_p_surname(base, p):
        return "Doe"

    def mock_get_occ(p):
        return 0

    def mock_person_ht_find_all(base, key):
        return []

    def mock_insert_string(base, s):
        return hash(s)

    def mock_gen_person_of_person(p):
        return SimpleNamespace(first_name=None, surname=None, occ=None)

    patched = []
    def mock_patch_person(base, ip, gen_p):
        patched.append((ip, gen_p))

    monkeypatch.setattr("lib.change_children.driver.poi", mock_poi)
    monkeypatch.setattr("lib.change_children.driver.get_iper", mock_get_iper)
    monkeypatch.setattr("lib.change_children.driver.p_first_name", mock_p_first_name)
    monkeypatch.setattr("lib.change_children.driver.p_surname", mock_p_surname)
    monkeypatch.setattr("lib.change_children.driver.get_occ", mock_get_occ)
    monkeypatch.setattr("lib.change_children.gutil.person_ht_find_all", mock_person_ht_find_all)
    monkeypatch.setattr("lib.change_children.driver.insert_string", mock_insert_string)
    monkeypatch.setattr("lib.change_children.driver.gen_person_of_person", mock_gen_person_of_person)
    monkeypatch.setattr("lib.change_children.driver.patch_person", mock_patch_person)

    conf = SimpleNamespace(env={
        "c1_first_name": "NewChild1",
        "c2_first_name": "NewChild2"
    })
    base = SimpleNamespace()
    ipl = [1, 2]

    result = change_children.change_children(conf, base, "Smith", ipl)
    assert len(result) == 2


def test_change_children_empty_list():
    conf = SimpleNamespace(env={})
    base = SimpleNamespace()

    result = change_children.change_children(conf, base, "Smith", [])
    assert result == []


def test_only_printable():
    result = change_children._only_printable("Hello\x00World\x01!")
    assert result == "HelloWorld!"


def test_only_printable_with_newlines():
    result = change_children._only_printable("Hello\nWorld\tTest")
    assert result == "Hello\nWorld\tTest"
