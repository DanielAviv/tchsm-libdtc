#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
from os.path import join
import argparse
import commands
from math import floor

"""
This module creates the configuration files of nodes and masters for testing purposes.
"""

__author__ = "Daniel Aviv"
__email__ = "daniel_avivnotario@hotmail.com"
__credits__ = ["Francisco Montoto", "Francisco Cifuentes"]
__status__ = "Development"

DEFAULT_TIMEOUT = 10

DEFAULT_MASTER_ID = "MASTER_MOCK_ID"

DEFAULT_INTERFACE = "*"

DEFAULT_DATABASE = "node"

DEFAULT_CRYPTOKI_DATABASE = "cryptoki"


def parse_nodes(nodes_info):
    """Tranforms the user input in a node info dictionary.

    nodes_info -- an array with the node info in the format ip:router_port:sub:port
    """
    node_dict = {}

    count = 0
    for node_info in nodes_info:
        node_info_array = node_info.split(":")
        node_public_key, node_private_key = get_keygen()
        node_dict[count] = [node_info_array[1],
                            node_info_array[2],
                            node_public_key,
                            node_private_key,
                            node_info_array[0]]
        count += 1

    return node_dict


def create_n_master_config(
    nodes,
     output_path,
     nb_of_masters,
     instance_id,
     timeout):
    """Creates one config file for each master

    nodes -- dictionary containing the info of the nodes, where the key is the an id, and the value an array containing the info.
    output_path -- where the config files will land
    nb_of_masters -- number of masters
    instance_id -- the prefix that the masters will have as id
    timeout -- conection timeout in the masters config
    """
    masters = {}

    for i in range(1, nb_of_masters + 1):
        index = ""
        if(nb_of_masters):
            index = i

        file_name = join(output_path, "master") + str(i) + ".conf"

        if nb_of_masters == 1:
            file_name = join(output_path, "master") + ".conf"

        config_file = open(file_name, "w")
        master_id, public_master_key, private_master_key = create_master_config(
            "master", config_file, nodes, instance_id + str(index), timeout)
        masters[master_id] = [public_master_key, private_master_key]

        config_file.close()

    return masters


def create_master_config(
    title,
     config_file,
     nodes,
     instance_id,
     timeout,
     master_info=None):
    """Creates one master configuration into the specified file.

    title -- title in the header
    config_file -- file handler where the config will be outputted
    instance_id -- master id in the config
    timeout -- conection timeout in the master config
    master_info -- if provided, the config will use this as public and private key (default None)
    """
    config_file.write(title + ":\n{\n")
    config_file.write("\tnodes = (\n")

    for node_id, info in nodes.iteritems():
        config_file.write("\t\t{\n")
        config_file.write("\t\tip=\"" + info[4] + "\"\n")
        config_file.write("\t\tdealer_port=" + info[0] + "\n")
        config_file.write("\t\tsub_port=" + info[1] + "\n")
        config_file.write("\t\tpublic_key=\"" + info[2] + "\"\n")
        config_file.write("\t\t},\n")

    # Removes extra comma
    config_file.seek(-2, os.SEEK_END)
    config_file.truncate()

    if master_info is None:
        master_info = get_keygen()

    config_file.write("\n\t)\n")
    config_file.write("\tpublic_key=\"" + master_info[0] + "\",\n")
    config_file.write("\tprivate_key=\"" + master_info[1] + "\",\n")
    config_file.write("\tinstance_id=\"" + instance_id + "\",\n")
    config_file.write("\ttimeout=" + str(timeout) + "\n")
    config_file.write("}")

    return instance_id, master_info[0], master_info[1]


def create_node_config(
    config_file,
     node_info,
     masters,
     index,
     interface,
     database):
    """Creates one node configuration into the specified file.

    config_file -- file handler where the config will be outputted
    node_info -- a dictionary containing the node information such as ports and keys
    masters -- a dictionary in which the keys are the mastrs ids and the value the masters public keys
    index -- node id
    interface -- interface in the node config
    database -- prefix in the database path in the nodes config
    """
    config_file.write("node:\n{\n")
    config_file.write("\tmasters = (\n")

    for master_id, master_key in masters.iteritems():
        config_file.write("\t\t{\n")
        config_file.write("\t\tpublic_key=\"" + master_key[0] + "\"\n")
        config_file.write("\t\tid=\"" + master_id + "\"\n")
        config_file.write("\t\t},\n")

    # Removes extra comma
    config_file.seek(-2, os.SEEK_END)
    config_file.truncate()

    config_file.write("\n\t)\n")
    config_file.write("\trouter_port=" + node_info[0] + ",\n")
    config_file.write("\tsub_port=" + node_info[1] + ",\n")
    config_file.write(
        "\tdatabase=\"" +
        database +
     "_" +
     index +
     ".db" +
     "\",\n")
    config_file.write("\tprivate_key=\"" + node_info[3] + "\",\n")
    config_file.write("\tpublic_key=\"" + node_info[2] + "\",\n")
    config_file.write("\tinterface=\"" + interface + "\"\n")
    config_file.write("}")


def get_keygen():
    """Parses the keygen output and returns just the public and private key as strings"""
    keygen_output = commands.getoutput("curve_keygen")

    private_key = keygen_output[-40:]
    public_key = keygen_output[-105:-65]

    return public_key, private_key


