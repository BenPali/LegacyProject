from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional, List, TypeVar, Generic, Tuple, Callable, Union, Any, Dict
from lib.adef import Cdate, Date, Calendar, Dmy, Dmy2, Precision, Fix, Couple

T = TypeVar('T')
U = TypeVar('U')
V = TypeVar('V')
W = TypeVar('W')
X = TypeVar('X')
Y = TypeVar('Y')
Z = TypeVar('Z')

class HttpStatus(Enum):
    OK = 200
    MOVED_TEMPORARILY = 302
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    CONFLICT = 409
    INTERNAL_SERVER_ERROR = 500
    SERVICE_UNAVAILABLE = 503

class HttpExn(Exception):
    def __init__(self, status: HttpStatus, message: str):
        self.status = status
        self.message = message
        super().__init__(f"{status.name}: {message}")

class Choice(Generic[T, U]):
    def __init__(self, value: Union[T, U], is_left: bool):
        self.value = value
        self.is_left = is_left

    @staticmethod
    def left(value: T) -> 'Choice[T, U]':
        return Choice(value, True)

    @staticmethod
    def right(value: U) -> 'Choice[T, U]':
        return Choice(value, False)

class RelationKind(Enum):
    MARRIED = auto()
    NOT_MARRIED = auto()
    ENGAGED = auto()
    NO_SEXES_CHECK_NOT_MARRIED = auto()
    NO_MENTION = auto()
    NO_SEXES_CHECK_MARRIED = auto()
    MARRIAGE_BANN = auto()
    MARRIAGE_CONTRACT = auto()
    MARRIAGE_LICENSE = auto()
    PACS = auto()
    RESIDENCE = auto()

@dataclass
class Divorce:
    pass

@dataclass
class NotDivorced(Divorce):
    pass

@dataclass
class DivorceWithDate(Divorce):
    date: Cdate

@dataclass
class SeparatedOld(Divorce):
    pass

@dataclass
class NotSeparated(Divorce):
    pass

@dataclass
class Separated(Divorce):
    date: Cdate

class DeathReason(Enum):
    KILLED = auto()
    MURDERED = auto()
    EXECUTED = auto()
    DISAPPEARED = auto()
    UNSPECIFIED = auto()

@dataclass
class Death:
    pass

@dataclass
class NotDead(Death):
    pass

@dataclass
class DeathWithReason(Death):
    reason: DeathReason
    date: Cdate

@dataclass
class DeadYoung(Death):
    pass

@dataclass
class DeadDontKnowWhen(Death):
    pass

@dataclass
class DontKnowIfDead(Death):
    pass

@dataclass
class OfCourseDead(Death):
    pass

@dataclass
class Burial:
    pass

@dataclass
class UnknownBurial(Burial):
    pass

@dataclass
class Buried(Burial):
    date: Cdate

@dataclass
class Cremated(Burial):
    date: Cdate

class Access(Enum):
    IF_TITLES = auto()
    PUBLIC = auto()
    SEMI_PUBLIC = auto()
    PRIVATE = auto()

@dataclass
class GenTitleName(Generic[T]):
    pass

@dataclass
class Tmain(GenTitleName[T]):
    pass

@dataclass
class Tname(GenTitleName[T]):
    name: T

@dataclass
class Tnone(GenTitleName[T]):
    pass

@dataclass
class GenTitle(Generic[T]):
    t_name: GenTitleName[T]
    t_ident: T
    t_place: T
    t_date_start: Cdate
    t_date_end: Cdate
    t_nth: int

class WitnessKind(Enum):
    WITNESS = auto()
    WITNESS_GOD_PARENT = auto()
    WITNESS_CIVIL_OFFICER = auto()
    WITNESS_RELIGIOUS_OFFICER = auto()
    WITNESS_INFORMANT = auto()
    WITNESS_ATTENDING = auto()
    WITNESS_MENTIONED = auto()
    WITNESS_OTHER = auto()

