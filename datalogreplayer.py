#! /usr/bin/env python

import argparse
import datetime
import time

parser = argparse.ArgumentParser(description="Simple datalog replayer")

parser.add_argument("input_filename")
parser.add_argument("output_tty")

opts = parser.parse_args()

print opts

ifile = open(opts.input_filename, "r")
firstline = ifile.readline()

ofile = open(opts.output_tty, "w")

print firstline.split(" ")[0]
# 2016-12-05T20:22:10.895945
starttime = datetime.datetime.strptime(firstline.split(" ")[0],
                                       "%Y-%m-%dT%H:%M:%S.%f:")
offset = datetime.datetime.now() - starttime
print "first line is {}".format(firstline)
for l in ifile.readlines():
    sl = l.rstrip().split(" ")
    ts = datetime.datetime.strptime(sl[0], "%Y-%m-%dT%H:%M:%S.%f:")
    delay = datetime.datetime.now()-ts
    print ts
    print l
    if delay < offset:
        time.sleep((offset-delay).total_seconds())
    print sl[1:]
    bin_data = bytearray([int("0x"+c[0:2], 0) for c in sl[1:]])
    ofile.write(bin_data)
    ofile.flush()
    print
