import pytest
from modernProject.lib.config import OutputConf, Config


def test_output_conf_creation():
    status_called = []
    header_called = []
    body_called = []
    flush_called = []

    def status_fn(x):
        status_called.append(x)

    def header_fn(s):
        header_called.append(s)

    def body_fn(s):
        body_called.append(s)

    def flush_fn():
        flush_called.append(True)

    output_conf = OutputConf(
        status=status_fn,
        header=header_fn,
        body=body_fn,
        flush=flush_fn
    )

    assert output_conf.status is status_fn
    assert output_conf.header is header_fn
    assert output_conf.body is body_fn
    assert output_conf.flush is flush_fn


def test_output_conf_functions_callable():
    results = {}

    def status_fn(x):
        results['status'] = x

    def header_fn(s):
        results['header'] = s

    def body_fn(s):
        results['body'] = s

    def flush_fn():
        results['flush'] = True

    output_conf = OutputConf(
        status=status_fn,
        header=header_fn,
        body=body_fn,
        flush=flush_fn
    )

    output_conf.status("test_status")
    output_conf.header("test_header")
    output_conf.body("test_body")
    output_conf.flush()

    assert results['status'] == "test_status"
    assert results['header'] == "test_header"
    assert results['body'] == "test_body"
    assert results['flush'] is True


def test_config_creation():
    def noop_status(x):
        pass

    def noop_header(s):
        pass

    def noop_body(s):
        pass

    def noop_flush():
        pass

    output_conf = OutputConf(
        status=noop_status,
        header=noop_header,
        body=noop_body,
        flush=noop_flush
    )

    config = Config(output_conf=output_conf)

    assert config.output_conf is output_conf
    assert config.output_conf.status is noop_status
    assert config.output_conf.header is noop_header
    assert config.output_conf.body is noop_body
    assert config.output_conf.flush is noop_flush
