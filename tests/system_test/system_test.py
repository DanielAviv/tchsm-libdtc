#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from os import chdir, environ
from os.path import exists, abspath, isdir, isfile
from tempfile import mkdtemp
import shutil
from commands import getstatusoutput
import subprocess
from threading import Timer
import argparse
from time import time

"""
Module for System Testing

To add a new test add it in the test array in main.
"""

__author__ = "Daniel Aviv"
__email__ = "daniel_avivnotario@hotmail.com"
__credits__ = ["Francisco Montoto", "Francisco Cifuentes"]
__status__ = "Development"

DUMP = ""
NODE_EXEC = "../../build/src"
TEST_EXEC_FOLDER = abspath("../../build/tests/system_test")

CONFIG_CREATOR_PATH = abspath("../../scripts/create_config.py")

NODE_RDY = "Both socket binded, node ready to talk with the Master."
TEST_TIMEOUT = 15


def erase_dump():
    if exists(DUMP):
        shutil.rmtree(DUMP)
    return 0


def exec_node(config):
    if not isdir(NODE_EXEC):
        return None, 1, "ERROR: Path doesn't exists >> " + NODE_EXEC

    node = None
    try:
        node = subprocess.Popen([NODE_EXEC + "/node", "-c", config + ".conf"], stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    except OSError as e:
        return node, 1, "ERROR: Exec could not be accesed >> " + NODE_EXEC + "/node"

    timer = Timer(TEST_TIMEOUT, node.terminate)
    timer.start()

    stdout_lines = iter(node.stderr.readline, "")
    for stdout_line in stdout_lines:
        if NODE_RDY in stdout_line:
            break

    if timer.is_alive():
        timer.cancel()
        return node, 0, ""
    else:
        return node, 1, "FAILURE: Timeout"


def exec_master(master_args, master_name):
    if isfile("cryptoki.conf"):
        environ["TCHSM_CONFIG"] = abspath("cryptoki.conf")
    else:
        return None, 1, "ERROR: TCHSM_CONFIG env. var. could not be set."

    master = None
    try:
        master = subprocess.Popen(master_args, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    except OSError:
        return None, 1, "ERROR: Exec could not be accesed >> " + master_name

    timer = Timer(TEST_TIMEOUT, master.terminate)
    if master is not None:
        timer.start()

    master.wait()

    if timer.is_alive():
        timer.cancel()
        if master.returncode != 0:
            return master, master.returncode, "FAILURE: Master return code: " + str(master.returncode)
        return None, master.returncode, ""
    else:
        return master, 1, "FAILURE: Timeout"


def create_dummy_file():
    fd = open("to_sign.txt", "w")
    fd.write(":)\n")
    return fd


# NODE ONLY TESTS
def test_one_node():
    status, output = getstatusoutput("python " + CONFIG_CREATOR_PATH + " 127.0.0.1:2121:2122")
    if(status != 0):
        return 1, "ERROR: Configuration files could not be created."

    proc, ret, mess = exec_node("node1")

    if proc is not None:
        proc.stderr.close()
        proc.terminate()

    return ret, mess


def test_two_nodes():
    status, output = getstatusoutput("python " + CONFIG_CREATOR_PATH + " 127.0.0.1:2121:2122 127.0.0.1:2123:2124")
    if(status != 0):
        return 1, "ERROR: Configuration files could not be created."

    node1, ret1, mess1 = exec_node("node1")
    if ret1 == 1:
        return 1, mess1

    node2, ret2, mess2 = exec_node("node2")

    if node1 is not None:
        node1.stderr.close()
        node1.terminate()

    if node2 is not None:
        node2.stderr.close()
        node2.terminate()

    return ret2, mess2


def test_opening_closing_node():
    status, output = getstatusoutput("python " + CONFIG_CREATOR_PATH + " 127.0.0.1:2121:2122")
    if(status != 0):
        return 1, "ERROR: Configuration files could not be created."

    node, ret, mess = exec_node("node1")
    if ret == 1:
        return 1, mess

    if node is not None:
        node.stderr.close()
        node.terminate()

    node, ret, mess = exec_node("node1")
    return ret, mess


def test_open_close_with_node_open():
    status, output = getstatusoutput("python " + CONFIG_CREATOR_PATH + " 127.0.0.1:2121:2122 127.0.0.1:2123:2124")
    if(status != 0):
        return 1, "ERROR: Configuration files could not be created."

    node1, ret1, mess1 = exec_node("node1")
    if ret1 == 1:
        return 1, mess1

    node2, ret2, mess2 = exec_node("node2")

    if node1 is not None:
        node1.stderr.close()
        node1.terminate()

    node3, ret3, mess3 = exec_node("node1")
    if ret3 == 1:
        return 1, mess3

    if node3 is not None:
        node3.stderr.close()
        node3.terminate()

    if node2 is not None:
        node2.stderr.close()
        node2.terminate()

    return ret2, mess2


# MASTER TESTS
def test_master_one_node(master_args, master_name):
    status, output = getstatusoutput("python " + CONFIG_CREATOR_PATH + " 127.0.0.1:2131:2132")
    if status != 0:
        return 1, "ERROR: Configuration files could not be created."

    node_proc, node_ret, node_mess = exec_node("node1")
    if node_ret == 1:
        return 1, node_mess

    master, master_ret, master_mess = exec_master(master_args, master_name)

    if node_proc is not None:
        node_proc.stderr.close()
        node_proc.terminate()

    if master is not None:
        master.stdout.close()
        master.stderr.close()

    return master_ret, master_mess


def test_master_two_nodes(master_args, master_name):
    status, output = getstatusoutput("python " + CONFIG_CREATOR_PATH + " 127.0.0.1:2121:2122 127.0.0.1:2123:2124")
    if status != 0:
        return 1, "ERROR: Configuration files could not be created."

    node_proc1, node_ret1, node_mess1 = exec_node("node1")
    if node_ret1 == 1:
        return 1, node_mess1

    node_proc2, node_ret2, node_mess2 = exec_node("node2")
    if node_ret2 == 1:
        return 1, node_mess2

    master, master_ret, master_mess = exec_master(master_args, master_name)

    if node_proc1 is not None:
        node_proc1.stderr.close()
        node_proc1.terminate()

    if node_proc2 is not None:
        node_proc2.stderr.close()
        node_proc2.terminate()

    if master is not None:
        master.stdout.close()
        master.stderr.close()

    return master_ret, master_mess


def test_pkcs11_one_node():
    dummy_file = create_dummy_file()
    master_args = [TEST_EXEC_FOLDER + "/pkcs_11_test", "-cf", dummy_file.name, "-p", "1234"]
    ret, mess = test_master_one_node(master_args, "pkcs_11_test")

    dummy_file.close()
    return ret, mess


def test_pkcs11_two_nodes():
    dummy_file = create_dummy_file()
    master_args = [TEST_EXEC_FOLDER + "/pkcs_11_test", "-cf", dummy_file.name, "-p", "1234"]
    ret, mess = test_master_two_nodes(master_args, "pkcs_11_test")

    dummy_file.close()
    return ret, mess


def test_dtc_master_one_node():
    master_args = [TEST_EXEC_FOLDER + "/dtc_master_test", abspath("./master.conf")]
    return test_master_one_node(master_args, "dtc_master_test")


def test_dtc_master_two_nodes():
    master_args = [TEST_EXEC_FOLDER + "/dtc_master_test", abspath("./master.conf")]
    return test_master_two_nodes(master_args, "dtc_master_test")


def pretty_print(index, name, result, mess, runtime, verbosity):
    if result == 0:
        if verbosity:
            print str(index) + " .- " + name + " passed! Running time: " + str(runtime)[:6] + " seconds."
    else:
        print str(index) + " .- " + name + " failed!"
        print "      " + str(mess)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="System Testing")
    parser.add_argument("node_exec",
                        help="path of the folder where node executable is",
                        type=str)
    parser.add_argument("-v",
                        "--verbosity",
                        help="specify this if you want to see every running test",
                        default=False,
                        action="store_true")
    parser.add_argument("-s",
                        "--store_failed_dumps",
                        help="specify this if you want to save dump folders",
                        default=False,
                        action="store_true")
    args = parser.parse_args()

    global NODE_EXEC
    NODE_EXEC = abspath(args.node_exec)

    print(" --- Testing starting --- \n")

    tests = [("TEST ONE NODE", test_one_node),
             ("TEST TWO NODE", test_two_nodes),
             ("TEST OPEN CLOSED NODE", test_opening_closing_node),
             ("TEST OPEN CLOSE w/ NODE OPEN", test_open_close_with_node_open),
             ("TEST PKCS11 ONE NODE", test_pkcs11_one_node),
             ("TEST PKCS11 TWO NODES", test_pkcs11_two_nodes),
             ("TEST DTC MASTER BASIC", test_dtc_master_one_node),
             ("TEST DTC MASTER TWO NODES", test_dtc_master_two_nodes)]

    tests_passed = 0
    tests_runned = len(tests)
    total_time = 0

    for index, test in zip(range(1, len(tests) + 1), tests):
        global DUMP
        DUMP = mkdtemp(prefix="test_" + str(index) + "_", dir="./")
        chdir(DUMP)

        name, func = test

        start = time()
        result, mess = func()
        end = time()
        total_time += end - start

        chdir("..")
        if result == 0:
            tests_passed += 1
            erase_dump()

        if not args.store_failed_dumps:
            erase_dump()

        pretty_print(index, name, result, mess, end - start, args.verbosity)

    passing_string = "|"*tests_passed + " "*(tests_runned-tests_passed)
    print("\n --- Tests passed " + str(tests_passed) + "/" + str(tests_runned) + ": [" + passing_string + "] ---")
    print(" --- Total run time: " + str(total_time)[:6] + " seconds ---")

    return 0


if __name__ == "__main__":
    main(sys.argv)
