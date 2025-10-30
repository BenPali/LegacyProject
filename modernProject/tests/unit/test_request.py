import sys
import os
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'bin'))
sys.path.insert(0, str(Path(__file__).parent.parent))

from bin import request
from lib import config, driver, secure, sosa


def test_imports():
    assert hasattr(request, 'treat_request')
    assert hasattr(request, 'w_base')
    assert hasattr(request, 'w_person')
    assert hasattr(request, 'w_wizard')
    assert hasattr(request, 'person_is_std_key')
    assert hasattr(request, 'select_std_eq')
    assert hasattr(request, 'find_all')


def test_only_special_env():
    assert request.only_special_env([("_test", "val"), ("lang", "en")]) == True
    assert request.only_special_env([("m", "P"), ("lang", "en")]) == False
    assert request.only_special_env([]) == True
    assert request.only_special_env([("_internal", "x")]) == True
    assert request.only_special_env([("key", "val")]) == False


def test_incorrect_request():
    output_buffer = []

    def capture_status(s):
        output_buffer.append(f"STATUS:{s}")

    def capture_header(h):
        output_buffer.append(f"HEADER:{h}")

    def capture_body(b):
        output_buffer.append(b)

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
    assert any("Incorrect request" in x for x in output_buffer)


def test_incorrect_request_without_comment():
    output_buffer = []

    def capture_body(b):
        output_buffer.append(b)

    output_conf = config.OutputConf(
        status=lambda x: None,
        header=lambda x: None,
        body=capture_body,
        flush=lambda: None
    )

    conf = config.Config(output_conf=output_conf)

    request.incorrect_request(conf)
    output = ''.join(output_buffer)
    assert "Incorrect request" in output


def test_make_senv():
    output_conf = config.OutputConf(
        status=lambda x: None,
        header=lambda x: None,
        body=lambda x: None,
        flush=lambda: None
    )

    conf = config.Config(
        output_conf=output_conf,
        env={"skey": "sval", "hkey": "hval", "other": "val", "s2": "s2val"}
    )

    new_conf = request.make_senv(conf, None)
    assert "skey" in new_conf.senv
    assert "s2" in new_conf.senv
    assert "hkey" not in new_conf.senv
    assert "other" not in new_conf.senv


def test_make_henv():
    output_conf = config.OutputConf(
        status=lambda x: None,
        header=lambda x: None,
        body=lambda x: None,
        flush=lambda: None
    )

    conf = config.Config(
        output_conf=output_conf,
        env={"skey": "sval", "hkey": "hval", "other": "val", "h2": "h2val"}
    )

    new_conf = request.make_henv(conf, None)
    assert "hkey" in new_conf.henv
    assert "h2" in new_conf.henv
    assert "skey" not in new_conf.henv
    assert "other" not in new_conf.henv


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


def test_w_base_with_nonexistent_base():
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

    result = request.w_base(none_callback, base_callback, conf, "nonexistent_db")
    assert result == "NO_BASE"


def test_w_wizard_without_wizard_access():
    import sys
    from io import StringIO

    old_stdout = sys.stdout
    sys.stdout = StringIO()

    output_conf = config.OutputConf(
        status=lambda s: None,
        header=lambda x: None,
        body=lambda b: None,
        flush=lambda: None
    )

    conf = config.Config(
        output_conf=output_conf,
        wizard=False
    )

    callback_called = []

    def callback(c, b):
        callback_called.append(True)

    request.w_wizard(callback, conf, None)

    output = sys.stdout.getvalue()
    sys.stdout = old_stdout

    assert "401 Unauthorized" in output
    assert len(callback_called) == 0


def test_w_wizard_with_wizard_access():
    output_buffer = []

    output_conf = config.OutputConf(
        status=lambda x: None,
        header=lambda x: None,
        body=lambda b: output_buffer.append(b),
        flush=lambda: None
    )

    conf = config.Config(
        output_conf=output_conf,
        wizard=True
    )

    def callback(c, b):
        output_buffer.append("CALLBACK_CALLED")

    request.w_wizard(callback, conf, None)
    assert "CALLBACK_CALLED" in output_buffer


def test_w_person_without_person():
    output_buffer = []

    output_conf = config.OutputConf(
        status=lambda x: None,
        header=lambda x: None,
        body=lambda b: output_buffer.append(b),
        flush=lambda: None
    )

    conf = config.Config(
        output_conf=output_conf,
        env={}
    )

    def none_callback(c, b):
        return "NO_PERSON"

    def person_callback(c, b, p):
        return "HAS_PERSON"

    class MockBase:
        pass

    result = request.w_person(none_callback, person_callback, conf, MockBase())
    assert result == "NO_PERSON"


