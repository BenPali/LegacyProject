from dataclasses import dataclass
from enum import Enum, auto
from typing import Callable, List, Optional, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from lib.gwdef import GenPerson, GenFamily
    from lib.adef import Couple

    DskPerson = GenPerson[int, int, int]
    DskFamily = GenFamily[int, int, int]
else:
    DskPerson = Any
    DskAscend = Any
    DskUnion = Any
    DskFamily = Any
    DskCouple = Any
    DskDescend = Any
    DskTitle = Any


@dataclass
class RecordAccess:
    load_array: Callable[[], None]
    get: Callable[[int], Any]
    get_nopending: Callable[[int], Any]
    len: int
    output_array: Callable[[Any], None]
    clear_array: Callable[[], None]


@dataclass
class StringPersonIndex:
    find: Callable[[int], List[int]]
    cursor: Callable[[str], int]
    next: Callable[[int], int]


@dataclass
class VisibleRecordAccess:
    v_write: Callable[[], None]
    v_get: Callable[[Callable[[DskPerson], bool], int], bool]


class Perm(Enum):
    RDONLY = auto()
    RDRW = auto()


@dataclass
class BaseData:
    persons: RecordAccess
    ascends: RecordAccess
    unions: RecordAccess
    visible: VisibleRecordAccess
    families: RecordAccess
    couples: RecordAccess
    descends: RecordAccess
    strings: RecordAccess
    particles_txt: List[str]
    particles: Any
    bnotes: Any
    bdir: str
    perm: Perm


@dataclass
class BaseFunc:
    person_of_key: Callable[[str, str, int], Optional[int]]
    persons_of_name: Callable[[str], List[int]]
    strings_of_sname: Callable[[str], List[int]]
    strings_of_fname: Callable[[str], List[int]]
    persons_of_surname: StringPersonIndex
    persons_of_first_name: StringPersonIndex
    patch_person: Callable[[int, DskPerson], None]
    patch_ascend: Callable[[int, DskAscend], None]
    patch_union: Callable[[int, DskUnion], None]
    patch_family: Callable[[int, DskFamily], None]
    patch_couple: Callable[[int, DskCouple], None]
    patch_descend: Callable[[int, DskDescend], None]
    patch_name: Callable[[str, int], None]
    insert_string: Callable[[str], int]
    commit_patches: Callable[[], None]
    commit_notes: Callable[[str, str], None]
    commit_wiznotes: Callable[[str, str], None]
    nb_of_real_persons: Callable[[], int]
    iper_exists: Callable[[int], bool]
    ifam_exists: Callable[[int], bool]


class BaseVersion(Enum):
    GNWB0020 = auto()
    GNWB0021 = auto()
    GNWB0022 = auto()
    GNWB0023 = auto()
    GNWB0024 = auto()


@dataclass
class DskBase:
    data: BaseData
    func: BaseFunc
    version: BaseVersion
