import hashlib
import os
import re
import urllib.parse
from typing import Optional, List, Tuple, Any, Dict
from pathlib import Path
from dataclasses import dataclass

from lib import driver, adef, gwdef, config as config_module, date, name, mutil, gutil, secure


@dataclass
class Title:
    name: str
    ident: str = ''
    place: str = ''
    date_start: Any = None
    date_end: Any = None
    nth: int = 0


def escape_html(s: str) -> str:
    replacements = {
        '&': '&#38;',
        '"': '&#34;',
        "'": '&#39;',
        '<': '&#60;',
        '>': '&#62;'
    }
    result = []
    for c in s:
        result.append(replacements.get(c, c))
    return ''.join(result)


def esc(s: str) -> str:
    return escape_html(s)


def escape_attribute(s: str) -> str:
    replacements = {
        '&': '&#38;',
        '"': '&#34;',
        "'": '&#39;'
    }
    result = []
    for c in s:
        result.append(replacements.get(c, c))
    return ''.join(result)


def clean_html_tags(s: str) -> str:
    return re.sub(r'<[^>]*>', '', s)


def clean_comment_tags(s: str) -> str:
    return re.sub(r'<!--.*?-->', '', s, flags=re.DOTALL)


def uri_encode(s: str) -> str:
    return urllib.parse.quote(s, safe='')


def uri_decode(s: str) -> str:
    return urllib.parse.unquote(s)


def hash_file(file_path: str) -> Optional[str]:
    try:
        md5 = hashlib.md5()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                md5.update(chunk)
        return md5.hexdigest()
    except (IOError, OSError):
        return None


_hash_cache = {}


def hash_file_cached(file_path: str) -> Optional[str]:
    try:
        mtime = os.path.getmtime(file_path)
        if file_path in _hash_cache:
            cached_mtime, cached_hash = _hash_cache[file_path]
            if cached_mtime == mtime:
                return cached_hash

        file_hash = hash_file(file_path)
        if file_hash:
            _hash_cache[file_path] = (mtime, file_hash)
        return file_hash
    except (IOError, OSError):
        return None


def is_hide_names(conf: config_module.Config, p: driver.GenPerson) -> bool:
    return conf.hide_names or p.access == gwdef.Access.PRIVATE


def is_hidden(p) -> bool:
    if isinstance(p, driver.Person):
        p._ensure_loaded()
        return p.gen_person.surname == ''
    return p.surname == ''


def is_public(conf: config_module.Config, base: Any, p: driver.GenPerson) -> bool:
    if p.access == gwdef.Access.PUBLIC:
        return True
    if p.access == gwdef.Access.IF_TITLES and len(p.titles) > 0:
        return True
    return is_old_person(conf, p)


def strictly_after_private_years(dmy: adef.Dmy, private_years: int) -> bool:
    import datetime
    current_year = datetime.datetime.now().year
    return dmy.year + private_years < current_year


def is_old_person(conf: config_module.Config, p: driver.GenPerson) -> bool:
    if isinstance(p.death, gwdef.NotDead):
        if isinstance(p.birth, adef.CdateDate):
            dmy_opt = date.cdate_to_dmy_opt(p.birth)
            if dmy_opt:
                dmy = dmy_opt
                if strictly_after_private_years(dmy, conf.private_years):
                    return True
        return False

    if isinstance(p.death, gwdef.DeadDontKnowWhen) or isinstance(p.death, gwdef.DontKnowIfDead):
        if isinstance(p.birth, adef.CdateDate):
            dmy_opt = date.cdate_to_dmy_opt(p.birth)
            if dmy_opt:
                dmy = dmy_opt
                if strictly_after_private_years(dmy, conf.private_years + conf.public_if_no_date):
                    return True
        return False

    if isinstance(p.death, (gwdef.DeathWithReason, gwdef.DeadYoung, gwdef.OfCourseDead)):
        death_date = getattr(p.death, 'date', None)
        if death_date and isinstance(death_date, adef.CdateDate):
            dmy_opt = date.cdate_to_dmy_opt(death_date)
            if dmy_opt:
                dmy = dmy_opt
                if strictly_after_private_years(dmy, conf.private_years):
                    return True
        elif isinstance(p.birth, adef.CdateDate):
            dmy_opt = date.cdate_to_dmy_opt(p.birth)
            if dmy_opt:
                dmy = dmy_opt
                if strictly_after_private_years(dmy, conf.private_years + conf.public_if_no_date):
                    return True

    return False


def authorized_age(conf: config_module.Config, base: Any, p: driver.GenPerson) -> bool:
    if not conf.use_restrict:
        return True
    return is_public(conf, base, p)


def is_restricted(conf: config_module.Config, base: Any, ip: int) -> bool:
    if not conf.use_restrict:
        return False
    person = driver.poi(base, ip)
    gen_p = driver.gen_person_of_person(person)
    return not authorized_age(conf, base, gen_p)


def pget_opt(conf: config_module.Config, base: Any, ip: int) -> Optional[driver.GenPerson]:
    person = driver.poi(base, ip)
    gen_p = driver.gen_person_of_person(person)
    if authorized_age(conf, base, gen_p):
        return gen_p
    return None


def pget(conf: config_module.Config, base: Any, ip: int) -> driver.GenPerson:
    p_opt = pget_opt(conf, base, ip)
    if p_opt:
        return p_opt
    return driver.empty_person(base, ip)


def access_status(p: driver.GenPerson) -> str:
    if p.access == gwdef.Access.PUBLIC:
        return 'public'
    elif p.access == gwdef.Access.PRIVATE:
        return 'private'
    else:
        return 'iftitles'


def start_with(prefix: str, start_idx: int, s: str) -> bool:
    if start_idx < 0 or start_idx >= len(s):
        return False
    return s[start_idx:].startswith(prefix)


def start_with_vowel(conf: config_module.Config, s: str) -> bool:
    if not s:
        return False
    vowels = conf.vowels if hasattr(conf, 'vowels') else 'aeiouyAEIOUY'
    return s[0] in vowels


def string_gen_person(base: Any, p: driver.GenPerson) -> driver.GenPerson:
    return driver.string_gen_person(base, p)


def string_gen_family(base: Any, f: driver.GenFamily) -> driver.GenFamily:
    return driver.string_gen_family(base, f)


def accessible_by_key(conf: config_module.Config, base: Any, p: driver.GenPerson,
                       fn: str, sn: str) -> bool:
    if not p.first_name or not p.surname:
        return False
    if p.first_name == '?' or p.surname == '?':
        return False
    return authorized_age(conf, base, p)


def commd(conf: config_module.Config, excl: Optional[List[str]] = None,
          trim: bool = False, pwd: bool = True, henv: bool = True,
          senv: bool = True) -> str:
    excl = excl or []
    result = f"{conf.command}?"

    params = []

    if pwd and conf.bname:
        params.append(f"b={uri_encode(conf.bname)}")

    if henv and hasattr(conf, 'henv'):
        for k, v in conf.henv.items():
            if k not in excl and v:
                if not (k in ('oc', 'ocz') and v == '0'):
                    params.append(f"{uri_encode(k)}={uri_encode(v)}")

    if senv and hasattr(conf, 'senv'):
        for k, v in conf.senv.items():
            if k not in excl and v:
                params.append(f"{uri_encode(k)}={uri_encode(v)}")

    result += '&'.join(params)
    return result


def prefix_base(conf: config_module.Config) -> str:
    return commd(conf, pwd=False)


