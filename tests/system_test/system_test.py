#!/usr/bin/env python
# -*- coding: utf-8 -*-

<<<<<<< 3915a949ba69999be9612735e4036f328eab34c9
import argparse
import shutil
import subprocess
import sys
from commands import getstatusoutput
from os import chdir, environ
from os.path import join, exists, abspath, isdir, isfile
from tempfile import mkdtemp
from threading import Timer
=======
import sys
from os import chdir, environ
from os.path import exists, abspath, isdir, isfile
from tempfile import mkdtemp
import shutil
from commands import getstatusoutput
import subprocess
from threading import Timer
import argparse
>>>>>>> Added tests related to the master, more to be added soon
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
<<<<<<< fde8daab1d3e31c4390b7f1c12d19af634e80a72
<<<<<<< 3915a949ba69999be9612735e4036f328eab34c9
EXEC_PATH = ""
CONFIG_CREATOR_PATH = abspath("../../scripts/create_config.py")

NODE_RDY = "Both socket binded, node ready to talk with the Master."

NODE_TIMEOUT = 5
MASTER_TIMEOUT = 20
=======
NODE_EXEC = ""
=======
NODE_EXEC = "../../build/src"
>>>>>>> Tests are up and running :).
TEST_EXEC_FOLDER = abspath("../../build/tests/system_test")

CONFIG_CREATOR_PATH = abspath("../../scripts/create_config.py")

NODE_RDY = "Both socket binded, node ready to talk with the Master."
<<<<<<< fde8daab1d3e31c4390b7f1c12d19af634e80a72
TEST_TIMEOUT = 10
>>>>>>> Added tests related to the master, more to be added soon
=======
TEST_TIMEOUT = 15
>>>>>>> Tests are up and running :).


def erase_dump():
    if exists(DUMP):
        shutil.rmtree(DUMP)
    return 0


def exec_node(config):
<<<<<<< 3915a949ba69999be9612735e4036f328eab34c9
    if not isdir(EXEC_PATH):
        return None, 1, "ERROR: Path doesn't exists >> " + EXEC_PATH

    if not isdir(join(EXEC_PATH, "src")):
        return None, 1, "ERROR: Path doesn't exists >> " + EXEC_PATH + "/src"

    node = None
    try:
        node = subprocess.Popen(
            [EXEC_PATH + "/src/node",
             "-c",
             config + ".conf"],
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE)
    except OSError as e:
        return node, 1, "ERROR: Exec could not be accesed >> " + EXEC_PATH + "/src/node"

    timer = Timer(NODE_TIMEOUT, node.terminate)
=======
    if not isdir(NODE_EXEC):
        return None, 1, "ERROR: Path doesn't exists >> " + NODE_EXEC

    node = None
    try:
        node = subprocess.Popen([NODE_EXEC + "/node", "-c", config + ".conf"], stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    except OSError as e:
        return node, 1, "ERROR: Exec could not be accesed >> " + NODE_EXEC + "/node"

    timer = Timer(TEST_TIMEOUT, node.terminate)
>>>>>>> Added tests related to the master, more to be added soon
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


<<<<<<< fde8daab1d3e31c4390b7f1c12d19af634e80a72
<<<<<<< 3915a949ba69999be9612735e4036f328eab34c9
def exec_master(master_args, master_name, cryptoki_conf="cryptoki.conf"):
    if isfile(cryptoki_conf):
        environ["TCHSM_CONFIG"] = abspath(cryptoki_conf)
    else:
        return None, 1, "ERROR: TCHSM_CONFIG env. var. could not be set."

    master = None
    try:
        master = subprocess.Popen(
            master_args,
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE)
    except OSError:
        return None, 1, "ERROR: Exec could not be accesed >> " + master_name

    timer = Timer(MASTER_TIMEOUT, master.terminate)
    if master is not None:
        timer.start()

    master.wait()

    if timer.is_alive():
        timer.cancel()
        if master.returncode != 0:
            return master, master.returncode, "FAILURE: Master return code: " + str(master.returncode)
        return None, master.returncode, ""
=======
def exec_master(signing_file, with_key=False):
=======
def exec_master(master_args, master_name):
>>>>>>> Tests are up and running :).
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
<<<<<<< fde8daab1d3e31c4390b7f1c12d19af634e80a72
        return master, 0, ""
>>>>>>> Added tests related to the master, more to be added soon
=======
        if master.returncode != 0:
            return master, master.returncode, "FAILURE: Master return code: " + str(master.returncode)
        return None, master.returncode, ""
