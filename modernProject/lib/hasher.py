import hashlib
from typing import Callable, Optional, List, Tuple, Any, TYPE_CHECKING
from lib import adef, gwdef

if TYPE_CHECKING:
    from hashlib import _Hash as HashContext
else:
    HashContext = Any

Feeder = Callable[[Any, HashContext], HashContext]
Hasher = Callable[[Any, Optional[str]], str]

def create_context() -> HashContext:
    return hashlib.sha256()

def feed_string(ctx: HashContext, value: str) -> HashContext:
    ctx.update(value.encode('utf-8'))
    return ctx

def feed_int(ctx: HashContext, value: int) -> HashContext:
    return feed_string(ctx, str(value))

def feed_bool(ctx: HashContext, value: bool) -> HashContext:
    return feed_string(ctx, "true" if value else "false")

def finalize_hash(ctx: HashContext) -> str:
    return ctx.hexdigest()

def compose(first_feeder: Feeder, second_feeder: Feeder) -> Feeder:
    def combined_feeder(value: Any, ctx: HashContext) -> HashContext:
        ctx = second_feeder(value, ctx)
        return first_feeder(value, ctx)
    return combined_feeder

def feeder_to_hasher(feeder: Feeder) -> Hasher:
    def hash_function(value: Any, salt: Optional[str] = None) -> str:
        ctx = create_context()
        ctx = feeder(value, ctx)
        if salt is not None:
            ctx = feed_string(ctx, salt)
        return finalize_hash(ctx)
    return hash_function

def string_feeder(value: str, ctx: HashContext) -> HashContext:
    return feed_string(ctx, value)

def int_feeder(value: int, ctx: HashContext) -> HashContext:
    return feed_int(ctx, value)

def bool_feeder(value: bool, ctx: HashContext) -> HashContext:
    return feed_bool(ctx, value)

def list_feeder(item_feeder: Feeder):
    def feed_list(items: List, ctx: HashContext) -> HashContext:
        for item in items:
            ctx = item_feeder(item, ctx)
        return ctx
    return feed_list

def array_feeder(item_feeder: Feeder):
    return list_feeder(item_feeder)

def pair_feeder(first_feeder: Feeder, second_feeder: Feeder):
    def feed_pair(pair: Tuple, ctx: HashContext) -> HashContext:
        ctx = first_feeder(pair[0], ctx)
        ctx = second_feeder(pair[1], ctx)
        return ctx
    return feed_pair

def option_feeder(item_feeder: Feeder):
    def feed_option(value: Optional[Any], ctx: HashContext) -> HashContext:
        if value is None:
            return feed_string(ctx, "None")
        ctx = feed_string(ctx, "Some")
        return item_feeder(value, ctx)
    return feed_option

def iper_feeder(value: int, ctx: HashContext) -> HashContext:
    return feed_string(ctx, str(value))

def ifam_feeder(value: int, ctx: HashContext) -> HashContext:
    return feed_string(ctx, str(value))

def istr_feeder(value: int, ctx: HashContext) -> HashContext:
    return feed_string(ctx, str(value))

def dmy2_feeder(value: adef.Dmy2, ctx: HashContext) -> HashContext:
    ctx = feed_int(ctx, value.day2)
    ctx = feed_int(ctx, value.month2)
    ctx = feed_int(ctx, value.year2)
    ctx = feed_int(ctx, value.delta2)
    return ctx

def precision_feeder(value: adef.PrecisionType, ctx: HashContext) -> HashContext:
    if value == adef.Precision.SURE:
        return feed_string(ctx, "Sure")
    elif value == adef.Precision.ABOUT:
        return feed_string(ctx, "about")
    elif value == adef.Precision.MAYBE:
        return feed_string(ctx, "Maybe")
    elif value == adef.Precision.BEFORE:
        return feed_string(ctx, "Before")
    elif value == adef.Precision.AFTER:
        return feed_string(ctx, "After")
    elif isinstance(value, adef.PrecisionOrYear):
        ctx = feed_string(ctx, "OrYear")
        return dmy2_feeder(value.dmy2, ctx)
    elif isinstance(value, adef.PrecisionYearInt):
        ctx = feed_string(ctx, "YearInt")
        return dmy2_feeder(value.dmy2, ctx)
    return ctx

def dmy_feeder(value: adef.Dmy, ctx: HashContext) -> HashContext:
    ctx = feed_int(ctx, value.day)
    ctx = feed_int(ctx, value.month)
    ctx = feed_int(ctx, value.year)
    ctx = precision_feeder(value.prec, ctx)
    ctx = feed_int(ctx, value.delta)
    return ctx

