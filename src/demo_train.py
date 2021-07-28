# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. 

import argparse
import os

# Obtain parameters from the calling module

parser = argparse.ArgumentParser("train")
parser.add_argument("--arg1", type=str, help="sample 1st_string argument")
parser.add_argument("--arg2", type=str, help="sample datapath argument")
parser.add_argument("--arg3", type=str, help="sample 2nd_string argument")

args = parser.parse_args()
# Do something with the parameters
print("Sample 1st_string argument  : %s" % args.arg1)
print("Sample datapath argument: %s" % args.arg2)
print("Sample 2nd_string argument: %s" % args.arg3)

# TODO - create a blob somewhere based on the params?