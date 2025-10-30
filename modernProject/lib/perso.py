from typing import Optional, Tuple, List, Any, Dict, Callable
from enum import Enum
import math

from lib import gwdef
from lib import adef
from lib import config
from lib import driver
from lib import util
from lib import date as gw_date
from lib import sosa
from lib import futil
from lib import mutil
from lib import name
from lib import gutil
from lib import templ
from lib import output

Base = Any


MAX_IM_WID = 240
INFINITE = 10000


class Pos(Enum):
    LEFT = "left"
    RIGHT = "right"
    CENTER = "center"
    ALONE = "alone"


class Cell(Enum):
    EMPTY = "empty"
    FULL = "full"


class Dup(Enum):
    DUP_FAM = "dup_fam"
    DUP_IND = "dup_ind"
    NO_DUP = "no_dup"


class GenerationPerson:
    pass


class GP_person(GenerationPerson):
    def __init__(self, sosa_num, iper, ifam):
        self.sosa = sosa_num
        self.iper = iper
        self.ifam = ifam


class GP_same(GenerationPerson):
    def __init__(self, sosa1, sosa2, iper):
        self.sosa1 = sosa1
        self.sosa2 = sosa2
        self.iper = iper


class GP_interv(GenerationPerson):
    def __init__(self, interval):
        self.interval = interval


class GP_missing(GenerationPerson):
    def __init__(self, sosa_num, iper):
        self.sosa = sosa_num
        self.iper = iper


def round_2_dec(x: float) -> float:
    return math.floor((x * 100.0) + 0.5) / 100.0


def hide_person(conf: config.Config, base: Any, p: driver.Person) -> bool:
    return (not util.authorized_age(conf, base, p)) or util.is_hide_names(conf, p)


def string_of_marriage_text(conf: config.Config, base: Base, fam: driver.Family) -> str:
    marriage = gw_date.od_of_cdate(driver.get_marriage(fam))
    marriage_place = driver.sou(base, driver.get_marriage_place(fam))
    s = ""
    if marriage:
        s = " " + str(marriage)
    if marriage_place:
        s = s + ", " + util.safe_html(util.string_with_macros(conf, [], marriage_place)) + ","
    return s


def string_of_title(conf: config.Config, base: Base, and_txt: str, p: driver.Person,
                    title_data: Tuple, safe: bool = False, link: bool = True) -> str:
    nth, name, title, places, dates = title_data
    return ""


def name_equiv(n1, n2) -> bool:
    return futil.eq_title_names(n1, n2) or (n1 == gwdef.Tmain and n2 == gwdef.Tnone) or (n1 == gwdef.Tnone and n2 == gwdef.Tmain)


def nobility_titles_list(conf: config.Config, base: Base, p: driver.Person) -> List:
    titles = []
    return titles


def has_history(conf: config.Config, base: Base, p: driver.Person, p_auth: bool) -> bool:
    return False


def get_death_text(conf: config.Config, p: driver.Person, p_auth: bool) -> str:
    if not p_auth:
        return ""
    sex_index = util.index_of_sex(driver.get_sex(p))
    death = driver.get_death(p)
    if isinstance(death, gwdef.DeathWithReason):
        dr = death.reason
        if dr == gwdef.DeathReason.UNSPECIFIED:
            return util.transl_nth(conf, "died", sex_index)
        elif dr == gwdef.DeathReason.MURDERED:
            return util.transl_nth(conf, "murdered", sex_index)
        elif dr == gwdef.DeathReason.KILLED:
            return util.transl_nth(conf, "killed (in action)", sex_index)
        elif dr == gwdef.DeathReason.EXECUTED:
            return util.transl_nth(conf, "executed (legally killed)", sex_index)
        elif dr == gwdef.DeathReason.DISAPPEARED:
            return util.transl_nth(conf, "disappeared", sex_index)
    elif isinstance(death, gwdef.DeadYoung):
        return util.transl_nth(conf, "died young", sex_index)
    elif isinstance(death, gwdef.DeadDontKnowWhen):
        return util.transl_nth(conf, "died", sex_index)
    elif isinstance(death, gwdef.DontKnowIfDead):
        return ""
    elif isinstance(death, gwdef.OfCourseDead):
        return util.transl_nth(conf, "died", sex_index)
    return ""


def get_baptism_text(conf: config.Config, p: driver.Person, p_auth: bool) -> str:
    if not p_auth:
        return ""
    sex_index = util.index_of_sex(driver.get_sex(p))
    return util.transl_nth(conf, "baptized", sex_index)