def calendar_feeder(value: adef.Calendar, ctx: HashContext) -> HashContext:
    if value == adef.Calendar.GREGORIAN:
        return feed_string(ctx, "Dgregorian")
    elif value == adef.Calendar.JULIAN:
        return feed_string(ctx, "Djulian")
    elif value == adef.Calendar.FRENCH:
        return feed_string(ctx, "Dfrench")
    elif value == adef.Calendar.HEBREW:
        return feed_string(ctx, "Dhebrew")
    return ctx

def date_feeder(value: adef.Date, ctx: HashContext) -> HashContext:
    if isinstance(value, adef.DateGreg):
        ctx = dmy_feeder(value.dmy, ctx)
        return calendar_feeder(value.calendar, ctx)
    elif isinstance(value, adef.DateText):
        ctx = feed_string(ctx, "Dtext")
        return feed_string(ctx, value.text)
    return ctx

def cdate_feeder(value: adef.Cdate, ctx: HashContext) -> HashContext:
    if isinstance(value, adef.CdateGregorian):
        ctx = feed_string(ctx, "Cgregorian")
        return feed_int(ctx, value.value)
    elif isinstance(value, adef.CdateJulian):
        ctx = feed_string(ctx, "Cjulian")
        return feed_int(ctx, value.value)
    elif isinstance(value, adef.CdateFrench):
        ctx = feed_string(ctx, "Cfrench")
        return feed_int(ctx, value.value)
    elif isinstance(value, adef.CdateHebrew):
        ctx = feed_string(ctx, "Chebrew")
        return feed_int(ctx, value.value)
    elif isinstance(value, adef.CdateText):
        ctx = feed_string(ctx, "Ctext")
        return feed_string(ctx, value.text)
    elif isinstance(value, adef.CdateDate):
        ctx = feed_string(ctx, "Cdate")
        return date_feeder(value.date, ctx)
    else:
        return feed_string(ctx, "Cnone")

def death_reason_feeder(value: gwdef.DeathReason, ctx: HashContext) -> HashContext:
    if value == gwdef.DeathReason.KILLED:
        return feed_string(ctx, "Killed")
    elif value == gwdef.DeathReason.MURDERED:
        return feed_string(ctx, "Murdered")
    elif value == gwdef.DeathReason.EXECUTED:
        return feed_string(ctx, "Executed")
    elif value == gwdef.DeathReason.DISAPPEARED:
        return feed_string(ctx, "Disappeared")
    elif value == gwdef.DeathReason.UNSPECIFIED:
        return feed_string(ctx, "Unspecified")
    return ctx

def death_feeder(value: gwdef.Death, ctx: HashContext) -> HashContext:
    if isinstance(value, gwdef.NotDead):
        return feed_string(ctx, "NotDead")
    elif isinstance(value, gwdef.DeathWithReason):
        ctx = death_reason_feeder(value.reason, ctx)
        return cdate_feeder(value.date, ctx)
    elif isinstance(value, gwdef.DeadYoung):
        return feed_string(ctx, "DeadYoung")
    elif isinstance(value, gwdef.DeadDontKnowWhen):
        return feed_string(ctx, "DeadDontKnowWhen")
    elif isinstance(value, gwdef.DontKnowIfDead):
        return feed_string(ctx, "DontKnowIfDead")
    elif isinstance(value, gwdef.OfCourseDead):
        return feed_string(ctx, "OfCourseDead")
    return ctx

def gen_title_name_feeder(string_feed: Feeder):
    def feed_title_name(value: gwdef.GenTitleName, ctx: HashContext) -> HashContext:
        if isinstance(value, gwdef.Tmain):
            return feed_string(ctx, "Tmain")
        elif isinstance(value, gwdef.Tname):
            ctx = feed_string(ctx, "Tname")
            return string_feed(value.name, ctx)
        elif isinstance(value, gwdef.Tnone):
            return feed_string(ctx, "Tnone")
        return ctx
    return feed_title_name

def gen_title_feeder(string_feed: Feeder):
    def feed_title(title: gwdef.GenTitle, ctx: HashContext) -> HashContext:
        ctx = gen_title_name_feeder(string_feed)(title.t_name, ctx)
        ctx = string_feed(title.t_ident, ctx)
        ctx = string_feed(title.t_place, ctx)
        ctx = cdate_feeder(title.t_date_start, ctx)
        ctx = cdate_feeder(title.t_date_end, ctx)
        ctx = feed_int(ctx, title.t_nth)
        return ctx
    return feed_title

