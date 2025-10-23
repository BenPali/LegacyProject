from typing import Optional, List, Tuple
from dataclasses import dataclass
from lib.gwdef import NLDB
from lib import driver, name

CHAR_DIR_SEP = ':'
DIR_SEP = ":"

@dataclass
class WLPage:
    pos: int
    pg_path: Tuple[List[str], str]
    fname: str
    anchor: str
    text: str

@dataclass
class WLPerson:
    pos: int
    key: NLDB.Key
    name: Optional[str]
    text: Optional[str]

@dataclass
class WLWizard:
    pos: int
    wiz: str
    wiz_name: str

@dataclass
class WLNone:
    pos: int
    content: str

WikiLink = WLPage | WLPerson | WLWizard | WLNone

def check_file_name(filename: str) -> Optional[Tuple[List[str], str]]:
    def is_valid_char(char: str) -> bool:
        return char.isalnum() or char in ('_', '-', '.')

    def parse_path(dirs: List[str], segment_start: int, pos: int) -> Optional[Tuple[List[str], str]]:
        if pos == len(filename):
            if pos > segment_start:
                return (list(reversed(dirs)), filename[segment_start:pos])
            return None

        char = filename[pos]
        if is_valid_char(char):
            return parse_path(dirs, segment_start, pos + 1)
        elif char == CHAR_DIR_SEP:
            if pos > segment_start:
                new_dirs = [filename[segment_start:pos]] + dirs
                return parse_path(new_dirs, pos + 1, pos + 1)
            return None
        else:
            return None

    return parse_path([], 0, 0)

def _find_stop_chars(text: str, start: int) -> int:
    stop_chars = ('%', "'", '{')
    pos = start
    while pos < len(text):
        if text[pos] in stop_chars:
            return pos
        if text[pos] == '[' and pos > start and pos + 1 < len(text) and text[pos + 1] == '[':
            return pos
        pos += 1
    return len(text)

def _find_closing_brackets(text: str, start: int, bracket_pattern: str) -> int:
    pos = start
    bracket_len = len(bracket_pattern)
    while pos < len(text):
        if pos <= len(text) - bracket_len and text[pos:pos + bracket_len] == bracket_pattern:
            return pos + bracket_len
        pos += 1
    return start if bracket_pattern == ']]]' else pos

def _parse_page_link(content: str) -> Tuple[str, str, str]:
    try:
        slash_pos = content.rindex('/')
    except ValueError:
        return content, "", content

    try:
        hash_pos = content[:slash_pos].rindex('#')
        fname_end = hash_pos
        anchor_start = min(hash_pos + 1, slash_pos)
    except ValueError:
        fname_end = slash_pos
        anchor_start = slash_pos

    filename = content[:fname_end]
    anchor = content[anchor_start:slash_pos]
    display_text = content[slash_pos + 1:]
    return filename, anchor, display_text

def _parse_wizard_link(content: str) -> Tuple[str, str]:
    try:
        slash_pos = content.index('/')
        wizard = content[:slash_pos]
        wizard_name = content[slash_pos + 1:]
    except ValueError:
        wizard = content
        wizard_name = ""
    return wizard, wizard_name

def _parse_person_link(content: str) -> Tuple[str, str, int, str]:
    parts = content.split('/')

    if len(parts) < 2:
        raise ValueError("Invalid person link")

    first_name = parts[0]
    surname = parts[1]
    occurrence = 0
    display_name = f"{first_name} {surname}"

    if len(parts) >= 3:
        if len(parts) == 3:
            try:
                occurrence = int(parts[2])
            except ValueError:
                pass
        elif len(parts) >= 4:
            try:
                occurrence = int(parts[2])
                display_name = parts[3]
            except ValueError:
                try:
                    occurrence = int(parts[3])
                except ValueError:
                    occurrence = 0
                    display_name = parts[3]

    return first_name, surname, occurrence, display_name

def misc_notes_link(text: str, start: int) -> WikiLink:
    text_len = len(text)

    def extract_content(end: int) -> str:
        return text[start:end]

    def find_next_link() -> WikiLink:
        stop_pos = _find_stop_chars(text, start)
        return WLNone(stop_pos, extract_content(stop_pos))

    if start >= text_len - 2 or text[start:start + 2] != '[[':
        return find_next_link()

    if text[start + 2] == '[':
        end_pos = _find_closing_brackets(text, start + 3, ']]]')
        if end_pos <= start + 6:
            return find_next_link()

        content = text[start + 3:end_pos - 3]
        filename, anchor, display_text = _parse_page_link(content)

        page_path = check_file_name(filename)
        if page_path is not None:
            return WLPage(end_pos, page_path, filename, anchor, display_text)
        return find_next_link()

    end_pos = _find_closing_brackets(text, start + 2, ']]')
    if end_pos <= start + 4:
        return find_next_link()

    content = text[start + 2:end_pos - 2]

    special_type = None
    if ':' in content:
        colon_pos = content.index(':')
        special_type = content[:colon_pos]
        content = content[colon_pos + 1:]

    display_text = None
    if ';' in content:
        semi_pos = content.index(';')
        main_content = content[:semi_pos]
        display_text = content[semi_pos + 1:]
    else:
        main_content = content

    if special_type == "w":
        wizard, wizard_name = _parse_wizard_link(main_content)
        return WLWizard(end_pos, wizard, wizard_name)

    try:
        first_name, surname, occurrence, person_name = _parse_person_link(main_content)
        first_lower = name.lower(first_name)
        surname_lower = name.lower(surname)
        person_key = (first_lower, surname_lower, occurrence)
        return WLPerson(end_pos, person_key, person_name, display_text)
    except ValueError:
        return find_next_link()

def add_in_db(
    db: List[Tuple[NLDB.Page, Tuple[List[str], List[Tuple[NLDB.Key, NLDB.Ind]]]]],
    page: NLDB.Page,
    links: Tuple[List[str], List[Tuple[NLDB.Key, NLDB.Ind]]]
) -> List[Tuple[NLDB.Page, Tuple[List[str], List[Tuple[NLDB.Key, NLDB.Ind]]]]]:
    note_links, person_links = links
    new_db = [(p, data) for p, data in db if p != page]
    if note_links or person_links:
        new_db.append((page, (note_links, person_links)))
    return new_db

def update_db(
    base,
    page: NLDB.Page,
    links: Tuple[List[str], List[Tuple[NLDB.Key, NLDB.Ind]]]
) -> None:
    current_db = driver.read_nldb(base)
    new_db = add_in_db(current_db, page, links)
    driver.write_nldb(base, new_db)
