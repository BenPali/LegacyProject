import sys
import os
import socket
import time
from typing import Optional, Dict, List, Tuple, Any
from pathlib import Path
import hashlib
import base64

sys.path.insert(0, str(Path(__file__).parent.parent))

from lib import config, driver, wserver, logs, mutil, util, database, secure


output_conf = config.OutputConf(
    status=wserver.http,
    header=wserver.header,
    body=wserver.print_string,
    flush=wserver.wflush
)

printer_conf = config.Config(output_conf=output_conf)

auth_file = ""
cache_langs: List[str] = []
cache_databases: List[str] = []
choose_browser_lang = False
conn_timeout = 120
daemon = False
default_lang = "fr"
friend_passwd = ""
green_color = "#2f6400"
images_dir = ""
gw_prefix = ""
images_prefix = ""
etc_prefix = ""
lexicon_list: List[str] = [os.path.join("lang", "lexicon.txt")]
login_timeout = 1800
default_n_workers = 20
n_workers = default_n_workers
default_max_pending_requests = 150
max_pending_requests = default_max_pending_requests
no_host_address = False
only_addresses: List[str] = []
plugins: List[str] = []
forced_plugins: List[str] = []
unsafe_plugins: List[str] = []
redirected_addr: Optional[str] = None
robot_xcl: Optional[Any] = None
selected_addr: Optional[str] = None
selected_port = 2317
setup_link = False
trace_failed_passwd = False
debug = False
use_auth_digest_scheme = False
wizard_just_friend = False
wizard_passwd = ""
predictable_mode = False
cgi_secret_salt: Optional[str] = None


def is_multipart_form(content_type: str) -> bool:
    s = "multipart/form-data"
    i = 0
    while i < len(content_type) and i < len(s):
        if content_type[i].lower() != s[i]:
            return False
        i += 1
    return i >= len(s)


def extract_boundary(content_type: str) -> str:
    env_list = util.create_env(content_type)
    for key, val in env_list:
        if key == "boundary":
            return val
    return ""


def split_username(username: str) -> Tuple[str, str]:
    l1 = username.split('|')
    if len(l1) == 1:
        return (username, "")
    elif len(l1) == 2:
        return (l1[0], l1[1])
    else:
        logs.syslog(logs.LOG_CRIT, "Bad .auth key or sosa encoding")
        return (l1[0], "")


def log_passwd_failed(ar: Dict[str, Any], tm: float, from_addr: str,
                      request: str, base_file: str):
    referer = mutil.extract_param("referer: ", '\n', request)
    user_agent = mutil.extract_param("user-agent: ", '\n', request)
    tm_struct = time.localtime(tm)
    logs.info(f"{time.strftime('%Y-%m-%d %H:%M:%S', tm_struct)} ({os.getpid()}) "
             f"{base_file}_{ar['ar_passwd']} => failed ({ar['ar_user']})")
    if trace_failed_passwd:
        logs.info(f" ({repr(ar['ar_uauth'])})")
    logs.info(f"\n  From: {from_addr}\n  Agent: {user_agent}")
    if referer:
        logs.info(f"  Referer: {referer}")


def copy_file(conf: config.Config, fname: str) -> bool:
    result = util.open_etc_file(conf, fname)
    if result:
        ic, _fname = result
        try:
            while True:
                c = ic.read(1)
                if not c:
                    break
                conf.output_conf.body(c)
        except:
            pass
        ic.close()
        return True
    return False


def http(conf: config.Config, status: int):
    conf.output_conf.status(status)
    conf.output_conf.header("Content-type: text/html; charset=iso-8859-1")


def robots_txt(conf: config.Config):
    logs.syslog(logs.LOG_NOTICE, "Robot request")
    conf.output_conf.status(200)
    conf.output_conf.header("Content-type: text/plain")
    if not copy_file(conf, "robots"):
        conf.output_conf.body("User-Agent: *\n")
        conf.output_conf.body("Disallow: /\n")


def refuse_log(conf: config.Config, from_addr: str):
    logs.syslog(logs.LOG_NOTICE, f"Excluded: {from_addr}")
    http(conf, 403)
    conf.output_conf.header("Content-type: text/html")
    conf.output_conf.body("Your access has been disconnected by administrator.\n")
    copy_file(conf, "refuse")


