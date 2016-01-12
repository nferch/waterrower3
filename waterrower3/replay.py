#! /usr/bin/env python2.7

import argparse
import datetime
import sys

from twisted.python import log
import waterrower3.file_interface as wr3_file_interface
import waterrower3.google_sheets as wr3_google_sheets
import waterrower3.session as wr3_session
from waterrower3 import util


class RowerReplaySession(wr3_session.RowerSession):
    def __init__(self, creds_filename=None, spreadsheet_name=None):
        self.creds_filename = creds_filename
        self.spreadsheet_name = spreadsheet_name
        return(wr3_session.RowerSession.__init__(self))

    def session_end(self):
        print "longest lull: {} at {}".format(*self.longest("lull"))
        print "longest interval: {} at {}".format(*self.longest("interval"))
        print "total time: {}".format(self.total_time())
        print "total distance: {}".format(self.total_distance())
        if self.creds_filename and self.spreadsheet_name:
            print "Adding to Google Spreadsheet"
            self.update_google_spreadsheet()

    def update_google_spreadsheet(self):
        gc = wr3_google_sheets.GoogleSheetsConnector(self.creds_filename)
        gsu = wr3_google_sheets.GoogleSheetsUpdater(
            gc, self.spreadsheet_name)

        gsu.update({
            "Date": self.first_stroke.strftime("%x"),
            "Distance": "{:1.3f}".format(self.total_distance()),
            "Time": util.format_time(self.total_time()),
            "Longest Lull": util.format_sec(self.longest("lull")[0]),
            "Longest Interval": util.format_sec(self.longest("interval")[0])
            })


def main():
    parser = argparse.ArgumentParser(description="WaterRower log replayer")

    parser.add_argument("-f", "--filename", required=True,
                        help="Name of replay file")
    parser.add_argument("-c", "--creds_filename",
                        help="Name of Google credentials file")
    parser.add_argument("-n", "--name", help="Name of Google Spreadsheet")

    opts = parser.parse_args()

    log.startLogging(sys.stdout)
    log.addObserver(
        log.FileLogObserver(
            file(
                "replay-{}.log".format(
                    datetime.datetime.now().replace(microsecond=0).isoformat()),
                'w')
            ).emit)

    wr3_file_interface.ReplayFile(
        RowerReplaySession(opts.creds_filename, opts.name),
        opts.filename).run()


if __name__ == '__main__':
    main()
