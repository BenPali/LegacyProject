import pytest
from lib import hasher, adef, gwdef, driver

def test_create_context():
    ctx = hasher.create_context()
    assert ctx is not None
    assert hasattr(ctx, 'update')
    assert hasattr(ctx, 'hexdigest')

def test_feed_string():
    ctx = hasher.create_context()
    ctx = hasher.feed_string(ctx, "test")
    result = hasher.finalize_hash(ctx)
    assert len(result) == 64
    assert isinstance(result, str)

def test_feed_int():
    ctx = hasher.create_context()
    ctx = hasher.feed_int(ctx, 42)
    result = hasher.finalize_hash(ctx)
    assert len(result) == 64

def test_feed_bool_true():
    ctx = hasher.create_context()
    ctx = hasher.feed_bool(ctx, True)
    result = hasher.finalize_hash(ctx)
    assert len(result) == 64

def test_feed_bool_false():
    ctx = hasher.create_context()
    ctx = hasher.feed_bool(ctx, False)
    result = hasher.finalize_hash(ctx)
    assert len(result) == 64

def test_feed_bool_different_values():
    ctx1 = hasher.create_context()
    ctx1 = hasher.feed_bool(ctx1, True)
    hash1 = hasher.finalize_hash(ctx1)

    ctx2 = hasher.create_context()
    ctx2 = hasher.feed_bool(ctx2, False)
    hash2 = hasher.finalize_hash(ctx2)

    assert hash1 != hash2

def test_string_feeder():
    ctx = hasher.create_context()
    ctx = hasher.string_feeder("hello", ctx)
    result = hasher.finalize_hash(ctx)
    assert len(result) == 64

def test_int_feeder():
    ctx = hasher.create_context()
    ctx = hasher.int_feeder(123, ctx)
    result = hasher.finalize_hash(ctx)
    assert len(result) == 64

def test_bool_feeder():
    ctx = hasher.create_context()
    ctx = hasher.bool_feeder(True, ctx)
    result = hasher.finalize_hash(ctx)
    assert len(result) == 64

def test_list_feeder():
    feed_list = hasher.list_feeder(hasher.string_feeder)
    ctx = hasher.create_context()
    ctx = feed_list(["a", "b", "c"], ctx)
    result = hasher.finalize_hash(ctx)
    assert len(result) == 64

def test_list_feeder_empty():
    feed_list = hasher.list_feeder(hasher.string_feeder)
    ctx = hasher.create_context()
    ctx = feed_list([], ctx)
    result = hasher.finalize_hash(ctx)
    assert len(result) == 64

def test_array_feeder():
    feed_array = hasher.array_feeder(hasher.int_feeder)
    ctx = hasher.create_context()
    ctx = feed_array([1, 2, 3], ctx)
    result = hasher.finalize_hash(ctx)
    assert len(result) == 64

def test_pair_feeder():
    feed_pair = hasher.pair_feeder(hasher.string_feeder, hasher.int_feeder)
    ctx = hasher.create_context()
    ctx = feed_pair(("hello", 42), ctx)
    result = hasher.finalize_hash(ctx)
    assert len(result) == 64

def test_option_feeder_some():
    feed_option = hasher.option_feeder(hasher.string_feeder)
    ctx = hasher.create_context()
    ctx = feed_option("value", ctx)
    result = hasher.finalize_hash(ctx)
    assert len(result) == 64

def test_option_feeder_none():
    feed_option = hasher.option_feeder(hasher.string_feeder)
    ctx = hasher.create_context()
    ctx = feed_option(None, ctx)
    result = hasher.finalize_hash(ctx)
    assert len(result) == 64

def test_option_feeder_different():
    feed_option = hasher.option_feeder(hasher.string_feeder)

    ctx1 = hasher.create_context()
    ctx1 = feed_option("value", ctx1)
    hash1 = hasher.finalize_hash(ctx1)

    ctx2 = hasher.create_context()
    ctx2 = feed_option(None, ctx2)
    hash2 = hasher.finalize_hash(ctx2)

    assert hash1 != hash2

def test_iper_feeder():
    iper = 123
    ctx = hasher.create_context()
    ctx = hasher.iper_feeder(iper, ctx)
    result = hasher.finalize_hash(ctx)
    assert len(result) == 64