def get_birth_text(conf: config.Config, p: driver.Person, p_auth: bool) -> str:
    if not p_auth:
        return ""
    sex_index = util.index_of_sex(driver.get_sex(p))
    return util.transl_nth(conf, "born", sex_index)


def get_marriage_date_text(conf: config.Config, fam: driver.Family, p_auth: bool) -> str:
    if not p_auth:
        return ""
    return ""


def get_burial_text(conf: config.Config, p: driver.Person, p_auth: bool) -> str:
    if not p_auth:
        return ""
    sex_index = util.index_of_sex(driver.get_sex(p))
    return util.transl_nth(conf, "buried", sex_index)


def get_cremation_text(conf: config.Config, p: driver.Person, p_auth: bool) -> str:
    if not p_auth:
        return ""
    sex_index = util.index_of_sex(driver.get_sex(p))
    return util.transl_nth(conf, "cremated", sex_index)


def limit_desc(conf: config.Config) -> int:
    try:
        return int(conf.base_env.get("max_desc_level", INFINITE))
    except:
        return INFINITE


def get_descendants_at_level(base: Base, p: driver.Person, lev2: int) -> List:
    descendants = []
    return descendants


def make_desc_level_table(conf: config.Config, base: Base, max_level: int, p: driver.Person):
    desc_mark = {}
    fam_mark = {}
    return desc_mark, fam_mark


def desc_level_max(base: Base, desc_level_table_l) -> int:
    return 0


def max_descendant_level(base: Base, desc_level_table_l) -> int:
    return 0


def next_generation(conf: config.Config, base: Base, mark, gpl: List) -> List:
    return []


def next_generation2(conf: config.Config, base: Base, mark, gpl: List) -> List:
    return []


def sosa_is_present(all_gp: List, n1) -> bool:
    return False


def get_link(all_gp: List, ip) -> Optional[GenerationPerson]:
    return None


def parent_sosa(conf: config.Config, base: Base, ip, all_gp, n, parent) -> Optional:
    return None


def will_print(gp) -> bool:
    return isinstance(gp, (GP_person, GP_same, GP_missing))


def get_all_generations(conf: config.Config, base: Base, p: driver.Person) -> List:
    return []


def enrich(lst1: List, lst2: List) -> List:
    return []


def is_empty(lst: List) -> bool:
    return all(x == Cell.EMPTY for x in lst)


def enrich_tree(lst: List) -> List:
    return lst


def tree_generation_list(conf: config.Config, base: Base, gv, p: driver.Person) -> List:
    return []


def get_date_place(conf: config.Config, base: Base, auth_for_all_anc: bool, p: driver.Person):
    return None


def gen_excluded_possible_duplications(conf: config.Config, s: str, i_of_string):
    return ([], [])


def excluded_possible_duplications(conf: config.Config):
    return gen_excluded_possible_duplications(conf, "excl_dup", lambda x: x)


def first_possible_duplication_children(iexcl, length, child, eq) -> Optional:
    return None


def first_possible_duplication(base: Base, ip, excl_dup) -> Dup:
    return Dup.NO_DUP


def has_possible_duplications(conf: config.Config, base: Base, p: driver.Person) -> bool:
    return False


def merge_date_place(conf: config.Config, base: Base, surn, date_place_auth, p: driver.Person):
    return []


def build_surnames_list(conf: config.Config, base: Base, v, p: driver.Person):
    return []


def build_list_eclair(conf: config.Config, base: Base, v, p: driver.Person):
    return []


def linked_page_text(conf: config.Config, base: Base, p: driver.Person, s: str, key, str_val, page_data) -> str:
    return ""


def compare_ls(sl1: List, sl2: List) -> int:
    return 0


def has_witness_for_event(conf: config.Config, base: Base, p: driver.Person, event_name: str) -> bool:
    return False


def get_env(v: str, env: Dict) -> Any:
    return env.get(v)


def get_vother(x):
    return None


def set_vother(x):
    return x


def extract_var(sini: str, s: str) -> Tuple:
    return ("", "")


def template_file_ref():
    return "perso.txt"


def warning_use_has_parents_before_parent(loc, var, r):
    pass


def bool_val(x: bool):
    return x


def str_val(x: str):
    return x


def null_val():
    return ""


def safe_val(x):
    return x


def gen_string_of_img_sz(max_w: int, max_h: int, conf: config.Config, base: Base, p_auth_tuple) -> str:
    return ""


def gen_string_of_fimg_sz(max_w: int, max_h: int, conf: config.Config, base: Base, p_auth_tuple) -> str:
    return ""