def prefix_base_password(conf: config_module.Config) -> str:
    return commd(conf, pwd=True)


def acces(conf: config_module.Config, base: Any, p: driver.GenPerson) -> str:
    return acces_n(conf, base, '', p)


def acces_n(conf: config_module.Config, base: Any, n: str, p: driver.GenPerson) -> str:
    fn = p.first_name
    sn = p.surname
    occ = p.occ

    if accessible_by_key(conf, base, p, fn, sn):
        params = []
        if n:
            params.append(f"p{n}={uri_encode(fn)}")
            params.append(f"n{n}={uri_encode(sn)}")
            if occ != 0:
                params.append(f"oc{n}={occ}")
        else:
            params.append(f"p={uri_encode(fn)}")
            params.append(f"n={uri_encode(sn)}")
            if occ != 0:
                params.append(f"oc={occ}")
        return '&'.join(params)
    else:
        ip = driver.get_iper(p)
        if n:
            return f"i{n}={ip}"
        else:
            return f"i={ip}"


def geneweb_link(conf: config_module.Config, href: str, s: str) -> str:
    base_url = commd(conf)
    if '?' in base_url:
        full_href = f"{base_url}&{href}"
    else:
        full_href = f"{base_url}?{href}"
    return f'<a href="{escape_attribute(full_href)}">{escape_html(s)}</a>'


def wprint_geneweb_link(conf: config_module.Config, href: str, s: str):
    print(geneweb_link(conf, href, s), end='')


def nobtit(conf: config_module.Config, base: Any, p: driver.GenPerson) -> List[Title]:
    allowed_titles = conf.allowed_titles if hasattr(conf, 'allowed_titles') else set()
    denied_titles = conf.denied_titles if hasattr(conf, 'denied_titles') else set()

    result = []
    for title in p.titles:
        title_name = title.name
        if allowed_titles and title_name not in allowed_titles:
            continue
        if denied_titles and title_name in denied_titles:
            continue
        result.append(title)
    return result


def main_title(conf: config_module.Config, base: Any, p: driver.GenPerson) -> Optional[Title]:
    titles = nobtit(conf, base, p)
    if titles:
        return titles[0]
    return None


def one_title_text(title: Title) -> str:
    result = title.name
    if title.place:
        result += f" {title.place}"
    return result


def person_title(conf: config_module.Config, base: Any, p: driver.GenPerson) -> str:
    title = main_title(conf, base, p)
    if title:
        return one_title_text(title)
    return ''


def titled_person_text(conf: config_module.Config, base: Any, p: driver.GenPerson,
                       p_title: Optional[Title] = None) -> str:
    if is_hidden(p):
        return '...'

    if is_hide_names(conf, p):
        return 'x x'

    title = p_title or main_title(conf, base, p)

    result = ''
    if title:
        result = one_title_text(title) + ' '

    if p.public_name:
        result += p.public_name
    else:
        result += p.first_name
        if p.qualifiers:
            result += f" <em>{p.qualifiers[0]}</em>"
        result += f" {p.surname}"

    return result


def gen_person_text(conf: config_module.Config, base: Any, p: driver.GenPerson,
                     escape: bool = True, html_tags: bool = True, sn: bool = True,
                     p_first_name: Optional[callable] = None,
                     p_surname: Optional[callable] = None) -> str:
    if is_hidden(p):
        return '...'

    if is_hide_names(conf, p):
        return 'x x'

    get_first_name = p_first_name or (lambda b, person: person.first_name)
    get_surname = p_surname or (lambda b, person: person.surname)

    first_name = get_first_name(base, p)
    surname = get_surname(base, p) if sn else ''

    if p.public_name:
        text = p.public_name
    else:
        text = first_name
        if p.qualifiers and html_tags:
            text += f" <em>{p.qualifiers[0]}</em>"
        elif p.qualifiers:
            text += f" {p.qualifiers[0]}"

        if sn and surname:
            text += f" {surname}"

    if escape:
        return escape_html(text)
    return text


def person_text_without_title(conf: config_module.Config, base: Any, p: driver.GenPerson) -> str:
    return gen_person_text(conf, base, p)


def referenced_person_text(conf: config_module.Config, base: Any, p: driver.GenPerson) -> str:
    text = gen_person_text(conf, base, p)
    href = acces(conf, base, p)
    return geneweb_link(conf, href, text)


def referenced_person_title_text(conf: config_module.Config, base: Any, p: driver.GenPerson) -> str:
    title = person_title(conf, base, p)
    text = title + ' ' + gen_person_text(conf, base, p) if title else gen_person_text(conf, base, p)
    href = acces(conf, base, p)
    return geneweb_link(conf, href, text)


def etc_file_name(conf: config_module.Config, fname: str) -> str:
    base_dir = conf.base_dir if hasattr(conf, 'base_dir') else '.'
    return os.path.join(base_dir, 'etc', fname)


def open_etc_file(conf: config_module.Config, fname: str) -> Optional[Tuple[object, str]]:
    file_path = etc_file_name(conf, fname)
    try:
        f = open(file_path, 'r', encoding='utf-8')
        return (f, file_path)
    except (IOError, OSError):
        return None


def is_full_html_template(conf: config_module.Config, fname: str) -> bool:
    result = open_etc_file(conf, fname)
    if not result:
        return False

    f, _ = result
    try:
        for i in range(3):
            line = f.readline()
            if '<!DOCTYPE html>' in line or '<!doctype html>' in line:
                return True
        return False
    finally:
        f.close()


def private_txt(conf: config_module.Config, txt: str) -> str:
    if conf.hide_private_names if hasattr(conf, 'hide_private_names') else False:
        return 'x'
    return txt


def html(conf: config_module.Config, content_type: str = 'text/html'):
    print(f"Content-Type: {content_type}")
    print()


def unauthorized(conf: config_module.Config, message: str):
    print("Status: 401 Unauthorized")
    print("Content-Type: text/html")
    print()
    print(f"<html><body><h1>Unauthorized</h1><p>{escape_html(message)}</p></body></html>")


def hidden_env_aux(conf: config_module.Config, env: List[Tuple[str, str]]):
    for k, v in env:
        print(f'<input type="hidden" name="{escape_attribute(k)}" value="{escape_attribute(v)}">')


def hidden_env(conf: config_module.Config):
    env = []
    if hasattr(conf, 'henv'):
        env.extend(conf.henv.items())
    if hasattr(conf, 'senv'):
        env.extend(conf.senv.items())
    hidden_env_aux(conf, env)


def hidden_input(conf: config_module.Config, k: str, v: str):
    print(f'<input type="hidden" name="{escape_attribute(k)}" value="{escape_attribute(v)}">')


def hidden_input_s(conf: config_module.Config, k: str, v: str):
    hidden_input(conf, k, v)


def hidden_textarea(conf: config_module.Config, k: str, v: str):
    print(f'<textarea style="display:none" name="{escape_attribute(k)}">{escape_html(v)}</textarea>')


def submit_input(conf: config_module.Config, k: str, v: str):
    print(f'<input type="submit" name="{escape_attribute(k)}" value="{escape_attribute(v)}">')


def nth_field(s: str, n: int) -> str:
    parts = s.split('/')
    if n < len(parts):
        return parts[n]
    return s


def tnf(w: str) -> str:
    return f"[{w}]"


def transl(conf: config_module.Config, w: str) -> str:
    return conf.lexicon.get(w, tnf(w))