def test_ifam_feeder():
    ifam = 456
    ctx = hasher.create_context()
    ctx = hasher.ifam_feeder(ifam, ctx)
    result = hasher.finalize_hash(ctx)
    assert len(result) == 64

def test_istr_feeder():
    istr = 789
    ctx = hasher.create_context()
    ctx = hasher.istr_feeder(istr, ctx)
    result = hasher.finalize_hash(ctx)
    assert len(result) == 64

def test_dmy2_feeder():
    dmy2 = adef.Dmy2(day2=1, month2=2, year2=2000, delta2=0)
    ctx = hasher.create_context()
    ctx = hasher.dmy2_feeder(dmy2, ctx)
    result = hasher.finalize_hash(ctx)
    assert len(result) == 64

def test_precision_feeder_sure():
    ctx = hasher.create_context()
    ctx = hasher.precision_feeder(adef.Precision.SURE, ctx)
    result = hasher.finalize_hash(ctx)
    assert len(result) == 64

def test_precision_feeder_about():
    ctx = hasher.create_context()
    ctx = hasher.precision_feeder(adef.Precision.ABOUT, ctx)
    result = hasher.finalize_hash(ctx)
    assert len(result) == 64

def test_precision_feeder_or_year():
    dmy2 = adef.Dmy2(day2=1, month2=1, year2=2001, delta2=0)
    precision = adef.PrecisionOrYear(dmy2)
    ctx = hasher.create_context()
    ctx = hasher.precision_feeder(precision, ctx)
    result = hasher.finalize_hash(ctx)
    assert len(result) == 64

def test_dmy_feeder():
    dmy = adef.Dmy(day=15, month=6, year=1990, prec=adef.Precision.SURE, delta=0)
    ctx = hasher.create_context()
    ctx = hasher.dmy_feeder(dmy, ctx)
    result = hasher.finalize_hash(ctx)
    assert len(result) == 64

def test_calendar_feeder_gregorian():
    ctx = hasher.create_context()
    ctx = hasher.calendar_feeder(adef.Calendar.GREGORIAN, ctx)
    result = hasher.finalize_hash(ctx)
    assert len(result) == 64

def test_calendar_feeder_julian():
    ctx = hasher.create_context()
    ctx = hasher.calendar_feeder(adef.Calendar.JULIAN, ctx)
    result = hasher.finalize_hash(ctx)
    assert len(result) == 64

def test_date_feeder_dgreg():
    dmy = adef.Dmy(day=1, month=1, year=2000, prec=adef.Precision.SURE, delta=0)
    date = adef.DateGreg(dmy, adef.Calendar.GREGORIAN)
    ctx = hasher.create_context()
    ctx = hasher.date_feeder(date, ctx)
    result = hasher.finalize_hash(ctx)
    assert len(result) == 64

def test_date_feeder_dtext():
    date = adef.DateText("circa 1850")
    ctx = hasher.create_context()
    ctx = hasher.date_feeder(date, ctx)
    result = hasher.finalize_hash(ctx)
    assert len(result) == 64

def test_cdate_feeder_cgregorian():
    cdate = adef.CdateGregorian(730000)
    ctx = hasher.create_context()
    ctx = hasher.cdate_feeder(cdate, ctx)
    result = hasher.finalize_hash(ctx)
    assert len(result) == 64

def test_cdate_feeder_cnone():
    cdate = adef.CdateNone()
    ctx = hasher.create_context()
    ctx = hasher.cdate_feeder(cdate, ctx)
    result = hasher.finalize_hash(ctx)
    assert len(result) == 64

def test_death_reason_feeder():
    ctx = hasher.create_context()
    ctx = hasher.death_reason_feeder(gwdef.DeathReason.KILLED, ctx)
    result = hasher.finalize_hash(ctx)
    assert len(result) == 64

def test_death_feeder_not_dead():
    ctx = hasher.create_context()
    ctx = hasher.death_feeder(gwdef.NotDead(), ctx)
    result = hasher.finalize_hash(ctx)
    assert len(result) == 64

def test_death_feeder_death():
    death = gwdef.DeathWithReason(gwdef.DeathReason.UNSPECIFIED, adef.CdateNone())
    ctx = hasher.create_context()
    ctx = hasher.death_feeder(death, ctx)
    result = hasher.finalize_hash(ctx)
    assert len(result) == 64