def sex_feeder(value: gwdef.Sex, ctx: HashContext) -> HashContext:
    if value == gwdef.Sex.MALE:
        return feed_string(ctx, "Male")
    elif value == gwdef.Sex.FEMALE:
        return feed_string(ctx, "Female")
    elif value == gwdef.Sex.NEUTER:
        return feed_string(ctx, "Neuter")
    return ctx

def access_feeder(value: gwdef.Access, ctx: HashContext) -> HashContext:
    if value == gwdef.Access.IF_TITLES:
        return feed_string(ctx, "IfTitles")
    elif value == gwdef.Access.PUBLIC:
        return feed_string(ctx, "Public")
    elif value == gwdef.Access.SEMI_PUBLIC:
        return feed_string(ctx, "SemiPublic")
    elif value == gwdef.Access.PRIVATE:
        return feed_string(ctx, "Private")
    return ctx

def relation_type_feeder(value: gwdef.RelationType, ctx: HashContext) -> HashContext:
    if value == gwdef.RelationType.ADOPTION:
        return feed_string(ctx, "Adoption")
    elif value == gwdef.RelationType.RECOGNITION:
        return feed_string(ctx, "Recognition")
    elif value == gwdef.RelationType.CANDIDATE_PARENT:
        return feed_string(ctx, "CandidateParent")
    elif value == gwdef.RelationType.GOD_PARENT:
        return feed_string(ctx, "GodParent")
    elif value == gwdef.RelationType.FOSTER_PARENT:
        return feed_string(ctx, "FosterParent")
    return ctx

def gen_relation_feeder(person_feed: Feeder, string_feed: Feeder):
    def feed_relation(relation: gwdef.GenRelation, ctx: HashContext) -> HashContext:
        ctx = relation_type_feeder(relation.r_type, ctx)
        ctx = option_feeder(person_feed)(relation.r_fath, ctx)
        ctx = option_feeder(person_feed)(relation.r_moth, ctx)
        ctx = string_feed(relation.r_sources, ctx)
        return ctx
    return feed_relation

def burial_feeder(value: gwdef.Burial, ctx: HashContext) -> HashContext:
    if isinstance(value, gwdef.UnknownBurial):
        return feed_string(ctx, "UnknownBurial")
    elif isinstance(value, gwdef.Buried):
        ctx = feed_string(ctx, "Buried")
        return cdate_feeder(value.date, ctx)
    elif isinstance(value, gwdef.Cremated):
        ctx = feed_string(ctx, "Cremated")
        return cdate_feeder(value.date, ctx)
    return ctx

def _convert_enum_to_ocaml_string(enum_name: str) -> str:
    name_parts = enum_name.split('_')
    first_part = name_parts[0].capitalize()
    remaining_parts = ''.join(
        word.capitalize() if word.upper() not in ('LDS', 'PACS') else word.upper()
        for word in name_parts[1:]
    )
    return f"{first_part}_{remaining_parts}"

def gen_pers_event_name_feeder(string_feed: Feeder):
    def feed_person_event_name(event_name, ctx: HashContext) -> HashContext:
        if isinstance(event_name, gwdef.EpersName):
            ctx = feed_string(ctx, "Epers_Name")
            return string_feed(event_name.name, ctx)
        ocaml_format = _convert_enum_to_ocaml_string(event_name.name)
        return feed_string(ctx, ocaml_format)
    return feed_person_event_name

def witness_kind_feeder(witness_kind: gwdef.WitnessKind, ctx: HashContext) -> HashContext:
    witness_kind_to_ocaml = {
        gwdef.WitnessKind.WITNESS: "Witness",
        gwdef.WitnessKind.WITNESS_GOD_PARENT: "Witness_GodParent",
        gwdef.WitnessKind.WITNESS_CIVIL_OFFICER: "Witness_CivilOfficer",
        gwdef.WitnessKind.WITNESS_RELIGIOUS_OFFICER: "Witness_ReligiousOfficer",
        gwdef.WitnessKind.WITNESS_INFORMANT: "Witness_Informant",
        gwdef.WitnessKind.WITNESS_ATTENDING: "Witness_Attending",
        gwdef.WitnessKind.WITNESS_MENTIONED: "Witness_Mentioned",
        gwdef.WitnessKind.WITNESS_OTHER: "Witness_Other",
    }
    ocaml_name = witness_kind_to_ocaml.get(witness_kind, "")
    return feed_string(ctx, ocaml_name)