def transl_nth(conf: config_module.Config, w: str, n: int) -> str:
    w_clean = w[:-3] if w.endswith(':::') else w
    translation = conf.lexicon.get(w_clean, w_clean)
    return nth_field(translation, n) if translation != w_clean else tnf(nth_field(w_clean, n))


def simple_decline(conf: config_module.Config, wt: str) -> str:
    result = []
    i = 0
    while i < len(wt):
        if wt[i] == '[':
            try:
                j = wt.index(']', i)
                k = wt.index('|', i)
                if k < j and j + 2 < len(wt):
                    s2 = wt[j + 1]
                    if start_with_vowel(conf, s2):
                        result.append(wt[k + 1:j])
                    else:
                        result.append(wt[i + 1:k])
                    i = j
                else:
                    result.append(wt[i:])
                    break
            except ValueError:
                result.append(wt[i:])
                break
        else:
            result.append(wt[i])
        i += 1
    return ''.join(result)


def gen_decline_basic(wt: str, s: str) -> str:
    s1 = '' if s == '' else f' {s}' if wt != '' else s
    if len(wt) >= 3 and wt[-3] == ':' and wt[-1] == ':':
        start = wt[:-3]
        decline_char = wt[-2]
        return start + mutil.decline(decline_char, s)

    plus_idx = wt.rfind('+')
    if plus_idx > 0 and wt[plus_idx - 1:plus_idx + 7] == ' +before':
        start = wt[:plus_idx - 1]
        return start if s == '' else mutil.decline('n', s) + ' ' + start

    return wt + mutil.decline('n', s1)


def transl_decline(conf: config_module.Config, w: str, s: str) -> str:
    wt = transl(conf, w)
    return gen_decline_basic(wt, s)


def gen_decline(conf: config_module.Config, wt: str, s1: str, s2: str, s2_raw: str) -> str:
    result = []
    i = 0
    while i < len(wt):
        if wt[i] == '%' and i + 1 < len(wt):
            if wt[i + 1] == '1':
                result.append(s1)
                i += 2
                continue
            elif wt[i + 1] == '2':
                result.append(s2)
                i += 2
                continue

        if i + 4 < len(wt) and wt[i:i + 3] == '::' and wt[i:i + 2] == ':' and wt[i + 3] == '%':
            c = wt[i + 1]
            if i + 4 < len(wt):
                if wt[i + 4] == '1':
                    result.append(mutil.decline(c, s1))
                    i += 5
                    continue
                elif wt[i + 4] == '2':
                    result.append(mutil.decline(c, s2))
                    i += 5
                    continue

        if wt[i] == '[':
            try:
                j = wt.index(']', i)
                k = wt.index('|', i)
                if k < j and j + 2 < len(wt) and wt[j + 1] == '%':
                    if wt[j + 2] in ('1', '2'):
                        s = s1 if wt[j + 2] == '1' else s2
                        if start_with_vowel(conf, s2_raw):
                            result.append(wt[k + 1:j] + s)
                        else:
                            result.append(wt[i + 1:k] + s)
                        i = j + 3
                        continue
            except ValueError:
                pass

        result.append(wt[i])
        i += 1

    return ''.join(result)


def transl_a_of_b(conf: config_module.Config, x: str, y1: str, y2: str) -> str:
    pattern = transl_nth(conf, '%1 of %2', 0)
    return gen_decline(conf, pattern, x, y1, y2)


def transl_a_of_gr_eq_gen_lev(conf: config_module.Config, x: str, y1: str, y2: str) -> str:
    pattern = transl_nth(conf, '%1 of %2', 1)
    return gen_decline(conf, pattern, x, y1, y2)


def ftransl(conf: config_module.Config, w: str) -> str:
    return transl(conf, w)


def ftransl_nth(conf: config_module.Config, w: str, n: int) -> str:
    return transl_nth(conf, w, n)


def string_of_ctime(conf: config_module.Config) -> str:
    import time
    return time.strftime('%a, %d %b %Y %H:%M:%S GMT', time.gmtime())


def week_day_txt(day: int) -> str:
    days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
    return days[day % 7]


def month_txt(month: int) -> str:
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    return months[(month - 1) % 12] if 1 <= month <= 12 else ''


def string_of_place(conf: config_module.Config, place: str) -> str:
    return escape_html(place)


def raw_string_of_place(place: str) -> str:
    return place


def place_of_string(conf: config_module.Config, place: str) -> Optional[Dict[str, str]]:
    gwf_place = None
    for key, val in conf.base_env:
        if key == 'place':
            gwf_place = val
            break

    if gwf_place is None:
        return None

    place_fields = [f.strip() for f in gwf_place.split(',')]
    place_parts = [p.strip() for p in place.split(',')]

    result = {
        'other': '',
        'town': '',
        'township': '',
        'canton': '',
        'district': '',
        'county': '',
        'region': '',
        'country': ''
    }

    for i, part in enumerate(place_parts):
        if i < len(place_fields):
            field_name = place_fields[i]
            if field_name in result:
                result[field_name] = part
            else:
                result['other'] += (' ' + part if result['other'] else part)
        else:
            result['other'] += (' ' + part if result['other'] else part)

    return result


def get_approx_date_place(date1: Optional[adef.Dmy], place1: str,
                          date2: Optional[adef.Dmy], place2: str) -> Tuple[Optional[adef.Dmy], str]:
    if date1 is not None:
        return date1, place1
    elif date2 is not None:
        return date2, place2
    else:
        return None, ''


def get_approx_birth_date_place(conf: config_module.Config, base: Any,
                                 p: driver.GenPerson) -> Tuple[Optional[adef.Dmy], str]:
    birth_date = date.cdate_to_dmy_opt(p.birth) if isinstance(p.birth, adef.CdateDate) else None
    birth_place = string_of_place(conf, driver.sou(base, p.birth_place))

    baptism_date = date.cdate_to_dmy_opt(p.baptism) if isinstance(p.baptism, adef.CdateDate) else None
    baptism_place = string_of_place(conf, driver.sou(base, p.baptism_place))

    return get_approx_date_place(birth_date, birth_place, baptism_date, baptism_place)


def get_approx_death_date_place(conf: config_module.Config, base: Any,
                                 p: driver.GenPerson) -> Tuple[Optional[adef.Dmy], str]:
    death_date = None
    if isinstance(p.death, gwdef.DeadDontKnowWhen):
        death_date = date.cdate_to_dmy_opt(p.death.date) if isinstance(p.death.date, adef.CdateDate) else None

    death_place = string_of_place(conf, driver.sou(base, p.death_place))

    burial_date = None
    burial_place = ''
    if isinstance(p.burial, gwdef.Buried):
        burial_date = date.cdate_to_dmy_opt(p.burial.date) if isinstance(p.burial.date, adef.CdateDate) else None
        burial_place = string_of_place(conf, driver.sou(base, p.burial_place))
    elif isinstance(p.burial, gwdef.Cremated):
        burial_date = date.cdate_to_dmy_opt(p.burial.date) if isinstance(p.burial.date, adef.CdateDate) else None
        burial_place = string_of_place(conf, driver.sou(base, p.burial_place))

    return get_approx_date_place(death_date, death_place, burial_date, burial_place)


def string_of_decimal_num(conf: config_module.Config, f: float) -> str:
    s = str(f)
    result = []
    for i, c in enumerate(s):
        if c == '.':
            if i < len(s) - 1:
                result.append(transl(conf, '(decimal separator)'))
        else:
            result.append(c)
    return ''.join(result)


