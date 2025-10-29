import sys
import os
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from lib import srcfile_display, config, driver


def test_imports():
    assert hasattr(srcfile_display, 'print_welcome')
    assert hasattr(srcfile_display, 'propose_base')
    assert hasattr(srcfile_display, 'list_databases')
    assert hasattr(srcfile_display, 'count')


def test_counter_dataclass():
    counter = srcfile_display.Counter(
        welcome_cnt=10,
        request_cnt=20,
        start_date="01/01/2025",
        wizard_cnt=5,
        friend_cnt=3,
        normal_cnt=2
    )
    assert counter.welcome_cnt == 10
    assert counter.request_cnt == 20
    assert counter.start_date == "01/01/2025"
    assert counter.wizard_cnt == 5
    assert counter.friend_cnt == 3
    assert counter.normal_cnt == 2


def test_get_date():
    output_conf = config.OutputConf(
        status=lambda x: None,
        header=lambda x: None,
        body=lambda x: None,
        flush=lambda: None
    )

    conf = config.Config(output_conf=output_conf)

    date_str = srcfile_display.get_date(conf)
    assert isinstance(date_str, str)
    assert len(date_str) == 10
    assert date_str.count('/') == 2


def test_list_databases_empty_directory():
    with tempfile.TemporaryDirectory() as tmpdir:
        databases = srcfile_display.list_databases(tmpdir)
        assert databases == []


def test_list_databases_with_gwb_files():
    with tempfile.TemporaryDirectory() as tmpdir:
        (Path(tmpdir) / "kennedy.gwb").mkdir()
        (Path(tmpdir) / "sample.gwb").mkdir()
        (Path(tmpdir) / "test.gwb").mkdir()
        (Path(tmpdir) / "notadb.txt").touch()

        databases = srcfile_display.list_databases(tmpdir)
        assert len(databases) == 3
        assert "kennedy" in databases
        assert "sample" in databases
        assert "test" in databases
        assert "notadb" not in databases


def test_list_databases_sorted():
    with tempfile.TemporaryDirectory() as tmpdir:
        (Path(tmpdir) / "zebra.gwb").mkdir()
        (Path(tmpdir) / "alpha.gwb").mkdir()
        (Path(tmpdir) / "beta.gwb").mkdir()

        databases = srcfile_display.list_databases(tmpdir)
        assert databases == ["alpha", "beta", "zebra"]


def test_list_databases_invalid_directory():
    databases = srcfile_display.list_databases("/nonexistent/path")
    assert databases == []


def test_propose_base_output():
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

    srcfile_display.propose_base(conf)

    output = ''.join(output_buffer)
    assert "STATUS:200" in output
    assert "Content-type: text/html" in output
    assert "GeneWeb Database Selection" in output
    assert "Enter Database Name:" in output
    assert "Open Database" in output
    assert '<input type=\'text\' name=\'b\'' in output


def test_propose_base_with_databases(monkeypatch):
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

    def mock_list_databases(base_dir):
        return ["kennedy", "sample", "test"]

    monkeypatch.setattr(srcfile_display, 'list_databases', mock_list_databases)

    srcfile_display.propose_base(conf)

    output = ''.join(output_buffer)
    assert "kennedy" in output
    assert "sample" in output
    assert "test" in output
    assert "?b=kennedy" in output
    assert "?b=sample" in output
    assert "?b=test" in output


def test_print_welcome_fallback():
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
        bname="test_database"
    )

    base = None

    srcfile_display.print_welcome(conf, base)

    output = ''.join(output_buffer)
    assert "Welcome to GeneWeb" in output
    assert "test_database" in output
    assert "Total persons: 0" in output


def test_count_returns_counter():
    output_conf = config.OutputConf(
        status=lambda x: None,
        header=lambda x: None,
        body=lambda x: None,
        flush=lambda: None
    )

    conf = config.Config(output_conf=output_conf)

    counter = srcfile_display.count(conf)
    assert isinstance(counter, srcfile_display.Counter)
    assert counter.welcome_cnt == 0
    assert counter.request_cnt == 0
    assert isinstance(counter.start_date, str)
    assert counter.wizard_cnt == 0
    assert counter.friend_cnt == 0
    assert counter.normal_cnt == 0


def test_skeleton_functions_exist():
    assert hasattr(srcfile_display, 'write_counter')
    assert hasattr(srcfile_display, 'incr_welcome_counter')
    assert hasattr(srcfile_display, 'incr_request_counter')
    assert hasattr(srcfile_display, 'lang_file_name')
    assert hasattr(srcfile_display, 'any_lang_file_name')
    assert hasattr(srcfile_display, 'source_file_name')
    assert hasattr(srcfile_display, 'print_source')
    assert hasattr(srcfile_display, 'print_file')
    assert hasattr(srcfile_display, 'copy_from_stream')


def test_skeleton_functions_raise_not_implemented():
    output_conf = config.OutputConf(
        status=lambda x: None,
        header=lambda x: None,
        body=lambda x: None,
        flush=lambda: None
    )

    conf = config.Config(output_conf=output_conf)
    counter = srcfile_display.Counter(0, 0, "", 0, 0, 0)

    try:
        srcfile_display.write_counter(conf, counter)
        assert False, "Should raise NotImplementedError"
    except NotImplementedError:
        pass

    try:
        srcfile_display.incr_welcome_counter(conf)
        assert False, "Should raise NotImplementedError"
    except NotImplementedError:
        pass

    try:
        srcfile_display.incr_request_counter(conf)
        assert False, "Should raise NotImplementedError"
    except NotImplementedError:
        pass

    try:
        srcfile_display.lang_file_name(conf, "test")
        assert False, "Should raise NotImplementedError"
    except NotImplementedError:
        pass