def test_w_person_with_none_callback_none():
    output_buffer = []

    output_conf = config.OutputConf(
        status=lambda x: None,
        header=lambda x: None,
        body=lambda b: output_buffer.append(b),
        flush=lambda: None
    )

    conf = config.Config(
        output_conf=output_conf,
        env={},
        bname="test"
    )

    def person_callback(c, b, p):
        return "HAS_PERSON"

    class MockBase:
        pass

    result = request.w_person(None, person_callback, conf, MockBase())
    output = ''.join(output_buffer)
    assert "Welcome" in output or "GeneWeb" in output


def test_specify():
    output_buffer = []

    output_conf = config.OutputConf(
        status=lambda x: None,
        header=lambda x: None,
        body=lambda b: output_buffer.append(b),
        flush=lambda: None
    )

    conf = config.Config(output_conf=output_conf)

    request.specify(conf, None, "TestName", [], [], [])
    output = ''.join(output_buffer)
    assert "TestName" in output
    assert "specify" in output


def test_relation_print_not_implemented():
    output_conf = config.OutputConf(
        status=lambda x: None,
        header=lambda x: None,
        body=lambda x: None,
        flush=lambda: None
    )

    conf = config.Config(output_conf=output_conf)

    try:
        request.relation_print(conf, None, None)
        assert False, "Should raise NotImplementedError"
    except NotImplementedError as e:
        assert "RelationDisplay" in str(e)


def test_w_lock_not_implemented():
    output_conf = config.OutputConf(
        status=lambda x: None,
        header=lambda x: None,
        body=lambda x: None,
        flush=lambda: None
    )

    conf = config.Config(output_conf=output_conf)

    def callback(c, b):
        return "SUCCESS"

    try:
        request.w_lock(callback, callback, conf, None)
        assert False, "Should raise NotImplementedError"
    except NotImplementedError as e:
        assert "Lock mechanism" in str(e)


def test_handle_gedcom_upload_with_content_disposition():
    with tempfile.TemporaryDirectory() as tmpdir:
        original_base_dir = secure.base_dir
        secure.set_base_dir(tmpdir)

        try:
            output_buffer = []
            status_list = []

            def capture_status(s):
                status_list.append(s)

            def capture_header(h):
                output_buffer.append(f"HEADER:{h}")

            def capture_body(b):
                output_buffer.append(b)

            output_conf = config.OutputConf(
                status=capture_status,
                header=capture_header,
                body=capture_body,
                flush=lambda: None
            )

            gedcom_data = b'0 HEAD\r\n1 SOUR Test\r\n0 TRLR\r\n'

            conf = config.Config(
                output_conf=output_conf,
                method='POST',
                headers={'content-disposition': 'filename="test.ged"'},
                body_data=gedcom_data
            )

            request.handle_gedcom_upload(conf)

            assert 303 in status_list
            assert any("Location: /" in x for x in output_buffer)

            ged_file = Path(tmpdir) / "test.ged"
            assert ged_file.exists()

        finally:
            secure.set_base_dir(original_base_dir())


def test_handle_gedcom_upload_with_headers():
    with tempfile.TemporaryDirectory() as tmpdir:
        original_base_dir = secure.base_dir
        secure.set_base_dir(tmpdir)

        try:
            output_buffer = []
            status_list = []

            def capture_status(s):
                status_list.append(s)

            def capture_header(h):
                output_buffer.append(f"HEADER:{h}")

            def capture_body(b):
                output_buffer.append(b)

            output_conf = config.OutputConf(
                status=capture_status,
                header=capture_header,
                body=capture_body,
                flush=lambda: None
            )

            gedcom_data = b'Content-Disposition: form-data\r\n\r\n0 HEAD\r\n1 SOUR Test\r\n0 TRLR\r\n--boundary--'

            conf = config.Config(
                output_conf=output_conf,
                method='POST',
                headers={'content-disposition': 'filename="family.ged"'},
                body_data=gedcom_data
            )

            request.handle_gedcom_upload(conf)

            assert 303 in status_list

            ged_file = Path(tmpdir) / "family.ged"
            assert ged_file.exists()

        finally:
            secure.set_base_dir(original_base_dir())


