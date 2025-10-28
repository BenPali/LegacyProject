import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'bin'))
sys.path.insert(0, str(Path(__file__).parent.parent))

from bin import gwd, request, robot
from lib import config


def test_gwd_imports():
    assert hasattr(gwd, 'geneweb_server')
    assert hasattr(gwd, 'geneweb_cgi')
    assert hasattr(gwd, 'main')


def test_request_imports():
    assert hasattr(request, 'treat_request')
    assert hasattr(request, 'w_base')
    assert hasattr(request, 'w_person')
    assert hasattr(request, 'w_wizard')


def test_robot_imports():
    assert hasattr(robot, 'robot_error')
    assert hasattr(robot, 'check')
    assert hasattr(robot, 'robot_excl')


def test_gwd_config_defaults():
    assert gwd.selected_port == 2317
    assert gwd.default_lang == "fr"
    assert gwd.conn_timeout == 120


def test_is_multipart_form():
    assert gwd.is_multipart_form("multipart/form-data; boundary=something") == True
    assert gwd.is_multipart_form("text/html") == False
    assert gwd.is_multipart_form("MULTIPART/FORM-DATA") == True


def test_split_username():
    assert gwd.split_username("user") == ("user", "")
    assert gwd.split_username("user|sosa") == ("user", "sosa")
    assert gwd.split_username("user|sosa|extra") == ("user", "")


def test_index_function():
    assert gwd.index("hello", "l") == 2
    assert gwd.index("hello", "z") == 5
    assert gwd.index("", "a") == 0


def test_alias_lang():
    assert gwd.alias_lang("fr") == "fr"
    assert gwd.alias_lang("en") == "en"
    assert gwd.alias_lang("br") == "bg"
    assert gwd.alias_lang("ca") == "es"


def test_robot_user_type():
    from bin.robot import UserType
    assert UserType.NORMAL.value == "normal"
    assert UserType.FRIEND.value == "friend"
    assert UserType.WIZARD.value == "wizard"


def test_robot_magic():
    assert robot.magic_robot == "GnWbRobotExcl001"
    assert robot.min_disp_req == 20


def test_request_only_special_env():
    assert request.only_special_env([("_test", "val"), ("lang", "en")]) == True
    assert request.only_special_env([("m", "P"), ("lang", "en")]) == False
    assert request.only_special_env([]) == True


def test_person_is_std_key():
    assert hasattr(request, 'person_is_std_key')
    assert hasattr(request, 'select_std_eq')
    assert hasattr(request, 'find_all')


def test_extract_boundary():
    assert gwd.extract_boundary("multipart/form-data; boundary=----WebKitFormBoundary") == "----WebKitFormBoundary"
    assert gwd.extract_boundary("text/html") == ""
    assert gwd.extract_boundary("boundary=test123") == "test123"


def test_extract_assoc():
    kvl = [("key1", "val1"), ("key2", "val2"), ("key3", "val3")]
    val, remaining = gwd.extract_assoc("key2", kvl)
    assert val != ""
    assert len(remaining) == 2

    val, remaining = gwd.extract_assoc("nonexistent", kvl)
    assert val == ""
    assert len(remaining) == 3


def test_index_from():
    assert gwd.index_from("hello world", 0, "o") == 4
    assert gwd.index_from("hello world", 5, "o") == 7
    assert gwd.index_from("hello", 0, "z") == 5


def test_parse_request_line():
    method, path, version = gwd.parse_request_line("GET /index.html HTTP/1.1")
    assert method == "GET"
    assert path == "/index.html"
    assert version == "HTTP/1.1"

    method, path, version = gwd.parse_request_line("POST /api HTTP/1.0")
    assert method == "POST"
    assert path == "/api"

    method, path, version = gwd.parse_request_line("")
    assert method == "GET"
    assert path == "/"