def only_log(conf: config.Config, from_addr: str):
    logs.syslog(logs.LOG_NOTICE, f"Connection refused from {from_addr}")
    http(conf, 200)
    conf.output_conf.header("Content-type: text/html; charset=iso-8859-1")
    conf.output_conf.body("<head><title>Invalid access</title></head>\n")
    conf.output_conf.body("<body><h1>Invalid access</h1></body>\n")


def refuse_auth(conf: config.Config, from_addr: str, auth: str, auth_type: str):
    logs.syslog(logs.LOG_NOTICE,
                f"Access failed --- From: {from_addr} --- Basic realm: {auth_type} --- Response: {auth}")
    util.unauthorized(conf, auth_type)


def index_from(s: str, o: int, c: str) -> int:
    try:
        return s.index(c, o)
    except ValueError:
        return len(s)


def index(s: str, c: str) -> int:
    return index_from(s, 0, c)


def extract_assoc(key: str, kvl: List[Tuple[str, str]]) -> Tuple[str, List[Tuple[str, str]]]:
    from urllib.parse import unquote
    result_val = ""
    result_list = []
    for k, v in kvl:
        if k == key:
            result_val = unquote(v)
        else:
            result_list.append((k, v))
    return (result_val, result_list)


lexicon_cache: Dict[str, Dict[str, str]] = {}


def load_lexicon(lang: str) -> Dict[str, str]:
    global lexicon_cache

    fname = f"lexicon.bin.{lang}"
    if fname in lexicon_cache:
        return lexicon_cache[fname]

    ht: Dict[str, str] = {}

    for lex_file in reversed(lexicon_list):
        fname_full = util.search_in_assets(lex_file)
        if os.path.exists(fname_full):
            try:
                with secure.open_in(fname_full) as f:
                    mutil.input_lexicon(lang, ht, f)
            except Exception as e:
                logs.syslog(logs.LOG_WARNING, f"File {fname_full} unavailable: {e}")
        else:
            logs.syslog(logs.LOG_WARNING, f"File {fname_full} unavailable")

    lexicon_cache[fname] = ht
    return ht


def cache_lexicon_all():
    for lang in cache_langs:
        load_lexicon(lang)


def alias_lang(lang: str) -> str:
    if len(lang) < 2:
        return lang
    lang_prefix = lang[:2].lower()

    aliases = {
        'br': 'bg',
        'ca': 'es',
        'co': 'fr',
        'eu': 'fr',
        'hr': 'bg',
        'ia': 'la',
        'mk': 'bg',
        'oc': 'ca',
        'sc': 'ca',
        'sk': 'cz',
        'sr': 'bg',
        'ur': 'ar'
    }

    return aliases.get(lang_prefix, lang)


def has_root_privileges() -> bool:
    if not hasattr(os, 'getuid'):
        return False
    return os.getuid() == 0 or os.getgid() == 0


def print_renamed(conf: config.Config, new_n: str):
    raise NotImplementedError("print_renamed not yet implemented")


def log_redirect(from_addr: str, request: str, req: str):
    logs.syslog(logs.LOG_INFO, f"Redirect: {from_addr} {request} -> {req}")


def print_redirected(conf: config.Config, req: str):
    raise NotImplementedError("print_redirected not yet implemented")


def nonce_private_key() -> str:
    return hashlib.sha256(str(time.time()).encode()).hexdigest()


def digest_nonce() -> str:
    return base64.b64encode(os.urandom(16)).decode('utf-8')


def trace_auth(conf: config.Config, auth_type: str, user: str):
    logs.syslog(logs.LOG_INFO, f"Auth: {auth_type} user={user}")


def unauth_server(conf: config.Config, auth_type: str):
    util.unauthorized(conf, auth_type)


def gen_match_auth_file(auth_file: str, request: str) -> Optional[Dict[str, Any]]:
    raise NotImplementedError("gen_match_auth_file not yet implemented")


def basic_match_auth_file(auth_file: str, request: str) -> Optional[Dict[str, Any]]:
    raise NotImplementedError("basic_match_auth_file not yet implemented")


def digest_match_auth_file(auth_file: str, request: str) -> Optional[Dict[str, Any]]:
    raise NotImplementedError("digest_match_auth_file not yet implemented")


def match_simple_passwd(passwd: str, request: str) -> bool:
    raise NotImplementedError("match_simple_passwd not yet implemented")


def basic_match_auth(auth_file: str, request: str) -> Optional[Dict[str, Any]]:
    if auth_file:
        return basic_match_auth_file(auth_file, request)
    return None


def compatible_tokens(token1: str, token2: str) -> bool:
    return token1 == token2