def string_of_pevent_name(conf: config_module.Config, base: Any, epers_name: str) -> str:
    event_translations = {
        'Epers_Birth': 'birth',
        'Epers_Baptism': 'baptism',
        'Epers_Death': 'death',
        'Epers_Burial': 'burial',
        'Epers_Cremation': 'cremation',
        'Epers_Accomplishment': 'accomplishment',
        'Epers_Acquisition': 'acquisition',
        'Epers_Adhesion': 'adhesion',
        'Epers_BaptismLDS': 'baptismLDS',
        'Epers_BarMitzvah': 'bar mitzvah',
        'Epers_BatMitzvah': 'bat mitzvah',
        'Epers_Benediction': 'benediction',
        'Epers_ChangeName': 'change name',
        'Epers_Circumcision': 'circumcision',
        'Epers_Confirmation': 'confirmation',
        'Epers_ConfirmationLDS': 'confirmation LDS',
        'Epers_Decoration': 'decoration',
        'Epers_DemobilisationMilitaire': 'demobilisationMilitaire',
        'Epers_Diploma': 'diploma',
        'Epers_Distinction': 'distinction',
        'Epers_Dotation': 'dotation',
        'Epers_DotationLDS': 'dotationLDS',
        'Epers_Education': 'education',
        'Epers_Election': 'election',
        'Epers_Emigration': 'emigration',
        'Epers_Excommunication': 'excommunication',
        'Epers_FamilyLinkLDS': 'familyLinkLDS',
        'Epers_FirstCommunion': 'firstCommunion',
        'Epers_Funeral': 'funeral',
        'Epers_Graduate': 'graduate',
        'Epers_Hospitalisation': 'hospitalisation',
        'Epers_Illness': 'illness',
        'Epers_Immigration': 'immigration',
        'Epers_ListePassenger': 'listePassenger',
        'Epers_MilitaryDistinction': 'militaryDistinction',
        'Epers_MilitaryPromotion': 'militaryPromotion',
        'Epers_MilitaryService': 'militaryService',
        'Epers_MobilisationMilitaire': 'mobilisationMilitaire',
        'Epers_Naturalisation': 'naturalisation',
        'Epers_Occupation': 'occupation/occupations',
        'Epers_Ordination': 'ordination',
        'Epers_Property': 'property',
        'Epers_Recensement': 'recensement',
        'Epers_Residence': 'residence',
        'Epers_Retired': 'retired',
        'Epers_ScellentChildLDS': 'scellentChildLDS',
        'Epers_ScellentParentLDS': 'scellentParentLDS',
        'Epers_ScellentSpouseLDS': 'scellentSpouseLDS',
        'Epers_VenteBien': 'venteBien',
        'Epers_Will': 'will'
    }

    if epers_name.startswith('Epers_Name:'):
        custom_name = epers_name[11:]
        return escape_html(driver.sou(base, custom_name))

    trans_key = event_translations.get(epers_name, epers_name)
    if '/' in trans_key:
        return transl_nth(conf, trans_key, 0)
    return transl(conf, trans_key)


def string_of_fevent_name(conf: config_module.Config, base: Any, efam_name: str) -> str:
    event_translations = {
        'Efam_Marriage': 'marriage event',
        'Efam_NoMarriage': 'no marriage event',
        'Efam_NoMention': 'no mention',
        'Efam_Engage': 'engage event',
        'Efam_Divorce': 'divorce event',
        'Efam_Separated': 'separate event',
        'Efam_Annulation': 'annulation',
        'Efam_MarriageBann': 'marriage bann',
        'Efam_MarriageContract': 'marriage contract',
        'Efam_MarriageLicense': 'marriage licence',
        'Efam_PACS': 'PACS',
        'Efam_Residence': 'residence'
    }

    if efam_name.startswith('Efam_Name:'):
        custom_name = efam_name[10:]
        return escape_html(driver.sou(base, custom_name))

    trans_key = event_translations.get(efam_name, efam_name)
    return transl(conf, trans_key)


def string_of_witness_kind(conf: config_module.Config, sex: gwdef.Sex, witness_kind: str) -> str:
    n = 0 if witness_kind == 'Witness' else index_of_sex(sex)

    witness_translations = {
        'Witness': 'witness/witness/witnesses',
        'Witness_CivilOfficer': 'civil registrar/civil registrar/civil registrar',
        'Witness_GodParent': 'godfather/godmother/godparents',
        'Witness_ReligiousOfficer': 'parrish registrar/parrish registrar/parrish registrar',
        'Witness_Informant': 'informant/informant/informant',
        'Witness_Attending': 'present/present/present',
        'Witness_Mentioned': 'mentioned/mentioned/mentioned',
        'Witness_Other': 'other/other/other'
    }

    trans_key = witness_translations.get(witness_kind, 'witness/witness/witnesses')
    return transl_nth(conf, trans_key, n)


def string_of_witness_kind_raw(witness_kind: str) -> str:
    witness_codes = {
        'Witness': '',
        'Witness_CivilOfficer': 'offi',
        'Witness_GodParent': 'godp',
        'Witness_ReligiousOfficer': 'reli',
        'Witness_Informant': 'info',
        'Witness_Attending': 'atte',
        'Witness_Mentioned': 'ment',
        'Witness_Other': 'othe'
    }
    return witness_codes.get(witness_kind, '')


def find_person_in_env(conf: config_module.Config, base: Any, suff: str) -> Optional[driver.GenPerson]:
    if hasattr(conf, 'env'):
        i_str = conf.env.get(f'i{suff}')
        if i_str:
            try:
                ip = int(i_str)
                return pget_opt(conf, base, ip)
            except ValueError:
                pass

        p_str = conf.env.get(f'p{suff}')
        n_str = conf.env.get(f'n{suff}')
        if p_str and n_str:
            oc_str = conf.env.get(f'oc{suff}', '0')
            try:
                occ = int(oc_str)
            except ValueError:
                occ = 0

            person = driver.person_of_key(base, p_str, n_str, occ)
            if person:
                return pget_opt(conf, base, driver.get_iper(person))

    return None


def default_sosa_ref(conf: config_module.Config, base: Any) -> Optional[driver.GenPerson]:
    for key, value in conf.base_env:
        if key == "default_sosa_ref":
            if value == "":
                return None
            ipl = gutil.person_ht_find_all(base, value)
            if len(ipl) == 1:
                ip = ipl[0]
                p = pget_opt(conf, base, ip)
                if p and not is_hidden(p):
                    return p
            return None
    return None


def find_sosa_ref(conf: config_module.Config, base: Any) -> Optional[driver.GenPerson]:
    p = find_person_in_env(conf, base, "z")
    if p:
        return p
    return default_sosa_ref(conf, base)


def search_in_assets(filename: str) -> str:
    asset_dirs = secure.assets()
    for asset_dir in asset_dirs:
        full_path = os.path.join(asset_dir, filename)
        if os.path.exists(full_path):
            return full_path
    return filename


def p_getenv(env: Dict[str, str], key: str) -> str:
    return env.get(key, '')


def p_getint(env: Dict[str, str], key: str) -> Optional[int]:
    val = env.get(key)
    if val:
        try:
            return int(val)
        except ValueError:
            return None
    return None


def designation(p: driver.GenPerson) -> str:
    if p.public_name:
        return p.public_name
    return f'{p.first_name} {p.surname}'