class GenPersEventName(Enum):
    EPERS_BIRTH = auto()
    EPERS_BAPTISM = auto()
    EPERS_DEATH = auto()
    EPERS_BURIAL = auto()
    EPERS_CREMATION = auto()
    EPERS_ACCOMPLISHMENT = auto()
    EPERS_ACQUISITION = auto()
    EPERS_ADHESION = auto()
    EPERS_BAPTISM_LDS = auto()
    EPERS_BAR_MITZVAH = auto()
    EPERS_BAT_MITZVAH = auto()
    EPERS_BENEDICTION = auto()
    EPERS_CHANGE_NAME = auto()
    EPERS_CIRCUMCISION = auto()
    EPERS_CONFIRMATION = auto()
    EPERS_CONFIRMATION_LDS = auto()
    EPERS_DECORATION = auto()
    EPERS_DEMOBILISATION_MILITAIRE = auto()
    EPERS_DIPLOMA = auto()
    EPERS_DISTINCTION = auto()
    EPERS_DOTATION = auto()
    EPERS_DOTATION_LDS = auto()
    EPERS_EDUCATION = auto()
    EPERS_ELECTION = auto()
    EPERS_EMIGRATION = auto()
    EPERS_EXCOMMUNICATION = auto()
    EPERS_FAMILY_LINK_LDS = auto()
    EPERS_FIRST_COMMUNION = auto()
    EPERS_FUNERAL = auto()
    EPERS_GRADUATE = auto()
    EPERS_HOSPITALISATION = auto()
    EPERS_ILLNESS = auto()
    EPERS_IMMIGRATION = auto()
    EPERS_LISTE_PASSENGER = auto()
    EPERS_MILITARY_DISTINCTION = auto()
    EPERS_MILITARY_PROMOTION = auto()
    EPERS_MILITARY_SERVICE = auto()
    EPERS_MOBILISATION_MILITAIRE = auto()
    EPERS_NATURALISATION = auto()
    EPERS_OCCUPATION = auto()
    EPERS_ORDINATION = auto()
    EPERS_PROPERTY = auto()
    EPERS_RECENSEMENT = auto()
    EPERS_RESIDENCE = auto()
    EPERS_RETIRED = auto()
    EPERS_SCELLENT_CHILD_LDS = auto()
    EPERS_SCELLENT_PARENT_LDS = auto()
    EPERS_SCELLENT_SPOUSE_LDS = auto()
    EPERS_VENTE_BIEN = auto()
    EPERS_WILL = auto()

@dataclass
class EpersName(Generic[T]):
    name: T

@dataclass
class GenPersEvent(Generic[T, U]):
    epers_name: Union[GenPersEventName, EpersName[U]]
    epers_date: Cdate
    epers_place: U
    epers_reason: U
    epers_note: U
    epers_src: U
    epers_witnesses: List[Tuple[T, WitnessKind]]

class GenFamEventName(Enum):
    EFAM_MARRIAGE = auto()
    EFAM_NO_MARRIAGE = auto()
    EFAM_NO_MENTION = auto()
    EFAM_ENGAGE = auto()
    EFAM_DIVORCE = auto()
    EFAM_SEPARATED = auto()
    EFAM_ANNULATION = auto()
    EFAM_MARRIAGE_BANN = auto()
    EFAM_MARRIAGE_CONTRACT = auto()
    EFAM_MARRIAGE_LICENSE = auto()
    EFAM_PACS = auto()
    EFAM_RESIDENCE = auto()

@dataclass
class EfamName(Generic[T]):
    name: T

@dataclass
class GenFamEvent(Generic[T, U]):
    efam_name: Union[GenFamEventName, EfamName[U]]
    efam_date: Cdate
    efam_place: U
    efam_reason: U
    efam_note: U
    efam_src: U
    efam_witnesses: List[Tuple[T, WitnessKind]]

class RelationType(Enum):
    ADOPTION = auto()
    RECOGNITION = auto()
    CANDIDATE_PARENT = auto()
    GOD_PARENT = auto()
    FOSTER_PARENT = auto()

@dataclass
class GenRelation(Generic[T, U]):
    r_type: RelationType
    r_fath: Optional[T]
    r_moth: Optional[T]
    r_sources: U

class Sex(Enum):
    MALE = auto()
    FEMALE = auto()
    NEUTER = auto()

@dataclass
class Place:
    other: str
    town: str
    township: str
    canton: str
    district: str
    county: str
    region: str
    country: str

@dataclass
class GenPerson(Generic[T, U, V]):
    first_name: V
    surname: V
    occ: int
    image: V
    public_name: V
    qualifiers: List[V]
    aliases: List[V]
    first_names_aliases: List[V]
    surnames_aliases: List[V]
    titles: List[GenTitle[V]]
    rparents: List[GenRelation[U, V]]
    related: List[U]
    occupation: V
    sex: Sex
    access: Access
    birth: Cdate
    birth_place: V
    birth_note: V
    birth_src: V
    baptism: Cdate
    baptism_place: V
    baptism_note: V
    baptism_src: V
    death: Death
    death_place: V
    death_note: V
    death_src: V
    burial: Burial
    burial_place: V
    burial_note: V
    burial_src: V
    pevents: List[GenPersEvent[U, V]]
    notes: V
    psources: V
    key_index: T

@dataclass
class GenAscend(Generic[T]):
    parents: Optional[T]
    consang: Fix

@dataclass
class GenUnion(Generic[T]):
    family: List[T]