def string_of_image_size(conf: config.Config, base: Base, p_auth_tuple) -> str:
    return gen_string_of_img_sz(MAX_IM_WID, MAX_IM_WID, conf, base, p_auth_tuple)


def string_of_image_medium_size(conf: config.Config, base: Base, p_auth_tuple) -> str:
    return gen_string_of_img_sz(160, 120, conf, base, p_auth_tuple)


def string_of_image_small_size(conf: config.Config, base: Base, p_auth_tuple) -> str:
    return gen_string_of_img_sz(100, 75, conf, base, p_auth_tuple)


def string_of_blason_size(conf: config.Config, base: Base, p_auth_tuple) -> str:
    return gen_string_of_fimg_sz(MAX_IM_WID, MAX_IM_WID, conf, base, p_auth_tuple)


def string_of_blason_medium_size(conf: config.Config, base: Base, p_auth_tuple) -> str:
    return gen_string_of_fimg_sz(160, 120, conf, base, p_auth_tuple)


def string_of_blason_small_size(conf: config.Config, base: Base, p_auth_tuple) -> str:
    return gen_string_of_fimg_sz(100, 75, conf, base, p_auth_tuple)


def string_of_blason_extra_small_size(conf: config.Config, base: Base, p_auth_tuple) -> str:
    return gen_string_of_fimg_sz(50, 37, conf, base, p_auth_tuple)


def get_sosa(conf: config.Config, base: Base, env: Dict, r, p: driver.Person):
    return None


def get_linked_page(conf: config.Config, base: Base, p: driver.Person, s: str) -> str:
    return ""


def make_ep(conf: config.Config, base: Base, ip):
    return None


def make_efam(conf: config.Config, base: Base, ip, ifam):
    return None


def mode_local(env: Dict) -> bool:
    return env.get("local", False)


def get_note_or_source(conf: config.Config, base: Base, note_or_src: str, p_auth_tuple):
    return ""


def date_aux(conf: config.Config, p_auth: bool, date):
    return ""


def get_marriage_witnesses(fam: driver.Family):
    return []


def get_nb_marriage_witnesses_of_kind(fam: driver.Family, wk):
    return 0


def number_of_descendants_aux(conf: config.Config, base: Base, env: Dict, all_levels: bool, sl: List, eval_int):
    return 0


def eval_var(conf: config.Config, base: Base, env: Dict, ep, loc, sl: List):
    return null_val()


def eval_transl(conf: config.Config, base: Base, env: Dict, upp: bool, s: str, c: str):
    return ""


def level_in_list(in_or_less: bool, level: int, lev_list: List) -> bool:
    return False


def print_foreach(conf: config.Config, base: Base, print_ast, eval_expr):
    pass


def eval_predefined_apply(conf: config.Config, env: Dict, f: str, vl: List):
    return None


