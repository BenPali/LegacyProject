import pytest
from lib.notes_links import (
    check_file_name,
    misc_notes_link,
    add_in_db,
    update_db,
    WLPage,
    WLPerson,
    WLWizard,
    WLNone,
    CHAR_DIR_SEP,
    DIR_SEP
)
from lib.gwdef import NLDB

def test_char_dir_sep():
    assert CHAR_DIR_SEP == ':'
    assert DIR_SEP == ":"

def test_check_file_name_simple():
    result = check_file_name("page")
    assert result == ([], "page")

def test_check_file_name_with_path():
    result = check_file_name("dir:page")
    assert result == (["dir"], "page")

def test_check_file_name_multiple_dirs():
    result = check_file_name("dir1:dir2:page")
    assert result == (["dir1", "dir2"], "page")

def test_check_file_name_with_valid_chars():
    result = check_file_name("my-file_2.txt")
    assert result == ([], "my-file_2.txt")

def test_check_file_name_with_numbers():
    result = check_file_name("page123")
    assert result == ([], "page123")

def test_check_file_name_invalid_char():
    result = check_file_name("page@name")
    assert result is None

def test_check_file_name_empty():
    result = check_file_name("")
    assert result is None

def test_check_file_name_trailing_sep():
    result = check_file_name("dir:")
    assert result is None

def test_check_file_name_leading_sep():
    result = check_file_name(":page")
    assert result is None

def test_check_file_name_double_sep():
    result = check_file_name("dir::page")
    assert result is None

def test_misc_notes_link_wlnone_empty():
    result = misc_notes_link("", 0)
    assert isinstance(result, WLNone)
    assert result.pos == 0
    assert result.content == ""

def test_misc_notes_link_wlnone_no_brackets():
    result = misc_notes_link("hello world", 0)
    assert isinstance(result, WLNone)
    assert result.pos == 11
    assert result.content == "hello world"

def test_misc_notes_link_wlnone_single_bracket():
    result = misc_notes_link("[hello", 0)
    assert isinstance(result, WLNone)
    assert result.pos == 6
    assert result.content == "[hello"

def test_misc_notes_link_wlnone_percent():
    result = misc_notes_link("hello%world", 0)
    assert isinstance(result, WLNone)
    assert result.pos == 5
    assert result.content == "hello"

def test_misc_notes_link_wlnone_quote():
    result = misc_notes_link("hello'world", 0)
    assert isinstance(result, WLNone)
    assert result.pos == 5
    assert result.content == "hello"

def test_misc_notes_link_wlnone_brace():
    result = misc_notes_link("hello{world", 0)
    assert isinstance(result, WLNone)
    assert result.pos == 5
    assert result.content == "hello"

def test_misc_notes_link_wlnone_double_bracket():
    result = misc_notes_link("hello[[world", 0)
    assert isinstance(result, WLNone)
    assert result.pos == 5
    assert result.content == "hello"

def test_misc_notes_link_page_simple():
    result = misc_notes_link("[[[page/text]]]", 0)
    assert isinstance(result, WLPage)
    assert result.pos == 15
    assert result.fname == "page"
    assert result.anchor == ""
    assert result.text == "text"
    assert result.pg_path == ([], "page")

def test_misc_notes_link_page_with_dir():
    result = misc_notes_link("[[[dir:page/text]]]", 0)
    assert isinstance(result, WLPage)
    assert result.pos == 19
    assert result.fname == "dir:page"
    assert result.text == "text"
    assert result.pg_path == (["dir"], "page")

def test_misc_notes_link_page_with_anchor():
    result = misc_notes_link("[[[page#anchor/text]]]", 0)
    assert isinstance(result, WLPage)
    assert result.pos == 22
    assert result.fname == "page"
    assert result.anchor == "anchor"
    assert result.text == "text"

def test_misc_notes_link_page_invalid_name():
    result = misc_notes_link("[[[page@invalid/text]]]", 0)
    assert isinstance(result, WLNone)

def test_misc_notes_link_page_too_short():
    result = misc_notes_link("[[[a]]]", 0)
    assert isinstance(result, WLPage)
    assert result.fname == "a"

def test_misc_notes_link_page_no_close():
    result = misc_notes_link("[[[page/text", 0)
    assert isinstance(result, WLNone)

def test_misc_notes_link_person_simple():
    result = misc_notes_link("[[john/smith]]", 0)
    assert isinstance(result, WLPerson)
    assert result.pos == 14
    assert result.key == ("john", "smith", 0)
    assert result.name == "john smith"
    assert result.text is None

def test_misc_notes_link_person_with_occ():
    result = misc_notes_link("[[john/smith/1]]", 0)
    assert isinstance(result, WLPerson)
    assert result.pos == 16
    assert result.key == ("john", "smith", 1)
    assert result.name == "john smith"
    assert result.text is None

def test_misc_notes_link_person_with_name():
    result = misc_notes_link("[[john/smith/0/John Smith Jr]]", 0)
    assert isinstance(result, WLPerson)
    assert result.pos == 30
    assert result.key == ("john", "smith", 0)
    assert result.name == "John Smith Jr"
    assert result.text is None

def test_misc_notes_link_person_with_text():
    result = misc_notes_link("[[john/smith;See also]]", 0)
    assert isinstance(result, WLPerson)
    assert result.key == ("john", "smith", 0)
    assert result.text == "See also"