def test_sex_feeder():
    ctx = hasher.create_context()
    ctx = hasher.sex_feeder(gwdef.Sex.MALE, ctx)
    result = hasher.finalize_hash(ctx)
    assert len(result) == 64

def test_access_feeder():
    ctx = hasher.create_context()
    ctx = hasher.access_feeder(gwdef.Access.PUBLIC, ctx)
    result = hasher.finalize_hash(ctx)
    assert len(result) == 64

def test_relation_type_feeder():
    ctx = hasher.create_context()
    ctx = hasher.relation_type_feeder(gwdef.RelationType.ADOPTION, ctx)
    result = hasher.finalize_hash(ctx)
    assert len(result) == 64

def test_burial_feeder_unknown():
    ctx = hasher.create_context()
    ctx = hasher.burial_feeder(gwdef.UnknownBurial(), ctx)
    result = hasher.finalize_hash(ctx)
    assert len(result) == 64

def test_burial_feeder_buried():
    burial = gwdef.Buried(adef.CdateNone())
    ctx = hasher.create_context()
    ctx = hasher.burial_feeder(burial, ctx)
    result = hasher.finalize_hash(ctx)
    assert len(result) == 64

def test_witness_kind_feeder():
    ctx = hasher.create_context()
    ctx = hasher.witness_kind_feeder(gwdef.WitnessKind.WITNESS, ctx)
    result = hasher.finalize_hash(ctx)
    assert len(result) == 64

def test_divorce_feeder_not_divorced():
    ctx = hasher.create_context()
    ctx = hasher.divorce_feeder(gwdef.NotDivorced(), ctx)
    result = hasher.finalize_hash(ctx)
    assert len(result) == 64

def test_divorce_feeder_divorced():
    divorce = gwdef.DivorceWithDate(adef.CdateNone())
    ctx = hasher.create_context()
    ctx = hasher.divorce_feeder(divorce, ctx)
    result = hasher.finalize_hash(ctx)
    assert len(result) == 64

def test_relation_kind_feeder():
    ctx = hasher.create_context()
    ctx = hasher.relation_kind_feeder(gwdef.RelationKind.MARRIED, ctx)
    result = hasher.finalize_hash(ctx)
    assert len(result) == 64

def test_feeder_to_hasher_no_salt():
    hash_func = hasher.feeder_to_hasher(hasher.string_feeder)
    result = hash_func("test")
    assert len(result) == 64

def test_feeder_to_hasher_with_salt():
    hash_func = hasher.feeder_to_hasher(hasher.string_feeder)
    result = hash_func("test", "salt123")
    assert len(result) == 64

def test_feeder_to_hasher_different_salt():
    hash_func = hasher.feeder_to_hasher(hasher.string_feeder)
    hash1 = hash_func("test", "salt1")
    hash2 = hash_func("test", "salt2")
    assert hash1 != hash2

def test_hash_string():
    result = hasher.hash_string("hello world")
    assert len(result) == 64

def test_hash_string_with_salt():
    result = hasher.hash_string("hello world", "salt")
    assert len(result) == 64

def test_hash_string_consistent():
    hash1 = hasher.hash_string("test")
    hash2 = hasher.hash_string("test")
    assert hash1 == hash2

def test_hash_string_different_values():
    hash1 = hasher.hash_string("test1")
    hash2 = hasher.hash_string("test2")
    assert hash1 != hash2

def test_gen_title_name_feeder_tmain():
    feed_title_name = hasher.gen_title_name_feeder(hasher.string_feeder)
    ctx = hasher.create_context()
    ctx = feed_title_name(gwdef.Tmain(), ctx)
    result = hasher.finalize_hash(ctx)
    assert len(result) == 64

def test_gen_title_name_feeder_tname():
    feed_title_name = hasher.gen_title_name_feeder(hasher.string_feeder)
    title_name = gwdef.Tname("Duke")
    ctx = hasher.create_context()
    ctx = feed_title_name(title_name, ctx)
    result = hasher.finalize_hash(ctx)
    assert len(result) == 64