>>>>>>> Tests are up and running :).
    else:
        return master, 1, "FAILURE: Timeout"


<<<<<<< 3915a949ba69999be9612735e4036f328eab34c9
def close_node(node_proc):
    if node_proc is not None:
        node_proc.stderr.close()
        node_proc.terminate()


def close_master(master):
    if master is not None:
        master.stdout.close()
        master.stderr.close()


def close_nodes(nodes):
    for node in nodes:
        close_node(node)


=======
>>>>>>> Added tests related to the master, more to be added soon
def create_dummy_file():
    fd = open("to_sign.txt", "w")
    fd.write(":)\n")
    return fd


# NODE ONLY TESTS
def test_one_node():
<<<<<<< 3915a949ba69999be9612735e4036f328eab34c9
    status, output = getstatusoutput(
        "python " + CONFIG_CREATOR_PATH + " 127.0.0.1:2121:2122")
=======
    status, output = getstatusoutput("python " + CONFIG_CREATOR_PATH + " 127.0.0.1:2121:2122")
>>>>>>> Added tests related to the master, more to be added soon
    if(status != 0):
        return 1, "ERROR: Configuration files could not be created."

    proc, ret, mess = exec_node("node1")
<<<<<<< 3915a949ba69999be9612735e4036f328eab34c9
    close_node(proc)
=======

    if proc is not None:
        proc.stderr.close()
        proc.terminate()

>>>>>>> Added tests related to the master, more to be added soon
    return ret, mess


def test_two_nodes():
<<<<<<< 3915a949ba69999be9612735e4036f328eab34c9
    status, output = getstatusoutput(
        "python " + CONFIG_CREATOR_PATH + " 127.0.0.1:2121:2122 127.0.0.1:2123:2124")
=======
    status, output = getstatusoutput("python " + CONFIG_CREATOR_PATH + " 127.0.0.1:2121:2122 127.0.0.1:2123:2124")
>>>>>>> Added tests related to the master, more to be added soon
    if(status != 0):
        return 1, "ERROR: Configuration files could not be created."

    node1, ret1, mess1 = exec_node("node1")
    if ret1 == 1:
<<<<<<< 3915a949ba69999be9612735e4036f328eab34c9
        close_node(node1)
=======
>>>>>>> Added tests related to the master, more to be added soon
        return 1, mess1

    node2, ret2, mess2 = exec_node("node2")

<<<<<<< 3915a949ba69999be9612735e4036f328eab34c9
    close_nodes([node1, node2])
=======
    if node1 is not None:
        node1.stderr.close()
        node1.terminate()

    if node2 is not None:
        node2.stderr.close()
        node2.terminate()

>>>>>>> Added tests related to the master, more to be added soon
    return ret2, mess2


def test_opening_closing_node():
<<<<<<< 3915a949ba69999be9612735e4036f328eab34c9
    status, output = getstatusoutput(
        "python " + CONFIG_CREATOR_PATH + " 127.0.0.1:2121:2122")
=======
    status, output = getstatusoutput("python " + CONFIG_CREATOR_PATH + " 127.0.0.1:2121:2122")
>>>>>>> Added tests related to the master, more to be added soon
    if(status != 0):
        return 1, "ERROR: Configuration files could not be created."

    node, ret, mess = exec_node("node1")
    if ret == 1:
<<<<<<< 3915a949ba69999be9612735e4036f328eab34c9
        close_node(node)
        return 1, mess

    close_node(node)

    node, ret, mess = exec_node("node1")
    close_node(node)
=======
        return 1, mess

    if node is not None:
        node.stderr.close()
        node.terminate()

    node, ret, mess = exec_node("node1")
>>>>>>> Added tests related to the master, more to be added soon
    return ret, mess


def test_open_close_with_node_open():
<<<<<<< 3915a949ba69999be9612735e4036f328eab34c9
    status, output = getstatusoutput(
        "python " + CONFIG_CREATOR_PATH + " 127.0.0.1:2121:2122 127.0.0.1:2123:2124")
=======
    status, output = getstatusoutput("python " + CONFIG_CREATOR_PATH + " 127.0.0.1:2121:2122 127.0.0.1:2123:2124")
>>>>>>> Added tests related to the master, more to be added soon
    if(status != 0):
        return 1, "ERROR: Configuration files could not be created."

    node1, ret1, mess1 = exec_node("node1")
    if ret1 == 1:
