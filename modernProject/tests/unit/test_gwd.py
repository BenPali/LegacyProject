import sys
from pathlib import Path
import socket
import pytest
import io
from bin import gwd, request, robot
from lib import config

sys.path.insert(0, str(Path(__file__).parent.parent / 'bin'))
sys.path.insert(0, str(Path(__file__).parent.parent))

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
    assert gwd.alias_lang("fr-CH") == "fr-CH"
    assert gwd.alias_lang("en-US") == "en-US"
    assert gwd.alias_lang("br") == "bg"
    assert gwd.alias_lang("ca") == "es"
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
    assert gwd.alias_lang("zz") == "zz"
    assert gwd.alias_lang("f") == "f"
    assert gwd.alias_lang("") == ""

def test_has_root_privileges():
    gwd.has_root_privileges()

def test_print_renamed_not_implemented():
    with pytest.raises(NotImplementedError):
        gwd.print_renamed(MagicMock(), "new_name")

def test_log_redirect():
    with patch('bin.gwd.logs.syslog') as mock_syslog:
        gwd.log_redirect("from_addr", "request", "req")
        mock_syslog.assert_called_once_with(gwd.logs.LOG_INFO, "Redirect: from_addr request -> req")

def test_print_redirected_not_implemented():
    with pytest.raises(NotImplementedError):
        gwd.print_redirected(MagicMock(), "req")

def test_nonce_private_key():
    key1 = gwd.nonce_private_key()
    key2 = gwd.nonce_private_key()
    assert isinstance(key1, str)
    assert len(key1) == 64
    assert key1 != key2

def test_digest_nonce():
    nonce = gwd.digest_nonce()
    assert isinstance(nonce, str)
    assert len(nonce) > 0

def test_trace_auth():
    with patch('bin.gwd.logs.syslog') as mock_syslog:
        gwd.trace_auth(MagicMock(), "Basic", "user1")
        mock_syslog.assert_called_once_with(gwd.logs.LOG_INFO, "Auth: Basic user=user1")

def test_unauth_server():
    with patch('bin.gwd.util.unauthorized') as mock_unauthorized:
        gwd.unauth_server(MagicMock(), "Basic")
        mock_unauthorized.assert_called_once()

def test_gen_match_auth_file_not_implemented():
    with pytest.raises(NotImplementedError):
        gwd.gen_match_auth_file("auth_file", "request")

def test_basic_match_auth_file_not_implemented():
    with pytest.raises(NotImplementedError):
        gwd.basic_match_auth_file("auth_file", "request")

def test_digest_match_auth_file_not_implemented():
    with pytest.raises(NotImplementedError):
        gwd.digest_match_auth_file("auth_file", "request")

def test_match_simple_passwd_not_implemented():
    with pytest.raises(NotImplementedError):
        gwd.match_simple_passwd("passwd", "request")

def test_basic_match_auth():
    with patch('bin.gwd.basic_match_auth_file') as mock_basic_match_auth_file:
        mock_basic_match_auth_file.return_value = {"user": "test"}
        result = gwd.basic_match_auth("auth_file", "request")
        assert result == {"user": "test"}
        mock_basic_match_auth_file.assert_called_once_with("auth_file", "request")

    result = gwd.basic_match_auth(None, "request")
    assert result == None

def test_compatible_tokens():
    assert gwd.compatible_tokens("token1", "token1") == True
    assert gwd.compatible_tokens("token1", "token2") == False

def test_get_actlog_not_implemented():
    with pytest.raises(NotImplementedError):
        gwd.get_actlog()

def test_set_actlog_not_implemented():
    with pytest.raises(NotImplementedError):
        gwd.set_actlog([])


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


import io
from unittest.mock import patch, MagicMock

def test_geneweb_cgi_success():
    with (
        patch('sys.stdout', new_callable=io.StringIO) as mock_stdout,
        patch('sys.stderr', new_callable=io.StringIO) as mock_stderr,
        patch('bin.gwd.parse_query_string') as mock_parse_query_string,
        patch('lib.config.Config') as mock_config_class,
        patch('bin.request.treat_request') as mock_treat_request
    ):
        mock_parse_query_string.return_value = [("key", "value")]
        mock_config_instance = MagicMock()
        mock_config_class.return_value = mock_config_instance

        gwd.geneweb_cgi("test_salt", "127.0.0.1", "script_name", "key=value")

        mock_parse_query_string.assert_called_once_with("key=value")
        mock_config_class.assert_called_once()
        mock_treat_request.assert_called_once_with(mock_config_instance)
        assert mock_stdout.getvalue() == ""
        assert mock_stderr.getvalue() == ""