def get_actlog() -> List[Tuple[str, str, float]]:
    raise NotImplementedError("get_actlog not yet implemented")


def set_actlog(actlog: List[Tuple[str, str, float]]):
    raise NotImplementedError("set_actlog not yet implemented")


def get_token(user: str, passwd: str) -> Optional[str]:
    raise NotImplementedError("get_token not yet implemented")


def mkpasswd(passwd: str) -> str:
    return hashlib.md5(passwd.encode()).hexdigest()


def set_token(user: str, passwd: str, token: str):
    raise NotImplementedError("set_token not yet implemented")


def index_not_name(s: str) -> int:
    for i, c in enumerate(s):
        if not c.isalnum() and c not in ['_', '-']:
            return i
    return len(s)


def refresh_url(conf: config.Config) -> str:
    raise NotImplementedError("refresh_url not yet implemented")


def http_preferred_language(accept_lang: str) -> Optional[str]:
    if not accept_lang:
        return None
    langs = accept_lang.split(',')
    if langs:
        lang = langs[0].split(';')[0].strip()
        return lang[:2] if len(lang) >= 2 else None
    return None


def allowed_denied_titles(conf: config.Config) -> Tuple[List[str], List[str]]:
    return ([], [])


def allowed_titles(conf: config.Config) -> List[str]:
    return []


def denied_titles(conf: config.Config) -> List[str]:
    return []


def parse_digest(auth_header: str) -> Dict[str, str]:
    result = {}
    if 'Digest ' in auth_header:
        params = auth_header.split('Digest ')[1]
        for param in params.split(','):
            if '=' in param:
                key, val = param.split('=', 1)
                result[key.strip()] = val.strip().strip('"')
    return result


def basic_authorization(auth_header: str) -> Tuple[Optional[str], Optional[str]]:
    if 'Basic ' not in auth_header:
        return (None, None)
    try:
        encoded = auth_header.split('Basic ')[1]
        decoded = base64.b64decode(encoded).decode('utf-8')
        if ':' in decoded:
            user, passwd = decoded.split(':', 1)
            return (user, passwd)
    except:
        pass
    return (None, None)


def bad_nonce_report(conf: config.Config):
    logs.syslog(logs.LOG_WARNING, "Bad nonce in digest auth")


def test_passwd(passwd_hash: str, passwd: str) -> bool:
    return mkpasswd(passwd) == passwd_hash


def digest_authorization(auth_header: str, method: str) -> Optional[Dict[str, Any]]:
    raise NotImplementedError("digest_authorization not yet implemented")


def authorization(conf: config.Config, request: str, auth_header: str) -> Dict[str, Any]:
    raise NotImplementedError("authorization not yet implemented")


def string_to_char_list(s: str) -> List[str]:
    return list(s)


def make_conf(from_addr: str, request: str, env: Dict[str, str], bname: str, command: str) -> config.Config:
    return config.Config(
        output_conf=output_conf,
        from_=from_addr,
        env=env,
        bname=bname,
        command=command,
        request=request
    )


def log(msg: str):
    logs.info(msg)


def is_robot(from_addr: str) -> bool:
    return False


def auth_err(conf: config.Config, msg: str):
    logs.syslog(logs.LOG_WARNING, f"Auth error: {msg}")
    util.unauthorized(conf, "Authentication required")


def no_access(conf: config.Config, from_addr: str):
    logs.syslog(logs.LOG_WARNING, f"No access: {from_addr}")
    refuse_log(conf, from_addr)


def log_and_robot_check(tm: float, from_addr: str, request: str, conf: config.Config):
    raise NotImplementedError("log_and_robot_check not yet implemented")


def conf_and_connection(from_addr: str, request: str) -> Optional[config.Config]:
    raise NotImplementedError("conf_and_connection not yet implemented")


def chop_extension(fname: str) -> str:
    if '.' in fname:
        return fname.rsplit('.', 1)[0]
    return fname


def match_strings(pattern: str, text: str) -> bool:
    import re
    try:
        return re.match(pattern, text) is not None
    except:
        return False


def excluded(fname: str) -> bool:
    return False


