import sys
from pathlib import Path
import pytest
import unittest.mock as um

from bin import robot
from lib import config

# Ensure bin and project root are importable, matching other tests
sys.path.insert(0, str(Path(__file__).parent.parent / 'bin'))
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_robot_check_wizard_counts_with_existing_who():
    from bin.robot import Excl, Who, UserType

    output_conf = config.OutputConf(
        status=lambda x: None,
        header=lambda x: None,
        body=lambda x: None,
        flush=lambda: None
    )
    conf = config.Config(output_conf=output_conf, user="wiz", bname="b", wizard=True)

    acc = [float(i) for i in range(1, 21)]
    excl = Excl(excl=[], who={"addr": Who(acc_times=acc, oldest_time=acc[0], nb_connect=len(acc), nbase="b", utype=UserType.WIZARD, uname="wiz")}, max_conn=(0, ""))

    with um.patch('bin.robot.robot_excl', return_value=(excl, '/dev/null')):
        normal, wizard, friend, wlist = robot.check(tm=22.0, from_addr="addr", max_call=1000, sec=10000, conf=conf, suicide=False)
        assert normal == 0 and wizard == 1 and friend == 0
        assert len(wlist) == 1 and wlist[0][0] == "wiz"


def test_robot_check_blocks_when_exceeding_max_call():
    from bin.robot import Excl, Who, UserType

    output_conf = config.OutputConf(
        status=lambda x: None,
        header=lambda x: None,
        body=lambda x: None,
        flush=lambda: None
    )
    conf = config.Config(output_conf=output_conf, user="user", bname="b")

    acc = [10.0, 11.0, 12.0]
    excl = Excl(excl=[], who={"addr2": Who(acc_times=acc, oldest_time=10.0, nb_connect=len(acc), nbase="b", utype=UserType.NORMAL, uname="user")}, max_conn=(0, ""))

    with um.patch('bin.robot.robot_excl', return_value=(excl, '/dev/null')):
        with um.patch('bin.robot.save_robot_excl'):
            with pytest.raises(SystemExit):
                robot.check(tm=13.0, from_addr="addr2", max_call=3, sec=10000, conf=conf, suicide=False)


def test_robot_check_friend_counts():
    from bin.robot import Excl, Who, UserType

    output_conf = config.OutputConf(
        status=lambda x: None,
        header=lambda x: None,
        body=lambda x: None,
        flush=lambda: None
    )
    conf = config.Config(output_conf=output_conf, user="friend", bname="b", friend=True)

    acc = [float(i) for i in range(1, 25)]
    excl = Excl(excl=[], who={"faddr": Who(acc_times=acc, oldest_time=acc[0], nb_connect=len(acc), nbase="b", utype=UserType.FRIEND, uname="friend")}, max_conn=(0, ""))

    with um.patch('bin.robot.robot_excl', return_value=(excl, '/dev/null')):
        normal, wizard, friend, wlist = robot.check(tm=26.0, from_addr="faddr", max_call=1000, sec=10000, conf=conf, suicide=False)
        assert normal == 0 and wizard == 0 and friend == 1
        assert wlist == []


def test_robot_check_initial_creation_branch():
    output_conf = config.OutputConf(
        status=lambda x: None,
        header=lambda x: None,
        body=lambda x: None,
        flush=lambda: None
    )
    conf = config.Config(output_conf=output_conf, user="wiz", bname="b", wizard=True)

    with um.patch('bin.robot.robot_excl', return_value=(robot.Excl(excl=[], who={}, max_conn=(0, "")), '/dev/null')):
        normal, wizard, friend, wlist = robot.check(tm=100.0, from_addr="newaddr", max_call=1000, sec=10000, conf=conf, suicide=False)
        assert normal == 0 and wizard == 0 and friend == 0
        assert wlist == []