def gen_pers_event_feeder(person_feed: Feeder, string_feed: Feeder):
    def feed_person_event(person_event: gwdef.GenPersEvent, ctx: HashContext) -> HashContext:
        ctx = gen_pers_event_name_feeder(string_feed)(person_event.epers_name, ctx)
        ctx = cdate_feeder(person_event.epers_date, ctx)
        ctx = string_feed(person_event.epers_place, ctx)
        ctx = string_feed(person_event.epers_reason, ctx)
        ctx = string_feed(person_event.epers_note, ctx)
        ctx = string_feed(person_event.epers_note, ctx)
        ctx = string_feed(person_event.epers_src, ctx)
        ctx = array_feeder(pair_feeder(person_feed, witness_kind_feeder))(person_event.epers_witnesses, ctx)
        return ctx
    return feed_person_event

def gen_person_feeder(iper_feed: Feeder, person_feed: Feeder, string_feed: Feeder):
    def feed_person(person: gwdef.GenPerson, ctx: HashContext) -> HashContext:
        ctx = string_feed(person.first_name, ctx)
        ctx = string_feed(person.surname, ctx)
        ctx = feed_int(ctx, person.occ)
        ctx = string_feed(person.image, ctx)
        ctx = string_feed(person.public_name, ctx)
        ctx = list_feeder(string_feed)(person.qualifiers, ctx)
        ctx = list_feeder(string_feed)(person.aliases, ctx)
        ctx = list_feeder(string_feed)(person.first_names_aliases, ctx)
        ctx = list_feeder(string_feed)(person.surnames_aliases, ctx)
        ctx = list_feeder(gen_title_feeder(string_feed))(person.titles, ctx)
        ctx = string_feed(person.occupation, ctx)
        ctx = list_feeder(gen_relation_feeder(person_feed, string_feed))(person.rparents, ctx)
        ctx = list_feeder(person_feed)(person.related, ctx)
        ctx = sex_feeder(person.sex, ctx)
        ctx = access_feeder(person.access, ctx)
        ctx = cdate_feeder(person.birth, ctx)
        ctx = string_feed(person.birth_place, ctx)
        ctx = string_feed(person.birth_note, ctx)
        ctx = string_feed(person.birth_src, ctx)
        ctx = cdate_feeder(person.baptism, ctx)
        ctx = string_feed(person.baptism_place, ctx)
        ctx = string_feed(person.baptism_note, ctx)
        ctx = string_feed(person.baptism_src, ctx)
        ctx = death_feeder(person.death, ctx)
        ctx = string_feed(person.death_place, ctx)
        ctx = string_feed(person.death_note, ctx)
        ctx = string_feed(person.death_src, ctx)
        ctx = burial_feeder(person.burial, ctx)
        ctx = string_feed(person.burial_place, ctx)
        ctx = string_feed(person.burial_note, ctx)
        ctx = string_feed(person.burial_src, ctx)
        ctx = list_feeder(gen_pers_event_feeder(person_feed, string_feed))(person.pevents, ctx)
        ctx = string_feed(person.notes, ctx)
        ctx = string_feed(person.psources, ctx)
        ctx = iper_feed(person.key_index, ctx)
        return ctx
    return feed_person

def divorce_feeder(value: gwdef.Divorce, ctx: HashContext) -> HashContext:
    if isinstance(value, gwdef.NotDivorced):
        return feed_string(ctx, "NotDivorced")
    elif isinstance(value, gwdef.DivorceWithDate):
        ctx = feed_string(ctx, "Divorced")
        return cdate_feeder(value.date, ctx)
    elif isinstance(value, gwdef.SeparatedOld):
        return feed_string(ctx, "Separated_old")
    elif isinstance(value, gwdef.NotSeparated):
        return feed_string(ctx, "NotSeparated")
    elif isinstance(value, gwdef.Separated):
        ctx = feed_string(ctx, "Separated")
        return cdate_feeder(value.date, ctx)
    return ctx

def gen_fam_event_name_feeder(string_feed: Feeder):
    def feed_family_event_name(event_name, ctx: HashContext) -> HashContext:
        if isinstance(event_name, gwdef.EfamName):
            ctx = feed_string(ctx, "Efam_Name")
            return string_feed(event_name.name, ctx)
        ocaml_format = _convert_enum_to_ocaml_string(event_name.name)
        return feed_string(ctx, ocaml_format)
    return feed_family_event_name