<<<<<<< 3915a949ba69999be9612735e4036f328eab34c9
        close_node(node1)
=======
>>>>>>> Added tests related to the master, more to be added soon
        return 1, mess1

    node2, ret2, mess2 = exec_node("node2")

<<<<<<< 3915a949ba69999be9612735e4036f328eab34c9
    close_node(node1)

    node3, ret3, mess3 = exec_node("node1")
    if ret3 == 1:
        close_nodes([node3, node2])
        return 1, mess3

    close_nodes([node3, node2])
    return ret2, mess2


def test_stress_open_close():
    status, output = getstatusoutput(
        "python " + CONFIG_CREATOR_PATH + " 127.0.0.1:2121:2122")
    if(status != 0):
        return 1, "ERROR: Configuration files could not be created."

    for i in range(0, 100):
        proc, ret, mess = exec_node("node1")
        close_node(proc)

        if ret != 0:
            return ret, mess

    return 0, ""


def test_stress_simultaneous():
    proc_array = []

    for port in range(2121, 2121 + 60, 2):
        status, output = getstatusoutput(
            "python " + CONFIG_CREATOR_PATH + " 127.0.0.1:" + str(port) + ":" + str(port + 1))
        if (status != 0):
            return 1, "ERROR: Configuration files could not be created."

        proc, ret, mess = exec_node("node1")
        proc_array.append(proc)

        if ret != 0:
            for proc in proc_array:
                close_node(proc)

            return ret, mess

    for proc in proc_array:
        close_node(proc)

    return 0, ""


# MASTER TESTS
def test_master_one_node(master_args, master_name):
    status, output = getstatusoutput(
        "python " + CONFIG_CREATOR_PATH + " 127.0.0.1:2131:2132")
=======
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
>>>>>>> Added tests related to the master, more to be added soon
    if status != 0:
        return 1, "ERROR: Configuration files could not be created."

    node_proc, node_ret, node_mess = exec_node("node1")
<<<<<<< fde8daab1d3e31c4390b7f1c12d19af634e80a72
<<<<<<< 3915a949ba69999be9612735e4036f328eab34c9
    if node_ret == 1:
        close_node(node_proc)
        return 1, node_mess

    master, master_ret, master_mess = exec_master(master_args, master_name)

    close_node(node_proc)
    close_master(master)
    return master_ret, master_mess


def test_master_two_nodes(master_args, master_name):
    status, output = getstatusoutput(
        "python " + CONFIG_CREATOR_PATH + " 127.0.0.1:2121:2122 127.0.0.1:2123:2124")
    if status != 0:
        return 1, "ERROR: Configuration files could not be created."

    node_proc1, node_ret1, node_mess1 = exec_node("node1")
    if node_ret1 == 1:
        close_node(node_proc1)
        return 1, node_mess1

    node_proc2, node_ret2, node_mess2 = exec_node("node2")
    if node_ret2 == 1:
        close_node(node_proc1)
        close_node(node_proc2)
        return 1, node_mess2

    master, master_ret, master_mess = exec_master(master_args, master_name)

    close_nodes([node_proc1, node_proc2])
    close_master(master)
    return master_ret, master_mess


def test_master_twice(master_args, master_name):
    status, output = getstatusoutput(
        "python " + CONFIG_CREATOR_PATH + " 127.0.0.1:2121:2122 127.0.0.1:2123:2124")
    if status != 0:
        return 1, "ERROR: Configuration files could not be created."

    node_proc1, node_ret1, node_mess1 = exec_node("node1")
    if node_ret1 == 1:
        close_node(node_proc1)
        return 1, node_mess1

    node_proc2, node_ret2, node_mess2 = exec_node("node2")
    if node_ret2 == 1:
        close_nodes([node_proc1, node_proc2])
        return 1, node_mess2

    master, master_ret, master_mess = exec_master(master_args, master_name)
    close_master(master)

    if master_ret != 0:
        close_nodes([node_proc1, node_proc2])
        return master_ret, master_mess

    master, master_ret, master_mess = exec_master(master_args, master_name)

    close_nodes([node_proc1, node_proc2])
    close_master(master)
    return master_ret, master_mess


