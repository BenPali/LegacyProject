import sys
from pathlib import Path
from typing import Optional, List, Callable, TypeVar, Any

sys.path.insert(0, str(Path(__file__).parent.parent))

from lib import config, driver, util, name, logs, sosa


T = TypeVar('T')


def person_is_std_key(conf: config.Config, base: Any,
                      p: driver.GenPerson, k: str) -> bool:
    k = name.strip_lower(k)

    first_surname = name.strip_lower(
        driver.p_first_name(base, p) + " " + driver.p_surname(base, p)
    )
    if k == first_surname:
        return True

    misc_names = driver.person_misc_names(base, p, util.nobtit(conf, base, p))
    for n in misc_names:
        if name.strip(n) == k:
            return True

    return False


def select_std_eq(conf: config.Config, base: Any,
                  pl: List[driver.GenPerson], k: str) -> List[driver.GenPerson]:
    result = []
    for p in pl:
        if person_is_std_key(conf, base, p, k):
            result.append(p)
    return result


def find_all(conf: config.Config, base: Any,
             an: str) -> tuple[List[driver.GenPerson], bool]:
    sosa_ref = util.find_sosa_ref(conf, base)
    try:
        sosa_nb = sosa.of_int(int(an))
    except:
        sosa_nb = None

    if sosa_ref and sosa_nb:
        if sosa_nb != sosa.zero():
            branch = util.branch_of_sosa(conf, base, sosa_nb, sosa_ref)
            if branch and len(branch) > 0:
                return ([branch[0]], True)
            return ([], False)
        return ([], False)

    acc = []
    if acc:
        return (acc, False)

    spl = select_std_eq(conf, base, acc, an)
    if spl:
        return (spl, False)
    elif acc:
        return (acc, False)
    else:
        return ([], False)


def relation_print(conf: config.Config, base: Any, p: driver.GenPerson):
    raise NotImplementedError("RelationDisplay module not yet implemented")


def specify(conf: config.Config, base: Any, n: str,
            pl1: List[driver.GenPerson], pl2: List[driver.GenPerson],
            pl3: List[driver.GenPerson]):
    conf.output_conf.body(f"<html><body><h1>{n} : specify</h1></body></html>")


def make_senv(conf: config.Config, base: Any) -> config.Config:
    env_dict = {}
    for key, val in conf.env.items():
        if key.startswith('s'):
            env_dict[key] = val

    new_conf = config.Config(
        output_conf=conf.output_conf,
        from_=conf.from_,
        env=conf.env,
        senv=env_dict,
        henv=conf.henv,
        base_env=conf.base_env,
        bname=conf.bname,
        command=conf.command
    )
    return new_conf


def make_henv(conf: config.Config, base: Any) -> config.Config:
    env_dict = {}
    for key, val in conf.env.items():
        if key.startswith('h'):
            env_dict[key] = val

    new_conf = config.Config(
        output_conf=conf.output_conf,
        from_=conf.from_,
        env=conf.env,
        senv=conf.senv,
        henv=env_dict,
        base_env=conf.base_env,
        bname=conf.bname,
        command=conf.command
    )
    return new_conf


def w_base(none: Callable[[config.Config], T],
           callback: Callable[[config.Config, Any], T],
           conf: config.Config, base_name: Optional[str]) -> T:
    if not base_name:
        return none(conf)

    try:
        base = driver.open_base(base_name)
        return callback(conf, base)
    except Exception as e:
        logs.syslog(logs.LOG_ERR, f"Failed to open base {base_name}: {e}")
        return none(conf)


def w_lock(onerror: Callable[[config.Config, Optional[str]], T],
           callback: Callable[[config.Config, Optional[str]], T],
           conf: config.Config, base_name: Optional[str]) -> T:
    raise NotImplementedError("Lock mechanism not yet implemented")


def w_wizard(callback: Callable[[config.Config, Any], None],
             conf: config.Config, base: Any):
    if not conf.wizard:
        util.unauthorized(conf, "Wizard access required")
        return

    callback(conf, base)


def w_person(none: Callable[[config.Config, Any], T],
             callback: Callable[[config.Config, Any, driver.GenPerson], T],
             conf: config.Config, base: Any) -> T:
    p = util.find_person_in_env(conf, base, "")
    if p is None:
        return none(conf, base)

    return callback(conf, base, p)


def incorrect_request(conf: config.Config, comment: Optional[str] = None):
    conf.output_conf.status(400)
    conf.output_conf.header("Content-type: text/html; charset=utf-8")

    msg = "Incorrect request"
    if comment:
        msg += f": {comment}"

    conf.output_conf.body(f"<html><head><title>{msg}</title></head>")
    conf.output_conf.body(f"<body><h1>{msg}</h1></body></html>")


def only_special_env(env: List[tuple[str, Any]]) -> bool:
    for key, _ in env:
        if not (key.startswith('_') or key == 'lang'):
            return False
    return True


