import os
import sys
import tempfile
import shutil
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'bin'))

from ged2gwb import GedcomParser, GedcomLine, DatabaseBuilder
from lib import gwdef, adef


def test_parse_line_simple():
    parser = GedcomParser('dummy.ged')
    line = parser.parse_line('0 HEAD')
    assert line.level == 0
    assert line.xref is None
    assert line.tag == 'HEAD'
    assert line.value == ''


def test_parse_line_with_value():
    parser = GedcomParser('dummy.ged')
    line = parser.parse_line('1 CHAR UTF-8')
    assert line.level == 1
    assert line.xref is None
    assert line.tag == 'CHAR'
    assert line.value == 'UTF-8'


def test_parse_line_with_xref():
    parser = GedcomParser('dummy.ged')
    line = parser.parse_line('0 @I1@ INDI')
    assert line.level == 0
    assert line.xref == '@I1@'
    assert line.tag == 'INDI'
    assert line.value == ''


def test_parse_line_with_xref_and_value():
    parser = GedcomParser('dummy.ged')
    line = parser.parse_line('1 NAME John /Doe/')
    assert line.level == 1
    assert line.xref is None
    assert line.tag == 'NAME'
    assert line.value == 'John /Doe/'


def test_parse_date():
    parser = GedcomParser('dummy.ged')
    cdate = parser.parse_date('29 MAY 1917')
    assert cdate is not None
    assert isinstance(cdate, adef.CdateDate)
    assert isinstance(cdate.date, adef.DateGreg)
    assert cdate.date.dmy.day == 29
    assert cdate.date.dmy.month == 5
    assert cdate.date.dmy.year == 1917


def test_parse_date_invalid():
    parser = GedcomParser('dummy.ged')
    cdate = parser.parse_date('invalid')
    assert cdate is not None
    assert isinstance(cdate, adef.CdateText)
    assert cdate.text == 'invalid'


def test_parse_name():
    parser = GedcomParser('dummy.ged')
    first, surname, occ, _, suffix = parser.parse_name('John Fitzgerald /Kennedy/')
    assert first == 'John Fitzgerald'
    assert surname == 'Kennedy'
    assert occ == 0


def test_parse_name_with_suffix():
    parser = GedcomParser('dummy.ged')
    first, surname, occ, _, suffix = parser.parse_name('John Fitzgerald /Kennedy Jr./')
    assert first == 'John Fitzgerald'
    assert surname == 'Kennedy Jr.'


def test_gedcom_parser_integration():
    test_gedcom = """0 HEAD
1 SOUR GeneWeb
1 GEDC
2 VERS 5.5.1
2 FORM LINEAGE-LINKED
1 CHAR UTF-8
0 @I1@ INDI
1 NAME John /Doe/
1 SEX M
1 BIRT
2 DATE 1 JAN 1900
2 PLAC New York
0 @F1@ FAM
1 HUSB @I1@
1 MARR
2 DATE 1 JAN 1920
0 TRLR
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.ged', delete=False) as f:
        f.write(test_gedcom)
        test_file = f.name

    try:
        parser = GedcomParser(test_file)
        parser.load()

        assert len(parser.individuals) == 1
        assert '@I1@' in parser.individuals

        person_data = parser.individuals['@I1@']
        person = person_data['person']
        assert person.first_name == 'John'
        assert person.surname == 'Doe'
        assert person.sex == gwdef.Sex.MALE

        assert len(parser.families) == 1
        assert '@F1@' in parser.families

    finally:
        if os.path.exists(test_file):
            os.unlink(test_file)


def test_database_builder_integration():
    test_gedcom = """0 HEAD
1 SOUR GeneWeb
1 GEDC
2 VERS 5.5.1
2 FORM LINEAGE-LINKED
1 CHAR UTF-8
0 @I1@ INDI
1 NAME Alice /Smith/
1 SEX F
1 BIRT
2 DATE 15 MAR 1950
2 PLAC Boston
0 @I2@ INDI
1 NAME Bob /Smith/
1 SEX M
0 @F1@ FAM
1 HUSB @I2@
1 WIFE @I1@
1 MARR
2 DATE 10 JUN 1970
0 TRLR
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.ged', delete=False) as f:
        f.write(test_gedcom)
        test_file = f.name

    temp_dir = tempfile.mkdtemp()
    output_path = os.path.join(temp_dir, 'test.gwb')

    try:
        parser = GedcomParser(test_file)
        parser.load()

        builder = DatabaseBuilder(parser)
        builder.build(output_path)

        assert os.path.exists(output_path)
        assert os.path.exists(os.path.join(output_path, 'base'))
        assert os.path.exists(os.path.join(output_path, 'base.acc'))
        assert os.path.exists(os.path.join(output_path, 'names.inx'))

    finally:
        if os.path.exists(test_file):
            os.unlink(test_file)
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)


