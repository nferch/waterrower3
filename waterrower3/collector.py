#! /usr/bin/env python2.7

import argparse
import curses
import datetime

from twisted.python import log
from twisted.internet import reactor
from twisted.internet.serialport import SerialPort
import waterrower3.google_sheets as wr3_google_sheets
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
    session_ending = False
    status_line = ""

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
        self.handle_command(c)

    def handle_command(self, c):
        if c > 256:
            return
        if chr(c) == "r":
            self.reset()
        elif chr(c) == "e":
            self.end_session()

        self.stdscr.addstr(0, 0, chr(c))
        self.paint()

    def end_session(self):
        self.session_ending = True
        self.status_line = "ending session..."
        self.cleanup_screen()
        self.session.session_end()
        reactor.stop()

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
        self.stdscr.addstr(6, 0, self.status_line)
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
    def __init__(self, record_datalog=True, creds_filename=None,
                 spreadsheet_name=None):
        self.creds_filename = creds_filename
        self.spreadsheet_name = spreadsheet_name
        return(
            wr3_serial_interface.SerialProtocol.__init__(
                self, record_datalog=record_datalog))

    def session_end(self):
        if self.creds_filename and self.spreadsheet_name:
            print "Adding to Google Spreadsheet"
            self.update_google_spreadsheet()
        wr3_serial_interface.SerialProtocol.session_end(self)

    def update_google_spreadsheet(self):
        gc = wr3_google_sheets.GoogleSheetsConnector(self.creds_filename)
        gsu = wr3_google_sheets.GoogleSheetsUpdater(
            gc, self.spreadsheet_name)

        update_data = {
            "Date": self.first_stroke.strftime("%x"),
            "Distance": "{:1.3f}".format(self.total_distance()),
            "Time": util.format_time(self.total_time())}

        if self.longest("lull"):
            update_data["Longest Lull"] = util.format_sec(
                self.longest("lull")[0])
        if self.longest("interval"):
            update_data["Longest Interval"] = util.format_sec(
                self.longest("interval")[0])

        gsu.update(update_data)


def main():
    parser = argparse.ArgumentParser(description="WaterRower monitor")

    parser.add_argument("-p", "--port", dest="serial_port",
                        default="/dev/ttyUSB0")
    parser.add_argument("-s", "--speed", dest="speed", default=1200)
    parser.add_argument("-n", "--nodatalog", dest="record_datalog",
                        action='store_false')
    parser.add_argument("-c", "--creds_filename",
                        help="Name of Google credentials file")
    parser.add_argument("-g", "--name", help="Name of Google Spreadsheet")

    opts = parser.parse_args()

    log.startLogging(file(
        "collector-{}.log".format(
            datetime.datetime.now().replace(microsecond=0).isoformat()),
        'w'))

    stdscr = curses.initscr()
    session = InternetWaterRower(
        record_datalog=opts.record_datalog,
        creds_filename=opts.creds_filename,
        spreadsheet_name=opts.name)
    cons = InternetWaterRowerConsole(stdscr, session)
    stdscr.refresh()

    reactor.addReader(cons)
    SerialPort(session, opts.serial_port, reactor, baudrate=opts.speed)

    reactor.run()
    cons.close()


if __name__ == '__main__':
    main()