def test_handle_gedcom_upload_multipart():
    with tempfile.TemporaryDirectory() as tmpdir:
        original_base_dir = secure.base_dir
        secure.set_base_dir(tmpdir)

        try:
            output_buffer = []
            status_list = []

            def capture_status(s):
                status_list.append(s)

            output_conf = config.OutputConf(
                status=capture_status,
                header=lambda h: output_buffer.append(f"HEADER:{h}"),
                body=lambda b: output_buffer.append(b),
                flush=lambda: None
            )

            boundary = b'----WebKitFormBoundary7MA4YWxkTrZu0gW'
            gedcom_content = b'0 HEAD\r\n1 SOUR Test\r\n0 TRLR\r\n'
            body_data = (
                b'------WebKitFormBoundary7MA4YWxkTrZu0gW\r\n'
                b'Content-Disposition: form-data; name="gedcom"; filename="upload.ged"\r\n'
                b'Content-Type: application/octet-stream\r\n\r\n'
                + gedcom_content +
                b'\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW--\r\n'
            )

            conf = config.Config(
                output_conf=output_conf,
                method='POST',
                headers={'content-type': 'multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW'},
                body_data=body_data
            )

            request.handle_gedcom_upload(conf)

            assert 303 in status_list

            ged_file = Path(tmpdir) / "upload.ged"
            assert ged_file.exists()

            with open(ged_file, 'rb') as f:
                content = f.read()
                assert b'0 HEAD' in content
                assert b'0 TRLR' in content

        finally:
            secure.set_base_dir(original_base_dir())


def test_handle_gedcom_upload_no_boundary():
    output_buffer = []
    status_list = []

    def capture_status(s):
        status_list.append(s)

    output_conf = config.OutputConf(
        status=capture_status,
        header=lambda h: output_buffer.append(f"HEADER:{h}"),
        body=lambda b: output_buffer.append(b),
        flush=lambda: None
    )

    conf = config.Config(
        output_conf=output_conf,
        method='POST',
        headers={'content-type': 'multipart/form-data'},
        body_data=b'some data'
    )

    request.handle_gedcom_upload(conf)

    assert 400 in status_list
    assert any("No boundary" in x for x in output_buffer)


def test_handle_gedcom_upload_no_file():
    output_buffer = []
    status_list = []

    def capture_status(s):
        status_list.append(s)

    output_conf = config.OutputConf(
        status=capture_status,
        header=lambda h: output_buffer.append(f"HEADER:{h}"),
        body=lambda b: output_buffer.append(b),
        flush=lambda: None
    )

    boundary = b'----WebKitFormBoundary7MA4YWxkTrZu0gW'
    body_data = (
        b'------WebKitFormBoundary7MA4YWxkTrZu0gW\r\n'
        b'Content-Disposition: form-data; name="other"\r\n\r\n'
        b'some value\r\n'
        b'------WebKitFormBoundary7MA4YWxkTrZu0gW--\r\n'
    )

    conf = config.Config(
        output_conf=output_conf,
        method='POST',
        headers={'content-type': 'multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW'},
        body_data=body_data
    )

    request.handle_gedcom_upload(conf)

    assert 400 in status_list
    assert any("No GEDCOM file" in x for x in output_buffer)


def test_handle_gedcom_upload_invalid_format():
    output_buffer = []
    status_list = []

    def capture_status(s):
        status_list.append(s)

    output_conf = config.OutputConf(
        status=capture_status,
        header=lambda h: output_buffer.append(f"HEADER:{h}"),
        body=lambda b: output_buffer.append(b),
        flush=lambda: None
    )

    conf = config.Config(
        output_conf=output_conf,
        method='POST',
        headers={},
        body_data=b'invalid data'
    )

    request.handle_gedcom_upload(conf)

    assert 400 in status_list
    assert any("Invalid upload format" in x for x in output_buffer)


def test_treat_request_upload():
    with tempfile.TemporaryDirectory() as tmpdir:
        original_base_dir = secure.base_dir
        secure.set_base_dir(tmpdir)

        try:
            output_buffer = []

            output_conf = config.OutputConf(
                status=lambda s: output_buffer.append(f"STATUS:{s}"),
                header=lambda h: output_buffer.append(f"HEADER:{h}"),
                body=lambda b: output_buffer.append(b),
                flush=lambda: None
            )

            gedcom_data = b'0 HEAD\r\n1 SOUR Test\r\n0 TRLR\r\n'

            conf = config.Config(
                output_conf=output_conf,
                method='POST',
                request='?upload=1',
                headers={'content-disposition': 'filename="test.ged"'},
                body_data=gedcom_data
            )

            request.treat_request(conf)

            assert any("STATUS:303" in x for x in output_buffer)

        finally:
            secure.set_base_dir(original_base_dir())