def test_three_nodes_one_down(master_args, master_name):
    node_info = " 127.0.0.1:2121:2122 127.0.0.1:2123:2124 127.0.0.1:2125:2126"
    status, output = getstatusoutput(
        "python " + CONFIG_CREATOR_PATH + node_info)
    if status != 0:
        return 1, "ERROR: Configuration files could not be created."

    node_proc1, node_ret1, node_mess1 = exec_node("node1")
    if node_ret1 == 1:
        close_node(node_proc1)
        return 1, node_mess1

    node_proc2, node_ret2, node_mess2 = exec_node("node2")
    if node_ret2 == 1:
        close_nodes([node_proc1, node_proc2])
        return 1, node_mess2

    node_proc3, node_ret3, node_mess3 = exec_node("node3")
    if node_ret2 == 1:
        close_nodes([node_proc1, node_proc2, node_proc3])
        return 1, node_mess3

    master, master_ret, master_mess = exec_master(master_args, master_name)
    close_master(master)

    if master_ret != 0:
        close_nodes([node_proc1, node_proc2, node_proc3])

        return master_ret, master_mess

    close_node(node_proc3)

    master, master_ret, master_mess = exec_master(master_args, master_name)
    close_nodes([node_proc1, node_proc2])
    close_master(master)
    return master_ret, master_mess


def test_insuff_threshold_bordercase(master_args, master_name):
    status, output = getstatusoutput(
        "python " + CONFIG_CREATOR_PATH + " 127.0.0.1:2121:2122 -ct -th 0")
=======

=======
>>>>>>> Tests are up and running :).
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


<<<<<<< fde8daab1d3e31c4390b7f1c12d19af634e80a72
def test_pkcs11_creating_key():
    return test_pkcs11_basic(True)


def test_pkcs11_two_nodes(with_key=False):
    status, output = getstatusoutput("python " + CONFIG_CREATOR_PATH + " 127.0.0.1:2131:2132")
>>>>>>> Added tests related to the master, more to be added soon
    if status != 0:
        return 1, "ERROR: Configuration files could not be created."

    node_proc, node_ret, node_mess = exec_node("node1")
<<<<<<< 3915a949ba69999be9612735e4036f328eab34c9
    if node_ret == 1:
        close_node(node_proc)
        return 1, node_mess

    master, master_ret, master_mess = exec_master(master_args, master_name)
    close_master(master)

    if master_ret != 0:
        close_node(node_proc)
        return master_ret, master_mess

    close_node(node_proc)

    master, master_ret, master_mess = exec_master(master_args, master_name)
    close_master(master)

    if master_ret != 0:
        return 0, ""
    else:
        return 1, "FAILURE: The master should not be able to sign."


def test_insuff_threshold(master_args, master_name):
    node_info = " 127.0.0.1:2121:2122 127.0.0.1:2123:2124 127.0.0.1:2125:2126"
    status, output = getstatusoutput(
        "python " + CONFIG_CREATOR_PATH + node_info + "-ct -th 3")
    if status != 0:
        return 1, "ERROR: Configuration files could not be created."

    node_proc1, node_ret1, node_mess1 = exec_node("node1")
    if node_ret1 == 1:
        close_node(node_proc1)
        return 1, node_mess1

    node_proc2, node_ret2, node_mess2 = exec_node("node2")
    if node_ret2 == 1:
        close_nodes([node_proc1, node_proc2])
        return 1, node_mess2

    node_proc3, node_ret3, node_mess3 = exec_node("node3")
    if node_ret2 == 1:
        close_nodes([node_proc1, node_proc2, node_proc3])
        return 1, node_mess3

    master, master_ret, master_mess = exec_master(master_args, master_name)
    close_master(master)

    if master_ret != 0:
        close_nodes([node_proc1, node_proc2])
        return master_ret, master_mess

    close_node(node_proc3)

    master, master_ret, master_mess = exec_master(master_args, master_name)
    close_nodes([node_proc1, node_proc2])
    close_master(master)

    if master_ret != 0:
        return 0, ""
    else:
        return 1, "FAILURE: The master should not be able to sign."


def test_three_nodes_two_open(master_args, master_name):
    node_info = " 127.0.0.1:2121:2122 127.0.0.1:2123:2124 127.0.0.1:2125:2126"
    status, output = getstatusoutput(
        "python " + CONFIG_CREATOR_PATH + node_info)
    if status != 0:
        return 1, "ERROR: Configuration files could not be created."

    node_proc1, node_ret1, node_mess1 = exec_node("node1")
    if node_ret1 == 1:
        close_node(node_proc1)
        return 1, node_mess1

    node_proc2, node_ret2, node_mess2 = exec_node("node2")
    if node_ret2 == 1:
        close_nodes([node_proc1, node_proc2])
        return 1, node_mess2

    master, master_ret, master_mess = exec_master(master_args, master_name)
    close_nodes([node_proc1, node_proc2])
    close_master(master)
    return master_ret, master_mess