def create_n_cryptoki_config(
    nodes,
     output_path,
     instance_id,
     masters,
     timeout,
     cryptoki_database,
     threshold):
    """Creates one cryptoki config file for each master.

    nodes -- dictionary containing the info of the nodes, where the key is the an id, and the value an array containing the info.
    output_path -- where the config files will land
    master_id -- prefix id of the masters
    masters -- dictionary of masters information
    timeout -- conection timeout in the masters config
    cryptoki_database -- prefix in the database path in the cryptoki config
    threshold -- min amount of nodes to the sign to occurr
    """
    for master_id, master_info in masters.iteritems():
        index = ""
        if len(masters) != 1:
            index = master_id[len(instance_id):]
            print index

        file_name = join(output_path, "cryptoki") + index + ".conf"

        if len(masters) == 1:
            file_name = join(output_path, "cryptoki") + ".conf"

        cryptoki_config_file = open(file_name, "w")
        create_master_config(
            "libdtc",
            cryptoki_config_file,
            nodes,
            master_id,
            timeout,
            master_info)
        create_cryptoki_config(
            cryptoki_config_file,
            len(nodes),
            index,
            cryptoki_database,
            threshold)

        cryptoki_config_file.close()


def create_cryptoki_config(
    config_file,
     amount_of_nodes,
     index,
     database_path,
     threshold):
    """Creates one cryptoki configuration into the specified file.

    config_file -- file handler where the config will be outputted
    amount_of_nodes -- total amount of nodes
    index -- cryptoki master id
    database_path -- prefix in the database path in the nodes config
    threshold -- min amount of nodes to the sign to occurr
    """
    config_file.write("\ncryptoki:\n{\n")
    config_file.write(
        "\tdatabase_path=\"" +
        database_path +
     index +
     ".db" +
     "\",\n")
    config_file.write("\tnodes_number=" + str(amount_of_nodes) + ",\n")
    config_file.write("\tthreshold=" + str(threshold) + ",\n")
    config_file.write("\tslots = (\n\t\t{label=\"TCBHSM\"}\n\t)\n")
    config_file.write("}")


def get_default_threshold(amount_of_nodes):
    """Computes default threshold"""
    return int(floor(float(amount_of_nodes) / 2) + 1)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Creates configuration files for testing purposes")
    parser.add_argument(
        "nodes",
        help="a list of ips and ports of the nodes",
     nargs="+")
    parser.add_argument(
        "-m",
        "--masters",
     help="the number of masters",
     default=1,
     type=int)
    parser.add_argument(
        "-mid",
        "--instance_id",
     help="changes default masters instance id",
     default=DEFAULT_MASTER_ID,
     type=str)
    parser.add_argument(
        "-t",
        "--timeout",
     help="changes default timeout value",
     default=DEFAULT_TIMEOUT,
     type=int)
    parser.add_argument(
        "-o",
        "--output_dir",
     help="where the config files will be stored",
     default=".",
     type=str)
    parser.add_argument(
        "-i",
        "--interface",
     help="interface of the nodes",
     default=DEFAULT_INTERFACE,
     type=str)
    parser.add_argument(
        "-db",
        "--database",
     help="path of database in the node config",
     default=DEFAULT_DATABASE,
     type=str)
    parser.add_argument(
        "-cdb",
        "--cryptoki_database",
     help="path of database in cryptoki config",
     default=DEFAULT_CRYPTOKI_DATABASE,
     type=str)
    parser.add_argument(
        "-ct",
        "--custom_threshold",
     help="specify this if you want to use a custom threshold",
     default=False,
     action="store_true")
    parser.add_argument(
        "-th",
        "--threshold",
     help="custom threshold for the cryptoki config",
     default=-1)
    args = parser.parse_args()

    nodes = None
    try:
        nodes = parse_nodes(args.nodes)
    except ValueError as e:
        print("ERROR: " + str(e))
        return 1

    masters = create_n_master_config(
        nodes,
        args.output_dir,
     args.masters,
     args.instance_id,
     args.timeout)

    count = 0
    for node in nodes.itervalues():
        index = str(count + 1)
        config_file = open(
            join(
                args.output_dir,
                "node") +
            index +
         ".conf",
         "w")
        create_node_config(
            config_file,
            node,
            masters,
            index,
            args.interface,
            args.database)
        count += 1

        config_file.close()

    threshold = 0
    if(args.custom_threshold):
        custom_threshold = args.threshold
        custom_threshold_as_int = 0

        try:
            custom_threshold_as_int = int(custom_threshold)
        except ValueError as e:
            print("ERROR: Inadaquate threshold")
            return 1

        if (custom_threshold_as_int < 0 or custom_threshold_as_int > len(nodes)):
            print("ERROR: Inadaquate threshold")
            return 1

        threshold = custom_threshold_as_int
    else:
        threshold = get_default_threshold(len(nodes))

    create_n_cryptoki_config(
        nodes,
        args.output_dir,
     args.instance_id,
     masters,
     args.timeout,
     args.cryptoki_database,
     threshold)

    return 0

if __name__ == "__main__":
    main(sys.argv)