def test_treat_request_robots():
    output_buffer = []

    output_conf = config.OutputConf(
        status=lambda s: None,
        header=lambda h: None,
        body=lambda b: output_buffer.append(b),
        flush=lambda: None
    )

    conf = config.Config(
        output_conf=output_conf,
        command='/robots.txt',
        request='robots.txt'
    )

    request.treat_request(conf)

    output = ''.join(output_buffer)
    assert "User-Agent" in output or "Disallow" in output


def test_treat_request_default():
    output_buffer = []

    output_conf = config.OutputConf(
        status=lambda s: None,
        header=lambda h: None,
        body=lambda b: output_buffer.append(b),
        flush=lambda: None
    )

    conf = config.Config(
        output_conf=output_conf,
        env={}
    )

    request.treat_request(conf)

    output = ''.join(output_buffer)
    assert "GeneWeb" in output


def test_treat_request_with_module_codes():
    test_cases = [
        ('A', 'Ascend'),
        ('D', 'Descend'),
        ('F', 'Family'),
        ('P', 'Incorrect request'),
        ('R', 'Relationship'),
        ('S', 'Search'),
        ('NG', 'Notes'),
        ('SRC', 'Sources'),
        ('CAL', 'Calendar'),
        ('H', 'History'),
        ('LB', 'Lists'),
        ('TT', 'Titles'),
        ('MISC', 'Miscellaneous'),
    ]

    for module_code, expected_text in test_cases:
        output_buffer = []

        output_conf = config.OutputConf(
            status=lambda s: None,
            header=lambda h: None,
            body=lambda b: output_buffer.append(b),
            flush=lambda: None
        )

        conf = config.Config(
            output_conf=output_conf,
            env={"m": module_code}
        )

        request.treat_request(conf)

        output = ''.join(output_buffer)
        assert expected_text in output, f"Expected '{expected_text}' for module code '{module_code}'"


def test_treat_request_unknown_module():
    output_buffer = []
    status_list = []

    output_conf = config.OutputConf(
        status=lambda s: status_list.append(s),
        header=lambda h: None,
        body=lambda b: output_buffer.append(b),
        flush=lambda: None
    )

    conf = config.Config(
        output_conf=output_conf,
        env={"m": "INVALID_MODULE"}
    )

    request.treat_request(conf)

    assert 400 in status_list
    output = ''.join(output_buffer)
    assert "Unknown module" in output


def test_default_person_page_no_bname():
    output_buffer = []

    output_conf = config.OutputConf(
        status=lambda s: None,
        header=lambda h: None,
        body=lambda b: output_buffer.append(b),
        flush=lambda: None
    )

    conf = config.Config(
        output_conf=output_conf,
        bname=None,
        env={}
    )

    request.default_person_page(conf)

    output = ''.join(output_buffer)
    assert "GeneWeb" in output


def test_default_person_page_with_bname_no_person():
    output_buffer = []

    output_conf = config.OutputConf(
        status=lambda s: None,
        header=lambda h: None,
        body=lambda b: output_buffer.append(b),
        flush=lambda: None
    )

    conf = config.Config(
        output_conf=output_conf,
        bname="test",
        env={}
    )

    request.default_person_page(conf)

    output = ''.join(output_buffer)
    assert "GeneWeb" in output or "Database" in output


def test_handle_person_page_no_base():
    output_buffer = []
    status_list = []

    output_conf = config.OutputConf(
        status=lambda s: status_list.append(s),
        header=lambda h: None,
        body=lambda b: output_buffer.append(b),
        flush=lambda: None
    )

    conf = config.Config(
        output_conf=output_conf,
        bname=None,
        env={}
    )

    request.handle_person_page(conf)

    assert 400 in status_list
    output = ''.join(output_buffer)
    assert "No base specified" in output


def test_handle_family_page():
    output_buffer = []

    output_conf = config.OutputConf(
        status=lambda s: None,
        header=lambda h: None,
        body=lambda b: output_buffer.append(b),
        flush=lambda: None
    )

    conf = config.Config(output_conf=output_conf)

    request.handle_family_page(conf)

    output = ''.join(output_buffer)
    assert "Family Page" in output