def test_parse_headers():
    lines = [
        "Host: localhost:2317",
        "User-Agent: Mozilla/5.0",
        "Content-Type: text/html",
        ""
    ]
    headers = gwd.parse_headers(lines)
    assert "host" in headers
    assert headers["host"] == "localhost:2317"
    assert "user-agent" in headers
    assert "content-type" in headers


def test_parse_query_string():
    result = gwd.parse_query_string("a=1&b=2&c=3")
    assert len(result) == 3
    assert ("a", "1") in result
    assert ("b", "2") in result

    result = gwd.parse_query_string("")
    assert len(result) == 0

    result = gwd.parse_query_string("key=value")
    assert len(result) == 1
    assert ("key", "value") in result

    result = gwd.parse_query_string("flag&key=val")
    assert len(result) == 2


def test_make_senv():
    output_conf = config.OutputConf(
        status=lambda x: None,
        header=lambda x: None,
        body=lambda x: None,
        flush=lambda: None
    )

    conf = config.Config(
        output_conf=output_conf,
        env={"skey": "sval", "hkey": "hval", "other": "val"}
    )

    new_conf = request.make_senv(conf, None)
    assert "skey" in new_conf.senv
    assert "hkey" not in new_conf.senv


def test_make_henv():
    output_conf = config.OutputConf(
        status=lambda x: None,
        header=lambda x: None,
        body=lambda x: None,
        flush=lambda: None
    )

    conf = config.Config(
        output_conf=output_conf,
        env={"skey": "sval", "hkey": "hval", "other": "val"}
    )

    new_conf = request.make_henv(conf, None)
    assert "hkey" in new_conf.henv
    assert "skey" not in new_conf.henv


def test_incorrect_request():
    output_buffer = []

    def capture_status(s):
        output_buffer.append(f"STATUS:{s}")

    def capture_header(h):
        output_buffer.append(f"HEADER:{h}")

    def capture_body(b):
        output_buffer.append(f"BODY:{b}")

    output_conf = config.OutputConf(
        status=capture_status,
        header=capture_header,
        body=capture_body,
        flush=lambda: None
    )

    conf = config.Config(output_conf=output_conf)

    request.incorrect_request(conf, "Test error")
    assert any("STATUS:400" in x for x in output_buffer)
    assert any("Test error" in x for x in output_buffer)


def test_robot_excl_no_file():
    import os
    original_cwd = os.getcwd()
    try:
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            excl, robot_file = robot.robot_excl()
            assert excl.excl == []
            assert excl.who == {}
            assert excl.max_conn == (0, "")
    finally:
        os.chdir(original_cwd)


def test_has_root_privileges():
    result = gwd.has_root_privileges()
    assert isinstance(result, bool)


def test_alias_lang_more_cases():
    assert gwd.alias_lang("co") == "fr"
    assert gwd.alias_lang("eu") == "fr"
    assert gwd.alias_lang("hr") == "bg"
    assert gwd.alias_lang("ia") == "la"
    assert gwd.alias_lang("mk") == "bg"
    assert gwd.alias_lang("oc") == "ca"
    assert gwd.alias_lang("sc") == "ca"
    assert gwd.alias_lang("sk") == "cz"
    assert gwd.alias_lang("sr") == "bg"
    assert gwd.alias_lang("ur") == "ar"
    assert gwd.alias_lang("xy") == "xy"
    assert gwd.alias_lang("") == ""


def test_w_base_with_no_base():
    def none_callback(c):
        return "NO_BASE"

    def base_callback(c, b):
        return "HAS_BASE"

    output_conf = config.OutputConf(
        status=lambda x: None,
        header=lambda x: None,
        body=lambda x: None,
        flush=lambda: None
    )

    conf = config.Config(output_conf=output_conf)

    result = request.w_base(none_callback, base_callback, conf, None)
    assert result == "NO_BASE"

    result = request.w_base(none_callback, base_callback, conf, "")
    assert result == "NO_BASE"