def gen_fam_event_feeder(person_feed: Feeder, string_feed: Feeder):
    def feed_family_event(family_event: gwdef.GenFamEvent, ctx: HashContext) -> HashContext:
        ctx = gen_fam_event_name_feeder(string_feed)(family_event.efam_name, ctx)
        ctx = cdate_feeder(family_event.efam_date, ctx)
        ctx = string_feed(family_event.efam_place, ctx)
        ctx = string_feed(family_event.efam_reason, ctx)
        ctx = string_feed(family_event.efam_note, ctx)
        ctx = string_feed(family_event.efam_src, ctx)
        ctx = array_feeder(pair_feeder(person_feed, witness_kind_feeder))(family_event.efam_witnesses, ctx)
        return ctx
    return feed_family_event

def relation_kind_feeder(relation_kind: gwdef.RelationKind, ctx: HashContext) -> HashContext:
    relation_kind_to_ocaml = {
        gwdef.RelationKind.MARRIED: "Married",
        gwdef.RelationKind.NOT_MARRIED: "NotMarried",
        gwdef.RelationKind.ENGAGED: "Engaged",
        gwdef.RelationKind.NO_SEXES_CHECK_NOT_MARRIED: "NoSexesCheckNotMarried",
        gwdef.RelationKind.NO_MENTION: "NoMention",
        gwdef.RelationKind.NO_SEXES_CHECK_MARRIED: "NoSexesCheckMarried",
        gwdef.RelationKind.MARRIAGE_BANN: "MarriageBann",
        gwdef.RelationKind.MARRIAGE_CONTRACT: "MarriageContract",
        gwdef.RelationKind.MARRIAGE_LICENSE: "MarriageLicense",
        gwdef.RelationKind.PACS: "Pacs",
        gwdef.RelationKind.RESIDENCE: "Residence",
    }
    ocaml_name = relation_kind_to_ocaml.get(relation_kind, "")
    return feed_string(ctx, ocaml_name)

def gen_couple_feeder(person_feed: Feeder):
    def feed_couple(couple: adef.Couple, ctx: HashContext) -> HashContext:
        ctx = person_feed(couple.father, ctx)
        ctx = person_feed(couple.mother, ctx)
        return ctx
    return feed_couple

def gen_union_feeder(family_feed: Feeder):
    def feed_union(union: gwdef.GenUnion, ctx: HashContext) -> HashContext:
        return array_feeder(family_feed)(union.family, ctx)
    return feed_union

def gen_descend_feeder(person_feed: Feeder):
    def feed_descend(descend: gwdef.GenDescend, ctx: HashContext) -> HashContext:
        return array_feeder(person_feed)(descend.children, ctx)
    return feed_descend

def gen_family_feeder(person_feed: Feeder, ifam_feed: Feeder, string_feed: Feeder):
    def feed_family(family: gwdef.GenFamily, ctx: HashContext) -> HashContext:
        ctx = cdate_feeder(family.marriage, ctx)
        ctx = string_feed(family.marriage_place, ctx)
        ctx = string_feed(family.marriage_note, ctx)
        ctx = string_feed(family.marriage_src, ctx)
        ctx = array_feeder(person_feed)(family.witnesses, ctx)
        ctx = relation_kind_feeder(family.relation, ctx)
        ctx = divorce_feeder(family.divorce, ctx)
        ctx = list_feeder(gen_fam_event_feeder(person_feed, string_feed))(family.fevents, ctx)
        ctx = string_feed(family.comment, ctx)
        ctx = string_feed(family.origin_file, ctx)
        ctx = string_feed(family.fsources, ctx)
        ctx = ifam_feed(family.fam_index, ctx)
        return ctx
    return feed_family

def hash_string(value: str, salt: Optional[str] = None) -> str:
    return feeder_to_hasher(string_feeder)(value, salt)

def hash_person(value: gwdef.GenPerson, salt: Optional[str] = None) -> str:
    return feeder_to_hasher(gen_person_feeder(iper_feeder, iper_feeder, string_feeder))(value, salt)

def hash_family(value: gwdef.GenFamily, salt: Optional[str] = None) -> str:
    return feeder_to_hasher(gen_family_feeder(iper_feeder, ifam_feeder, string_feeder))(value, salt)