def test_parse_date_with_precision():
    parser = GedcomParser('dummy.ged')

    cdate = parser.parse_date('ABT 1950')
    assert cdate is not None
    assert isinstance(cdate, adef.CdateDate)

    cdate = parser.parse_date('BEF 1 JAN 1900')
    assert cdate is not None

    cdate = parser.parse_date('AFT 1920')
    assert cdate is not None


def test_get_merged_value():
    parser = GedcomParser('dummy.ged')
    record = GedcomLine(0, '@I1@', 'INDI', '')
    note_line = GedcomLine(1, None, 'NOTE', 'First line')
    conc_line = GedcomLine(2, None, 'CONC', ' continued')
    cont_line = GedcomLine(2, None, 'CONT', 'New line')

    note_line.children.append(conc_line)
    note_line.children.append(cont_line)
    record.children.append(note_line)

    merged = parser.get_merged_value(record, 'NOTE')
    assert 'First line continued' in merged
    assert 'New line' in merged


def test_parse_person_with_occupation():
    test_gedcom = """0 HEAD
1 SOUR GeneWeb
1 GEDC
2 VERS 5.5.1
2 FORM LINEAGE-LINKED
1 CHAR UTF-8
0 @I1@ INDI
1 NAME John /Doe/
1 SEX M
1 OCCU Engineer
1 NOTE This is a note
0 TRLR
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.ged', delete=False) as f:
        f.write(test_gedcom)
        test_file = f.name

    try:
        parser = GedcomParser(test_file)
        parser.load()

        person_data = parser.individuals['@I1@']
        person = person_data['person']
        assert person.occupation == 'Engineer'
        assert person.notes == 'This is a note'

    finally:
        if os.path.exists(test_file):
            os.unlink(test_file)


def test_parse_family_with_divorce():
    test_gedcom = """0 HEAD
1 SOUR GeneWeb
1 GEDC
2 VERS 5.5.1
2 FORM LINEAGE-LINKED
1 CHAR UTF-8
0 @I1@ INDI
1 NAME Alice /Smith/
1 SEX F
0 @I2@ INDI
1 NAME Bob /Smith/
1 SEX M
0 @F1@ FAM
1 HUSB @I2@
1 WIFE @I1@
1 MARR
2 DATE 10 JUN 1970
1 DIV
2 DATE 15 DEC 1980
0 TRLR
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.ged', delete=False) as f:
        f.write(test_gedcom)
        test_file = f.name

    try:
        parser = GedcomParser(test_file)
        parser.load()

        family_data = parser.families['@F1@']
        family = family_data['family']
        assert isinstance(family.divorce, gwdef.DivorceWithDate)

    finally:
        if os.path.exists(test_file):
            os.unlink(test_file)


def test_parse_line_edge_cases():
    parser = GedcomParser('dummy.ged')

    empty_line = parser.parse_line('')
    assert empty_line is None

    short_line = parser.parse_line('0')
    assert short_line is None

    line_with_newline = parser.parse_line('0 HEAD\n')
    assert line_with_newline.tag == 'HEAD'


def test_parse_date_month_year():
    parser = GedcomParser('dummy.ged')

    cdate = parser.parse_date('MAY 1917')
    assert cdate is not None
    assert isinstance(cdate, adef.CdateDate)
    assert cdate.date.dmy.month == 5
    assert cdate.date.dmy.year == 1917
    assert cdate.date.dmy.day == 0


def test_parse_date_year_only():
    parser = GedcomParser('dummy.ged')

    cdate = parser.parse_date('1950')
    assert cdate is not None
    assert isinstance(cdate, adef.CdateDate)
    assert cdate.date.dmy.year == 1950
    assert cdate.date.dmy.month == 0
    assert cdate.date.dmy.day == 0


def test_parse_date_empty():
    parser = GedcomParser('dummy.ged')

    cdate = parser.parse_date('')
    assert cdate is None

    cdate = parser.parse_date(None)
    assert cdate is None


def test_parse_name_edge_cases():
    parser = GedcomParser('dummy.ged')

    first, surname, occ, _, suffix = parser.parse_name('')
    assert first == ''
    assert surname == ''

    first, surname, occ, _, suffix = parser.parse_name('SingleName')
    assert first == 'SingleName'
    assert surname == ''


def test_detect_encoding_utf8():
    test_gedcom = """0 HEAD
1 CHAR UTF-8
0 TRLR
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.ged', delete=False) as f:
        f.write(test_gedcom)
        test_file = f.name

    try:
        parser = GedcomParser(test_file)
        encoding = parser.detect_encoding()
        assert encoding in ['utf-8', 'ansel', 'ascii', 'utf-16']

    finally:
        if os.path.exists(test_file):
            os.unlink(test_file)


def test_parse_person_with_baptism():
    test_gedcom = """0 HEAD