def has_children(base: Any, p: driver.GenPerson) -> bool:
    families = driver.get_family(p)
    for ifam in families:
        fam = driver.foi(base, ifam)
        if fam.children:
            return True
    return False


def hexa_string(s: str) -> str:
    return ''.join(format(ord(c), '02x') for c in s)


def is_number(s: str) -> bool:
    return s and s[0].isdigit()


def only_printable(s: str) -> bool:
    return all(c.isprintable() for c in s)


def cut_words(s: str) -> List[str]:
    return s.split()


def reduce_list(max_len: int, lst: List[Any]) -> List[Any]:
    return lst[:max_len]


def string_of_pevent_name(conf: config_module.Config, event_name: str) -> str:
    return transl(conf, event_name)


def string_of_fevent_name(conf: config_module.Config, event_name: str) -> str:
    return transl(conf, event_name)


def string_of_witness_kind(conf: config_module.Config, kind: Any) -> str:
    if kind == gwdef.WitnessKind.WITNESS:
        return transl(conf, 'witness')
    elif kind == gwdef.WitnessKind.WITNESS_GOD_PARENT:
        return transl(conf, 'godparent')
    else:
        return transl(conf, 'witness')


def relation_txt(conf: config_module.Config, relation: gwdef.RelationKind) -> str:
    if relation == gwdef.RelationKind.MARRIED:
        return transl(conf, 'married')
    elif relation == gwdef.RelationKind.NOT_MARRIED:
        return transl(conf, 'not married')
    elif relation == gwdef.RelationKind.ENGAGED:
        return transl(conf, 'engaged')
    elif relation == gwdef.RelationKind.NO_SEXES_CHECK_NOT_MARRIED:
        return transl(conf, 'relationship')
    elif relation == gwdef.RelationKind.NO_SEXES_CHECK_MARRIED:
        return transl(conf, 'civil marriage')
    elif relation == gwdef.RelationKind.NO_MENTION:
        return ''
    elif relation == gwdef.RelationKind.NO_SEXES_CHECK_ENGAGED:
        return transl(conf, 'engagement')
    elif relation == gwdef.RelationKind.MARRIAGE_BANNS:
        return transl(conf, 'marriage banns')
    elif relation == gwdef.RelationKind.MARRIAGE_CONTRACT:
        return transl(conf, 'marriage contract')
    elif relation == gwdef.RelationKind.MARRIAGE_LICENSE:
        return transl(conf, 'marriage license')
    elif relation == gwdef.RelationKind.PACS:
        return transl(conf, 'PACS')
    elif relation == gwdef.RelationKind.RESIDENCE:
        return transl(conf, 'residence')
    else:
        return ''


def get_referer(conf: config_module.Config) -> str:
    return conf.env.get('HTTP_REFERER', '')


def index_of_sex(sex: gwdef.Sex) -> int:
    if sex == gwdef.Sex.MALE:
        return 0
    elif sex == gwdef.Sex.FEMALE:
        return 1
    else:
        return 2


def is_empty_name(p: driver.GenPerson) -> bool:
    return p.surname == '?' and p.first_name == '?'


def translate_eval(s: str) -> str:
    return s


def relation_date(conf: config_module.Config, fam: driver.GenFamily) -> str:
    dmy_opt = date.cdate_to_dmy_opt(fam.marriage)
    if dmy_opt:
        return f" {transl(conf, 'in (year)')} {dmy_opt.year}"
    return ''


def child_of_parent(conf: config_module.Config, base: Any, p: driver.GenPerson) -> str:
    def print_father(fath: driver.GenPerson) -> str:
        if p.surname != fath.surname:
            return gen_person_text(conf, base, fath)
        else:
            return gen_person_text(conf, base, fath, sn=False)

    a = pget(conf, base, driver.get_iper(p))
    parents = driver.get_parents(a)

    if parents is None:
        return ''

    ifam = parents
    cpl = driver.foi(base, ifam)

    fath_ip = driver.get_father(cpl)
    fath = pget(conf, base, fath_ip)
    fath_obj = None if fath.first_name == '?' else fath

    moth_ip = driver.get_mother(cpl)
    moth = pget(conf, base, moth_ip)
    moth_obj = None if moth.first_name == '?' else moth

    if fath_obj is None and moth_obj is None:
        return ''

    if fath_obj and moth_obj:
        s = transl_a_of_b(conf,
                          transl_nth(conf, 'son/daughter/child', index_of_sex(p.sex)),
                          print_father(fath_obj),
                          gen_person_text(conf, base, fath_obj))
        s += f" {transl(conf, 'and')} {gen_person_text(conf, base, moth_obj)}"
        return s
    elif fath_obj:
        return transl_a_of_b(conf,
                            transl_nth(conf, 'son/daughter/child', index_of_sex(p.sex)),
                            print_father(fath_obj),
                            gen_person_text(conf, base, fath_obj))
    else:
        return transl_a_of_b(conf,
                            transl_nth(conf, 'son/daughter/child', index_of_sex(p.sex)),
                            gen_person_text(conf, base, moth_obj),
                            gen_person_text(conf, base, moth_obj))


def husband_wife(conf: config_module.Config, base: Any, p: driver.GenPerson, all: bool) -> str:
    families = driver.get_family(p)

    if not families:
        return ''

    def check_multiple() -> int:
        if len(families) == 0:
            return 0

        kind = None
        for i, ifam in enumerate(families):
            fam = driver.foi(base, ifam)
            cur_type = fam.relation
            if i == 0:
                kind = cur_type
            elif cur_type != kind:
                return -1
        return len(families)

    multiple = check_multiple()

    relation = ''
    if len(families) > 0:
        if multiple >= 0:
            fam = driver.foi(base, families[0])
            relation = relation_txt(conf, fam.relation)
        else:
            relation = transl(conf, 'marriages with')

    nb_fam = len(families)
    result_parts = []

    for i in range(nb_fam):
        fam = driver.foi(base, families[i])
        ip = driver.get_iper(p)
        conjoint_ip = gutil.spouse(ip, fam)
        conjoint = pget(conf, base, conjoint_ip)

        if not is_empty_name(conjoint):
            if all or i == 0:
                result_parts.append(gen_person_text(conf, base, conjoint))
                rd = relation_date(conf, fam)
                if rd:
                    result_parts.append(rd)

    if result_parts:
        s = relation
        if s:
            s += ' '
        s += ', '.join(result_parts)
        return s

    return ''


def first_child(conf: config_module.Config, base: Any, p: driver.GenPerson) -> str:
    is_idx = index_of_sex(p.sex)
    families = driver.get_family(p)

    for ifam in families:
        fam = driver.foi(base, ifam)
        children = fam.children

        if children:
            enfant = pget(conf, base, children[0])

            if is_hide_names(conf, enfant) and not authorized_age(conf, base, enfant):
                child = 'xx'
            elif p.surname != enfant.surname:
                child = gen_person_text(conf, base, enfant)
            else:
                child = gen_person_text(conf, base, enfant, sn=False)

            return transl_a_of_b(conf,
                                transl_nth(conf, 'father/mother', is_idx),
                                child,
                                child)

    return ''