@dataclass
class GenDescend(Generic[T]):
    children: List[T]

@dataclass
class GenFamily(Generic[T, U, V]):
    marriage: Cdate
    marriage_place: V
    marriage_note: V
    marriage_src: V
    witnesses: List[T]
    relation: RelationKind
    divorce: Divorce
    fevents: List[GenFamEvent[T, V]]
    comment: V
    origin_file: V
    fsources: V
    fam_index: U

GenCouple = Couple

@dataclass
class PersonError(Generic[T]):
    pass

@dataclass
class AlreadyDefined(PersonError[T]):
    person: T

@dataclass
class OwnAncestor(PersonError[T]):
    person: T

@dataclass
class BadSexOfMarriedPerson(PersonError[T]):
    person: T

class RnMode(Enum):
    RN_ALL = auto()
    RN_1LN = auto()
    RN_DEG = auto()

@dataclass
class BaseNotes:
    nread: Callable[[str, RnMode], str]
    norigin_file: str
    efiles: Callable[[], List[str]]

@dataclass
class BaseWarning(Generic[T, U, V, W, X, Y, Z]):
    pass

@dataclass
class BigAgeBetweenSpouses(BaseWarning[T, U, V, W, X, Y, Z]):
    person1: U
    person2: U
    age_diff: Dmy

@dataclass
class BirthAfterDeath(BaseWarning[T, U, V, W, X, Y, Z]):
    person: U

@dataclass
class IncoherentSex(BaseWarning[T, U, V, W, X, Y, Z]):
    person: U
    count1: int
    count2: int

@dataclass
class ChangedOrderOfChildren(BaseWarning[T, U, V, W, X, Y, Z]):
    family: V
    descend: W
    old_order: List[T]
    new_order: List[T]

@dataclass
class ChangedOrderOfMarriages(BaseWarning[T, U, V, W, X, Y, Z]):
    person: U
    old_order: List[V]
    new_order: List[V]

@dataclass
class ChangedOrderOfFamilyEvents(BaseWarning[T, U, V, W, X, Y, Z]):
    family: V
    old_order: List[Z]
    new_order: List[Z]

@dataclass
class ChangedOrderOfPersonEvents(BaseWarning[T, U, V, W, X, Y, Z]):
    person: U
    old_order: List[Y]
    new_order: List[Y]

@dataclass
class ChildrenNotInOrder(BaseWarning[T, U, V, W, X, Y, Z]):
    family: V
    descend: W
    child1: U
    child2: U

@dataclass
class CloseChildren(BaseWarning[T, U, V, W, X, Y, Z]):
    family: V
    child1: U
    child2: U

@dataclass
class DeadOld(BaseWarning[T, U, V, W, X, Y, Z]):
    person: U
    death_date: Dmy

@dataclass
class DeadTooEarlyToBeFather(BaseWarning[T, U, V, W, X, Y, Z]):
    father: U
    child: U

@dataclass
class DistantChildren(BaseWarning[T, U, V, W, X, Y, Z]):
    family: V
    child1: U
    child2: U

@dataclass
class FEventOrder(BaseWarning[T, U, V, W, X, Y, Z]):
    person: U
    event1: Z
    event2: Z

@dataclass
class FWitnessEventAfterDeath(BaseWarning[T, U, V, W, X, Y, Z]):
    person: U
    event: Z
    family: V

@dataclass
class FWitnessEventBeforeBirth(BaseWarning[T, U, V, W, X, Y, Z]):
    person: U
    event: Z
    family: V

@dataclass
class IncoherentAncestorDate(BaseWarning[T, U, V, W, X, Y, Z]):
    ancestor: U
    descendant: U

@dataclass
class MarriageDateAfterDeath(BaseWarning[T, U, V, W, X, Y, Z]):
    person: U

@dataclass
class MarriageDateBeforeBirth(BaseWarning[T, U, V, W, X, Y, Z]):
    person: U

@dataclass
class MotherDeadBeforeChildBirth(BaseWarning[T, U, V, W, X, Y, Z]):
    mother: U
    child: U

@dataclass
class ParentBornAfterChild(BaseWarning[T, U, V, W, X, Y, Z]):
    parent: U
    child: U

@dataclass
class ParentTooOld(BaseWarning[T, U, V, W, X, Y, Z]):
    parent: U
    birth_date: Dmy
    child: U

@dataclass
class ParentTooYoung(BaseWarning[T, U, V, W, X, Y, Z]):
    parent: U
    birth_date: Dmy
    child: U

@dataclass
class PEventOrder(BaseWarning[T, U, V, W, X, Y, Z]):
    person: U
    event1: Y
    event2: Y