def test_master_stress_open_close(master_args, master_name):
    status, output = getstatusoutput(
        "python " + CONFIG_CREATOR_PATH + " 127.0.0.1:2121:2122 127.0.0.1:2123:2124")
    if status != 0:
        return 1, "ERROR: Configuration files could not be created."

    node_proc1, node_ret1, node_mess1 = exec_node("node1")
    if node_ret1 == 1:
        close_node(node_proc1)
        return 1, node_mess1

    node_proc2, node_ret2, node_mess2 = exec_node("node2")
    if node_ret2 == 1:
        close_nodes([node_proc1, node_proc2])
        return 1, node_mess2

    master = None
    for i in range(0, 10):
        master, master_ret, master_mess = exec_master(master_args, master_name)
        close_master(master)

        if master_ret != 0:
            close_nodes([node_proc1, node_proc2])
            return master_ret, master_mess

    close_nodes([node_proc1, node_proc2])
    return 0, ""


def test_stress_multiple_masters(master_args, master_name):
    status, output = getstatusoutput(
        "python " + CONFIG_CREATOR_PATH + " 127.0.0.1:2121:2122 127.0.0.1:2123:2124 -m 10")
    if status != 0:
        return 1, "ERROR: Configuration files could not be created."

    node_proc1, node_ret1, node_mess1 = exec_node("node1")
    if node_ret1 == 1:
        close_node(node_proc1)
        return 1, node_mess1

    node_proc2, node_ret2, node_mess2 = exec_node("node2")
    if node_ret2 == 1:
        close_nodes([node_proc1, node_proc2])
        return 1, node_mess2

    for i in range(1, 11):
        master, master_ret, master_mess = exec_master(
            master_args, master_name, "cryptoki" + str(i) + ".conf")
        close_master(master)

        if master_ret != 0:
            close_nodes([node_proc1, node_proc2])
            return master_ret, master_mess

    close_nodes([node_proc1, node_proc2])
    return 0, ""


def test_cryptoki_wout_key():
    status, output = getstatusoutput(
        "python " + CONFIG_CREATOR_PATH + " 127.0.0.1:2121:2122 127.0.0.1:2123:2124")
    if status != 0:
        return 1, "ERROR: Configuration files could not be created."

    node_proc1, node_ret1, node_mess1 = exec_node("node1")
    if node_ret1 == 1:
        close_node(node_proc1)
        return 1, node_mess1

    node_proc2, node_ret2, node_mess2 = exec_node("node2")
    if node_ret2 == 1:
        close_nodes([node_proc1, node_proc2])
        return 1, node_mess2

    dummy_file = create_dummy_file()
    master_args = [join(
                   EXEC_PATH,
                   "tests/system_test/pkcs_11_test"),
                   "-cf",
                   dummy_file.name,
                   "-p",
                   "1234"]
    master_name = "pkcs_11_test"
    master, master_ret, master_mess = exec_master(master_args, master_name)
    close_master(master)

    if master_ret != 0:
        close_nodes([node_proc1, node_proc2])
        return master_ret, master_mess

    master_args = [join(
                   EXEC_PATH,
                   "tests/system_test/pkcs_11_test"),
                   "-f",
                   dummy_file.name,
                   "-p",
                   "1234"]
    master_name = "pkcs_11_test"
    master, master_ret, master_mess = exec_master(master_args, master_name)
    dummy_file.close()

    close_nodes([node_proc1, node_proc2])
    close_master(master)
    return master_ret, master_mess


def test_two_masters_one_nodes(master_args, master_name):
    status, output = getstatusoutput(
        "python " + CONFIG_CREATOR_PATH + " 127.0.0.1:2121:2122 -m 2")
    if status != 0:
        return 1, "ERROR: Configuration files could not be created."

    node_proc1, node_ret1, node_mess1 = exec_node("node1")
    if node_ret1 == 1:
        close_node(node_proc1)
        return 1, node_mess1

    master, master_ret, master_mess = exec_master(
        master_args, master_name, "cryptoki1.conf")
    close_master(master)

    if master_ret != 0:
        close_node(node_proc1)
        return master_ret, master_mess

    master, master_ret, master_mess = exec_master(
        master_args, master_name, "cryptoki2.conf")

    close_node(node_proc1)
    close_master(master)
    return master_ret, master_mess