def specify_homonymous(conf: config_module.Config, base: Any, p: driver.GenPerson,
                       specify_public_name: bool) -> str:
    result = []

    if p.public_name and specify_public_name:
        result.append(' ')
        result.append(escape_html(p.public_name))
        if p.qualifiers:
            result.append(' <em>')
            result.append(escape_html(p.qualifiers[0]))
            result.append('</em>')
    elif not p.public_name and p.qualifiers and specify_public_name:
        result.append(' ')
        result.append(escape_html(p.first_name))
        result.append(' <em>')
        result.append(escape_html(p.qualifiers[0]))
        result.append('</em>')
    elif p.public_name and not p.qualifiers and specify_public_name:
        result.append(' ')
        result.append(escape_html(p.public_name))
    else:
        cop = child_of_parent(conf, base, p)
        if cop:
            result.append(', ')
            result.append(cop)

        hw = husband_wife(conf, base, p, True)
        if not hw:
            fc = first_child(conf, base, p)
            if fc:
                result.append(', ')
                result.append(fc)
        else:
            result.append(', ')
            result.append(hw)

    return ''.join(result)


def relation_type_text(conf: config_module.Config, t: gwdef.RelationType, n: int) -> str:
    if t == gwdef.RelationType.ADOPTION:
        return transl_nth(conf, 'adoptive father/adoptive mother/adoptive parents', n)
    elif t == gwdef.RelationType.RECOGNITION:
        return transl_nth(conf, 'recognizing father/recognizing mother/recognizing parents', n)
    elif t == gwdef.RelationType.CANDIDATE_PARENT:
        return transl_nth(conf, 'candidate father/candidate mother/candidate parents', n)
    elif t == gwdef.RelationType.GOD_PARENT:
        return transl_nth(conf, 'godfather/godmother/godparents', n)
    elif t == gwdef.RelationType.FOSTER_PARENT:
        return transl_nth(conf, 'foster father/foster mother/foster parents', n)
    return ''


def rchild_type_text(conf: config_module.Config, t: gwdef.RelationType, n: int) -> str:
    if t == gwdef.RelationType.ADOPTION:
        return transl_nth(conf, 'adoptive son/adoptive daughter/adoptive child', n)
    elif t == gwdef.RelationType.RECOGNITION:
        return transl_nth(conf, 'recognized son/recognized daughter/recognized child', n)
    elif t == gwdef.RelationType.CANDIDATE_PARENT:
        return transl_nth(conf, 'candidate son/candidate daughter/candidate child', n)
    elif t == gwdef.RelationType.GOD_PARENT:
        return transl_nth(conf, 'godson/goddaughter/godchild', n)
    elif t == gwdef.RelationType.FOSTER_PARENT:
        return transl_nth(conf, 'foster son/foster daughter/foster child', n)
    return ''


def skip_spaces(s: str, i: int) -> int:
    while i < len(s) and s[i] == ' ':
        i += 1
    return i


def create_env(s: str) -> List[Tuple[str, str]]:
    use_amp = 'content-disposition' not in s.lower()

    def get_assoc(beg: int, i: int) -> List[str]:
        if i == len(s):
            if i == beg:
                return []
            else:
                return [s[beg:i]]
        elif s[i] == ';' or (s[i] == '&' and use_amp):
            next_i = skip_spaces(s, i + 1)
            return [s[beg:i]] + get_assoc(next_i, next_i)
        else:
            return get_assoc(beg, i + 1)

    def separate(s: str) -> Tuple[str, str]:
        for i in range(len(s)):
            if s[i] == '=':
                return (s[:i], s[i+1:])
        return (s, '')

    return [separate(item) for item in get_assoc(0, 0)]


def find_file_in_directories(directories: List[str], filename: str) -> Optional[str]:
    for directory in directories:
        full_path = os.path.join(directory, filename)
        if os.path.exists(full_path):
            return full_path
    return None


def generate_search_directories(conf: config_module.Config) -> List[str]:
    base_etc = os.path.join(conf.base_dir if hasattr(conf, 'base_dir') else '.',
                           'etc', conf.bname)

    asset_dirs = []
    if hasattr(conf, 'asset_dirs'):
        asset_dirs = conf.asset_dirs

    configured_templates = [conf.bname]
    allow_all = True

    if hasattr(conf, 'base_env'):
        template_config = ''
        for key, val in conf.base_env:
            if key == 'template':
                template_config = val
                break
        if template_config:
            templates = [t.strip() for t in template_config.split(',') if t.strip()]
            allow_all = '*' in templates
            configured_templates = [t for t in templates if t != '*']

    current_template = None
    if hasattr(conf, 'env'):
        templ = conf.env.get('templ', '')
        if templ and (allow_all or templ in configured_templates):
            current_template = templ

    if not current_template and configured_templates:
        current_template = configured_templates[0]

    template_dirs = []
    if current_template:
        template_dirs.append(os.path.join(base_etc, current_template))
    template_dirs.append(base_etc)

    asset_template_dirs = []
    for asset_dir in asset_dirs:
        etc_dir = os.path.join(asset_dir, 'etc')
        if current_template:
            asset_template_dirs.append(os.path.join(etc_dir, current_template))
        asset_template_dirs.append(etc_dir)

    return template_dirs + asset_template_dirs


def find_template_file(conf: config_module.Config, fname: str, auto_txt: bool = False) -> str:
    normalized_fname = os.path.join(*fname.split('/'))

    final_fname = normalized_fname
    if auto_txt and not normalized_fname.endswith('.txt'):
        final_fname = normalized_fname + '.txt'

    search_dirs = generate_search_directories(conf)

    found = find_file_in_directories(search_dirs, final_fname)
    if found:
        return found

    if hasattr(conf, 'gw_prefix'):
        fallback = os.path.join(conf.gw_prefix, 'etc', final_fname)
        if os.path.exists(fallback):
            return fallback

    return os.path.join('etc', final_fname)


def resolve_asset_file(conf: config_module.Config, fname: str) -> str:
    return find_template_file(conf, fname, auto_txt=False)


def read_base_env(bname: str, gw_prefix: str, debug: bool = False) -> List[Tuple[str, str]]:
    def load_file(fname: str) -> List[Tuple[str, str]]:
        try:
            env = []
            with open(fname, 'r', encoding='utf-8') as f:
                for line in f:
                    s = line.rstrip()
                    if not s or s[0] == '#':
                        continue

                    eq_idx = s.find('=')
                    if eq_idx >= 0:
                        env.append((s[:eq_idx], s[eq_idx+1:]))
                    else:
                        env.append((s, ''))

            return env
        except (IOError, OSError) as e:
            if debug:
                print(f"Error {e} while loading {fname}, using empty config", file=__import__('sys').stderr)
            return []

    config_dir = os.path.join(gw_prefix, 'etc', bname)
    fname1 = os.path.join(config_dir, f'{bname}.gwf')

    if os.path.exists(fname1):
        return load_file(fname1)

    fname2 = os.path.join(gw_prefix, 'a.gwf')
    if os.path.exists(fname2):
        if debug:
            print(f"Using configuration from {fname2}", file=__import__('sys').stderr)
        return load_file(fname2)

    if debug:
        print(f"No config file found in either {fname1} or {fname2}", file=__import__('sys').stderr)

    return []


