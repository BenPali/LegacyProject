from dataclasses import dataclass
from typing import Callable, Any


@dataclass
class OutputConf:
    status: Callable[[Any], None]
    header: Callable[[str], None]
    body: Callable[[str], None]
    flush: Callable[[], None]


@dataclass
class Config:
    output_conf: OutputConf
