#! /usr/bin/env python2.7

import argparse
import datetime
import sys

from twisted.python import log
import waterrower3.session as wr3_session
import waterrower3.file_interface as wr3_file_interface


parser = argparse.ArgumentParser(description="WaterRower log replayer")

parser.add_argument("-f", "--filename")

opts = parser.parse_args()

log.startLogging(sys.stdout)
log.addObserver(
    log.FileLogObserver(
        file("replay-{}.log".format(
            datetime.datetime.now().replace(microsecond=0).isoformat()), 'w')
        ).emit)

wr3_file_interface.ReplayFile(wr3_session.RowerSession(), opts.filename).run()
