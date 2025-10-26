#!/usr/bin/env python3

import sys
import os
import re
from pathlib import Path
from typing import Optional, List, Tuple

sys.path.insert(0, str(Path(__file__).parent.parent))

from lib import database, gwdef, adef, name, iovalue, secure, ansel


class GedcomLine:
    def __init__(self, level, xref, tag, value):
        self.level = level
        self.xref = xref
        self.tag = tag
        self.value = value
        self.children = []


class GedcomParser:
    def __init__(self, filename):
        self.filename = filename
        self.individuals = {}
        self.families = {}
        self.xref_map = {}
        self.encoding = 'utf-8'
        self.source_encoding = None
        self.warnings = []
        self.errors = []

    def parse_line(self, line):
        line = line.rstrip('\n\r')
        if not line:
            return None

        parts = line.split(' ', 2)
        level = int(parts[0])

        if len(parts) < 2:
            return None

        xref = None
        tag = parts[1]
        value = ''

        if tag.startswith('@') and tag.endswith('@'):
            xref = tag
            if len(parts) > 2:
                tag_value = parts[2].split(' ', 1)
                tag = tag_value[0]
                value = tag_value[1] if len(tag_value) > 1 else ''
        else:
            value = parts[2] if len(parts) > 2 else ''

        return GedcomLine(level, xref, tag, value)

    def parse_file(self):
        with open(self.filename, 'r', encoding='utf-8') as f:
            lines = [self.parse_line(line) for line in f]
            lines = [l for l in lines if l is not None]

        stack = []
        for line in lines:
            while stack and stack[-1].level >= line.level:
                stack.pop()

            if stack:
                stack[-1].children.append(line)

            stack.append(line)

        root_records = [l for l in lines if l.level == 0]
        return root_records

    def find_child(self, record, tag):
        for child in record.children:
            if child.tag == tag:
                return child
        return None

    def find_children(self, record, tag):
        return [child for child in record.children if child.tag == tag]

    def get_value(self, record, tag, default=''):
        child = self.find_child(record, tag)
        return child.value if child else default

    def get_merged_value(self, record, tag, default=''):
        child = self.find_child(record, tag)
        if not child:
            return default
        value = child.value
        for cont_child in child.children:
            if cont_child.tag == 'CONC':
                value += cont_child.value
            elif cont_child.tag == 'CONT':
                value += '\n' + cont_child.value
        return value

    def detect_encoding(self):
        with open(self.filename, 'rb') as f:
            header = f.read(1000)
            if b'ANSEL' in header or b'ANSI' in header:
                return 'ansel'
            elif b'UTF-8' in header or b'UTF8' in header:
                return 'utf-8'
            elif b'UNICODE' in header:
                return 'utf-16'
            elif b'ASCII' in header:
                return 'ascii'
        return 'utf-8'

    def convert_from_ansel(self, text):
        if isinstance(text, bytes):
            return ansel.ansel_to_utf8(text.decode('latin-1'))
        return ansel.ansel_to_utf8(text)

    def parse_date(self, date_str):
        if not date_str:
            return None

        date_str = date_str.strip()

        precision_map = {
            'ABT': adef.Precision.ABOUT,
            'ABOUT': adef.Precision.ABOUT,
            'CAL': adef.Precision.MAYBE,
            'CALCULATED': adef.Precision.MAYBE,
            'EST': adef.Precision.MAYBE,
            'ESTIMATED': adef.Precision.MAYBE,
            'BEF': adef.Precision.BEFORE,
            'BEFORE': adef.Precision.BEFORE,
            'AFT': adef.Precision.AFTER,
            'AFTER': adef.Precision.AFTER,
        }

        prec = adef.Precision.SURE
        parts = date_str.split()

        if parts and parts[0].upper() in precision_map:
            prec = precision_map[parts[0].upper()]
            parts = parts[1:]
            date_str = ' '.join(parts)

        if not parts:
            return None

        if 'FROM' in date_str.upper() or 'TO' in date_str.upper():
            return self.parse_simple_date(' '.join(parts), prec)

        if 'BET' in date_str.upper() or 'BETWEEN' in date_str.upper() or 'AND' in date_str.upper():
            return self.parse_simple_date(' '.join(parts), prec)

        return self.parse_simple_date(date_str, prec)

    def parse_simple_date(self, date_str, prec=adef.Precision.SURE):
        if not date_str:
            return None

        month_map = {
            'JAN': 1, 'FEB': 2, 'MAR': 3, 'APR': 4, 'MAY': 5, 'JUN': 6,
            'JUL': 7, 'AUG': 8, 'SEP': 9, 'OCT': 10, 'NOV': 11, 'DEC': 12
        }

        parts = date_str.split()

        if len(parts) == 1:
            try:
                year = int(parts[0])
                dmy = adef.Dmy(day=0, month=0, year=year, prec=prec, delta=0)
                date_greg = adef.DateGreg(dmy=dmy, calendar=adef.Calendar.GREGORIAN)
                return adef.CdateDate(date=date_greg)
            except:
                return adef.CdateText(text=date_str)

        if len(parts) == 2:
            try:
                month_str = parts[0]
                year = int(parts[1])
                month = month_map.get(month_str.upper(), 0)
                dmy = adef.Dmy(day=0, month=month, year=year, prec=prec, delta=0)
                date_greg = adef.DateGreg(dmy=dmy, calendar=adef.Calendar.GREGORIAN)
                return adef.CdateDate(date=date_greg)
            except:
                return adef.CdateText(text=date_str)

        if len(parts) == 3:
            try:
                day = int(parts[0])
                month_str = parts[1]
                year = int(parts[2])
                month = month_map.get(month_str.upper(), 0)
                dmy = adef.Dmy(day=day, month=month, year=year, prec=prec, delta=0)
                date_greg = adef.DateGreg(dmy=dmy, calendar=adef.Calendar.GREGORIAN)
                return adef.CdateDate(date=date_greg)
            except:
                return adef.CdateText(text=date_str)

        return adef.CdateText(text=date_str)

    def parse_name(self, name_str):
        if not name_str:
            return '', '', 0, '', ''

        surname_match = re.search(r'/([^/]+)/', name_str)
        if surname_match:
            surname = surname_match.group(1)
            parts = name_str.split('/')
            first_name = parts[0].strip() if len(parts) > 0 else ''
            suffix = parts[2].strip() if len(parts) > 2 else ''
        else:
            parts = name_str.split()
            first_name = ' '.join(parts[:-1]) if len(parts) > 1 else name_str
            surname = parts[-1] if len(parts) > 1 else ''
            suffix = ''

        return first_name, surname, 0, '', suffix

    def parse_person(self, record):
        name_str = self.get_value(record, 'NAME')
        first_name, surname, occ, _, suffix = self.parse_name(name_str)

        public_name = self.get_value(record, 'NICK')
        occupation = self.get_merged_value(record, 'OCCU')

        sex_str = self.get_value(record, 'SEX', 'U')
        sex = gwdef.Sex.MALE if sex_str == 'M' else gwdef.Sex.FEMALE if sex_str == 'F' else gwdef.Sex.NEUTER

        birth_rec = self.find_child(record, 'BIRT')
        birth_date = None
        birth_place = ''
        birth_note = ''
        birth_src = ''
        if birth_rec:
            date_str = self.get_value(birth_rec, 'DATE')
            birth_date = self.parse_date(date_str)
            birth_place = self.get_value(birth_rec, 'PLAC')
            birth_note = self.get_merged_value(birth_rec, 'NOTE')
            birth_src = self.get_merged_value(birth_rec, 'SOUR')

        baptism_rec = self.find_child(record, 'BAPM') or self.find_child(record, 'CHR')
        baptism_date = None
        baptism_place = ''
        baptism_note = ''
        baptism_src = ''
        if baptism_rec:
            date_str = self.get_value(baptism_rec, 'DATE')
            baptism_date = self.parse_date(date_str)
            baptism_place = self.get_value(baptism_rec, 'PLAC')
            baptism_note = self.get_merged_value(baptism_rec, 'NOTE')
            baptism_src = self.get_merged_value(baptism_rec, 'SOUR')

        death_rec = self.find_child(record, 'DEAT')
        death_place = ''
        death_note = ''
        death_src = ''
        death_type = gwdef.NotDead()
        if death_rec:
            date_str = self.get_value(death_rec, 'DATE')
            death_date = self.parse_date(date_str)
            death_place = self.get_value(death_rec, 'PLAC')
            death_note = self.get_merged_value(death_rec, 'NOTE')
            death_src = self.get_merged_value(death_rec, 'SOUR')
            if death_date:
                death_type = gwdef.DeadDontKnowWhen()
            else:
                death_type = gwdef.DontKnowIfDead()

        burial_rec = self.find_child(record, 'BURI')
        burial_type = gwdef.UnknownBurial()
        burial_place = ''
        burial_note = ''
        burial_src = ''
        if burial_rec:
            date_str = self.get_value(burial_rec, 'DATE')
            burial_date = self.parse_date(date_str)
            burial_place = self.get_value(burial_rec, 'PLAC')
            burial_note = self.get_merged_value(burial_rec, 'NOTE')
            burial_src = self.get_merged_value(burial_rec, 'SOUR')
            if burial_date:
                burial_type = gwdef.Buried(date=burial_date)

        cremation_rec = self.find_child(record, 'CREM')
        if cremation_rec:
            date_str = self.get_value(cremation_rec, 'DATE')
            cremation_date = self.parse_date(date_str)
            if cremation_date:
                burial_type = gwdef.Cremated(date=cremation_date)
            burial_place = self.get_value(cremation_rec, 'PLAC')

        notes = self.get_merged_value(record, 'NOTE')
        psources = self.get_merged_value(record, 'SOUR')

        image = ''
        obje_rec = self.find_child(record, 'OBJE')
        if obje_rec:
            image = self.get_value(obje_rec, 'FILE')

        person = gwdef.GenPerson(
            first_name=first_name,
            surname=surname,
            occ=occ,
            image=image,
            public_name=public_name,
            qualifiers=[],
            aliases=[],
            first_names_aliases=[],
            surnames_aliases=[],
            titles=[],
            rparents=[],
            related=[],
            occupation=occupation,
            sex=sex,
            access=gwdef.Access.IF_TITLES,
            birth=birth_date or adef.CdateNone(),
            birth_place=birth_place,
            birth_note=birth_note,
            birth_src=birth_src,
            baptism=baptism_date or adef.CdateNone(),
            baptism_place=baptism_place,
            baptism_note=baptism_note,
            baptism_src=baptism_src,
            death=death_type,
            death_place=death_place,
            death_note=death_note,
            death_src=death_src,
            burial=burial_type,
            burial_place=burial_place,
            burial_note=burial_note,
            burial_src=burial_src,
            pevents=[],
            notes=notes,
            psources=psources,
            key_index=''
        )

        fams_refs = [c.value for c in self.find_children(record, 'FAMS')]
        famc_refs = [c.value for c in self.find_children(record, 'FAMC')]

        return person, fams_refs, famc_refs

    def parse_family(self, record):
        husb_ref = self.get_value(record, 'HUSB')
        wife_ref = self.get_value(record, 'WIFE')
        chil_refs = [c.value for c in self.find_children(record, 'CHIL')]

        marr_rec = self.find_child(record, 'MARR')
        marr_date = None
        marr_place = ''
        marr_note = ''
        marr_src = ''
        relation = gwdef.RelationKind.MARRIED
        if marr_rec:
            date_str = self.get_value(marr_rec, 'DATE')
            marr_date = self.parse_date(date_str)
            marr_place = self.get_value(marr_rec, 'PLAC')
            marr_note = self.get_merged_value(marr_rec, 'NOTE')
            marr_src = self.get_merged_value(marr_rec, 'SOUR')
        else:
            if self.find_child(record, '_NMR'):
                relation = gwdef.RelationKind.NOT_MARRIED
            else:
                relation = gwdef.RelationKind.NO_MENTION

        div_rec = self.find_child(record, 'DIV')
        divorce = gwdef.NotDivorced()
        if div_rec:
            date_str = self.get_value(div_rec, 'DATE')
            div_date = self.parse_date(date_str)
            if div_date:
                divorce = gwdef.DivorceWithDate(date=div_date)

        comment = self.get_merged_value(record, 'NOTE')
        fsources = self.get_merged_value(record, 'SOUR')

        family = gwdef.GenFamily(
            marriage=marr_date or adef.CdateNone(),
            marriage_place=marr_place,
            marriage_note=marr_note,
            marriage_src=marr_src,
            witnesses=[],
            relation=relation,
            divorce=divorce,
            fevents=[],
            comment=comment,
            origin_file='',
            fsources=fsources,
            fam_index=-1
        )

        return family, husb_ref, wife_ref, chil_refs

    def load(self):
        records = self.parse_file()

        for record in records:
            if record.tag == 'INDI' and record.xref:
                person, fams_refs, famc_refs = self.parse_person(record)
                self.individuals[record.xref] = {
                    'person': person,
                    'fams': fams_refs,
                    'famc': famc_refs
                }
            elif record.tag == 'FAM' and record.xref:
                family, husb_ref, wife_ref, chil_refs = self.parse_family(record)
                self.families[record.xref] = {
                    'family': family,
                    'husb': husb_ref,
                    'wife': wife_ref,
                    'children': chil_refs
                }