def test_two_masters_two_nodes(master_args, master_name):
    status, output = getstatusoutput(
        "python " + CONFIG_CREATOR_PATH + " 127.0.0.1:2121:2122 127.0.0.1:2123:2124 -m 2")
    if status != 0:
        return 1, "ERROR: Configuration files could not be created."

    node_proc1, node_ret1, node_mess1 = exec_node("node1")
    if node_ret1 == 1:
        close_node(node_proc1)
        return 1, node_mess1

    node_proc2, node_ret2, node_mess2 = exec_node("node2")
    if node_ret2 == 1:
        close_nodes([node_proc1, node_proc2])
        return 1, node_mess2

    master, master_ret, master_mess = exec_master(
        master_args, master_name, "cryptoki1.conf")
    close_master(master)

    if master_ret != 0:
        close_nodes([node_proc1, node_proc2])
        return master_ret, master_mess

    master, master_ret, master_mess = exec_master(
        master_args, master_name, "cryptoki2.conf")

    close_nodes([node_proc1, node_proc2])
    close_master(master)
    return master_ret, master_mess


def test_two_masters_simultaneous(master_args, master_name):
    status, output = getstatusoutput(
        "python " + CONFIG_CREATOR_PATH + " 127.0.0.1:2121:2122 127.0.0.1:2123:2124 -m 2")
    if status != 0:
        return 1, "ERROR: Configuration files could not be created."

    node_proc1, node_ret1, node_mess1 = exec_node("node1")
    if node_ret1 == 1:
        close_node(node_proc1)
        return 1, node_mess1

    node_proc2, node_ret2, node_mess2 = exec_node("node2")
    if node_ret2 == 1:
        close_nodes([node_proc1, node_proc2])
        return 1, node_mess2

    master1, master_ret1, master_mess1 = exec_master(
        master_args, master_name, "cryptoki1.conf")
    master2, master_ret2, master_mess2 = exec_master(
        master_args, master_name, "cryptoki2.conf")

    if master_ret1 != 0:
        close_nodes([node_proc1, node_proc2])
        return master_ret1, master_mess1

    if master_ret2 != 0:
        close_nodes([node_proc1, node_proc2])
        return master_ret2, master_mess2

    close_nodes([node_proc1, node_proc2])
    close_master(master1)
    close_master(master2)
    return 0, ""


def test_two_masters_thres2_nodes3(master_args, master_name):
    info = " 127.0.0.1:2121:2122 127.0.0.1:2123:2124 127.0.0.1:2125:2126 -m 2"
    status, output = getstatusoutput("python " + CONFIG_CREATOR_PATH + info)
    if status != 0:
        return 1, "ERROR: Configuration files could not be created."

    node_proc1, node_ret1, node_mess1 = exec_node("node1")
    if node_ret1 == 1:
        close_node(node_proc1)
        return 1, node_mess1

    node_proc2, node_ret2, node_mess2 = exec_node("node2")
    if node_ret2 == 1:
        close_nodes([node_proc1, node_proc2])
        return 1, node_mess2

    master1, master_ret1, master_mess1 = exec_master(
        master_args, master_name, "cryptoki1.conf")
    close_master(master1)

    if master_ret1 != 0:
        close_nodes([node_proc1, node_proc2])
        return master_ret1, master_mess1

    master2, master_ret2, master_mess2 = exec_master(
        master_args, master_name, "cryptoki2.conf")

    close_nodes([node_proc1, node_proc2])
    close_master(master2)
    return master_ret2, master_mess2


# INTERFACES FOR DIFFERENT TESTS
def perform_test_on_pkcs11(test):
    dummy_file = create_dummy_file()
    master_args = [join(
                   EXEC_PATH,
                   "tests/system_test/pkcs_11_test"),
                   "-cf",
                   dummy_file.name,
                   "-p",
                   "1234"]
    ret, mess = test(master_args, "pkcs_11_test")

    dummy_file.close()
    return ret, mess


def perform_test_on_dtc(test):
    master_args = [join(
                   EXEC_PATH,
                   "tests/system_test/dtc_master_test"),
                   abspath("./master.conf")]
    return test(master_args, "dtc_master_test")


def pretty_print(index, name, result, mess, runtime, verbosity):
    if result == 0:
        if verbosity:
            print str(index) + ".- " + name + " passed! Run time: " + str(runtime)[:6] + " seconds."
    else:
        print str(index) + ".- " + name + " failed!"