def test_misc_notes_link_person_occ_in_name_field():
    result = misc_notes_link("[[john/smith/2]]", 0)
    assert isinstance(result, WLPerson)
    assert result.key == ("john", "smith", 2)

def test_misc_notes_link_person_no_surname():
    result = misc_notes_link("[[john]]", 0)
    assert isinstance(result, WLNone)

def test_misc_notes_link_person_too_short():
    result = misc_notes_link("[[j]]", 0)
    assert isinstance(result, WLNone)

def test_misc_notes_link_wizard_simple():
    result = misc_notes_link("[[w:wizard/name]]", 0)
    assert isinstance(result, WLWizard)
    assert result.pos == 17
    assert result.wiz == "wizard"
    assert result.wiz_name == "name"

def test_misc_notes_link_wizard_no_name():
    result = misc_notes_link("[[w:wizard]]", 0)
    assert isinstance(result, WLWizard)
    assert result.pos == 12
    assert result.wiz == "wizard"
    assert result.wiz_name == ""

def test_misc_notes_link_at_offset():
    result = misc_notes_link("text[[john/smith]]more", 4)
    assert isinstance(result, WLPerson)
    assert result.pos == 18
    assert result.key == ("john", "smith", 0)

def test_misc_notes_link_nested_brackets():
    result = misc_notes_link("[[john/smith]]extra", 0)
    assert isinstance(result, WLPerson)
    assert result.key == ("john", "smith", 0)
    assert result.pos == 14

def test_add_in_db_empty():
    db = []
    who = NLDB.PgNotes()
    data = ([], [])
    result = add_in_db(db, who, data)
    assert result == []

def test_add_in_db_with_notes():
    db = []
    who = NLDB.PgNotes()
    data = (["note1", "note2"], [])
    result = add_in_db(db, who, data)
    assert len(result) == 1
    assert result[0] == (who, (["note1", "note2"], []))

def test_add_in_db_with_persons():
    db = []
    who = NLDB.PgNotes()
    key = ("john", "smith", 0)
    ind = NLDB.Ind(ln_txt="John Smith", ln_pos=10)
    data = ([], [(key, ind)])
    result = add_in_db(db, who, data)
    assert len(result) == 1
    assert result[0] == (who, ([], [(key, ind)]))

def test_add_in_db_replace_existing():
    who = NLDB.PgNotes()
    old_data = (["old"], [])
    db = [(who, old_data)]
    new_data = (["new"], [])
    result = add_in_db(db, who, new_data)
    assert len(result) == 1
    assert result[0] == (who, (["new"], []))

def test_add_in_db_remove_when_empty():
    who = NLDB.PgNotes()
    db = [(who, (["note"], []))]
    result = add_in_db(db, who, ([], []))
    assert len(result) == 0

def test_add_in_db_preserve_others():
    who1 = NLDB.PgNotes()
    who2 = NLDB.PgMisc(name="misc")
    db = [
        (who1, (["note1"], [])),
        (who2, (["note2"], []))
    ]
    result = add_in_db(db, who1, (["updated"], []))
    assert len(result) == 2
    assert (who2, (["note2"], [])) in result
    assert (who1, (["updated"], [])) in result

def test_update_db_integration():
    class MockBase:
        def __init__(self):
            self.nldb = []
            self.func = self

        def read_nldb(self):
            return self.nldb

        def write_nldb(self, db):
            self.nldb = db

    base = MockBase()
    who = NLDB.PgNotes()
    data = (["note"], [])

    update_db(base, who, data)

    assert len(base.nldb) == 1
    assert (who, data) in base.nldb

def test_misc_notes_link_page_multiple_dirs():
    result = misc_notes_link("[[[dir1:dir2:page/text]]]", 0)
    assert isinstance(result, WLPage)
    assert result.pg_path == (["dir1", "dir2"], "page")

def test_misc_notes_link_person_case_sensitive():
    result = misc_notes_link("[[John/Smith]]", 0)
    assert isinstance(result, WLPerson)
    assert result.key[0] == "john"
    assert result.key[1] == "smith"

def test_check_file_name_underscores():
    result = check_file_name("my_file_name")
    assert result == ([], "my_file_name")

def test_check_file_name_hyphens():
    result = check_file_name("my-file-name")
    assert result == ([], "my-file-name")

def test_check_file_name_dots():
    result = check_file_name("my.file.name")
    assert result == ([], "my.file.name")

def test_misc_notes_link_complex_person():
    result = misc_notes_link("[[Jean-Paul/D'Arcy/2/Jean Paul D'Arcy II]]", 0)
    assert isinstance(result, WLPerson)
    assert result.key[2] == 2
    assert result.name == "Jean Paul D'Arcy II"

def test_add_in_db_with_different_page_types():
    db = []
    pg_notes = NLDB.PgNotes()
    pg_misc = NLDB.PgMisc(name="test")
    pg_wizard = NLDB.PgWizard(name="wiz")

    result = add_in_db(db, pg_notes, (["n1"], []))
    result = add_in_db(result, pg_misc, (["n2"], []))
    result = add_in_db(result, pg_wizard, (["n3"], []))

    assert len(result) == 3
    assert (pg_notes, (["n1"], [])) in result
    assert (pg_misc, (["n2"], [])) in result
    assert (pg_wizard, (["n3"], [])) in result