def test_gen_couple_feeder():
    feed_couple = hasher.gen_couple_feeder(hasher.iper_feeder)
    couple = adef.Couple(1, 2)
    ctx = hasher.create_context()
    ctx = feed_couple(couple, ctx)
    result = hasher.finalize_hash(ctx)
    assert len(result) == 64

def test_gen_union_feeder():
    feed_union = hasher.gen_union_feeder(hasher.ifam_feeder)
    union = gwdef.GenUnion([1, 2])
    ctx = hasher.create_context()
    ctx = feed_union(union, ctx)
    result = hasher.finalize_hash(ctx)
    assert len(result) == 64

def test_gen_descend_feeder():
    feed_descend = hasher.gen_descend_feeder(hasher.iper_feeder)
    descend = gwdef.GenDescend([1, 2])
    ctx = hasher.create_context()
    ctx = feed_descend(descend, ctx)
    result = hasher.finalize_hash(ctx)
    assert len(result) == 64

def test_pers_event_name_feeder():
    feed_event_name = hasher.gen_pers_event_name_feeder(hasher.string_feeder)
    ctx = hasher.create_context()
    ctx = feed_event_name(gwdef.GenPersEventName.EPERS_BIRTH, ctx)
    result = hasher.finalize_hash(ctx)
    assert len(result) == 64

def test_pers_event_name_feeder_custom():
    feed_event_name = hasher.gen_pers_event_name_feeder(hasher.string_feeder)
    event_name = gwdef.EpersName("Custom Event")
    ctx = hasher.create_context()
    ctx = feed_event_name(event_name, ctx)
    result = hasher.finalize_hash(ctx)
    assert len(result) == 64

def test_fam_event_name_feeder():
    feed_event_name = hasher.gen_fam_event_name_feeder(hasher.string_feeder)
    ctx = hasher.create_context()
    ctx = feed_event_name(gwdef.GenFamEventName.EFAM_MARRIAGE, ctx)
    result = hasher.finalize_hash(ctx)
    assert len(result) == 64

def test_fam_event_name_feeder_custom():
    feed_event_name = hasher.gen_fam_event_name_feeder(hasher.string_feeder)
    event_name = gwdef.EfamName("Custom Family Event")
    ctx = hasher.create_context()
    ctx = feed_event_name(event_name, ctx)
    result = hasher.finalize_hash(ctx)
    assert len(result) == 64

def test_consistency_across_multiple_feeds():
    ctx1 = hasher.create_context()
    ctx1 = hasher.string_feeder("hello", ctx1)
    ctx1 = hasher.int_feeder(42, ctx1)
    hash1 = hasher.finalize_hash(ctx1)

    ctx2 = hasher.create_context()
    ctx2 = hasher.string_feeder("hello", ctx2)
    ctx2 = hasher.int_feeder(42, ctx2)
    hash2 = hasher.finalize_hash(ctx2)

    assert hash1 == hash2

def test_order_matters():
    ctx1 = hasher.create_context()
    ctx1 = hasher.string_feeder("hello", ctx1)
    ctx1 = hasher.int_feeder(42, ctx1)
    hash1 = hasher.finalize_hash(ctx1)

    ctx2 = hasher.create_context()
    ctx2 = hasher.int_feeder(42, ctx2)
    ctx2 = hasher.string_feeder("hello", ctx2)
    hash2 = hasher.finalize_hash(ctx2)

    assert hash1 != hash2

def test_precision_feeder_maybe():
    ctx = hasher.create_context()
    ctx = hasher.precision_feeder(adef.Precision.MAYBE, ctx)
    result = hasher.finalize_hash(ctx)
    assert len(result) == 64

def test_precision_feeder_before():
    ctx = hasher.create_context()
    ctx = hasher.precision_feeder(adef.Precision.BEFORE, ctx)
    result = hasher.finalize_hash(ctx)
    assert len(result) == 64

def test_precision_feeder_after():
    ctx = hasher.create_context()
    ctx = hasher.precision_feeder(adef.Precision.AFTER, ctx)
    result = hasher.finalize_hash(ctx)
    assert len(result) == 64

def test_precision_feeder_year_int():
    dmy2 = adef.Dmy2(day2=1, month2=1, year2=2001, delta2=0)
    precision = adef.PrecisionYearInt(dmy2)
    ctx = hasher.create_context()
    ctx = hasher.precision_feeder(precision, ctx)
    result = hasher.finalize_hash(ctx)
    assert len(result) == 64