1 SOUR GeneWeb
1 GEDC
2 VERS 5.5.1
2 FORM LINEAGE-LINKED
1 CHAR UTF-8
0 @I1@ INDI
1 NAME John /Doe/
1 SEX M
1 BAPM
2 DATE 15 FEB 1900
2 PLAC Boston
0 TRLR
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.ged', delete=False) as f:
        f.write(test_gedcom)
        test_file = f.name

    try:
        parser = GedcomParser(test_file)
        parser.load()

        person_data = parser.individuals['@I1@']
        person = person_data['person']
        assert isinstance(person.baptism, adef.CdateDate)

    finally:
        if os.path.exists(test_file):
            os.unlink(test_file)


def test_parse_person_with_death():
    test_gedcom = """0 HEAD
1 SOUR GeneWeb
1 GEDC
2 VERS 5.5.1
2 FORM LINEAGE-LINKED
1 CHAR UTF-8
0 @I1@ INDI
1 NAME John /Doe/
1 SEX M
1 DEAT
2 DATE 1 JAN 1980
2 PLAC New York
0 TRLR
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.ged', delete=False) as f:
        f.write(test_gedcom)
        test_file = f.name

    try:
        parser = GedcomParser(test_file)
        parser.load()

        person_data = parser.individuals['@I1@']
        person = person_data['person']
        assert isinstance(person.death, gwdef.DeadDontKnowWhen)
        assert person.death_place == 'New York'

    finally:
        if os.path.exists(test_file):
            os.unlink(test_file)


def test_parse_person_with_burial():
    test_gedcom = """0 HEAD
1 SOUR GeneWeb
1 GEDC
2 VERS 5.5.1
2 FORM LINEAGE-LINKED
1 CHAR UTF-8
0 @I1@ INDI
1 NAME John /Doe/
1 SEX M
1 DEAT Y
1 BURI
2 DATE 5 JAN 1980
2 PLAC Cemetery
0 TRLR
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.ged', delete=False) as f:
        f.write(test_gedcom)
        test_file = f.name

    try:
        parser = GedcomParser(test_file)
        parser.load()

        person_data = parser.individuals['@I1@']
        person = person_data['person']
        assert isinstance(person.burial, gwdef.Buried)
        assert isinstance(person.burial.date, adef.CdateDate)
        assert person.burial_place == 'Cemetery'

    finally:
        if os.path.exists(test_file):
            os.unlink(test_file)


def test_parse_family_with_children():
    test_gedcom = """0 HEAD
1 SOUR GeneWeb
1 GEDC
2 VERS 5.5.1
2 FORM LINEAGE-LINKED
1 CHAR UTF-8
0 @I1@ INDI
1 NAME Alice /Smith/
1 SEX F
0 @I2@ INDI
1 NAME Bob /Smith/
1 SEX M
0 @I3@ INDI
1 NAME Charlie /Smith/
1 SEX M
0 @F1@ FAM
1 HUSB @I2@
1 WIFE @I1@
1 CHIL @I3@
0 TRLR
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.ged', delete=False) as f:
        f.write(test_gedcom)
        test_file = f.name

    try:
        parser = GedcomParser(test_file)
        parser.load()

        family_data = parser.families['@F1@']
        assert '@I3@' in family_data['children']

    finally:
        if os.path.exists(test_file):
            os.unlink(test_file)


def test_parse_person_female():
    test_gedcom = """0 HEAD
1 SOUR GeneWeb
1 GEDC
2 VERS 5.5.1
2 FORM LINEAGE-LINKED
1 CHAR UTF-8
0 @I1@ INDI
1 NAME Jane /Doe/
1 SEX F
0 TRLR
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.ged', delete=False) as f:
        f.write(test_gedcom)
        test_file = f.name

    try:
        parser = GedcomParser(test_file)
        parser.load()

        person_data = parser.individuals['@I1@']
        person = person_data['person']
        assert person.sex == gwdef.Sex.FEMALE

    finally:
        if os.path.exists(test_file):
            os.unlink(test_file)


def test_parse_person_neuter_sex():
    test_gedcom = """0 HEAD
1 SOUR GeneWeb
1 GEDC
2 VERS 5.5.1
2 FORM LINEAGE-LINKED
1 CHAR UTF-8
0 @I1@ INDI
1 NAME Unknown /Person/
0 TRLR
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.ged', delete=False) as f:
        f.write(test_gedcom)
        test_file = f.name

    try:
        parser = GedcomParser(test_file)
        parser.load()

        person_data = parser.individuals['@I1@']
        person = person_data['person']
        assert person.sex == gwdef.Sex.NEUTER

    finally:
        if os.path.exists(test_file):
            os.unlink(test_file)


def test_get_merged_value_not_found():
    parser = GedcomParser('dummy.ged')
    record = GedcomLine(0, '@I1@', 'INDI', '')

    merged = parser.get_merged_value(record, 'NONEXISTENT', 'default')
    assert merged == 'default'
