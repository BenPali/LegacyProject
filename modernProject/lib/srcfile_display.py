import sys
import os
from pathlib import Path
from typing import Optional, Tuple, List, Any
from dataclasses import dataclass

sys.path.insert(0, str(Path(__file__).parent.parent))

from lib import config, driver, secure, templ, util, translate


@dataclass
class Counter:
    welcome_cnt: int
    request_cnt: int
    start_date: str
    wizard_cnt: int
    friend_cnt: int
    normal_cnt: int


def get_date(conf: config.Config) -> str:
    from datetime import datetime
    now = datetime.now()
    return f"{now.day:02d}/{now.month:02d}/{now.year}"


def list_databases(base_dir: str = ".") -> List[str]:
    try:
        base_path = Path(base_dir)
        gwb_files = list(base_path.glob("*.gwb"))
        return sorted([f.stem for f in gwb_files])
    except Exception:
        return []


def propose_base(conf: config.Config):
    conf.output_conf.status(200)
    conf.output_conf.header("Content-type: text/html; charset=utf-8")

    conf.output_conf.body("<html><head><title>GeneWeb - Select Database</title>")
    conf.output_conf.body("<style>")
    conf.output_conf.body("body { font-family: sans-serif; margin: 40px; }")
    conf.output_conf.body("h1 { color: #2f6400; }")
    conf.output_conf.body(".form-container { margin: 30px 0; }")
    conf.output_conf.body("input[type='text'] { padding: 8px; font-size: 16px; width: 300px; }")
    conf.output_conf.body("button { padding: 10px 20px; font-size: 16px; background: #2f6400; color: white; border: none; cursor: pointer; }")
    conf.output_conf.body("button:hover { background: #3d8000; }")
    conf.output_conf.body(".db-list { margin: 20px 0; }")
    conf.output_conf.body(".db-item { margin: 10px 0; }")
    conf.output_conf.body(".db-link { color: #2f6400; text-decoration: none; font-size: 18px; }")
    conf.output_conf.body(".db-link:hover { text-decoration: underline; }")
    conf.output_conf.body("</style>")
    conf.output_conf.body("</head><body>")

    conf.output_conf.body("<h1>GeneWeb Database Selection</h1>")

    databases = list_databases(secure.base_dir())

    if databases:
        conf.output_conf.body("<h2>Available Databases:</h2>")
        conf.output_conf.body("<div class='db-list'>")
        for db_name in databases:
            conf.output_conf.body("<div class='db-item'>")
            conf.output_conf.body(f"<a class='db-link' href='?b={db_name}'>&#8226; {db_name}</a>")
            conf.output_conf.body("</div>")
        conf.output_conf.body("</div>")

    conf.output_conf.body("<h2>Or Enter Database Name:</h2>")
    conf.output_conf.body("<div class='form-container'>")
    conf.output_conf.body("<form method='GET'>")
    conf.output_conf.body("<input type='text' name='b' size='40' placeholder='Database name'>")
    conf.output_conf.body(" ")
    conf.output_conf.body("<button type='submit'>Open Database</button>")
    conf.output_conf.body("</form>")
    conf.output_conf.body("</div>")

    conf.output_conf.body("</body></html>")


def print_welcome(conf: config.Config, base: Any):
    try:
        env = templ.Env.empty()
        templ.output_simple(conf, env, "welcome")
    except:
        conf.output_conf.status(200)
        conf.output_conf.header("Content-type: text/html; charset=utf-8")

        conf.output_conf.body("<html><head><title>GeneWeb</title>")
        conf.output_conf.body("<style>")
        conf.output_conf.body("body { font-family: sans-serif; margin: 40px; }")
        conf.output_conf.body("h1 { color: #2f6400; }")
        conf.output_conf.body("p { font-size: 18px; line-height: 1.6; }")
        conf.output_conf.body("</style>")
        conf.output_conf.body("</head><body>")
        conf.output_conf.body("<h1>Welcome to GeneWeb</h1>")
        conf.output_conf.body(f"<p>Database: <strong>{conf.bname}</strong></p>")
        conf.output_conf.body("<p>Explore your genealogical data.</p>")
        conf.output_conf.body("</body></html>")


