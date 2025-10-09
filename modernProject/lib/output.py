from typing import Any
from lib.config import Config
from lib.adef import SafeString, EscapedString, EncodedString


def status(conf: Config, s: Any) -> None:
    conf.output_conf.status(s)


def header(conf: Config, fmt: str, *args) -> None:
    conf.output_conf.header(fmt % args if args else fmt)


def print_sstring(conf: Config, s: str) -> None:
    conf.output_conf.body(s)


def print_string(conf: Config, s: SafeString | EscapedString | EncodedString) -> None:
    conf.output_conf.body(str(s))


def printf(conf: Config, fmt: str, *args) -> None:
    conf.output_conf.body(fmt % args if args else fmt)


def flush(conf: Config) -> None:
    conf.output_conf.flush()
