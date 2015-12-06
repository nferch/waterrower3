#! /usr/bin/env python2.7

import datetime
import sys

import waterrower3
from twisted.python import log
from twisted.internet import reactor
from twisted.internet.serialport import SerialPort

class InternetWaterRower(waterrower3.WaterRower3):
    def msg_powerstroke(self):
        pass
#    def msg_distance(self, dist):
#        log.msg("got distance %i" % dist)
#
#    def msg_strokespeed(self, strokes_min, speed_m_s):
#        log.msg("got strokespeed %i %i" % (strokes_min, speed_m_s))
#

log.startLogging(sys.stdout)
log.addObserver(log.FileLogObserver(file("foo-{}.log".format(datetime.datetime.now().replace(microsecond=0).isoformat()),'w')).emit)

SerialPort(InternetWaterRower(), "/dev/ttyUSB0", reactor, baudrate=1200)

reactor.run()