def test_treat_request_robots():
    output_buffer = []

    def capture_body(b):
        output_buffer.append(b)

    output_conf = config.OutputConf(
        status=lambda x: None,
        header=lambda x: None,
        body=capture_body,
        flush=lambda: None
    )

    conf = config.Config(
        output_conf=output_conf,
        command="/robots.txt"
    )

    request.treat_request(conf)
    result = ''.join(output_buffer)
    assert "User-Agent" in result or "Disallow" in result


def test_treat_request_default():
    output_buffer = []

    def capture_body(b):
        output_buffer.append(b)

    output_conf = config.OutputConf(
        status=lambda x: None,
        header=lambda x: None,
        body=capture_body,
        flush=lambda: None
    )

    conf = config.Config(
        output_conf=output_conf,
        env={}
    )

    request.treat_request(conf)
    result = ''.join(output_buffer)
    assert "GeneWeb" in result


def test_treat_request_with_module():
    output_buffer = []

    def capture_body(b):
        output_buffer.append(b)

    output_conf = config.OutputConf(
        status=lambda x: None,
        header=lambda x: None,
        body=capture_body,
        flush=lambda: None
    )

    conf = config.Config(
        output_conf=output_conf,
        env={"m": "F"}
    )

    request.treat_request(conf)
    result = ''.join(output_buffer)
    assert "Family" in result


def test_robot_save_and_load():
    import os
    import tempfile
    original_cwd = os.getcwd()
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)

            excl = robot.Excl(
                excl=[("192.168.1.1", 5), ("10.0.0.1", 3)],
                who={},
                max_conn=(0, "")
            )

            robot_file = os.path.join(tmpdir, "test_robot.txt")
            robot.save_robot_excl(excl, robot_file)

            assert os.path.exists(robot_file)

            with open(robot_file, 'r') as f:
                content = f.read()
                assert robot.magic_robot in content
                assert "192.168.1.1 5" in content
                assert "10.0.0.1 3" in content
    finally:
        os.chdir(original_cwd)


def test_lexicon_cache():
    cache_key = "lexicon.bin.fr"
    if cache_key in gwd.lexicon_cache:
        cached = gwd.lexicon_cache[cache_key]
        assert isinstance(cached, dict)


def test_http_functions():
    import io
    import sys

    old_stdout = sys.stdout
    sys.stdout = io.StringIO()

    from lib import wserver
    wserver.http(200)
    output = sys.stdout.getvalue()
    assert "HTTP/1.1 200" in output

    sys.stdout = io.StringIO()
    wserver.header("Content-Type: text/html")
    output = sys.stdout.getvalue()
    assert "Content-Type: text/html" in output

    sys.stdout = io.StringIO()
    wserver.print_string("Hello World")
    output = sys.stdout.getvalue()
    assert "Hello World" in output

    sys.stdout = old_stdout


def test_copy_file_nonexistent():
    output_buffer = []

    output_conf = config.OutputConf(
        status=lambda x: None,
        header=lambda x: None,
        body=lambda b: output_buffer.append(b),
        flush=lambda: None
    )

    conf = config.Config(output_conf=output_conf)

    result = gwd.copy_file(conf, "nonexistent_file_xyz")
    assert result == False


def test_http_helper():
    output_buffer = []

    def capture_status(s):
        output_buffer.append(f"STATUS:{s}")

    def capture_header(h):
        output_buffer.append(f"HEADER:{h}")

    output_conf = config.OutputConf(
        status=capture_status,
        header=capture_header,
        body=lambda x: None,
        flush=lambda: None
    )

    conf = config.Config(output_conf=output_conf)

    gwd.http(conf, 404)
    assert any("STATUS:404" in x for x in output_buffer)
    assert any("Content-type" in x for x in output_buffer)


