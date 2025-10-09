import pytest
from lib import output, config, adef


class TestOutput:
    def test_status(self):
        calls = []
        out_conf = config.OutputConf(
            status=lambda s: calls.append(('status', s)),
            header=lambda s: None,
            body=lambda s: None,
            flush=lambda: None
        )
        conf = config.Config(output_conf=out_conf)
        output.status(conf, "OK")
        assert calls == [('status', 'OK')]

    def test_header(self):
        calls = []
        out_conf = config.OutputConf(
            status=lambda s: None,
            header=lambda s: calls.append(('header', s)),
            body=lambda s: None,
            flush=lambda: None
        )
        conf = config.Config(output_conf=out_conf)
        output.header(conf, "Title: %s", "Test")
        assert calls == [('header', 'Title: Test')]

    def test_header_no_args(self):
        calls = []
        out_conf = config.OutputConf(
            status=lambda s: None,
            header=lambda s: calls.append(('header', s)),
            body=lambda s: None,
            flush=lambda: None
        )
        conf = config.Config(output_conf=out_conf)
        output.header(conf, "Simple Title")
        assert calls == [('header', 'Simple Title')]

    def test_print_sstring(self):
        calls = []
        out_conf = config.OutputConf(
            status=lambda s: None,
            header=lambda s: None,
            body=lambda s: calls.append(('body', s)),
            flush=lambda: None
        )
        conf = config.Config(output_conf=out_conf)
        output.print_sstring(conf, "Hello")
        assert calls == [('body', 'Hello')]

    def test_print_string_safe(self):
        calls = []
        out_conf = config.OutputConf(
            status=lambda s: None,
            header=lambda s: None,
            body=lambda s: calls.append(('body', s)),
            flush=lambda: None
        )
        conf = config.Config(output_conf=out_conf)
        safe_str = adef.SafeString("Safe text")
        output.print_string(conf, safe_str)
        assert calls == [('body', 'Safe text')]

    def test_print_string_escaped(self):
        calls = []
        out_conf = config.OutputConf(
            status=lambda s: None,
            header=lambda s: None,
            body=lambda s: calls.append(('body', s)),
            flush=lambda: None
        )
        conf = config.Config(output_conf=out_conf)
        escaped_str = adef.EscapedString("Escaped &lt;text&gt;")
        output.print_string(conf, escaped_str)
        assert calls == [('body', 'Escaped &lt;text&gt;')]

    def test_printf(self):
        calls = []
        out_conf = config.OutputConf(
            status=lambda s: None,
            header=lambda s: None,
            body=lambda s: calls.append(('body', s)),
            flush=lambda: None
        )
        conf = config.Config(output_conf=out_conf)
        output.printf(conf, "Value: %d", 42)
        assert calls == [('body', 'Value: 42')]

    def test_printf_no_args(self):
        calls = []
        out_conf = config.OutputConf(
            status=lambda s: None,
            header=lambda s: None,
            body=lambda s: calls.append(('body', s)),
            flush=lambda: None
        )
        conf = config.Config(output_conf=out_conf)
        output.printf(conf, "Plain text")
        assert calls == [('body', 'Plain text')]

    def test_flush(self):
        calls = []
        out_conf = config.OutputConf(
            status=lambda s: None,
            header=lambda s: None,
            body=lambda s: None,
            flush=lambda: calls.append('flush')
        )
        conf = config.Config(output_conf=out_conf)
        output.flush(conf)
        assert calls == ['flush']
