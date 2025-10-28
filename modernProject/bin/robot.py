import sys
import time
import os
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

sys.path.insert(0, str(Path(__file__).parent.parent))

from lib import config, logs


magic_robot = "GnWbRobotExcl001"


class UserType(Enum):
    NORMAL = "normal"
    FRIEND = "friend"
    WIZARD = "wizard"


@dataclass
class Who:
    acc_times: List[float]
    oldest_time: float
    nb_connect: int
    nbase: str
    utype: UserType
    uname: str = ""


@dataclass
class Excl:
    excl: List[Tuple[str, int]]
    who: Dict[str, Who]
    max_conn: Tuple[int, str]


min_disp_req = 20


def robot_error(conf: config.Config, nb_conn: int, max_conn: int):
    conf.output_conf.status(403)
    conf.output_conf.header("Content-type: text/html; charset=utf-8")

    conf.output_conf.body("<html><head><title>Access refused</title></head>\n")
    conf.output_conf.body("<body>\n")
    conf.output_conf.body("<h1>Access refused</h1>\n")
    conf.output_conf.body("<p>You are making too many requests in a short time.</p>\n")
    conf.output_conf.body(f"<p>Connections: {nb_conn}, Maximum allowed: {max_conn}</p>\n")
    conf.output_conf.body("<p>Please wait a few seconds before retrying.</p>\n")
    conf.output_conf.body("</body></html>\n")

    raise SystemExit(1)


def robot_excl() -> Tuple[Excl, str]:
    robot_file = os.path.join(os.getcwd(), "gwd_robot.txt")

    excl_data = Excl(
        excl=[],
        who={},
        max_conn=(0, "")
    )

    if not os.path.exists(robot_file):
        return excl_data, robot_file

    try:
        with open(robot_file, 'r') as f:
            first_line = f.readline().strip()
            if first_line != magic_robot:
                logs.syslog(logs.LOG_WARNING, f"Invalid robot file magic: {robot_file}")
                return excl_data, robot_file

            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue

                parts = line.split()
                if len(parts) >= 2:
                    addr = parts[0]
                    count = int(parts[1])
                    excl_data.excl.append((addr, count))

    except Exception as e:
        logs.syslog(logs.LOG_ERR, f"Error reading robot file {robot_file}: {e}")

    return excl_data, robot_file


def save_robot_excl(excl: Excl, robot_file: str):
    try:
        with open(robot_file, 'w') as f:
            f.write(magic_robot + "\n")
            f.write("# GeneWeb robot exclusion file\n")
            f.write("# Format: address count\n")
            f.write("#\n")

            for addr, count in excl.excl:
                f.write(f"{addr} {count}\n")

    except Exception as e:
        logs.syslog(logs.LOG_ERR, f"Error writing robot file {robot_file}: {e}")


def check(tm: float, from_addr: str, max_call: int, sec: int,
          conf: config.Config, suicide: bool) -> Tuple[int, int, int, List[Tuple[str, float]]]:
    excl, robot_file = robot_excl()

    for addr, count in excl.excl:
        if addr == from_addr:
            if suicide:
                excl.excl = [(a, c) for a, c in excl.excl if a != from_addr]
                save_robot_excl(excl, robot_file)
            robot_error(conf, count, max_call)

    who_entry = excl.who.get(from_addr)

    if who_entry is None:
        utype = UserType.NORMAL
        if conf.wizard:
            utype = UserType.WIZARD
        elif conf.friend:
            utype = UserType.FRIEND

        who_entry = Who(
            acc_times=[tm],
            oldest_time=tm,
            nb_connect=1,
            nbase=conf.bname,
            utype=utype,
            uname=conf.user
        )
        excl.who[from_addr] = who_entry
    else:
        cutoff_time = tm - sec
        recent_times = [t for t in who_entry.acc_times if t >= cutoff_time]
        recent_times.append(tm)

        who_entry.acc_times = recent_times
        who_entry.nb_connect = len(recent_times)
        who_entry.oldest_time = recent_times[0] if recent_times else tm

        if who_entry.nb_connect > max_call:
            excl.excl.append((from_addr, who_entry.nb_connect))
            del excl.who[from_addr]
            save_robot_excl(excl, robot_file)

            logs.syslog(logs.LOG_NOTICE,
                       f"Robot blocked: {from_addr} ({who_entry.nb_connect} connections)")
            robot_error(conf, who_entry.nb_connect, max_call)

    max_conn_count, max_conn_addr = excl.max_conn
    if who_entry.nb_connect > max_conn_count:
        excl.max_conn = (who_entry.nb_connect, from_addr)

    normal_robots = sum(1 for w in excl.who.values()
                       if w.utype == UserType.NORMAL and w.nb_connect >= min_disp_req)
    wizard_robots = sum(1 for w in excl.who.values()
                       if w.utype == UserType.WIZARD and w.nb_connect >= min_disp_req)
    friend_robots = sum(1 for w in excl.who.values()
                       if w.utype == UserType.FRIEND and w.nb_connect >= min_disp_req)

    wizard_list = [(w.uname, w.acc_times[-1] if w.acc_times else tm)
                   for w in excl.who.values()
                   if w.utype == UserType.WIZARD and w.nb_connect >= min_disp_req]

    return normal_robots, wizard_robots, friend_robots, wizard_list