def image_request(request: str) -> bool:
    lower = request.lower()
    return any(lower.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.svg', '.ico'])


def content_misc(fname: str) -> str:
    if fname.endswith('.css'):
        return 'text/css'
    elif fname.endswith('.js'):
        return 'application/javascript'
    elif fname.endswith('.jpg') or fname.endswith('.jpeg'):
        return 'image/jpeg'
    elif fname.endswith('.png'):
        return 'image/png'
    elif fname.endswith('.gif'):
        return 'image/gif'
    elif fname.endswith('.svg'):
        return 'image/svg+xml'
    elif fname.endswith('.ico'):
        return 'image/x-icon'
    elif fname.endswith('.html'):
        return 'text/html'
    else:
        return 'application/octet-stream'


def find_misc_file(fname: str) -> Optional[str]:
    raise NotImplementedError("find_misc_file not yet implemented")


def print_misc_file(conf: config.Config, fname: str):
    raise NotImplementedError("print_misc_file not yet implemented")


def misc_request(conf: config.Config, request: str):
    raise NotImplementedError("misc_request not yet implemented")


def strip_quotes(s: str) -> str:
    if s.startswith('"') and s.endswith('"'):
        return s[1:-1]
    return s


def extract_multipart(boundary: str, content: str) -> List[Tuple[str, str]]:
    raise NotImplementedError("extract_multipart not yet implemented")


def build_env(query: str, content_type: str, content: str) -> List[Tuple[str, str]]:
    if is_multipart_form(content_type):
        boundary = extract_boundary(content_type)
        return extract_multipart(boundary, content)
    else:
        return parse_query_string(query)


def connection(tm: float, sock, from_addr: Tuple[str, int], request_data: bytes):
    raise NotImplementedError("connection not yet implemented")


def null_reopen():
    pass


def generate_secret_salt(random: bool = False) -> str:
    if random:
        return base64.b64encode(os.urandom(32)).decode('utf-8')
    return hashlib.sha256(str(time.time()).encode()).hexdigest()


def retrieve_secret_salt() -> str:
    raise NotImplementedError("retrieve_secret_salt not yet implemented")


def cgi_timeout():
    logs.syslog(logs.LOG_WARNING, "CGI timeout")


def manage_cgi_timeout(timeout: int):
    raise NotImplementedError("manage_cgi_timeout not yet implemented")


def read_input(content_length: int) -> str:
    return sys.stdin.read(content_length)


def arg_parse_in_file(filename: str) -> List[str]:
    raise NotImplementedError("arg_parse_in_file not yet implemented")


def robot_exclude_arg(fname: str):
    raise NotImplementedError("robot_exclude_arg not yet implemented")


def slashify(dir: str) -> str:
    if not dir.endswith('/'):
        return dir + '/'
    return dir


def make_sock_dir():
    raise NotImplementedError("make_sock_dir not yet implemented")


def register_plugin(dir: str):
    logs.info(f"Registering plugin: {dir}")


def cache_lexicon():
    cache_lexicon_all()


def deprecated_warning_max_clients():
    logs.warn("The -max_clients option is deprecated")


def deprecated_warning_no_fork():
    logs.warn("The -no-fork option is deprecated")


def parse_request_line(line: str) -> Tuple[str, str, str]:
    parts = line.strip().split(' ')
    if len(parts) >= 3:
        return (parts[0], parts[1], parts[2])
    return ('GET', '/', 'HTTP/1.1')


def parse_headers(lines: List[str]) -> Dict[str, str]:
    headers = {}
    for line in lines:
        if ':' in line:
            key, val = line.split(':', 1)
            headers[key.strip().lower()] = val.strip()
    return headers


def parse_query_string(query: str) -> List[Tuple[str, str]]:
    if not query:
        return []
    result = []
    for pair in query.split('&'):
        if '=' in pair:
            key, val = pair.split('=', 1)
            result.append((key, val))
        else:
            result.append((pair, ''))
    return result


def handle_connection(conn, addr):
    try:
        request_data = b''
        while True:
            chunk = conn.recv(4096)
            if not chunk:
                break
            request_data += chunk
            if b'\r\n\r\n' in request_data:
                break

        if not request_data:
            return

        request_str = request_data.decode('utf-8', errors='ignore')
        lines = request_str.split('\r\n')

        if not lines:
            return

        method, path, version = parse_request_line(lines[0])
        headers = parse_headers(lines[1:])

        path_parts = path.split('?')
        script_name = path_parts[0]
        query_string = path_parts[1] if len(path_parts) > 1 else ''

        env = parse_query_string(query_string)

        base_env = {}
        for key, val in env:
            base_env[key] = val

        bname = base_env.get('b', '')

        from bin import request

        conf = config.Config(
            output_conf=output_conf,
            from_=addr[0] if isinstance(addr, tuple) else addr,
            env=base_env,
            bname=bname,
            command=script_name,
            request=path
        )

        response_buffer = []
        original_stdout = sys.stdout

        class ResponseCapture:
            def write(self, s):
                response_buffer.append(s)
            def flush(self):
                pass

        sys.stdout = ResponseCapture()

        try:
            request.treat_request(conf)
        except Exception as e:
            logs.syslog(logs.LOG_ERR, f"Error handling request: {e}")
            response_buffer.append("HTTP/1.1 500 Internal Server Error\r\n")
            response_buffer.append("Content-Type: text/html\r\n")
            response_buffer.append("\r\n")
            response_buffer.append("<html><body><h1>Internal Server Error</h1></body></html>")

        sys.stdout = original_stdout

        response = ''.join(response_buffer)
        if not response.startswith('HTTP/'):
            response = 'HTTP/1.1 200 OK\r\n' + response

        conn.sendall(response.encode('utf-8'))

    except Exception as e:
        logs.syslog(logs.LOG_ERR, f"Connection error: {e}")
    finally:
        try:
            conn.close()
        except:
            pass


def geneweb_server(predictable_mode: bool = False):
    logs.info("GeneWeb server starting...")
    logs.info(f"Port: {selected_port}")
    logs.info(f"Workers: {n_workers}")

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        server_socket.bind((selected_addr or '', selected_port))
        server_socket.listen(5)
        logs.info(f"Server listening on port {selected_port}")

        while True:
            try:
                conn, addr = server_socket.accept()
                logs.info(f"Connection from {addr}")
                handle_connection(conn, addr)
            except KeyboardInterrupt:
                logs.info("Server shutdown requested")
                break
            except Exception as e:
                logs.syslog(logs.LOG_ERR, f"Accept error: {e}")

    finally:
        server_socket.close()
        logs.info("Server stopped")


def geneweb_cgi(secret_salt: str, addr: str, script: str, query: str):
    env = parse_query_string(query)

    base_env = {}
    for key, val in env:
        base_env[key] = val

    bname = base_env.get('b', '')

    from . import request

    conf = config.Config(
        output_conf=output_conf,
        from_=addr,
        env=base_env,
        bname=bname,
        command=script,
        request=query
    )

    try:
        request.treat_request(conf)
    except Exception as e:
        logs.syslog(logs.LOG_ERR, f"CGI error: {e}")
        print("Status: 500 Internal Server Error")
        print("Content-Type: text/html")
        print()
        print("<html><body><h1>Internal Server Error</h1></body></html>")


def main():
    global selected_port, daemon, debug

    if len(sys.argv) > 1:
        for i, arg in enumerate(sys.argv[1:], 1):
            if arg == '-p' and i + 1 < len(sys.argv):
                selected_port = int(sys.argv[i + 1])
            elif arg == '-daemon':
                daemon = True
            elif arg == '-debug':
                debug = True

    cgi = os.environ.get('GATEWAY_INTERFACE')
    if cgi:
        addr = os.environ.get('REMOTE_ADDR', '')
        query = os.environ.get('QUERY_STRING', '')
        script = os.environ.get('SCRIPT_NAME', sys.argv[0])
        secret_salt_val = cgi_secret_salt if cgi_secret_salt else ""
        geneweb_cgi(secret_salt_val, addr, os.path.basename(script), query)
    else:
        geneweb_server(predictable_mode=predictable_mode)


if __name__ == '__main__':
    if has_root_privileges():
        print("Error: The gwd server should never be run with root privileges.", file=sys.stderr)
        print("If you need elevated privileges, for example to open a port below 1024,", file=sys.stderr)
        print("see the security section of the documentation.", file=sys.stderr)
        sys.exit(1)

    try:
        main()
    except OSError as e:
        if e.errno == 98:
            print(f"Error: the port {selected_port} is already used by another GeneWeb daemon or", file=sys.stderr)
            print(f"by another program. Solution: kill the other program or launch", file=sys.stderr)
            print(f"GeneWeb with another port number (option -p)", file=sys.stderr)
        elif e.errno == 13:
            print(f"Error: invalid access to the port {selected_port}: users port number less than", file=sys.stderr)
            print(f"1024 are reserved to the system. Please, read the security", file=sys.stderr)
            print(f"section of the documentation.", file=sys.stderr)
        else:
            raise
    except Exception as e:
        import traceback
        logs.syslog(logs.LOG_CRIT, str(e))
        if debug:
            traceback.print_exc()