def test_geneweb_cgi_error_handling():
    with (
        patch('sys.stdout', new_callable=io.StringIO) as mock_stdout,
        patch('sys.stderr', new_callable=io.StringIO) as mock_stderr,
        patch('bin.gwd.parse_query_string') as mock_parse_query_string,
        patch('lib.config.Config') as mock_config_class,
        patch('bin.request.treat_request') as mock_treat_request,
        patch('bin.gwd.logs.syslog') as mock_syslog
    ):
        mock_parse_query_string.return_value = []
        mock_config_class.return_value = MagicMock()
        mock_treat_request.side_effect = Exception("Test CGI Error")

        gwd.geneweb_cgi("test_salt", "127.0.0.1", "script_name", "")

        mock_syslog.assert_called_once_with(gwd.logs.LOG_ERR, "CGI error: Test CGI Error")
        assert "Status: 500 Internal Server Error" in mock_stdout.getvalue()
        assert "Content-Type: text/html" in mock_stdout.getvalue()
        assert "Internal Server Error" in mock_stdout.getvalue()
        assert mock_stderr.getvalue() == ""


def test_geneweb_server_initialization_and_shutdown():
    with (
        patch('socket.socket') as mock_socket_class,
        patch('bin.gwd.logs.info') as mock_logs_info,
        patch('bin.gwd.logs.syslog') as mock_logs_syslog,
        patch('bin.gwd.handle_connection') as mock_handle_connection,
        patch('bin.gwd.selected_port', 8080),
        patch('bin.gwd.selected_addr', "127.0.0.1"),
        patch('bin.gwd.n_workers', 1)
    ):
        mock_socket_instance = MagicMock()
        mock_socket_class.return_value = mock_socket_instance

        mock_socket_instance.accept.side_effect = [
            ((MagicMock(), ("127.0.0.1", 12345)),),
            KeyboardInterrupt
        ]

        gwd.geneweb_server()

        mock_socket_class.assert_called_once_with(socket.AF_INET, socket.SOCK_STREAM)
        mock_socket_instance.setsockopt.assert_called_once_with(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        mock_socket_instance.bind.assert_called_once_with(("127.0.0.1", 8080))
        mock_socket_instance.listen.assert_called_once_with(5)

        mock_logs_info.assert_any_call("GeneWeb server starting...")
        mock_logs_info.assert_any_call("Port: 8080")
        mock_logs_info.assert_any_call("Workers: 1")
        mock_logs_info.assert_any_call("Server listening on port 8080")
        connection_log_found = False
        for call_arg in mock_logs_info.call_args_list:
            if call_arg.args and call_arg.args[0] == "Connection from ('127.0.0.1', 12345)":
                connection_log_found = True
                break
        mock_logs_info.assert_any_call("Server shutdown requested")
        mock_logs_info.assert_any_call("Server stopped")


def test_geneweb_server_accept_error_logging():
    with (
        patch('socket.socket') as mock_socket_class,
        patch('bin.gwd.logs.info') as mock_logs_info,
        patch('bin.gwd.logs.syslog') as mock_logs_syslog,
        patch('bin.gwd.handle_connection') as mock_handle_connection,
        patch('bin.gwd.selected_port', 8080),
        patch('bin.gwd.selected_addr', "127.0.0.1"),
        patch('bin.gwd.n_workers', 1)
    ):
        mock_socket_instance = MagicMock()
        mock_socket_class.return_value = mock_socket_instance

        mock_socket_instance.accept.side_effect = [
            Exception("Mock Accept Error"),
            KeyboardInterrupt
        ]

        gwd.geneweb_server()

        mock_logs_syslog.assert_called_once_with(gwd.logs.LOG_ERR, "Accept error: Mock Accept Error")
        mock_socket_instance.close.assert_called_once()

        mock_socket_instance.close.assert_called_once()

def test_handle_connection_success():
    with (
        patch('bin.gwd.parse_request_line') as mock_parse_request_line,
        patch('bin.gwd.parse_headers') as mock_parse_headers,
        patch('bin.gwd.parse_query_string') as mock_parse_query_string,
        patch('lib.config.Config') as mock_config_class,
        patch('bin.request.treat_request') as mock_treat_request,
        patch('sys.stdout', new_callable=io.StringIO) as mock_stdout
    ):
        mock_conn = MagicMock()
        mock_addr = ("127.0.0.1", 12345)

        mock_conn.recv.side_effect = [
            b"GET /test?param=value HTTP/1.1\r\nHost: localhost\r\n\r\n",
            b""
        ]
        mock_parse_request_line.return_value = ("GET", "/test?param=value", "HTTP/1.1")
        mock_parse_headers.return_value = {"host": "localhost"}
        mock_parse_query_string.return_value = [("param", "value")]
        mock_config_instance = MagicMock()
        mock_config_class.return_value = mock_config_instance
        mock_treat_request.return_value = None 

        gwd.handle_connection(mock_conn, mock_addr)

        mock_conn.recv.assert_any_call(4096)
        mock_parse_request_line.assert_called_once_with("GET /test?param=value HTTP/1.1")
        mock_parse_headers.assert_called_once()
        mock_parse_query_string.assert_called_once_with("param=value")
        mock_config_class.assert_called_once()
        mock_treat_request.assert_called_once_with(mock_config_instance)
        mock_conn.sendall.assert_called_once()
        mock_conn.close.assert_called_once()
        assert "HTTP/1.1 200 OK" in mock_conn.sendall.call_args[0][0].decode('utf-8')


def test_handle_connection_error_during_request_processing():
    with (
        patch('bin.gwd.parse_request_line') as mock_parse_request_line,
        patch('bin.gwd.parse_headers') as mock_parse_headers,
        patch('bin.gwd.parse_query_string') as mock_parse_query_string,
        patch('lib.config.Config') as mock_config_class,
        patch('bin.request.treat_request') as mock_treat_request,
        patch('sys.stdout', new_callable=io.StringIO) as mock_stdout,
        patch('bin.gwd.logs.syslog') as mock_syslog
    ):
        mock_conn = MagicMock()
        mock_addr = ("127.0.0.1", 12345)

        mock_conn.recv.side_effect = [
            b"GET /error HTTP/1.1\r\nHost: localhost\r\n\r\n",
            b""
        ]
        mock_parse_request_line.return_value = ("GET", "/error", "HTTP/1.1")
        mock_parse_headers.return_value = {"host": "localhost"}
        mock_parse_query_string.return_value = []
        mock_config_instance = MagicMock()
        mock_config_class.return_value = mock_config_instance
        mock_treat_request.side_effect = Exception("Test Request Processing Error")

        gwd.handle_connection(mock_conn, mock_addr)

        mock_syslog.assert_called_once_with(gwd.logs.LOG_ERR, "Error handling request: Test Request Processing Error")
        mock_conn.sendall.assert_called_once()
        mock_conn.close.assert_called_once()
        response_content = mock_conn.sendall.call_args[0][0].decode('utf-8')
        assert "HTTP/1.1 500 Internal Server Error" in response_content
        assert "Internal Server Error" in response_content


def test_handle_connection_general_exception():
    with (
        patch('bin.gwd.logs.syslog') as mock_syslog
    ):
        mock_conn = MagicMock()
        mock_addr = ("127.0.0.1", 12345)

        mock_conn.recv.side_effect = Exception("Test General Connection Error")

        gwd.handle_connection(mock_conn, mock_addr)

        mock_syslog.assert_called_once_with(gwd.logs.LOG_ERR, "Connection error: Test General Connection Error")
        mock_conn.close.assert_called_once()

def test_strip_quotes():
    assert gwd.strip_quotes('"hello"') == "hello"
    assert gwd.strip_quotes('hello') == "hello"
    assert gwd.strip_quotes('"hello\"world"') == "hello\"world"
    assert gwd.strip_quotes('""') == ""
    assert gwd.strip_quotes('') == ''

def test_extract_multipart_not_implemented():
    with pytest.raises(NotImplementedError):
        gwd.extract_multipart("boundary", "content")

def test_build_env():
    with (
        patch('bin.gwd.is_multipart_form') as mock_is_multipart_form,
        patch('bin.gwd.extract_boundary') as mock_extract_boundary,
        patch('bin.gwd.extract_multipart') as mock_extract_multipart,
        patch('bin.gwd.parse_query_string') as mock_parse_query_string
    ):
        mock_is_multipart_form.return_value = True
        mock_extract_boundary.return_value = "test_boundary"
        mock_extract_multipart.return_value = [("key1", "val1")]
        result = gwd.build_env("", "multipart/form-data; boundary=test_boundary", "content")
        mock_is_multipart_form.assert_called_once_with("multipart/form-data; boundary=test_boundary")
        mock_extract_boundary.assert_called_once_with("multipart/form-data; boundary=test_boundary")
        mock_extract_multipart.assert_called_once_with("test_boundary", "content")
        assert result == [("key1", "val1")]

        mock_is_multipart_form.return_value = False
        mock_parse_query_string.return_value = [("key2", "val2")]
        result = gwd.build_env("param=value", "application/x-www-form-urlencoded", "")
        mock_is_multipart_form.assert_called_with("application/x-www-form-urlencoded")
        mock_parse_query_string.assert_called_once_with("param=value")
        assert result == [("key2", "val2")]

def test_connection_not_implemented():
    with pytest.raises(NotImplementedError):
        gwd.connection(0.0, MagicMock(), ("127.0.0.1", 12345), b"")

def test_null_reopen():
    gwd.null_reopen()
    assert True

def test_generate_secret_salt():
    salt1 = gwd.generate_secret_salt(random=False)
    assert isinstance(salt1, str)
    assert len(salt1) > 0

    salt2 = gwd.generate_secret_salt(random=True)
    assert isinstance(salt2, str)
    assert len(salt2) > 0
    assert salt1 != salt2

def test_retrieve_secret_salt_not_implemented():
    with pytest.raises(NotImplementedError):
        gwd.retrieve_secret_salt()

def test_cgi_timeout():
    with patch('bin.gwd.logs.syslog') as mock_syslog:
        gwd.cgi_timeout()
        mock_syslog.assert_called_once_with(gwd.logs.LOG_WARNING, "CGI timeout")

def test_manage_cgi_timeout_not_implemented():
    with pytest.raises(NotImplementedError):
        gwd.manage_cgi_timeout(10)

def test_read_input():
    with patch('sys.stdin', new_callable=io.StringIO) as mock_stdin:
        mock_stdin.write("test input")
        mock_stdin.seek(0)
        result = gwd.read_input(4)
        assert result == "test"
        result = gwd.read_input(100)
        assert result == " input"

def test_arg_parse_in_file_not_implemented():
    with pytest.raises(NotImplementedError):
        gwd.arg_parse_in_file("filename.txt")

def test_robot_exclude_arg_not_implemented():
    with pytest.raises(NotImplementedError):
        gwd.robot_exclude_arg("fname")

def test_slashify():
    assert gwd.slashify("/path") == "/path/"
    assert gwd.slashify("/path/") == "/path/"
    assert gwd.slashify("") == "/"
    assert gwd.slashify("path") == "path/"

def test_make_sock_dir_not_implemented():
    with pytest.raises(NotImplementedError):
        gwd.make_sock_dir()

def test_register_plugin():
    with patch('bin.gwd.logs.info') as mock_logs_info:
        gwd.register_plugin("/path/to/plugin")
        mock_logs_info.assert_called_once_with("Registering plugin: /path/to/plugin")

def test_cache_lexicon():
    with patch('bin.gwd.cache_lexicon_all') as mock_cache_lexicon_all:
        gwd.cache_lexicon()
        mock_cache_lexicon_all.assert_called_once()

def test_deprecated_warning_max_clients():
    with patch('bin.gwd.logs.warn') as mock_logs_warn:
        gwd.deprecated_warning_max_clients()
        mock_logs_warn.assert_called_once_with("The -max_clients option is deprecated")

def test_deprecated_warning_no_fork():
    with patch('bin.gwd.logs.warn') as mock_logs_warn:
        gwd.deprecated_warning_no_fork()
        mock_logs_warn.assert_called_once_with("The -no-fork option is deprecated")


def test_content_misc():
    assert gwd.content_misc("test.css") == "text/css"
    assert gwd.content_misc("test.js") == "application/javascript"
    assert gwd.content_misc("test.png") == "image/png"
    assert gwd.content_misc("test.gif") == "image/gif"
    assert gwd.content_misc("test.svg") == "image/svg+xml"
    assert gwd.content_misc("test.ico") == "image/x-icon"
    assert gwd.content_misc("test.html") == "text/html"
    assert gwd.content_misc("test.txt") == "application/octet-stream"
    assert gwd.content_misc("test.unknown") == "application/octet-stream"
    assert gwd.content_misc("test") == "application/octet-stream"


def test_log():
    with patch('bin.gwd.logs.info') as mock_logs_info:
        gwd.log("Test message")
        mock_logs_info.assert_called_once_with("Test message")


def test_is_robot():
    assert gwd.is_robot("some_address") == False


def test_auth_err():
    mock_conf = MagicMock()
    with (
        patch('bin.gwd.logs.syslog') as mock_syslog,
        patch('bin.gwd.util.unauthorized') as mock_unauthorized
    ):
        gwd.auth_err(mock_conf, "Auth failed")
        mock_syslog.assert_called_once_with(gwd.logs.LOG_WARNING, "Auth error: Auth failed")
        mock_unauthorized.assert_called_once_with(mock_conf, "Authentication required")


def test_no_access():
    mock_conf = MagicMock()
    with (
        patch('bin.gwd.logs.syslog') as mock_syslog,
        patch('bin.gwd.refuse_log') as mock_refuse_log
    ):
        gwd.no_access(mock_conf, "192.168.1.1")
        mock_syslog.assert_called_once_with(gwd.logs.LOG_WARNING, "No access: 192.168.1.1")
        mock_refuse_log.assert_called_once_with(mock_conf, "192.168.1.1")


def test_log_and_robot_check_not_implemented():
    with pytest.raises(NotImplementedError):
        gwd.log_and_robot_check(0.0, "addr", "req", MagicMock())


def test_conf_and_connection_not_implemented():
    with pytest.raises(NotImplementedError):
        gwd.conf_and_connection("addr", "req")


def test_chop_extension():
    assert gwd.chop_extension("file.txt") == "file"
    assert gwd.chop_extension("file.tar.gz") == "file.tar"
    assert gwd.chop_extension("nofileextension") == "nofileextension"
    assert gwd.chop_extension(".bashrc") == ""
    assert gwd.chop_extension("") == ""


def test_match_strings():
    assert gwd.match_strings("hello", "hello world") == True
    assert gwd.match_strings("world", "hello world") == False
    assert gwd.match_strings("\\d+", "12345") == True
    assert gwd.match_strings("\\d+", "abc") == False
    assert gwd.match_strings("[a-z]+", "abc") == True
    assert gwd.match_strings("[a-z]+", "123") == False
    assert gwd.match_strings("", "anything") == True
    assert gwd.match_strings("anything", "") == False


def test_excluded():
    assert gwd.excluded("some_file") == False


def test_mkpasswd():
    assert gwd.mkpasswd("password") == "5f4dcc3b5aa765d61d8327deb882cf99"
    assert gwd.mkpasswd("") == "d41d8cd98f00b204e9800998ecf8427e"


def test_set_token_not_implemented():
    with pytest.raises(NotImplementedError):
        gwd.set_token("user", "passwd", "token")


def test_index_not_name():
    assert gwd.index_not_name("name_123-abc") == 12
    assert gwd.index_not_name("name.123") == 4
    assert gwd.index_not_name("name") == 4
    assert gwd.index_not_name("") == 0


def test_refresh_url_not_implemented():
    with pytest.raises(NotImplementedError):
        gwd.refresh_url(MagicMock())


def test_http_preferred_language():
    assert gwd.http_preferred_language("fr-CH, fr;q=0.9, en;q=0.8, de;q=0.7, *;q=0.5") == "fr"
    assert gwd.http_preferred_language("en-US,en;q=0.5") == "en"
    assert gwd.http_preferred_language("en") == "en"
    assert gwd.http_preferred_language("") == None
    assert gwd.http_preferred_language("fr;q=0.9") == "fr"
    assert gwd.http_preferred_language("f") == None


def test_allowed_denied_titles():
    assert gwd.allowed_denied_titles(MagicMock()) == ([], [])


def test_allowed_titles():
    assert gwd.allowed_titles(MagicMock()) == []


def test_denied_titles():
    assert gwd.denied_titles(MagicMock()) == []


def test_parse_digest():
    auth_header = 'Digest username="Mufasa", realm="testrealm@host.com", nonce="dcd98b7102dd2f0e8b11d0f600bfb0c093", uri="/dir/index.html", qop=auth, nc=00000001, cnonce="0a4f113b", response="6629fae49393a05397450978507c4ef1", opaque="5ccc069c403eb9246851ca56"'
    result = gwd.parse_digest(auth_header)
    assert result["username"] == "Mufasa"
    assert result["realm"] == "testrealm@host.com"
    assert result["nonce"] == "dcd98b7102dd2f0e8b11d0f600bfb0c093"
    assert result["uri"] == "/dir/index.html"
    assert result["qop"] == "auth"
    assert result["nc"] == "00000001"
    assert result["cnonce"] == "0a4f113b"
    assert result["response"] == "6629fae49393a05397450978507c4ef1"
    assert result["opaque"] == "5ccc069c403eb9246851ca56"

    assert gwd.parse_digest("Basic some_token") == {}
    assert gwd.parse_digest("") == {}


def test_basic_authorization():
    user, passwd = gwd.basic_authorization("Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ==")
    assert user == "Aladdin"
    assert passwd == "open sesame"

    user, passwd = gwd.basic_authorization("Bearer some_token")
    assert user == None
    assert passwd == None


def test_bad_nonce_report():
    with patch('bin.gwd.logs.syslog') as mock_syslog:
        gwd.bad_nonce_report(MagicMock())
        mock_syslog.assert_called_once_with(gwd.logs.LOG_WARNING, "Bad nonce in digest auth")


def test_test_passwd():
    assert gwd.test_passwd("5f4dcc3b5aa765d61d8327deb882cf99", "password") == True
    assert gwd.test_passwd("wrong_hash", "password") == False


def test_digest_authorization_not_implemented():
    with pytest.raises(NotImplementedError):
        gwd.digest_authorization("auth_header", "method")


def test_authorization_not_implemented():
    with pytest.raises(NotImplementedError):
        gwd.authorization(MagicMock(), "request", "auth_header")


def test_refuse_log():
    with (
        patch('bin.gwd.logs.syslog') as mock_syslog,
        patch('bin.gwd.http') as mock_http,
        patch('bin.gwd.copy_file') as mock_copy_file,
        patch('lib.config.Config') as mock_config_class,
        patch('lib.config.OutputConf') as mock_output_conf_class
    ):
        mock_output_conf = MagicMock()
        mock_output_conf_class.return_value = mock_output_conf
        mock_config = MagicMock()
        mock_config_class.return_value = mock_config
        mock_config.output_conf = mock_output_conf

        from_addr = "192.168.1.1"
        gwd.refuse_log(mock_config, from_addr)

        mock_syslog.assert_called_once_with(gwd.logs.LOG_NOTICE, f"Excluded: {from_addr}")
        mock_http.assert_called_once_with(mock_config, 403)
        mock_output_conf.header.assert_called_once_with("Content-type: text/html")
        mock_output_conf.body.assert_called_once_with("Your access has been disconnected by administrator.\n")
        mock_copy_file.assert_called_once_with(mock_config, "refuse")


def test_only_log():
    with (
        patch('bin.gwd.logs.syslog') as mock_syslog,
        patch('bin.gwd.http') as mock_http,
        patch('lib.config.Config') as mock_config_class,
        patch('lib.config.OutputConf') as mock_output_conf_class
    ):
        mock_output_conf = MagicMock()
        mock_output_conf_class.return_value = mock_output_conf
        mock_config = MagicMock()
        mock_config_class.return_value = mock_config
        mock_config.output_conf = mock_output_conf

        from_addr = "192.168.1.2"
        gwd.only_log(mock_config, from_addr)

        mock_syslog.assert_called_once_with(gwd.logs.LOG_NOTICE, f"Connection refused from {from_addr}")
        mock_http.assert_called_once_with(mock_config, 200)
        mock_output_conf.header.assert_called_once_with("Content-type: text/html; charset=iso-8859-1")
        mock_output_conf.body.assert_any_call("<head><title>Invalid access</title></head>\n")
        mock_output_conf.body.assert_any_call("<body><h1>Invalid access</h1></body>\n")


def test_refuse_auth():
    with (
        patch('bin.gwd.logs.syslog') as mock_syslog,
        patch('lib.util.unauthorized') as mock_unauthorized,
        patch('lib.config.Config') as mock_config_class
    ):
        mock_config = MagicMock()
        mock_config_class.return_value = mock_config

        from_addr = "192.168.1.3"
        auth = "Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ=="
        auth_type = "Basic"
        gwd.refuse_auth(mock_config, from_addr, auth, auth_type)

        mock_syslog.assert_called_once_with(gwd.logs.LOG_NOTICE,
                                            f"Access failed --- From: {from_addr} --- Basic realm: {auth_type} --- Response: {auth}")
        mock_unauthorized.assert_called_once_with(mock_config, auth_type)
