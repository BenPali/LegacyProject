from typing import Optional, Tuple, List, Callable
from types import SimpleNamespace
from lib import gwdef, date as date_mod, pqueue, driver
from lib.adef import Precision


def get_k(conf) -> int:
    k_val = conf.env.get("k")
    if k_val is not None:
        return int(k_val)
    try:
        return int(conf.base_env.get("latest_event", 20))
    except (ValueError, AttributeError):
        return 20


def select(pq_class, nb_of, iterator, get, get_date, conf, base):
    n = min(max(0, get_k(conf)), nb_of(base))
    ref_date = None
    by_val = conf.env.get("by")
    if by_val is not None:
        bm = conf.env.get("bm", -1)
        bd = conf.env.get("bd", -1)
        ref_date = SimpleNamespace(
            day=bd,
            month=bm,
            year=int(by_val),
            prec=Precision.SURE,
            delta=0
        )

    q = pq_class()
    length = 0

    for i in iterator(base):
        x = get(base, i)
        dt = get_date(x)
        if dt is not None:
            if hasattr(dt, 'dmy') and hasattr(dt, 'cal'):
                d = dt.dmy
                cal = dt.cal
            elif isinstance(dt, tuple) and len(dt) == 2:
                d, cal = dt
            else:
                continue

            aft = False
            if ref_date is not None:
                if date_mod.compare_dmy(ref_date, d) <= 0:
                    aft = True

            if not aft:
                e = (x, d, cal)
                if length < n:
                    q = q.add(e)
                    length += 1
                else:
                    q = q.add(e)
                    _, q = q.take()

    result = []
    while not q.is_empty():
        e, q = q.take()
        result.append(e)

    return (result, length)


def select_person(conf, base, get_date: Callable, find_oldest: bool):
    if find_oldest:
        class PersonComparator(pqueue.OrderedType):
            def leq(self, a, b):
                return date_mod.compare_dmy(b[1], a[1]) <= 0
        pq_class = lambda: pqueue.PQueue.create(PersonComparator())
    else:
        class PersonComparator(pqueue.OrderedType):
            def leq(self, a, b):
                return date_mod.compare_dmy(a[1], b[1]) <= 0
        pq_class = lambda: pqueue.PQueue.create(PersonComparator())

    def pget_wrapper(base, i):
        return driver.poi(base, i)

    return select(
        pq_class,
        driver.nb_of_persons,
        driver.ipers,
        pget_wrapper,
        get_date,
        conf,
        base
    )


def select_family(conf, base, get_date: Callable, find_oldest: bool):
    if find_oldest:
        class FamilyComparator(pqueue.OrderedType):
            def leq(self, a, b):
                return date_mod.compare_dmy(b[1], a[1]) <= 0
        pq_class = lambda: pqueue.PQueue.create(FamilyComparator())
    else:
        class FamilyComparator(pqueue.OrderedType):
            def leq(self, a, b):
                return date_mod.compare_dmy(a[1], b[1]) <= 0
        pq_class = lambda: pqueue.PQueue.create(FamilyComparator())

    return select(
        pq_class,
        driver.nb_of_families,
        driver.ifams,
        driver.foi,
        get_date,
        conf,
        base
    )


def death_date(p) -> Optional:
    return date_mod.date_of_death(driver.get_death(p))


def make_population_pyramid(nb_intervals: int, interval: int, limit: int,
                            at_date, conf, base) -> Tuple[List[int], List[int]]:
    men = [0] * (nb_intervals + 1)
    wom = [0] * (nb_intervals + 1)

    for i in driver.ipers(base):
        p = driver.poi(base, i)
        sex = driver.get_sex(p)
        dea = driver.get_death(p)

        if sex != gwdef.Sex.NEUTER:
            birth = driver.get_birth(p)
            dmy = date_mod.cdate_to_dmy_opt(birth)
            if dmy is not None:
                if date_mod.compare_dmy(dmy, at_date) <= 0:
                    elapsed = date_mod.time_elapsed(dmy, at_date)
                    j = min(nb_intervals, elapsed.year // interval)

                    is_alive = False
                    if isinstance(dea, gwdef.NotDead):
                        is_alive = True
                    elif isinstance(dea, gwdef.DontKnowIfDead) and elapsed.year < limit:
                        is_alive = True
                    else:
                        death_dmy = date_mod.dmy_of_death(dea)
                        if death_dmy is not None:
                            if date_mod.compare_dmy(death_dmy, at_date) > 0:
                                is_alive = True

                    if is_alive:
                        if sex == gwdef.Sex.MALE:
                            men[j] += 1
                        else:
                            wom[j] += 1

    return (men, wom)