def test_list_databases_handles_permissions():
    with tempfile.TemporaryDirectory() as tmpdir:
        (Path(tmpdir) / "readable.gwb").mkdir()

        databases = srcfile_display.list_databases(tmpdir)
        assert "readable" in databases


def test_propose_base_html_structure():
    output_buffer = []

    output_conf = config.OutputConf(
        status=lambda x: None,
        header=lambda x: None,
        body=lambda b: output_buffer.append(b),
        flush=lambda: None
    )

    conf = config.Config(output_conf=output_conf)

    srcfile_display.propose_base(conf)

    output = ''.join(output_buffer)
    assert "<html>" in output
    assert "</html>" in output
    assert "<head>" in output
    assert "</head>" in output
    assert "<body>" in output
    assert "</body>" in output
    assert "<h1>" in output
    assert "</h1>" in output
    assert "<form" in output
    assert "</form>" in output


def test_print_welcome_with_bname():
    output_buffer = []

    output_conf = config.OutputConf(
        status=lambda x: None,
        header=lambda x: None,
        body=lambda b: output_buffer.append(b),
        flush=lambda: None
    )

    conf = config.Config(
        output_conf=output_conf,
        bname="mygenealogy"
    )

    srcfile_display.print_welcome(conf, None)

    output = ''.join(output_buffer)
    assert "mygenealogy" in output


def test_get_date_formatting():
    output_conf = config.OutputConf(
        status=lambda x: None,
        header=lambda x: None,
        body=lambda x: None,
        flush=lambda: None
    )

    conf = config.Config(output_conf=output_conf)

    date_str = srcfile_display.get_date(conf)
    assert isinstance(date_str, str)
    assert len(date_str) == 10
    parts = date_str.split('/')
    assert len(parts) == 3
    assert all(part.isdigit() for part in parts)


def test_convert_ged_if_needed_no_files():
    with tempfile.TemporaryDirectory() as tmpdir:
        result = srcfile_display.convert_ged_if_needed(tmpdir, "nonexistent")
        assert result == False


def test_convert_ged_if_needed_gwb_exists():
    with tempfile.TemporaryDirectory() as tmpdir:
        (Path(tmpdir) / "test.gwb").mkdir()
        result = srcfile_display.convert_ged_if_needed(tmpdir, "test")
        assert result == True


def test_convert_ged_if_needed_with_ged():
    with tempfile.TemporaryDirectory() as tmpdir:
        ged_file = Path(tmpdir) / "test.ged"
        ged_file.write_text("0 HEAD\n1 SOUR Test\n0 TRLR\n")
        result = srcfile_display.convert_ged_if_needed(tmpdir, "test")
        assert isinstance(result, bool)


def test_list_databases_with_ged():
    with tempfile.TemporaryDirectory() as tmpdir:
        (Path(tmpdir) / "test1.ged").touch()
        (Path(tmpdir) / "test2.ged").touch()
        databases = srcfile_display.list_databases(tmpdir)
        assert "test1" in databases
        assert "test2" in databases


def test_list_databases_mixed():
    with tempfile.TemporaryDirectory() as tmpdir:
        (Path(tmpdir) / "db1.gwb").mkdir()
        (Path(tmpdir) / "db2.ged").touch()
        databases = srcfile_display.list_databases(tmpdir)
        assert "db1" in databases
        assert "db2" in databases
        assert len(databases) == 2


def test_print_welcome_with_people():
    output_buffer = []

    output_conf = config.OutputConf(
        status=lambda x: None,
        header=lambda x: None,
        body=lambda b: output_buffer.append(b),
        flush=lambda: None
    )

    conf = config.Config(
        output_conf=output_conf,
        bname="testbase"
    )

    class MockPerson:
        first_name = b"John"
        surname = b"Doe"

    class MockBase:
        pass

    mock_base = MockBase()

    def mock_nb_of_persons(base):
        return 2

    def mock_poi(base, i):
        return MockPerson()

    def mock_p_first_name(base, p):
        return p.first_name

    def mock_p_surname(base, p):
        return p.surname

    import lib.driver as driver_module
    old_nb = driver_module.nb_of_persons
    old_poi = driver_module.poi
    old_pfn = driver_module.p_first_name
    old_psn = driver_module.p_surname

    try:
        driver_module.nb_of_persons = mock_nb_of_persons
        driver_module.poi = mock_poi
        driver_module.p_first_name = mock_p_first_name
        driver_module.p_surname = mock_p_surname

        srcfile_display.print_welcome(conf, mock_base)

        output = ''.join(output_buffer)
        assert "Welcome to GeneWeb" in output
        assert "testbase" in output
        assert "Total persons: 2" in output
        assert "John Doe" in output

    finally:
        driver_module.nb_of_persons = old_nb
        driver_module.poi = old_poi
        driver_module.p_first_name = old_pfn
        driver_module.p_surname = old_psn


def test_propose_base_upload_form():
    output_buffer = []

    output_conf = config.OutputConf(
        status=lambda x: None,
        header=lambda x: None,
        body=lambda b: output_buffer.append(b),
        flush=lambda: None
    )

    conf = config.Config(output_conf=output_conf)

    srcfile_display.propose_base(conf)

    output = ''.join(output_buffer)
    assert "Upload GEDCOM File:" in output
    assert "multipart/form-data" in output
    assert "name='gedcom'" in output
    assert "type='file'" in output
