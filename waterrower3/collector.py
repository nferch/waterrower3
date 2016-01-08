#! /usr/bin/env python2.7

import argparse
import curses
import datetime

from twisted.python import log
from twisted.internet import reactor
from twisted.internet.serialport import SerialPort
import waterrower3.serial_interface as wr3_serial_interface
from waterrower3 import util


class CursesStdIO(object):
    def fileno(self):
        return(0)

    def doRead(self):
        pass

    def logPrefix(self):
        return('CursesClient')


class InternetWaterRowerConsole(CursesStdIO):
    def __init__(self, stdscr, session):
        self.timer = 0
        self.stdscr = stdscr

        self.setup_screen()

        self.session = session
        self.session.updatecallback = self

    def connectionLost(self, _):
        self.close()

    def doRead(self):
        curses.noecho()
        c = self.stdscr.getch()

        if chr(c) == "r":
            self.reset()

        self.stdscr.addstr(0, 0, chr(c))
        self.paint()

    def setup_screen(self):
        self.stdscr.nodelay(1)
        curses.cbreak()
        self.stdscr.keypad(1)
        curses.curs_set(0)

        self.rows, self.cols = self.stdscr.getmaxyx()
        self.lines = []
        self.paint()

    def cleanup_screen(self):
        curses.nocbreak()
        self.stdscr.keypad(0)
        curses.echo()
        curses.endwin()

    def paint(self):
        self.stdscr.addstr(1, 0, str(datetime.datetime.now()))
        self.stdscr.refresh()

    def update_session(self):
        self.stdscr.addstr(
            2, 0,
            util.format_sec(self.session.total_time()))
        self.stdscr.addstr(
            3, 0,
            "{:1.3f}".format(self.session.total_distance()))
        self.stdscr.addstr(
            4, 0,
            "Longest Lull: " + util.format_longest(
                self.session.longest("lull")))
        self.stdscr.addstr(
            5, 0,
            "Longest Interval: " + util.format_longest(
                self.session.longest("interval")))
        self.paint()

    def reset(self):
        self.session.reset()

    def close(self):
        self.cleanup_screen()


class InternetWaterRower(wr3_serial_interface.SerialProtocol):
    def __init__(self, record_datalog=True):
        return(
            wr3_serial_interface.SerialProtocol.__init__(
                self, record_datalog=record_datalog))


def main():
    parser = argparse.ArgumentParser(description="WaterRower monitor")

    parser.add_argument("-p", "--port", dest="serial_port",
                        default="/dev/ttyUSB0")
    parser.add_argument("-s", "--speed", dest="speed", default=1200)
    parser.add_argument("-n", "--nodatalog", dest="record_datalog",
                        action='store_false')

    opts = parser.parse_args()

    log.startLogging(file(
        "collector-{}.log".format(
            datetime.datetime.now().replace(microsecond=0).isoformat()),
        'w'))

    stdscr = curses.initscr()
    session = InternetWaterRower(record_datalog=opts.record_datalog)
    cons = InternetWaterRowerConsole(stdscr, session)
    stdscr.refresh()

    reactor.addReader(cons)
    SerialPort(session, opts.serial_port, reactor, baudrate=opts.speed)

    reactor.run()
    cons.close()


if __name__ == '__main__':
    main()
