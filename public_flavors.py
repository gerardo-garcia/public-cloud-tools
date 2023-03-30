#!/usr/bin/python3

import boto3
import yaml
import argparse
from prettytable import PrettyTable
import logging


def print_pretty_table(headers, rows):
    table = PrettyTable(headers)
    for row in rows:
        table.add_row(row)
    table.align = "l"
    print(table)


def print_csv(headers, rows):
    print(";".join(headers))
    for row in rows:
        str_row = list(map(str, row))
        print(";".join(str_row))


def print_yaml(headers, rows):
    output = []
    for row in rows:
        item_dict = {}
        for i, value in enumerate(headers):
            item_dict[value] = str(row[i])
            output.append(item_dict)
    print(yaml.safe_dump(output, indent=4, default_flow_style=False))


def print_table(headers, rows, output_format):
    if output_format == "table":
        print_pretty_table(headers, rows)
    elif output_format == "csv":
        print_csv(headers, rows)
    elif output_format == "yaml":
        print_yaml(headers, rows)


def set_logger(verbose):
    global logger
    log_format_simple = "%(levelname)s %(message)s"
    log_format_complete = "%(asctime)s %(levelname)s %(name)s %(filename)s:%(lineno)s %(funcName)s(): %(message)s"
    log_formatter_simple = logging.Formatter(log_format_simple, datefmt="%Y-%m-%dT%H:%M:%S")
    handler = logging.StreamHandler()
    handler.setFormatter(log_formatter_simple)
    logger = logging.getLogger("public_flavors")
    logger.setLevel(level=logging.WARNING)
    logger.addHandler(handler)
    if verbose == 1:
        logger.setLevel(level=logging.INFO)
    elif verbose > 1:
        log_formatter = logging.Formatter(log_format_complete, datefmt="%Y-%m-%dT%H:%M:%S")
        handler.setFormatter(log_formatter)
        logger.setLevel(level=logging.DEBUG)


####################################
# Functions
####################################
def get_aws_instance_types(flavor_list):
    # Create a connection to the EC2 service
    ec2 = boto3.client('ec2', region_name='us-west-2')
    cloud_name = "AWS"

    # Use the describe_instance_types() method to retrieve information about instance types
    response = ec2.describe_instance_types()

    n_flavors = 0
    # Extract the instance types from the response and add them to the table
    while True:
        for instance_type in response["InstanceTypes"]:
            n_flavors += 1
            logger.info(f"Flavor: {n_flavors}")
            logger.debug(f"{instance_type}")
    
            name = instance_type["InstanceType"]
            logger.info(f"Name: {name}")
            generation = name[0]
            logger.info(f"Generation: {generation}")
            vcpus = instance_type["VCpuInfo"]["DefaultVCpus"]
            logger.info(f"VCpus: {vcpus}")
            memory = instance_type["MemoryInfo"]["SizeInMiB"] / 1024.0
            logger.info(f"Memory: {memory}")
            storage = instance_type.get("InstanceStorageInfo", "")
            if storage:
                storage_disks = storage.get("Disks")
                storage_total_size = sum([disk.get("SizeInGB") for disk in storage_disks])
                storage = str(storage_total_size)
            logger.info(f"Storage: {storage}")
    
            # Add the flavor
            flavor_list.append(
                [
                    cloud_name,
                    name,
                    generation,
                    vcpus,
                    memory,
                    storage,
                ]
            )
        if "NextToken" in response:
            response = ec2.describe_instance_types(NextToken=response["NextToken"])
        else:
            break

    return


####################################
# Global variables
####################################
# TODO


####################################
# Main
####################################
if __name__ == "__main__":
    # Argument parse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-o",
        "--output",
        choices=["table", "csv", "yaml"],
        default="table",
        help="output format",
    )
    parser.add_argument("-v", "--verbose", action="count", default=0, help="increase output verbosity")
    args = parser.parse_args()

    # Initialize logger
    set_logger(args.verbose)

    # Initialize variables
    headers = [
        "Cloud",
        "Instance Type",
        "Generation",
        "vCPUs",
        "Memory (GiB)",
        "Storage",
    ]
    rows = []

    # Get flavor types
    get_aws_instance_types(rows)

    # Print output
    print_table(headers, rows, args.output)