def treat_request(conf: config.Config):
    if 'robots.txt' in conf.command or 'robots' in conf.request:
        from . import gwd
        gwd.robots_txt(conf)
        return

    m = util.p_getenv(conf.env, 'm')

    if not m:
        default_person_page(conf)
        return

    if m == 'A':
        handle_ascend_page(conf)
    elif m == 'D':
        handle_descend_page(conf)
    elif m == 'F':
        handle_family_page(conf)
    elif m == 'P':
        handle_person_page(conf)
    elif m == 'R':
        handle_relation_page(conf)
    elif m == 'S':
        handle_search_page(conf)
    elif m == 'NG':
        handle_notes_page(conf)
    elif m == 'SRC':
        handle_sources_page(conf)
    elif m == 'CAL':
        handle_calendar_page(conf)
    elif m == 'H':
        handle_history_page(conf)
    elif m == 'LB':
        handle_list_page(conf)
    elif m == 'TT':
        handle_titles_page(conf)
    elif m == 'MISC':
        handle_misc_page(conf)
    else:
        incorrect_request(conf, f"Unknown module: {m}")


def default_person_page(conf: config.Config):
    i = util.p_getenv(conf.env, 'i')
    if i:
        handle_person_page(conf)
    else:
        conf.output_conf.body("<html><body><h1>GeneWeb</h1>")
        conf.output_conf.body("<p>Welcome to GeneWeb</p></body></html>")


def handle_person_page(conf: config.Config):
    def none_callback(c: config.Config, b: Any):
        incorrect_request(c, "Person not found")

    def person_callback(c: config.Config, b: Any, p: driver.GenPerson):
        c.output_conf.body(f"<html><head><title>{p.first_name} {p.surname}</title></head>")
        c.output_conf.body(f"<body><h1>{p.first_name} {p.surname}</h1>")
        c.output_conf.body(f"<p><em>[Full person page coming when perso.py is ready]</em></p>")
        c.output_conf.body("</body></html>")

    def base_callback(c: config.Config, b: Any):
        return w_person(none_callback, person_callback, c, b)

    w_base(lambda c: incorrect_request(c, "No base specified"),
           base_callback, conf, conf.bname)


def handle_family_page(conf: config.Config):
    conf.output_conf.body("<html><body><h1>Family Page</h1>")
    conf.output_conf.body("<p><em>[Coming when famille.py is ready]</em></p>")
    conf.output_conf.body("</body></html>")


def handle_ascend_page(conf: config.Config):
    conf.output_conf.body("<html><body><h1>Ascendants</h1>")
    conf.output_conf.body("<p><em>[Coming when ascendDisplay.py is ready]</em></p>")
    conf.output_conf.body("</body></html>")


def handle_descend_page(conf: config.Config):
    conf.output_conf.body("<html><body><h1>Descendants</h1>")
    conf.output_conf.body("<p><em>[Coming when descendDisplay.py is ready]</em></p>")
    conf.output_conf.body("</body></html>")


def handle_relation_page(conf: config.Config):
    conf.output_conf.body("<html><body><h1>Relationship</h1>")
    conf.output_conf.body("<p><em>[Coming when relation.py is ready]</em></p>")
    conf.output_conf.body("</body></html>")


def handle_search_page(conf: config.Config):
    conf.output_conf.body("<html><body><h1>Search</h1>")
    conf.output_conf.body("<p><em>[Coming when searchName.py is ready]</em></p>")
    conf.output_conf.body("</body></html>")


def handle_notes_page(conf: config.Config):
    conf.output_conf.body("<html><body><h1>Notes and Links</h1>")
    conf.output_conf.body("<p><em>[Coming when notesLinks display is ready]</em></p>")
    conf.output_conf.body("</body></html>")


def handle_sources_page(conf: config.Config):
    conf.output_conf.body("<html><body><h1>Sources</h1>")
    conf.output_conf.body("<p><em>[Coming when sources display is ready]</em></p>")
    conf.output_conf.body("</body></html>")


def handle_calendar_page(conf: config.Config):
    conf.output_conf.body("<html><body><h1>Calendar</h1>")
    conf.output_conf.body("<p><em>[Coming when calendar display is ready]</em></p>")
    conf.output_conf.body("</body></html>")


def handle_history_page(conf: config.Config):
    conf.output_conf.body("<html><body><h1>History</h1>")
    conf.output_conf.body("<p><em>[Coming when history display is ready]</em></p>")
    conf.output_conf.body("</body></html>")


def handle_list_page(conf: config.Config):
    conf.output_conf.body("<html><body><h1>Lists</h1>")
    conf.output_conf.body("<p><em>[Coming when list display is ready]</em></p>")
    conf.output_conf.body("</body></html>")


def handle_titles_page(conf: config.Config):
    conf.output_conf.body("<html><body><h1>Titles</h1>")
    conf.output_conf.body("<p><em>[Coming when title display is ready]</em></p>")
    conf.output_conf.body("</body></html>")


def handle_misc_page(conf: config.Config):
    conf.output_conf.body("<html><body><h1>Miscellaneous</h1>")
    conf.output_conf.body("<p><em>[Coming soon]</em></p>")
    conf.output_conf.body("</body></html>")