def test_skeleton_auth_functions():
    assert hasattr(gwd, 'nonce_private_key')
    assert hasattr(gwd, 'digest_nonce')
    assert hasattr(gwd, 'basic_authorization')
    assert hasattr(gwd, 'parse_digest')
    assert hasattr(gwd, 'mkpasswd')
    assert hasattr(gwd, 'test_passwd')

    key = gwd.nonce_private_key()
    assert isinstance(key, str)
    assert len(key) > 0

    nonce = gwd.digest_nonce()
    assert isinstance(nonce, str)

    passwd_hash = gwd.mkpasswd("test123")
    assert isinstance(passwd_hash, str)
    assert gwd.test_passwd(passwd_hash, "test123")
    assert not gwd.test_passwd(passwd_hash, "wrong")

    user, passwd = gwd.basic_authorization("Basic dGVzdDoxMjM=")
    assert user == "test"
    assert passwd == "123"


def test_skeleton_misc_functions():
    assert hasattr(gwd, 'chop_extension')
    assert hasattr(gwd, 'image_request')
    assert hasattr(gwd, 'content_misc')
    assert hasattr(gwd, 'strip_quotes')
    assert hasattr(gwd, 'slashify')

    assert gwd.chop_extension("file.txt") == "file"
    assert gwd.chop_extension("file.tar.gz") == "file.tar"
    assert gwd.chop_extension("noext") == "noext"

    assert gwd.image_request("/img/photo.jpg") == True
    assert gwd.image_request("/img/icon.png") == True
    assert gwd.image_request("/page.html") == False

    assert gwd.content_misc("style.css") == "text/css"
    assert gwd.content_misc("script.js") == "application/javascript"
    assert gwd.content_misc("photo.jpg") == "image/jpeg"

    assert gwd.strip_quotes('"hello"') == "hello"
    assert gwd.strip_quotes('hello') == "hello"

    assert gwd.slashify("/path") == "/path/"
    assert gwd.slashify("/path/") == "/path/"


def test_skeleton_session_functions():
    assert hasattr(gwd, 'get_token')
    assert hasattr(gwd, 'set_token')
    assert hasattr(gwd, 'compatible_tokens')

    assert gwd.compatible_tokens("abc", "abc") == True
    assert gwd.compatible_tokens("abc", "xyz") == False


def test_skeleton_http_functions():
    assert hasattr(gwd, 'http_preferred_language')

    lang = gwd.http_preferred_language("en-US,en;q=0.9,fr;q=0.8")
    assert lang == "en"

    lang = gwd.http_preferred_language("")
    assert lang is None


def test_skeleton_security_functions():
    assert hasattr(gwd, 'allowed_titles')
    assert hasattr(gwd, 'denied_titles')
    assert hasattr(gwd, 'allowed_denied_titles')
    assert hasattr(gwd, 'is_robot')
    assert hasattr(gwd, 'excluded')

    output_conf = config.OutputConf(
        status=lambda x: None,
        header=lambda x: None,
        body=lambda x: None,
        flush=lambda: None
    )
    conf = config.Config(output_conf=output_conf)

    allowed, denied = gwd.allowed_denied_titles(conf)
    assert isinstance(allowed, list)
    assert isinstance(denied, list)


def test_skeleton_util_functions():
    assert hasattr(gwd, 'index_not_name')
    assert hasattr(gwd, 'string_to_char_list')
    assert hasattr(gwd, 'match_strings')

    idx = gwd.index_not_name("hello123")
    assert idx == 8

    idx = gwd.index_not_name("hello world")
    assert idx == 5

    chars = gwd.string_to_char_list("abc")
    assert chars == ['a', 'b', 'c']


def test_skeleton_crypto_functions():
    assert hasattr(gwd, 'generate_secret_salt')

    salt1 = gwd.generate_secret_salt(random=False)
    assert isinstance(salt1, str)
    assert len(salt1) > 0

    salt2 = gwd.generate_secret_salt(random=True)
    assert isinstance(salt2, str)
    assert len(salt2) > 0


def test_skeleton_plugin_functions():
    assert hasattr(gwd, 'register_plugin')
    assert hasattr(gwd, 'cache_lexicon')

    gwd.register_plugin("/path/to/plugin")
