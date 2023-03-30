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

    # Initialize a PrettyTable with column names
    table = PrettyTable()
    table.field_names = ["Instance Type", "vCPUs", "Memory (GiB)"]

    # Extract the instance types from the response and add them to the table
    for instance_type in response["InstanceTypes"]:
        name = instance_type["InstanceType"]
        vcpus = instance_type["VCpuInfo"]["DefaultVCpus"]
        memory = instance_type["MemoryInfo"]["SizeInMiB"] / 1024.0

        # Add the flavor
        flavor_list.append(
            [
                cloud_name,
                name,
                vcpus,
                memory,
            ]
        )

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
        "vCPUs",
        "Memory (GiB)",
    ]
    rows = []

    # Get flavor types
    get_aws_instance_types(rows)

    # Print output
    print_table(headers, rows, args.output)