class DatabaseBuilder:
    def __init__(self, parser):
        self.parser = parser
        self.person_map = {}
        self.family_map = {}
        self.strings = ['', '?']
        self.string_map = {'': 0, '?': 1}

    def add_string(self, s):
        if not s:
            return 0
        if s in self.string_map:
            return self.string_map[s]
        idx = len(self.strings)
        self.strings.append(s)
        self.string_map[s] = idx
        return idx

    def cdate_to_iovalue(self, cdate):
        if isinstance(cdate, adef.CdateNone):
            return {'tag': 5, 'fields': []}
        elif isinstance(cdate, adef.CdateDate):
            date = cdate.date
            if isinstance(date, adef.DateGreg):
                dmy = date.dmy
                prec = dmy.prec
                if isinstance(prec, adef.Precision):
                    prec_tag = prec.value - 1
                    prec_value = {'tag': prec_tag, 'fields': []}
                else:
                    prec_value = {'tag': 0, 'fields': []}

                dmy_value = [dmy.day, dmy.month, dmy.year, prec_value, dmy.delta]
                date_value = {'tag': 0, 'fields': [dmy_value, date.calendar.value - 1]}
                return {'tag': 4, 'fields': [date_value]}
            elif isinstance(date, adef.DateText):
                date_text_idx = self.add_string(date.text)
                date_value = {'tag': 1, 'fields': [date_text_idx]}
                return {'tag': 4, 'fields': [date_value]}
        return {'tag': 5, 'fields': []}

    def person_to_iovalue(self, person):
        first_name_idx = self.add_string(person.first_name)
        surname_idx = self.add_string(person.surname)
        image_idx = self.add_string(person.image)
        public_name_idx = self.add_string(person.public_name)
        occupation_idx = self.add_string(person.occupation)
        birth_place_idx = self.add_string(person.birth_place)
        birth_note_idx = self.add_string(person.birth_note)
        birth_src_idx = self.add_string(person.birth_src)
        baptism_place_idx = self.add_string(person.baptism_place)
        baptism_note_idx = self.add_string(person.baptism_note)
        baptism_src_idx = self.add_string(person.baptism_src)
        death_place_idx = self.add_string(person.death_place)
        death_note_idx = self.add_string(person.death_note)
        death_src_idx = self.add_string(person.death_src)
        burial_place_idx = self.add_string(person.burial_place)
        burial_note_idx = self.add_string(person.burial_note)
        burial_src_idx = self.add_string(person.burial_src)
        notes_idx = self.add_string(person.notes)
        psources_idx = self.add_string(person.psources)
        key_index_idx = self.add_string(person.key_index)

        sex_value = 0 if person.sex == gwdef.Sex.MALE else 1 if person.sex == gwdef.Sex.FEMALE else 2
        access_value = person.access.value - 1
        birth_cdate = self.cdate_to_iovalue(person.birth)
        baptism_cdate = self.cdate_to_iovalue(person.baptism)

        death_tag = 0
        death_fields = []
        if isinstance(person.death, gwdef.NotDead):
            death_tag = 0
        elif isinstance(person.death, gwdef.DeadDontKnowWhen):
            death_tag = 2
        else:
            death_tag = 0

        burial_tag = 0
        burial_fields = []
        if isinstance(person.burial, gwdef.UnknownBurial):
            burial_tag = 0

        return {
            'tag': 0,
            'fields': [
                first_name_idx,
                surname_idx,
                person.occ,
                image_idx,
                public_name_idx,
                [],
                [],
                [],
                [],
                [],
                [],
                [],
                occupation_idx,
                sex_value,
                access_value,
                birth_cdate,
                birth_place_idx,
                birth_note_idx,
                birth_src_idx,
                baptism_cdate,
                baptism_place_idx,
                baptism_note_idx,
                baptism_src_idx,
                {'tag': death_tag, 'fields': death_fields},
                death_place_idx,
                death_note_idx,
                death_src_idx,
                {'tag': burial_tag, 'fields': burial_fields},
                burial_place_idx,
                burial_note_idx,
                burial_src_idx,
                [],
                notes_idx,
                psources_idx,
                key_index_idx
            ]
        }

    def family_to_iovalue(self, family, father_idx, mother_idx, children_idxs):
        marriage_place_idx = self.add_string(family.marriage_place)
        marriage_note_idx = self.add_string(family.marriage_note)
        marriage_src_idx = self.add_string(family.marriage_src)
        comment_idx = self.add_string(family.comment)
        origin_file_idx = self.add_string(family.origin_file)
        fsources_idx = self.add_string(family.fsources)

        relation_value = family.relation.value - 1
        divorce_tag = 0
        if isinstance(family.divorce, gwdef.NotDivorced):
            divorce_tag = 0

        marriage_cdate = self.cdate_to_iovalue(family.marriage)

        return {
            'tag': 0,
            'fields': [
                marriage_cdate,
                marriage_place_idx,
                marriage_note_idx,
                marriage_src_idx,
                [],
                relation_value,
                {'tag': divorce_tag, 'fields': []},
                [],
                comment_idx,
                origin_file_idx,
                fsources_idx,
                family.fam_index
            ]
        }

    def build(self, output_path):
        for xref, data in self.parser.individuals.items():
            self.person_map[xref] = len(self.person_map)

        for xref, data in self.parser.families.items():
            self.family_map[xref] = len(self.family_map)

        persons = []
        ascends = []
        unions = []

        for xref, data in sorted(self.parser.individuals.items(), key=lambda x: self.person_map[x[0]]):
            person_iovalue = self.person_to_iovalue(data['person'])
            persons.append(person_iovalue)

            parents_fam = None
            if data['famc']:
                famc_ref = data['famc'][0]
                if famc_ref in self.family_map:
                    parents_fam = self.family_map[famc_ref]

            ascend_val = {'tag': 0, 'fields': [
                {'tag': 1 if parents_fam is not None else 0, 'fields': [parents_fam] if parents_fam is not None else []},
                {'tag': 0, 'fields': []}
            ]}
            ascends.append(ascend_val)

            union_fams = []
            for fam_ref in data['fams']:
                if fam_ref in self.family_map:
                    union_fams.append(self.family_map[fam_ref])

            unions.append({'tag': 0, 'fields': [union_fams]})

        families = []
        couples = []
        descends = []

        for xref, data in sorted(self.parser.families.items(), key=lambda x: self.family_map[x[0]]):
            father_idx = self.person_map.get(data['husb'], -1) if data['husb'] else -1
            mother_idx = self.person_map.get(data['wife'], -1) if data['wife'] else -1
            children_idxs = [self.person_map[c] for c in data['children'] if c in self.person_map]

            family_iovalue = self.family_to_iovalue(data['family'], father_idx, mother_idx, children_idxs)
            families.append(family_iovalue)

            couple_val = {'tag': 0, 'fields': [
                father_idx if father_idx >= 0 else -1,
                {'tag': 1 if mother_idx >= 0 else 0, 'fields': [mother_idx] if mother_idx >= 0 else []}
            ]}
            couples.append(couple_val)

            descends.append({'tag': 0, 'fields': [children_idxs]})

        os.makedirs(output_path, exist_ok=True)
        secure.add_assets(output_path)

        os.makedirs(os.path.join(output_path, "notes_d"), exist_ok=True)
        os.makedirs(os.path.join(output_path, "wiznotes"), exist_ok=True)
        open(os.path.join(output_path, "notes"), 'w').close()

        base_file = os.path.join(output_path, "base")

        with open(base_file, 'wb') as f:
            f.write(database.MAGIC_GNWB0024)

            database.output_binary_int(f, len(persons))
            database.output_binary_int(f, len(families))
            database.output_binary_int(f, len(self.strings))

            header_end = f.tell()

            for _ in range(7):
                database.output_binary_int(f, 0)

            iovalue.output(f, "")

            persons_pos = f.tell()
            iovalue.output(f, persons)

            ascends_pos = f.tell()
            iovalue.output(f, ascends)

            unions_pos = f.tell()
            iovalue.output(f, unions)

            families_pos = f.tell()
            iovalue.output(f, families)

            couples_pos = f.tell()
            iovalue.output(f, couples)

            descends_pos = f.tell()
            iovalue.output(f, descends)

            strings_pos = f.tell()
            iovalue.output(f, self.strings)

            f.seek(header_end)
            database.output_binary_int(f, persons_pos)
            database.output_binary_int(f, ascends_pos)
            database.output_binary_int(f, unions_pos)
            database.output_binary_int(f, families_pos)
            database.output_binary_int(f, couples_pos)
            database.output_binary_int(f, descends_pos)
            database.output_binary_int(f, strings_pos)

        persons_offsets = []
        current_pos = persons_pos + iovalue.array_header_size(len(persons))
        for person in persons:
            persons_offsets.append(current_pos)
            current_pos += iovalue.size(person)

        ascends_offsets = []
        current_pos = ascends_pos + iovalue.array_header_size(len(ascends))
        for ascend in ascends:
            ascends_offsets.append(current_pos)
            current_pos += iovalue.size(ascend)

        unions_offsets = []
        current_pos = unions_pos + iovalue.array_header_size(len(unions))
        for union in unions:
            unions_offsets.append(current_pos)
            current_pos += iovalue.size(union)

        families_offsets = []
        current_pos = families_pos + iovalue.array_header_size(len(families))
        for family in families:
            families_offsets.append(current_pos)
            current_pos += iovalue.size(family)

        couples_offsets = []
        current_pos = couples_pos + iovalue.array_header_size(len(couples))
        for couple in couples:
            couples_offsets.append(current_pos)
            current_pos += iovalue.size(couple)

        descends_offsets = []
        current_pos = descends_pos + iovalue.array_header_size(len(descends))
        for descend in descends:
            descends_offsets.append(current_pos)
            current_pos += iovalue.size(descend)

        strings_offsets = []
        current_pos = strings_pos + iovalue.array_header_size(len(self.strings))
        for string in self.strings:
            strings_offsets.append(current_pos)
            current_pos += iovalue.size(string)

        base_acc_file = os.path.join(output_path, "base.acc")
        with open(base_acc_file, 'wb') as f:
            for offset in persons_offsets:
                database.output_binary_int(f, offset)
            for offset in ascends_offsets:
                database.output_binary_int(f, offset)
            for offset in unions_offsets:
                database.output_binary_int(f, offset)
            for offset in families_offsets:
                database.output_binary_int(f, offset)
            for offset in couples_offsets:
                database.output_binary_int(f, offset)
            for offset in descends_offsets:
                database.output_binary_int(f, offset)
            for offset in strings_offsets:
                database.output_binary_int(f, offset)

        self.generate_name_indexes(output_path, persons)

    def generate_name_indexes(self, gwb_path, persons):
        names_table = [[] for _ in range(database.TABLE_SIZE)]
        snames_table = {}
        fnames_table = {}

        for i, person in enumerate(persons):
            fields = person['fields']
            fname_idx = fields[0]
            sname_idx = fields[1]

            if fname_idx >= len(self.strings) or sname_idx >= len(self.strings):
                continue

            fname = self.strings[fname_idx]
            sname = self.strings[sname_idx]

            if fname and sname and fname != "?" and sname != "?":
                full_name = f"{fname} {sname}"
                idx = hash(name.crush_lower(full_name)) % database.TABLE_SIZE
                if i not in names_table[idx]:
                    names_table[idx].append(i)

                if sname_idx not in snames_table:
                    snames_table[sname_idx] = []
                if i not in snames_table[sname_idx]:
                    snames_table[sname_idx].append(i)

                if fname_idx not in fnames_table:
                    fnames_table[fname_idx] = []
                if i not in fnames_table[fname_idx]:
                    fnames_table[fname_idx].append(i)

        names_inx_file = os.path.join(gwb_path, "names.inx")
        with open(names_inx_file, 'wb') as f:
            database.output_binary_int(f, 0)
            iovalue.output(f, names_table)

        snames_bt = sorted(snames_table.items(), key=lambda x: self.strings[x[0]] if x[0] < len(self.strings) else "")
        snames_dat_file = os.path.join(gwb_path, "snames.dat")
        with open(snames_dat_file, 'wb') as f:
            snames_inx_data = []
            for istr, ipers in snames_bt:
                pos = f.tell()
                database.output_binary_int(f, len(ipers))
                for ip in ipers:
                    database.output_binary_int(f, ip)
                snames_inx_data.append([istr, pos])

        snames_inx_file = os.path.join(gwb_path, "snames.inx")
        with open(snames_inx_file, 'wb') as f:
            iovalue.output(f, snames_inx_data)

        fnames_bt = sorted(fnames_table.items(), key=lambda x: self.strings[x[0]] if x[0] < len(self.strings) else "")
        fnames_dat_file = os.path.join(gwb_path, "fnames.dat")
        with open(fnames_dat_file, 'wb') as f:
            fnames_inx_data = []
            for istr, ipers in fnames_bt:
                pos = f.tell()
                database.output_binary_int(f, len(ipers))
                for ip in ipers:
                    database.output_binary_int(f, ip)
                fnames_inx_data.append([istr, pos])

        fnames_inx_file = os.path.join(gwb_path, "fnames.inx")
        with open(fnames_inx_file, 'wb') as f:
            iovalue.output(f, fnames_inx_data)