def test_calendar_feeder_french():
    ctx = hasher.create_context()
    ctx = hasher.calendar_feeder(adef.Calendar.FRENCH, ctx)
    result = hasher.finalize_hash(ctx)
    assert len(result) == 64

def test_calendar_feeder_hebrew():
    ctx = hasher.create_context()
    ctx = hasher.calendar_feeder(adef.Calendar.HEBREW, ctx)
    result = hasher.finalize_hash(ctx)
    assert len(result) == 64

def test_cdate_feeder_cjulian():
    cdate = adef.CdateJulian(730000)
    ctx = hasher.create_context()
    ctx = hasher.cdate_feeder(cdate, ctx)
    result = hasher.finalize_hash(ctx)
    assert len(result) == 64

def test_cdate_feeder_cfrench():
    cdate = adef.CdateFrench(730000)
    ctx = hasher.create_context()
    ctx = hasher.cdate_feeder(cdate, ctx)
    result = hasher.finalize_hash(ctx)
    assert len(result) == 64

def test_cdate_feeder_chebrew():
    cdate = adef.CdateHebrew(730000)
    ctx = hasher.create_context()
    ctx = hasher.cdate_feeder(cdate, ctx)
    result = hasher.finalize_hash(ctx)
    assert len(result) == 64

def test_cdate_feeder_ctext():
    cdate = adef.CdateText("circa 1800")
    ctx = hasher.create_context()
    ctx = hasher.cdate_feeder(cdate, ctx)
    result = hasher.finalize_hash(ctx)
    assert len(result) == 64

def test_cdate_feeder_cdate():
    dmy = adef.Dmy(day=1, month=1, year=2000, prec=adef.Precision.SURE, delta=0)
    date = adef.DateGreg(dmy, adef.Calendar.GREGORIAN)
    cdate = adef.CdateDate(date)
    ctx = hasher.create_context()
    ctx = hasher.cdate_feeder(cdate, ctx)
    result = hasher.finalize_hash(ctx)
    assert len(result) == 64

def test_death_reason_feeder_murdered():
    ctx = hasher.create_context()
    ctx = hasher.death_reason_feeder(gwdef.DeathReason.MURDERED, ctx)
    result = hasher.finalize_hash(ctx)
    assert len(result) == 64

def test_death_reason_feeder_executed():
    ctx = hasher.create_context()
    ctx = hasher.death_reason_feeder(gwdef.DeathReason.EXECUTED, ctx)
    result = hasher.finalize_hash(ctx)
    assert len(result) == 64

def test_death_reason_feeder_disappeared():
    ctx = hasher.create_context()
    ctx = hasher.death_reason_feeder(gwdef.DeathReason.DISAPPEARED, ctx)
    result = hasher.finalize_hash(ctx)
    assert len(result) == 64

def test_death_feeder_dead_young():
    ctx = hasher.create_context()
    ctx = hasher.death_feeder(gwdef.DeadYoung(), ctx)
    result = hasher.finalize_hash(ctx)
    assert len(result) == 64

def test_death_feeder_dead_dont_know_when():
    ctx = hasher.create_context()
    ctx = hasher.death_feeder(gwdef.DeadDontKnowWhen(), ctx)
    result = hasher.finalize_hash(ctx)
    assert len(result) == 64

def test_death_feeder_dont_know_if_dead():
    ctx = hasher.create_context()
    ctx = hasher.death_feeder(gwdef.DontKnowIfDead(), ctx)
    result = hasher.finalize_hash(ctx)
    assert len(result) == 64

def test_death_feeder_of_course_dead():
    ctx = hasher.create_context()
    ctx = hasher.death_feeder(gwdef.OfCourseDead(), ctx)
    result = hasher.finalize_hash(ctx)
    assert len(result) == 64

def test_gen_title_name_feeder_tnone():
    feed_title_name = hasher.gen_title_name_feeder(hasher.string_feeder)
    ctx = hasher.create_context()
    ctx = feed_title_name(gwdef.Tnone(), ctx)
    result = hasher.finalize_hash(ctx)
    assert len(result) == 64