def print_default_gwf_file(bname: str, config_dir: str):
    gwf = [
        "access_by_key=yes",
        "disable_forum=yes",
        "hide_private_names=no",
        "use_restrict=no",
        "show_consang=yes",
        "display_sosa=yes",
        "place_surname_link_to_ind=yes",
        "max_anc_level=8",
        "max_anc_tree=7",
        "max_desc_level=12",
        "max_desc_tree=4",
        "max_cousins=2000",
        "max_cousins_level=5",
        "latest_event=20",
        "template=*",
        "long_date=no",
        "counter=no",
        "full_siblings=yes",
        "hide_advanced_request=no",
        "p_mod=",
    ]

    fname = os.path.join(config_dir, f'{bname}.gwf')

    if not os.path.exists(fname):
        try:
            if not os.path.exists(config_dir):
                os.makedirs(config_dir, mode=0o755)

            if bname == '' or os.path.exists(fname):
                return

            with open(fname, 'w', encoding='utf-8') as f:
                for line in gwf:
                    f.write(line + '\n')
        except (IOError, OSError):
            pass


def begin_centered(conf: config_module.Config):
    border = conf.border if hasattr(conf, 'border') else 0
    print(f'<table border="{border}" width="100%"><tr><td align="center">')


def end_centered(conf: config_module.Config):
    print('</td></tr></table>')


def menu_threshold() -> int:
    return 20


def print_alphab_list(conf: config_module.Config, crit: callable,
                     print_elem: callable, liste: List[Any]):
    length = len(liste)

    if not liste:
        print('<ul></ul>')
        return

    threshold = menu_threshold()

    if length > threshold:
        print('<p>')

        seen = []
        for elem in liste:
            t = crit(elem)
            if t not in seen:
                print(f'<a href="#ai{hexa_string(t)}">{escape_html(t)}</a>')
                seen.append(t)

        print('</p>')
        print('<ul>')
    else:
        print('<ul>')

    current_group = []
    current_index = None

    def print_group(group: List[Any], index: Optional[str]):
        if not group:
            return

        if length > threshold or (group and is_number(crit(group[0]))):
            if index:
                print(f'</ul><h3 class="subtitle mx-3" id="ai{hexa_string(index)}">{escape_html(index)}</h3><ul>')

        for elem in group:
            print('<li>')
            print_elem(elem)
            print('</li>')

    for elem in liste:
        t = crit(elem)

        if length > threshold or is_number(t):
            if current_index is None or t != current_index:
                print_group(current_group, current_index)
                current_group = [elem]
                current_index = t
            else:
                current_group.append(elem)
        else:
            print('<li>')
            print_elem(elem)
            print('</li>')

    if current_group:
        print_group(current_group, current_index)

    print('</ul>')