=======
=======
def test_master_two_nodes(master_args, master_name):
    status, output = getstatusoutput("python " + CONFIG_CREATOR_PATH + " 127.0.0.1:2121:2122 127.0.0.1:2123:2124")
    if status != 0:
        return 1, "ERROR: Configuration files could not be created."

    node_proc1, node_ret1, node_mess1 = exec_node("node1")
    if node_ret1 == 1:
        return 1, node_mess1
>>>>>>> Tests are up and running :).

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
>>>>>>> Added tests related to the master, more to be added soon
        print "      " + str(mess)


def main(argv=None):
<<<<<<< 3915a949ba69999be9612735e4036f328eab34c9
    global NODE_TIMEOUT
    global MASTER_TIMEOUT

    parser = argparse.ArgumentParser(description="System Testing")
    parser.add_argument("build_path",
                        help="path of the folder where the project is build",
=======
    parser = argparse.ArgumentParser(
        description="System Testing")
    parser.add_argument("node_exec",
                        help="path of the folder where node executable is",
>>>>>>> Added tests related to the master, more to be added soon
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
<<<<<<< 3915a949ba69999be9612735e4036f328eab34c9
    parser.add_argument("-nt",
                        "--node_timeout",
                        help="maximum time for nodes to respond (default: 5 seg)",
                        default=NODE_TIMEOUT,
                        type=int)
    parser.add_argument("-mt",
                        "--master_timeout",
                        help="maximum time for masters to respond (default: 15 seg)",
                        default=MASTER_TIMEOUT,
                        type=int)
    parser.add_argument("-ws",
                        "--with_stress_tests",
                        help="specify this if you want to add stress tests to the test case",
                        default=False,
                        action="store_true")
    args = parser.parse_args()

    NODE_TIMEOUT = args.node_timeout
    MASTER_TIMEOUT = args.master_timeout

    global EXEC_PATH
    EXEC_PATH = abspath(args.build_path)

    print(" --- Testing starting --- \n")

    tests = [("TEST ONE NODE", test_one_node, None),
             ("TEST TWO NODE", test_two_nodes, None),
             ("TEST OPEN CLOSED NODE", test_opening_closing_node, None),
             ("TEST OPEN CLOSE w/ NODE OPEN",
              test_open_close_with_node_open, None),
             ("TEST PKCS11 ONE NODE",
              perform_test_on_pkcs11, test_master_one_node),
             ("TEST PKCS11 TWO NODES",
              perform_test_on_pkcs11, test_master_two_nodes),
             ("TEST DTC ONE NODE", perform_test_on_dtc, test_master_one_node),
             ("TEST DTC TWO NODES", perform_test_on_dtc,
              test_master_two_nodes),
             ("TEST PKCS11 RUN TWICE",
              perform_test_on_pkcs11, test_master_twice),
             ("TEST DTC RUN TWICE", perform_test_on_dtc, test_master_twice),
             ("TEST PKCS11 THREE NODES, ONE FALLS",
              perform_test_on_pkcs11, test_three_nodes_one_down),
             ("TEST DTC THREE NODES, ONE FALLS",
              perform_test_on_dtc, test_three_nodes_one_down),
             ("TEST PKCS11 THREE NODES, TWO OPEN",
              perform_test_on_pkcs11, test_three_nodes_two_open),
             ("TEST DTC THREE NODES, TWO OPEN",
              perform_test_on_dtc, test_three_nodes_two_open),
             ("TEST PKCS11 INSUFF THRESHOLD BORDER CASE",
              perform_test_on_pkcs11, test_insuff_threshold_bordercase),
             ("TEST DTC INSUFF THRESHOLD BORDER CASE",
              perform_test_on_dtc, test_insuff_threshold_bordercase),
             ("TEST PKCS11 INSUFFICIENT THRESHOLD",
              perform_test_on_pkcs11, test_insuff_threshold),
             ("TEST DTC INSUFFICIENT THRESHOLD",
              perform_test_on_dtc, test_insuff_threshold),
             ("TEST PKCS11 TWO MASTERS ONE NODE",
              perform_test_on_pkcs11, test_two_masters_one_nodes),
             ("TEST DTC TWO MASTERS ONE NODE",
              perform_test_on_dtc, test_two_masters_one_nodes),
             ("TEST PKCS11 TWO MASTERS TWO NODE",
              perform_test_on_pkcs11, test_two_masters_two_nodes),
             ("TEST DTC TWO MASTERS TWO NODE",
              perform_test_on_dtc, test_two_masters_two_nodes),
             ("TEST PKCS11 MASTERS SIMULTANEOUS",
              perform_test_on_pkcs11, test_two_masters_simultaneous),
             ("TEST DTC MASTERS SIMULTANEOUS",
              perform_test_on_dtc, test_two_masters_simultaneous),
             ("TEST PKCS11 MASTERS:2 THRES:2 NODES:3",
              perform_test_on_pkcs11, test_two_masters_thres2_nodes3),
             ("TEST DTC  MASTERS:2 THRES:2 NODES:3",
              perform_test_on_dtc, test_two_masters_thres2_nodes3),
             ("TEST PKCS11 SAME DATABASE", test_cryptoki_wout_key, None)]

    stress_tests = [("NODE STRESS OPEN CLOSE", test_stress_open_close, None),
                    ("NODE STRESS SIMULTANEOUS",
                     test_stress_simultaneous, None),
                    ("PKCS11 STRESS SAME NODE", perform_test_on_pkcs11,
                     test_master_stress_open_close),
                    ("DTC STRESS SAME NODE", perform_test_on_dtc,
                     test_master_stress_open_close),
                    ("PKCS11 STRESS MULTIPLE MASTERS",
                     perform_test_on_pkcs11, test_stress_multiple_masters),
                    ("DTC STRESS MULTIPLE MASTERS", perform_test_on_dtc, test_stress_multiple_masters)]

    if args.with_stress_tests:
        tests.extend(stress_tests)
=======
    args = parser.parse_args()

    global NODE_EXEC
    NODE_EXEC = abspath(args.node_exec)

    print(" --- Testing starting --- \n")

    tests = [("TEST ONE NODE", test_one_node),
             ("TEST TWO NODE", test_two_nodes),
             ("TEST OPEN CLOSED NODE", test_opening_closing_node),
             ("TEST OPEN CLOSE w/ NODE OPEN", test_open_close_with_node_open),
<<<<<<< fde8daab1d3e31c4390b7f1c12d19af634e80a72
             ("TEST PKCS11 BASIC", test_pkcs11_basic),
             ("TEST PKCS11 CREATE KEY", test_pkcs11_creating_key),
             ("TEST PKCS11 TWO NODES", test_pkcs11_two_nodes)]
>>>>>>> Added tests related to the master, more to be added soon
=======
             ("TEST PKCS11 ONE NODE", test_pkcs11_one_node),
             ("TEST PKCS11 TWO NODES", test_pkcs11_two_nodes),
             ("TEST DTC MASTER BASIC", test_dtc_master_one_node),
             ("TEST DTC MASTER TWO NODES", test_dtc_master_two_nodes)]
>>>>>>> Tests are up and running :).

    tests_passed = 0
    tests_runned = len(tests)
    total_time = 0

    for index, test in zip(range(1, len(tests) + 1), tests):
        global DUMP
        DUMP = mkdtemp(prefix="test_" + str(index) + "_", dir="./")
        chdir(DUMP)