def test_gen_title_feeder():
    feed_title = hasher.gen_title_feeder(hasher.string_feeder)
    title = gwdef.GenTitle(
        t_name=gwdef.Tname("Duke"),
        t_ident="duke1",
        t_place="London",
        t_date_start=adef.CdateNone(),
        t_date_end=adef.CdateNone(),
        t_nth=1
    )
    ctx = hasher.create_context()
    ctx = feed_title(title, ctx)
    result = hasher.finalize_hash(ctx)
    assert len(result) == 64

def test_sex_feeder_neuter():
    ctx = hasher.create_context()
    ctx = hasher.sex_feeder(gwdef.Sex.NEUTER, ctx)
    result = hasher.finalize_hash(ctx)
    assert len(result) == 64

def test_access_feeder_if_titles():
    ctx = hasher.create_context()
    ctx = hasher.access_feeder(gwdef.Access.IF_TITLES, ctx)
    result = hasher.finalize_hash(ctx)
    assert len(result) == 64

def test_access_feeder_semi_public():
    ctx = hasher.create_context()
    ctx = hasher.access_feeder(gwdef.Access.SEMI_PUBLIC, ctx)
    result = hasher.finalize_hash(ctx)
    assert len(result) == 64

def test_access_feeder_private():
    ctx = hasher.create_context()
    ctx = hasher.access_feeder(gwdef.Access.PRIVATE, ctx)
    result = hasher.finalize_hash(ctx)
    assert len(result) == 64

def test_relation_type_feeder_recognition():
    ctx = hasher.create_context()
    ctx = hasher.relation_type_feeder(gwdef.RelationType.RECOGNITION, ctx)
    result = hasher.finalize_hash(ctx)
    assert len(result) == 64

def test_relation_type_feeder_candidate_parent():
    ctx = hasher.create_context()
    ctx = hasher.relation_type_feeder(gwdef.RelationType.CANDIDATE_PARENT, ctx)
    result = hasher.finalize_hash(ctx)
    assert len(result) == 64

def test_relation_type_feeder_god_parent():
    ctx = hasher.create_context()
    ctx = hasher.relation_type_feeder(gwdef.RelationType.GOD_PARENT, ctx)
    result = hasher.finalize_hash(ctx)
    assert len(result) == 64

def test_relation_type_feeder_foster_parent():
    ctx = hasher.create_context()
    ctx = hasher.relation_type_feeder(gwdef.RelationType.FOSTER_PARENT, ctx)
    result = hasher.finalize_hash(ctx)
    assert len(result) == 64

def test_gen_relation_feeder():
    feed_relation = hasher.gen_relation_feeder(hasher.iper_feeder, hasher.string_feeder)
    relation = gwdef.GenRelation(
        r_type=gwdef.RelationType.ADOPTION,
        r_fath=1,
        r_moth=2,
        r_sources="source1"
    )
    ctx = hasher.create_context()
    ctx = feed_relation(relation, ctx)
    result = hasher.finalize_hash(ctx)
    assert len(result) == 64

def test_burial_feeder_cremated():
    burial = gwdef.Cremated(adef.CdateNone())
    ctx = hasher.create_context()
    ctx = hasher.burial_feeder(burial, ctx)
    result = hasher.finalize_hash(ctx)
    assert len(result) == 64

def test_gen_pers_event_feeder():
    feed_event = hasher.gen_pers_event_feeder(hasher.iper_feeder, hasher.string_feeder)
    event = gwdef.GenPersEvent(
        epers_name=gwdef.GenPersEventName.EPERS_BIRTH,
        epers_date=adef.CdateNone(),
        epers_place="Hospital",
        epers_reason="",
        epers_note="note",
        epers_src="source",
        epers_witnesses=[]
    )
    ctx = hasher.create_context()
    ctx = feed_event(event, ctx)
    result = hasher.finalize_hash(ctx)
    assert len(result) == 64

def test_divorce_feeder_separated_old():
    ctx = hasher.create_context()
    ctx = hasher.divorce_feeder(gwdef.SeparatedOld(), ctx)
    result = hasher.finalize_hash(ctx)
    assert len(result) == 64

def test_divorce_feeder_not_separated():
    ctx = hasher.create_context()
    ctx = hasher.divorce_feeder(gwdef.NotSeparated(), ctx)
    result = hasher.finalize_hash(ctx)
    assert len(result) == 64

