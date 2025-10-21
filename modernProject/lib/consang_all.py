import sys
from typing import Optional, Tuple, Callable
from lib import driver
from lib import consang
from lib import adef
from lib import gutil
from lib import progr_bar


_progress_bar = None


def _start_progress():
    global _progress_bar
    _progress_bar = progr_bar.ProgressBar()


def _run_progress(current: int, total: int):
    global _progress_bar
    if _progress_bar:
        _progress_bar.progress(current, total)


def _finish_progress():
    global _progress_bar
    if _progress_bar:
        _progress_bar.finish()
        _progress_bar = None


def _relationship(base, tab: consang.RelationshipInfo, ip1: int, ip2: int) -> float:
    return consang.relationship_and_links(base, tab, False, ip1, ip2)[0]


def _trace(verbosity: int, cnt: int, max_cnt: int):
    if verbosity >= 2:
        sys.stderr.write(f"{cnt:7d}\b\b\b\b\b\b\b")
        sys.stderr.flush()
    elif verbosity >= 1:
        _run_progress(max_cnt - cnt, max_cnt)


def _consang_array(base) -> Tuple[Callable[[int], Optional[int]], Callable[[int], adef.Fix], Callable[[int, adef.Fix], None], list]:
    patched = [False]

    def fget(i: int) -> Optional[int]:
        person = driver.poi(base, i)
        return driver.get_parents(person)

    def cget(i: int) -> adef.Fix:
        person = driver.poi(base, i)
        return driver.get_consang(person)

    def cset(i: int, v: adef.Fix):
        patched[0] = True
        person = driver.poi(base, i)
        ascend = driver.gen_ascend_of_person(person)
        from lib.gwdef import GenAscend
        new_ascend = GenAscend(
            parents=ascend.parents,
            consang=v
        )
        driver.patch_ascend(base, i, new_ascend)

    return (fget, cget, cset, patched)


def compute(base, from_scratch: bool, verbosity: int = 2) -> bool:
    driver.load_ascends_array(base)
    driver.load_couples_array(base)
    fget, cget, cset, patched = _consang_array(base)

    try:
        ts = consang.topological_sort(base, driver.poi)
        tab = consang.make_relationship_info(base, ts)
        persons = driver.ipers(base)
        families = driver.ifams(base)
        consang_tab = driver.ifam_marker(families, adef.NO_CONSANG)
        cnt = 0

        for idx in range(persons.length):
            i = persons.get(idx)
            if i is not None:
                if from_scratch:
                    cset(i, adef.NO_CONSANG)
                    cnt += 1
                else:
                    cg = cget(i)
                    ifam = fget(i)
                    if ifam is not None:
                        consang_tab.set(ifam, cg)
                    if cg == adef.NO_CONSANG:
                        cnt += 1

        max_cnt = cnt
        most = None

        if verbosity >= 1:
            sys.stderr.write(f"To do: {max_cnt} persons\n")

        if max_cnt != 0:
            if verbosity >= 2:
                sys.stderr.write("Computing consanguinity...")
                sys.stderr.flush()
            elif verbosity >= 1:
                _start_progress()

        running = True
        while running:
            running = False
            for idx in range(persons.length):
                i = persons.get(idx)
                if i is None:
                    continue
                if cget(i) == adef.NO_CONSANG:
                    ifam = fget(i)
                    if ifam is not None:
                        pconsang = consang_tab.get(ifam)
                        if pconsang == adef.NO_CONSANG:
                            cpl = driver.foi(base, ifam)
                            ifath = driver.get_father(cpl)
                            imoth = driver.get_mother(cpl)
                            if cget(ifath) != adef.NO_CONSANG and cget(imoth) != adef.NO_CONSANG:
                                relationship_val = _relationship(base, tab, ifath, imoth)
                                _trace(verbosity, cnt, max_cnt)
                                cnt -= 1
                                cg = adef.Fix.from_float(relationship_val)
                                cset(i, cg)
                                consang_tab.set(ifam, cg)
                                if verbosity >= 2:
                                    if most is None or cg > cget(most):
                                        sys.stderr.write(f"\nMax consanguinity {relationship_val} for {gutil.designation(base, driver.poi(base, i))}... ")
                                        sys.stderr.flush()
                                        most = i
                            else:
                                running = True
                        else:
                            _trace(verbosity, cnt, max_cnt)
                            cnt -= 1
                            cset(i, pconsang)
                    else:
                        _trace(verbosity, cnt, max_cnt)
                        cnt -= 1
                        cset(i, adef.Fix.from_float(0.0))

        if max_cnt != 0:
            if verbosity >= 2:
                sys.stderr.write(" done   \n")
                sys.stderr.flush()
            elif verbosity >= 1:
                _finish_progress()

    except KeyboardInterrupt:
        if verbosity > 0:
            sys.stderr.write("\n")
            sys.stderr.flush()

    if patched[0]:
        driver.commit_patches(base)

    return patched[0]