<<<<<<< 3915a949ba69999be9612735e4036f328eab34c9
        name, func, func_args = test

        start = time()

        if func_args is None:
            result, mess = func()
        else:
            result, mess = func(func_args)

=======
        name, func = test

        start = time()
        result, mess = func()
>>>>>>> Added tests related to the master, more to be added soon
        end = time()
        total_time += end - start

        chdir("..")
        if result == 0:
            tests_passed += 1
            erase_dump()

        if not args.store_failed_dumps:
            erase_dump()

        pretty_print(index, name, result, mess, end - start, args.verbosity)

<<<<<<< 3915a949ba69999be9612735e4036f328eab34c9
    test_percentage = str(
        100 * float(tests_passed) / float(tests_runned))[:5] + "%"
    passing_string = "|" * tests_passed + " " * (tests_runned - tests_passed)
    print("\n --- Tests passed " + str(tests_passed) + "/" + str(tests_runned)
          + " (" + test_percentage + "): [" + passing_string + "] ---")
    print(" --- Total run time: " + str(total_time)[:6] + " seconds ---")

    return tests_runned - tests_passed
=======
    passing_string = "|"*tests_passed + " "*(tests_runned-tests_passed)
    print("\n --- Tests passed " + str(tests_passed) + "/" + str(tests_runned) + ": [" + passing_string + "] ---")
    print(" --- Total run time: " + str(total_time)[:6] + " seconds ---")

    return 0
>>>>>>> Added tests related to the master, more to be added soon


if __name__ == "__main__":
    main(sys.argv)