def test_handle_ascend_page():
    output_buffer = []

    output_conf = config.OutputConf(
        status=lambda s: None,
        header=lambda h: None,
        body=lambda b: output_buffer.append(b),
        flush=lambda: None
    )

    conf = config.Config(output_conf=output_conf)

    request.handle_ascend_page(conf)

    output = ''.join(output_buffer)
    assert "Ascendants" in output


def test_handle_descend_page():
    output_buffer = []

    output_conf = config.OutputConf(
        status=lambda s: None,
        header=lambda h: None,
        body=lambda b: output_buffer.append(b),
        flush=lambda: None
    )

    conf = config.Config(output_conf=output_conf)

    request.handle_descend_page(conf)

    output = ''.join(output_buffer)
    assert "Descendants" in output


def test_handle_relation_page():
    output_buffer = []

    output_conf = config.OutputConf(
        status=lambda s: None,
        header=lambda h: None,
        body=lambda b: output_buffer.append(b),
        flush=lambda: None
    )

    conf = config.Config(output_conf=output_conf)

    request.handle_relation_page(conf)

    output = ''.join(output_buffer)
    assert "Relationship" in output


def test_handle_search_page():
    output_buffer = []

    output_conf = config.OutputConf(
        status=lambda s: None,
        header=lambda h: None,
        body=lambda b: output_buffer.append(b),
        flush=lambda: None
    )

    conf = config.Config(output_conf=output_conf)

    request.handle_search_page(conf)

    output = ''.join(output_buffer)
    assert "Search" in output


def test_handle_notes_page():
    output_buffer = []

    output_conf = config.OutputConf(
        status=lambda s: None,
        header=lambda h: None,
        body=lambda b: output_buffer.append(b),
        flush=lambda: None
    )

    conf = config.Config(output_conf=output_conf)

    request.handle_notes_page(conf)

    output = ''.join(output_buffer)
    assert "Notes" in output


def test_handle_sources_page():
    output_buffer = []

    output_conf = config.OutputConf(
        status=lambda s: None,
        header=lambda h: None,
        body=lambda b: output_buffer.append(b),
        flush=lambda: None
    )

    conf = config.Config(output_conf=output_conf)

    request.handle_sources_page(conf)

    output = ''.join(output_buffer)
    assert "Sources" in output


def test_handle_calendar_page():
    output_buffer = []

    output_conf = config.OutputConf(
        status=lambda s: None,
        header=lambda h: None,
        body=lambda b: output_buffer.append(b),
        flush=lambda: None
    )

    conf = config.Config(output_conf=output_conf)

    request.handle_calendar_page(conf)

    output = ''.join(output_buffer)
    assert "Calendar" in output


def test_handle_history_page():
    output_buffer = []

    output_conf = config.OutputConf(
        status=lambda s: None,
        header=lambda h: None,
        body=lambda b: output_buffer.append(b),
        flush=lambda: None
    )

    conf = config.Config(output_conf=output_conf)

    request.handle_history_page(conf)

    output = ''.join(output_buffer)
    assert "History" in output


def test_handle_list_page():
    output_buffer = []

    output_conf = config.OutputConf(
        status=lambda s: None,
        header=lambda h: None,
        body=lambda b: output_buffer.append(b),
        flush=lambda: None
    )

    conf = config.Config(output_conf=output_conf)

    request.handle_list_page(conf)

    output = ''.join(output_buffer)
    assert "Lists" in output


def test_handle_titles_page():
    output_buffer = []

    output_conf = config.OutputConf(
        status=lambda s: None,
        header=lambda h: None,
        body=lambda b: output_buffer.append(b),
        flush=lambda: None
    )

    conf = config.Config(output_conf=output_conf)

    request.handle_titles_page(conf)

    output = ''.join(output_buffer)
    assert "Titles" in output


def test_handle_misc_page():
    output_buffer = []

    output_conf = config.OutputConf(
        status=lambda s: None,
        header=lambda x: None,
        body=lambda b: output_buffer.append(b),
        flush=lambda: None
    )

    conf = config.Config(output_conf=output_conf)

    request.handle_misc_page(conf)

    output = ''.join(output_buffer)
    assert "Miscellaneous" in output


def test_select_std_eq():
    output_conf = config.OutputConf(
        status=lambda x: None,
        header=lambda x: None,
        body=lambda x: None,
        flush=lambda: None
    )

    conf = config.Config(output_conf=output_conf)

    result = request.select_std_eq(conf, None, [], "test")
    assert isinstance(result, list)