def gen_interp_templ(menu, title: str, templ_fname: str, conf: config.Config, base: Base, p: driver.Person, no_headers: bool = False):
    person_obj = driver.gen_person_of_person(p)
    first_name = driver.sou(base, driver.get_first_name(p)).decode('utf-8')
    surname = driver.sou(base, driver.get_surname(p)).decode('utf-8')
    person_name = f"{first_name} {surname}"

    if not no_headers:
        conf.output_conf.status(200)
        conf.output_conf.header("Content-type: text/html; charset=utf-8")
        conf.output_conf.header("")

    conf.output_conf.body(f"<html><head><title>{person_name}</title>")
    conf.output_conf.body("<style>")
    conf.output_conf.body("body { font-family: Georgia, serif; margin: 0; padding: 20px; background: #f5f5f5; }")
    conf.output_conf.body(".container { max-width: 900px; margin: 0 auto; background: white; padding: 30px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }")
    conf.output_conf.body("h1 { color: #2f6400; border-bottom: 2px solid #2f6400; padding-bottom: 10px; }")
    conf.output_conf.body("h2 { color: #3d8000; margin-top: 30px; }")
    conf.output_conf.body(".info-section { margin: 20px 0; }")
    conf.output_conf.body(".info-label { font-weight: bold; color: #555; display: inline-block; width: 120px; }")
    conf.output_conf.body(".info-value { color: #333; }")
    conf.output_conf.body(".back-link { display: inline-block; margin-top: 20px; color: #2f6400; text-decoration: none; }")
    conf.output_conf.body(".back-link:hover { text-decoration: underline; }")
    conf.output_conf.body("</style>")
    conf.output_conf.body("</head><body>")
    conf.output_conf.body("<div class='container'>")

    conf.output_conf.body(f"<h1>{person_name}</h1>")

    p_auth = util.authorized_age(conf, base, person_obj)

    conf.output_conf.body("<div class='info-section'>")

    sex = driver.get_sex(p)
    # Sex can be int (0=Male, 1=Female, 2=Neuter) or enum
    sex_str = "Unknown"
    if isinstance(sex, int):
        sex_str = "Male" if sex == 0 else "Female" if sex == 1 else "Unknown"
    elif hasattr(sex, 'name'):
        # It's an enum
        sex_str = "Male" if sex.name == 'MALE' else "Female" if sex.name == 'FEMALE' else "Unknown"
    conf.output_conf.body(f"<div><span class='info-label'>Sex:</span> <span class='info-value'>{sex_str}</span></div>")

    occ = driver.get_occ(p)
    if occ > 0:
        conf.output_conf.body(f"<div><span class='info-label'>Occurrence:</span> <span class='info-value'>{occ}</span></div>")

    birth = driver.get_birth(p)
    if birth and p_auth:
        birth_place = driver.get_birth_place(p)
        if birth_place:
            place_str = driver.sou(base, birth_place).decode('utf-8')
            if place_str:
                conf.output_conf.body(f"<div><span class='info-label'>Born:</span> <span class='info-value'>{place_str}</span></div>")

    baptism = driver.get_baptism(p)
    if baptism and p_auth:
        pass

    death = driver.get_death(p)
    if death and not isinstance(death, gwdef.NotDead) and p_auth:
        death_place = driver.get_death_place(p)
        if death_place:
            place_str = driver.sou(base, death_place).decode('utf-8')
            if place_str:
                conf.output_conf.body(f"<div><span class='info-label'>Died:</span> <span class='info-value'>{place_str}</span></div>")

    burial = driver.get_burial(p)
    if burial and p_auth:
        pass

    occupation = driver.get_occupation(p)
    if occupation:
        occ_str = driver.sou(base, occupation).decode('utf-8')
        if occ_str:
            conf.output_conf.body(f"<div><span class='info-label'>Occupation:</span> <span class='info-value'>{occ_str}</span></div>")

    conf.output_conf.body("</div>")

    def decode_variant_iper(val):
        """Decode OCaml variant-encoded person index to integer"""
        if isinstance(val, int):
            return val
        if isinstance(val, dict) and 'tag' in val:
            if val['tag'] == 0:
                return None
            elif val['tag'] == 1 and 'fields' in val:
                return val['fields'][0] if val['fields'] else None
        return val

    parents_fam = driver.get_parents(p)
    if parents_fam is not None and isinstance(parents_fam, int):
        fam = driver.foi(base, parents_fam)
        father_ip = decode_variant_iper(driver.get_father(fam))
        mother_ip = decode_variant_iper(driver.get_mother(fam))

        has_parents = False
        if not driver.Iper.is_dummy(father_ip) or not driver.Iper.is_dummy(mother_ip):
            has_parents = True

        if has_parents:
            conf.output_conf.body("<h2>Parents</h2>")
            conf.output_conf.body("<div class='info-section'>")

            if not driver.Iper.is_dummy(father_ip):
                father = driver.poi(base, father_ip)
                father_first = driver.sou(base, driver.get_first_name(father)).decode('utf-8')
                father_last = driver.sou(base, driver.get_surname(father)).decode('utf-8')
                conf.output_conf.body(f"<div><span class='info-label'>Father:</span> <span class='info-value'><a href='?b={conf.bname}&i={father_ip}'>{father_first} {father_last}</a></span></div>")

            if not driver.Iper.is_dummy(mother_ip):
                mother = driver.poi(base, mother_ip)
                mother_first = driver.sou(base, driver.get_first_name(mother)).decode('utf-8')
                mother_last = driver.sou(base, driver.get_surname(mother)).decode('utf-8')
                conf.output_conf.body(f"<div><span class='info-label'>Mother:</span> <span class='info-value'><a href='?b={conf.bname}&i={mother_ip}'>{mother_first} {mother_last}</a></span></div>")

            conf.output_conf.body("</div>")

        siblings = []
        if parents_fam is not None:
            siblings_list = driver.get_children(fam)
            person_iper = driver.get_iper(p)
            if siblings_list:
                for sib_ip in siblings_list:
                    sib_ip_decoded = decode_variant_iper(sib_ip)
                    if sib_ip_decoded is not None and sib_ip_decoded != person_iper:
                        siblings.append(sib_ip_decoded)

        if siblings:
            conf.output_conf.body("<h2>Siblings</h2>")
            conf.output_conf.body("<div class='info-section'>")
            conf.output_conf.body("<ul>")
            for sib_ip in siblings:
                sibling = driver.poi(base, sib_ip)
                sib_first = driver.sou(base, driver.get_first_name(sibling)).decode('utf-8')
                sib_last = driver.sou(base, driver.get_surname(sibling)).decode('utf-8')
                sib_ip_int = int(sib_ip)
                conf.output_conf.body(f"<li><a href='?b={conf.bname}&i={sib_ip_int}'>{sib_first} {sib_last}</a></li>")
            conf.output_conf.body("</ul>")
            conf.output_conf.body("</div>")

    unions = driver.get_family(p)
    if unions and len(unions) > 0:
        person_iper = driver.get_iper(p)
        for ifam in unions:
            if not isinstance(ifam, int):
                continue
            fam = driver.foi(base, ifam)
            father_ip = decode_variant_iper(driver.get_father(fam))
            mother_ip = decode_variant_iper(driver.get_mother(fam))

            spouse_ip = mother_ip if father_ip == person_iper else father_ip

            if not driver.Iper.is_dummy(spouse_ip):
                spouse = driver.poi(base, spouse_ip)
                spouse_first = driver.sou(base, driver.get_first_name(spouse)).decode('utf-8')
                spouse_last = driver.sou(base, driver.get_surname(spouse)).decode('utf-8')
                spouse_ip_int = int(spouse_ip)

                conf.output_conf.body("<h2>Married to</h2>")
                conf.output_conf.body("<div class='info-section'>")
                conf.output_conf.body(f"<div><a href='?b={conf.bname}&i={spouse_ip_int}'>{spouse_first} {spouse_last}</a></div>")
                conf.output_conf.body("</div>")

            children = driver.get_children(fam)
            if children and len(children) > 0:
                conf.output_conf.body("<h2>Children</h2>")
                conf.output_conf.body("<div class='info-section'>")
                conf.output_conf.body("<ul>")
                for child_ip in children:
                    child_ip_decoded = decode_variant_iper(child_ip)
                    if child_ip_decoded is None:
                        continue
                    child = driver.poi(base, child_ip_decoded)
                    child_first = driver.sou(base, driver.get_first_name(child)).decode('utf-8')
                    child_last = driver.sou(base, driver.get_surname(child)).decode('utf-8')
                    child_ip_int = int(child_ip_decoded)
                    conf.output_conf.body(f"<li><a href='?b={conf.bname}&i={child_ip_int}'>{child_first} {child_last}</a></li>")
                conf.output_conf.body("</ul>")
                conf.output_conf.body("</div>")

    conf.output_conf.body(f"<a href='?b={conf.bname}' class='back-link'>&larr; Back to database</a>")
    conf.output_conf.body("</div></body></html>")