def test_divorce_feeder_separated():
    divorce = gwdef.Separated(adef.CdateNone())
    ctx = hasher.create_context()
    ctx = hasher.divorce_feeder(divorce, ctx)
    result = hasher.finalize_hash(ctx)
    assert len(result) == 64

def test_gen_fam_event_feeder():
    feed_event = hasher.gen_fam_event_feeder(hasher.iper_feeder, hasher.string_feeder)
    event = gwdef.GenFamEvent(
        efam_name=gwdef.GenFamEventName.EFAM_MARRIAGE,
        efam_date=adef.CdateNone(),
        efam_place="Church",
        efam_reason="",
        efam_note="note",
        efam_src="source",
        efam_witnesses=[]
    )
    ctx = hasher.create_context()
    ctx = feed_event(event, ctx)
    result = hasher.finalize_hash(ctx)
    assert len(result) == 64

def test_hash_person():
    person = gwdef.GenPerson(
        first_name="John",
        surname="Doe",
        occ=0,
        image="",
        public_name="",
        qualifiers=[],
        aliases=[],
        first_names_aliases=[],
        surnames_aliases=[],
        titles=[],
        rparents=[],
        related=[],
        occupation="",
        sex=gwdef.Sex.MALE,
        access=gwdef.Access.PUBLIC,
        birth=adef.CdateNone(),
        birth_place="",
        birth_note="",
        birth_src="",
        baptism=adef.CdateNone(),
        baptism_place="",
        baptism_note="",
        baptism_src="",
        death=gwdef.NotDead(),
        death_place="",
        death_note="",
        death_src="",
        burial=gwdef.UnknownBurial(),
        burial_place="",
        burial_note="",
        burial_src="",
        pevents=[],
        notes="",
        psources="",
        key_index=1
    )
    result = hasher.hash_person(person)
    assert len(result) == 64
    assert isinstance(result, str)

def test_hash_person_with_salt():
    person = gwdef.GenPerson(
        first_name="Jane",
        surname="Smith",
        occ=0,
        image="",
        public_name="",
        qualifiers=[],
        aliases=[],
        first_names_aliases=[],
        surnames_aliases=[],
        titles=[],
        rparents=[],
        related=[],
        occupation="",
        sex=gwdef.Sex.FEMALE,
        access=gwdef.Access.PUBLIC,
        birth=adef.CdateNone(),
        birth_place="",
        birth_note="",
        birth_src="",
        baptism=adef.CdateNone(),
        baptism_place="",
        baptism_note="",
        baptism_src="",
        death=gwdef.NotDead(),
        death_place="",
        death_note="",
        death_src="",
        burial=gwdef.UnknownBurial(),
        burial_place="",
        burial_note="",
        burial_src="",
        pevents=[],
        notes="",
        psources="",
        key_index=2
    )
    result = hasher.hash_person(person, "mysalt")
    assert len(result) == 64
    assert isinstance(result, str)

def test_hash_family():
    family = gwdef.GenFamily(
        marriage=adef.CdateNone(),
        marriage_place="",
        marriage_note="",
        marriage_src="",
        witnesses=[],
        relation=gwdef.RelationKind.MARRIED,
        divorce=gwdef.NotDivorced(),
        fevents=[],
        comment="",
        origin_file="",
        fsources="",
        fam_index=1
    )
    result = hasher.hash_family(family)
    assert len(result) == 64
    assert isinstance(result, str)

def test_hash_family_with_salt():
    family = gwdef.GenFamily(
        marriage=adef.CdateNone(),
        marriage_place="Church",
        marriage_note="",
        marriage_src="",
        witnesses=[],
        relation=gwdef.RelationKind.MARRIED,
        divorce=gwdef.NotDivorced(),
        fevents=[],
        comment="",
        origin_file="",
        fsources="",
        fam_index=2
    )
    result = hasher.hash_family(family, "familysalt")
    assert len(result) == 64
    assert isinstance(result, str)

def test_compose():
    ctx = hasher.create_context()
    combined = hasher.compose(hasher.string_feeder, hasher.string_feeder)
    ctx = combined("test", ctx)
    result = hasher.finalize_hash(ctx)
    assert len(result) == 64