def dispatch_in_columns(ncol: int, lst: List[Any], order: callable) -> Tuple[List[int], List[Tuple[str, str, Any]]]:
    class ElemKind:
        HEAD_ELEM = 'head'
        CONT_ELEM = 'cont'
        ELEM = 'elem'

    def kind_size(kind: str) -> int:
        return 4 if kind in (ElemKind.HEAD_ELEM, ElemKind.CONT_ELEM) else 1

    rlist = []
    prev_ord = None

    for elem in lst:
        ord = order(elem)

        if not rlist:
            kind = ElemKind.HEAD_ELEM
        else:
            if ord == prev_ord or (ord and prev_ord and ord[0] == prev_ord[0]):
                kind = ElemKind.ELEM
            else:
                kind = ElemKind.HEAD_ELEM

        rlist.insert(0, [kind, ord, elem])
        prev_ord = ord

    ini_list = []
    ini_len = 0

    for kind_ref, ord, elem in rlist:
        ini_list.insert(0, (kind_ref, ord, elem))
        ini_len += kind_size(kind_ref[0])

    def compute_lens(ncol: int, ini_list: List, ini_len: int) -> List[int]:
        def loop(cnt: int, col: int, accu: int, length: int, remaining: List) -> List[int]:
            if col > ncol:
                result = []
                total = 0
                for _ in range(ncol):
                    result.append(ini_len // ncol)
                    total += ini_len // ncol

                if total < ini_len:
                    result[0] += ini_len - total

                return result

            if not remaining:
                if col == ncol:
                    return [cnt]
                else:
                    return [cnt] + loop(0, col + 1, 0, length, ini_list)

            kind_ref, _, _ = remaining[0]
            remaining_tail = remaining[1:]

            new_accu = accu + (ncol * kind_size(kind_ref[0]))
            new_cnt = cnt + 1

            if new_accu > length and kind_ref[0] == ElemKind.ELEM:
                kind_ref[0] = ElemKind.CONT_ELEM
                return loop(0, 1, 0, length + kind_size(ElemKind.CONT_ELEM) - 1, ini_list)
            else:
                result = loop(new_cnt, col, new_accu, length, remaining_tail)
                if col == ncol and remaining_tail:
                    return [cnt] + loop(0, col + 1, 0, length, remaining_tail)
                return result

        return loop(0, 1, 0, ini_len, ini_list)

    len_list = compute_lens(ncol, ini_list, ini_len)

    return len_list, ini_list


def print_in_columns(conf: config_module.Config, ncols: int, len_list: List[int],
                    lst: List[Tuple[str, str, Any]], wprint_elem: callable):
    begin_centered(conf)

    border = conf.border if hasattr(conf, 'border') else 0
    print(f'<table width="95%" border="{border}">')

    left = conf.left if hasattr(conf, 'left') else 'left'
    print(f'<tr align="{left}" valign="top">')

    remaining = lst
    first = True

    for length in len_list:
        def process_column(n: int, items: List) -> List:
            if n == 0:
                print('</ul>\n</td>')
                return items

            if not items:
                return []

            kind_ref, ord, elem = items[0]
            rest = items[1:]

            if n == length:
                print(f'<td width="{100 // ncols}">')
            elif kind_ref[0] != 'elem':
                print('</ul>')

            if kind_ref[0] != 'elem':
                ord_display = '...' if not ord else ord[0]
                continued = '' if kind_ref[0] == 'head' else f" ({transl(conf, 'continued')})"
                print(f'<h3 class="subtitle mx-3">{ord_display}{continued}</h3>')
                print('<ul>')

            print('<li>')
            wprint_elem(elem)
            print('</li>')

            return process_column(n - 1, rest)

        remaining = process_column(length, remaining)

    print('</tr>')
    print('</table>')
    end_centered(conf)


def wprint_in_columns(conf: config_module.Config, order: callable,
                     wprint_elem: callable, lst: List[Any]):
    ncols = p_getint(conf.env, 'ncols') or 3
    ncols = max(1, ncols)

    len_list, ordered_list = dispatch_in_columns(ncols, lst, order)
    print_in_columns(conf, ncols, len_list, ordered_list, wprint_elem)


def expand_env(conf: config_module.Config, s: str) -> str:
    if not hasattr(conf, 'base_env'):
        return s

    expand_enabled = 'no'
    for key, val in conf.base_env:
        if key == 'expand_env':
            expand_enabled = val
            break
    if expand_enabled != 'yes':
        return s

    result = []
    i = 0

    while i < len(s):
        if i + 1 < len(s) and s[i] == '$' and s[i + 1] == '{':
            try:
                j = s.index('}', i + 1)
                var_name = s[i + 2:j]
                var_value = os.environ.get(var_name, '')
                result.append(var_value)
                i = j + 1
            except ValueError:
                result.append(s[i])
                i += 1
        else:
            result.append(s[i])
            i += 1

    return ''.join(result)


def string_with_macros(conf: config_module.Config, env: Dict[str, callable], s: str) -> str:
    result = []
    i = 0

    while i < len(s):
        if i + 1 < len(s) and s[i] == '%':
            char = s[i + 1]

            if char in env:
                result.append(env[char]())
                i += 2
                continue
            elif char == 's':
                result.append(commd(conf))
                i += 2
                continue
            elif char == 'v':
                var_start = i + 2
                var_end = var_start

                while var_end < len(s) and s[var_end].isalnum() or (var_end < len(s) and s[var_end] == '_'):
                    var_end += 1

                if var_end > var_start:
                    var_name = s[var_start:var_end]

                    if hasattr(conf, 'base_env'):
                        var_key = f'var_{var_name}'
                        var_value = conf.base_env.get(var_key, '')
                        if var_value:
                            result.append(expand_env(conf, var_value))
                            i = var_end
                            continue

                result.append(s[i])
                i += 1
                continue

        result.append(s[i])
        i += 1

    return ''.join(result)


def name_with_roman_number(s: str) -> Optional[str]:
    result = []
    found = False
    i = 0

    while i < len(s):
        if s[i].isdigit():
            n = 0
            while i < len(s) and s[i].isdigit():
                n = n * 10 + int(s[i])
                i += 1

            if 1 <= n < 4000:
                result.append(mutil.roman_of_arabian(n))
                found = True
            else:
                result.append(str(n))
        else:
            result.append(s[i])
            i += 1

    if found:
        return ''.join(result)
    return None


def p_of_sosa(conf: config_module.Config, base: Any, sosa_num: Any, p0: driver.GenPerson) -> Optional[driver.GenPerson]:
    from lib import sosa
    path = sosa.branches(sosa_num)

    current = p0
    for branch in path:
        parents = driver.get_parents(current)
        if parents is None:
            return None

        cpl = driver.foi(base, parents)
        if branch == 0:
            current = pget(conf, base, driver.get_father(cpl))
        else:
            current = pget(conf, base, driver.get_mother(cpl))

    return current


def branch_of_sosa(conf: config_module.Config, base: Any, sosa_num: Any, p: driver.GenPerson) -> Optional[List[driver.GenPerson]]:
    from lib import sosa

    if sosa.eq(sosa_num, sosa.zero()):
        raise ValueError("branch_of_sosa: sosa cannot be zero")

    def expand_branches(sosa_val):
        bl = []
        while not sosa.eq(sosa_val, sosa.one()):
            bl.insert(0, sosa.even(sosa_val))
            sosa_val = sosa.half(sosa_val)
        return bl

    branches = expand_branches(sosa_num)

    result = []
    current = p
    for is_male in branches:
        result.append(current)
        parents = driver.get_parents(current)
        if parents is None:
            return None

        cpl = driver.foi(base, parents)
        if is_male:
            current = pget(conf, base, driver.get_father(cpl))
        else:
            current = pget(conf, base, driver.get_mother(cpl))

    result.append(current)
    return result


def sosa_of_branch(person_list: List[driver.GenPerson]) -> Any:
    from lib import sosa

    if not person_list:
        raise ValueError("sosa_of_branch: empty list")

    reversed_list = list(reversed(person_list))
    ipl = reversed_list[1:]

    result = sosa.one()
    for p in ipl:
        result = sosa.twice(result)
        if driver.get_sex(p) == gwdef.Sex.FEMALE:
            result = sosa.inc(result, 1)
        elif driver.get_sex(p) != gwdef.Sex.MALE:
            raise AssertionError("sosa_of_branch: neuter sex not allowed")

    return result


def is_that_user_and_password(auth_scheme: str, user: str, passwd: str) -> bool:
    return False


def browser_doesnt_have_tables(conf: config_module.Config) -> bool:
    user_agent = ''
    for item in conf.request:
        if item.lower().startswith('user-agent:'):
            user_agent = item.split('/', 1)[0].lower()
            break
    return 'lynx' in user_agent


def of_course_died(conf: config_module.Config, p: driver.GenPerson) -> bool:
    birth_dmy = date.cdate_to_dmy_opt(p.birth) if isinstance(p.birth, adef.CdateDate) else None
    if birth_dmy:
        import datetime
        current_year = datetime.datetime.now().year
        return current_year - birth_dmy.year > conf.private_years + 20
    return False


def escache_value(base: Any) -> str:
    t = driver.date_of_last_change(base)
    v = int(t % 2147483647)
    return str(v)


def start_equiv_with(case_sens: bool, s: str, m: str, i: int) -> Optional[int]:
    def test(idx_m, idx_s):
        if idx_s == len(s):
            return idx_m
        if idx_m == len(m):
            return None

        if case_sens:
            if m[idx_m] == s[idx_s]:
                return test(idx_m + 1, idx_s + 1)
            return None
        else:
            next_chars = name.next_chars_if_equiv(m, idx_m, s, idx_s)
            if next_chars:
                return test(next_chars[0], next_chars[1])
            return None

    if case_sens:
        if i < len(m) and m[i] == s[0]:
            return test(i + 1, 1)
        return None
    else:
        next_chars = name.next_chars_if_equiv(m, i, s, 0)
        if next_chars:
            return test(next_chars[0], next_chars[1])
        return None


def in_text(case_sens: bool, s: str, m: str) -> bool:
    def loop(in_tag, i):
        if i >= len(m):
            return False
        if in_tag:
            return loop(m[i] != '>', i + 1)
        if m[i] == '<':
            return loop(True, i + 1)

        match_pos = start_equiv_with(case_sens, s, m, i)
        if match_pos is not None:
            return True
        return loop(False, i + 1)

    return loop(False, 0)


def html_highlight(case_sens: bool, h: str, s: str) -> str:
    def highlight_text(start, end):
        return f'<span class="found">{s[start:end]}</span>'

    result = []
    i = 0
    in_tag = False

    while i < len(s):
        if in_tag:
            result.append(s[i])
            in_tag = s[i] != '>'
            i += 1
        elif s[i] == '<':
            result.append(s[i])
            in_tag = True
            i += 1
        else:
            match_end = start_equiv_with(case_sens, h, s, i)
            if match_end is not None:
                result.append(highlight_text(i, match_end))
                i = match_end
            else:
                result.append(s[i])
                i += 1

    return ''.join(result)


def cache_visited(conf: config_module.Config) -> str:
    bname = conf.bname
    if not bname.endswith('.gwb'):
        bname = bname + '.gwb'
    return os.path.join(bname, 'cache_visited')


def read_visited(conf: config_module.Config) -> Dict[str, List[Tuple[int, str]]]:
    fname = cache_visited(conf)
    if not os.path.exists(fname):
        return {}

    try:
        import pickle
        with open(fname, 'rb') as f:
            return pickle.load(f)
    except Exception:
        return {}


def write_visited(conf: config_module.Config, ht: Dict[str, List[Tuple[int, str]]]):
    fname = cache_visited(conf)
    try:
        import pickle
        os.makedirs(os.path.dirname(fname), exist_ok=True)
        with open(fname, 'wb') as f:
            pickle.dump(ht, f)
    except Exception:
        pass


def record_visited(conf: config_module.Config, ip: int):
    if conf.friend or conf.wizard:
        ht = read_visited(conf)
        import datetime
        time_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        if conf.user not in ht:
            ht[conf.user] = []

        vl = ht[conf.user]
        vl.insert(0, (ip, time_str))

        unique_vl = []
        seen_ips = set()
        for entry in vl:
            if entry[0] not in seen_ips:
                unique_vl.append(entry)
                seen_ips.add(entry[0])

        max_entries = 100
        ht[conf.user] = unique_vl[:max_entries]

        write_visited(conf, ht)