def input_int(ic) -> int:
    raise NotImplementedError("input_int not yet implemented")


def count(conf: config.Config) -> Counter:
    return Counter(
        welcome_cnt=0,
        request_cnt=0,
        start_date=get_date(conf),
        wizard_cnt=0,
        friend_cnt=0,
        normal_cnt=0
    )


def write_counter(conf: config.Config, counter: Counter):
    raise NotImplementedError("write_counter not yet implemented")


def set_wizard_and_friend_traces(conf: config.Config):
    raise NotImplementedError("set_wizard_and_friend_traces not yet implemented")


def incr_counter(f, conf: config.Config) -> Optional[Tuple[int, int, str]]:
    raise NotImplementedError("incr_counter not yet implemented")


def incr_welcome_counter(conf: config.Config) -> Optional[Tuple[int, int, str]]:
    raise NotImplementedError("incr_welcome_counter not yet implemented")


def incr_request_counter(conf: config.Config) -> Optional[Tuple[int, int, str]]:
    raise NotImplementedError("incr_request_counter not yet implemented")


def lang_file_name(conf: config.Config, fname: str) -> str:
    raise NotImplementedError("lang_file_name not yet implemented")


def any_lang_file_name(conf: config.Config, fname: str) -> str:
    raise NotImplementedError("any_lang_file_name not yet implemented")


def source_file_name(conf: config.Config, fname: str) -> str:
    raise NotImplementedError("source_file_name not yet implemented")


def extract_date(s: str):
    raise NotImplementedError("extract_date not yet implemented")


def string_of_start_date(conf: config.Config) -> str:
    raise NotImplementedError("string_of_start_date not yet implemented")


def string_of_int_sep_aux(conf: config.Config, n: int) -> str:
    raise NotImplementedError("string_of_int_sep_aux not yet implemented")


def macro(conf: config.Config, base: Any, key: str):
    raise NotImplementedError("macro not yet implemented")


def lexicon_translate(conf: config.Config, base: Any, nomin: bool, stream, first_c: str):
    raise NotImplementedError("lexicon_translate not yet implemented")


def browser_cannot_handle_passwords(conf: config.Config) -> bool:
    raise NotImplementedError("browser_cannot_handle_passwords not yet implemented")


def get_variable(stream):
    raise NotImplementedError("get_variable not yet implemented")


def stream_line(stream):
    raise NotImplementedError("stream_line not yet implemented")


def gen_print(mode: str, conf: config.Config, base: Any, fname: str):
    raise NotImplementedError("gen_print not yet implemented")


def print_source(conf: config.Config, base: Any, fname: str):
    raise NotImplementedError("print_source not yet implemented")


def get_env(v: str, env):
    raise NotImplementedError("get_env not yet implemented")


def get_vother(v):
    raise NotImplementedError("get_vother not yet implemented")


def set_vother(x):
    raise NotImplementedError("set_vother not yet implemented")


def eval_var(conf: config.Config, base: Any, env, unit, loc, var):
    raise NotImplementedError("eval_var not yet implemented")


def print_foreach(conf: config.Config, print_ast, eval_expr):
    raise NotImplementedError("print_foreach not yet implemented")


def eval_predefined_apply(conf: config.Config, env, f: str, vl: List):
    raise NotImplementedError("eval_predefined_apply not yet implemented")


def print_file(conf: config.Config, base: Any, fname: str):
    raise NotImplementedError("print_file not yet implemented")


def copy_from_stream(conf: config.Config, base: Any, stream, mode: str):
    raise NotImplementedError("copy_from_stream not yet implemented")