@dataclass
class PossibleDuplicateFam(BaseWarning[T, U, V, W, X, Y, Z]):
    family1: V
    family2: V

@dataclass
class PossibleDuplicateFamHomonymous(BaseWarning[T, U, V, W, X, Y, Z]):
    family1: V
    family2: V
    person: U

@dataclass
class PWitnessEventAfterDeath(BaseWarning[T, U, V, W, X, Y, Z]):
    witness: U
    event: Y
    person: U

@dataclass
class PWitnessEventBeforeBirth(BaseWarning[T, U, V, W, X, Y, Z]):
    witness: U
    event: Y
    person: U

@dataclass
class TitleDatesError(BaseWarning[T, U, V, W, X, Y, Z]):
    person: U
    title: X

@dataclass
class UndefinedSex(BaseWarning[T, U, V, W, X, Y, Z]):
    person: U

@dataclass
class YoungForMarriage(BaseWarning[T, U, V, W, X, Y, Z]):
    person: U
    marriage_date: Dmy
    family: V

@dataclass
class OldForMarriage(BaseWarning[T, U, V, W, X, Y, Z]):
    person: U
    marriage_date: Dmy
    family: V

class MissingSources:
    pass

@dataclass
class BaseChanged(Generic[T, U, V, W]):
    pass

@dataclass
class UAddPerson(BaseChanged[T, U, V, W]):
    person: GenPerson[T, U, W]

@dataclass
class UModifyPerson(BaseChanged[T, U, V, W]):
    old_person: GenPerson[T, U, W]
    new_person: GenPerson[T, U, W]

@dataclass
class UDeletePerson(BaseChanged[T, U, V, W]):
    person: GenPerson[T, U, W]

@dataclass
class UMergePerson(BaseChanged[T, U, V, W]):
    person1: GenPerson[T, U, W]
    person2: GenPerson[T, U, W]
    result: GenPerson[T, U, W]

@dataclass
class USendImage(BaseChanged[T, U, V, W]):
    person: GenPerson[T, U, W]

@dataclass
class UDeleteImage(BaseChanged[T, U, V, W]):
    person: GenPerson[T, U, W]

@dataclass
class UAddFamily(BaseChanged[T, U, V, W]):
    person: GenPerson[T, U, W]
    family: GenFamily[U, V, W]

@dataclass
class UModifyFamily(BaseChanged[T, U, V, W]):
    person: GenPerson[T, U, W]
    old_family: GenFamily[U, V, W]
    new_family: GenFamily[U, V, W]

@dataclass
class UDeleteFamily(BaseChanged[T, U, V, W]):
    person: GenPerson[T, U, W]
    family: GenFamily[U, V, W]

@dataclass
class UInvertFamily(BaseChanged[T, U, V, W]):
    person: GenPerson[T, U, W]
    family_index: V

@dataclass
class UMergeFamily(BaseChanged[T, U, V, W]):
    person: GenPerson[T, U, W]
    family1: GenFamily[U, V, W]
    family2: GenFamily[U, V, W]
    result: GenFamily[U, V, W]

@dataclass
class UChangeChildrenName(BaseChanged[T, U, V, W]):
    person: GenPerson[T, U, W]
    changes: List[Tuple[Tuple[str, str, int, U], Tuple[str, str, int, U]]]

@dataclass
class UAddParent(BaseChanged[T, U, V, W]):
    person: GenPerson[T, U, W]
    family: GenFamily[U, V, W]

@dataclass
class UKillAncestors(BaseChanged[T, U, V, W]):
    person: GenPerson[T, U, W]

@dataclass
class UMulti(BaseChanged[T, U, V, W]):
    person1: GenPerson[T, U, W]
    person2: GenPerson[T, U, W]
    flag: bool

@dataclass
class UNotes(BaseChanged[T, U, V, W]):
    index: Optional[int]
    text: str

class NLDB:
    @dataclass
    class Page(Generic[T, U]):
        pass

    @dataclass
    class PgInd(Page[T, U]):
        person: T

    @dataclass
    class PgFam(Page[T, U]):
        family: U

    @dataclass
    class PgNotes(Page[T, U]):
        pass

    @dataclass
    class PgMisc(Page[T, U]):
        name: str

    @dataclass
    class PgWizard(Page[T, U]):
        name: str

    Key = Tuple[str, str, int]

    @dataclass
    class Ind:
        ln_txt: Optional[str]
        ln_pos: int

    @staticmethod
    def equal_key(key1: Tuple[str, str, int], key2: Tuple[str, str, int]) -> bool:
        fn1, sn1, oc1 = key1
        fn2, sn2, oc2 = key2
        return oc1 == oc2 and fn1 == fn2 and sn1 == sn2