def interp_templ(title: str, conf: config.Config, base: Base, p: driver.Person, no_headers: bool = False):
    gen_interp_templ(False, title, "perso.txt", conf, base, p, no_headers)


def interp_templ_with_menu(menu_fn, title: str, conf: config.Config, base: Base, p: driver.Person):
    gen_interp_templ(menu_fn, title, "perso.txt", conf, base, p, False)


def interp_notempl_with_menu(title_fn, templ_fname: str, conf: config.Config, base: Base, p: driver.Person):
    title_fn(True)
    gen_interp_templ(True, "", templ_fname, conf, base, p, False)


def print_person(conf: config.Config, base: Base, p: driver.Person, no_headers: bool = False):
    passwd = None
    if not conf.wizard and not conf.friend:
        parents = driver.get_parents(p)
        if parents:
            ifam = parents
            fam = driver.foi(base, ifam)
            src = driver.sou(base, driver.get_origin_file(fam))
        else:
            src = ""
        try:
            passwd_key = f"passwd_{src}"
            if passwd_key in conf.base_env:
                passwd = (src, conf.base_env[passwd_key])
        except:
            pass
    if passwd:
        src, pwd = passwd
        if not util.is_that_user_and_password(conf.auth_scheme, "", pwd):
            util.unauthorized(conf, src)
            return
    interp_templ("perso", conf, base, p, no_headers)


def string_of_died(conf: config.Config, p: driver.Person, p_auth: bool) -> str:
    return get_death_text(conf, p, p_auth)


def string_of_parent_age(conf: config.Config, base: Base, p_auth_tuple, get_parent_fn) -> str:
    return ""


def string_of_image_url(conf: config.Config, base: Base, p_auth_tuple, html_img: bool, image_type: bool) -> str:
    return ""
