from dataclasses import dataclass
from typing import Union


@dataclass(frozen=True)
class SourceFile:
    filename: str


@dataclass(frozen=True)
class SourceRaw:
    content: str


Source = Union[SourceFile, SourceRaw]


@dataclass(frozen=True)
class Loc:
    src: Source
    start: int
    stop: int


DUMMY = Loc(src=SourceFile("<dummy>"), start=-1, stop=-1)


def of_positions(src: Source, start: int, stop: int) -> Loc:
    return Loc(src=src, start=start, stop=stop)