def main():
    if len(sys.argv) < 2:
        print("Usage: ged2gwb.py <input.ged> [-o <output.gwb>] [-v]")
        print()
        print("Arguments:")
        print("  <input.ged>      Input GEDCOM file")
        print("  -o <output.gwb>  Output GeneWeb database path (default: <input>.gwb)")
        print("  -v, --verbose    Verbose output")
        print()
        print("Supported GEDCOM features:")
        print("  - Character encodings: UTF-8, ANSEL, ASCII")
        print("  - Date formats: ABOUT, BEFORE, AFTER, FROM/TO, exact dates")
        print("  - Person tags: NAME, SEX, BIRT, BAPM/CHR, DEAT, BURI, CREM, OCCU, NOTE, SOUR, OBJE")
        print("  - Family tags: HUSB, WIFE, CHIL, MARR, DIV, NOTE, SOUR")
        print("  - Continuation: CONC, CONT")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = None
    verbose = False

    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == '-o' and i + 1 < len(sys.argv):
            output_file = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] in ['-v', '--verbose']:
            verbose = True
            i += 1
        else:
            i += 1

    if output_file is None:
        output_file = Path(input_file).stem + '.gwb'

    try:
        print(f"GEDCOM to GeneWeb converter")
        print(f"Input:  {input_file}")
        print(f"Output: {output_file}")
        print()

        if verbose:
            print("Detecting character encoding...")
        parser = GedcomParser(input_file)
        encoding = parser.detect_encoding()
        if verbose:
            print(f"  Detected encoding: {encoding}")

        if verbose:
            print("Parsing GEDCOM file...")
        parser.load()

        print(f"Parsed successfully:")
        print(f"  Persons:  {len(parser.individuals)}")
        print(f"  Families: {len(parser.families)}")

        if parser.warnings and verbose:
            print(f"  Warnings: {len(parser.warnings)}")
            for warning in parser.warnings[:10]:
                print(f"    - {warning}")
            if len(parser.warnings) > 10:
                print(f"    ... and {len(parser.warnings) - 10} more")

        if parser.errors:
            print(f"  Errors:   {len(parser.errors)}")
            for error in parser.errors[:10]:
                print(f"    - {error}")
            if len(parser.errors) > 10:
                print(f"    ... and {len(parser.errors) - 10} more")

        print()
        if verbose:
            print("Building database structure...")
        builder = DatabaseBuilder(parser)

        if verbose:
            print("Writing database files...")
        builder.build(output_file)

        if verbose:
            print(f"  Strings: {len(builder.strings)}")

        print()
        print(f"Success! Created {output_file}")

    except FileNotFoundError:
        print(f"Error: File not found: {input_file}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
