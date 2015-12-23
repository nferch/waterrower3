import json


import gspread
from oauth2client.client import SignedJwtAssertionCredentials


class GoogleSheetsUpdater(object):
    DEFAULT_COLUMN = "Date"
    DATA_POSITIONS = {"Date": 2,
                      "Distance": 4,
                      "Time": 5}

    def __init__(self, creds_file, sheet):
        json_key = json.load(open(creds_file))
        scope = ['https://spreadsheets.google.com/feeds']

        creds = SignedJwtAssertionCredentials(json_key['client_email'],
                                              json_key['private_key'].encode(),
                                              scope)

        self.gc = gspread.authorize(creds)
        self.wks = self.gc.open(sheet).sheet1

    def update(self, update_data):
        last_row = self.find_last_row() + 1

        if last_row > self.wks.row_count:
            self.wks.add_rows(10)
            return(self.update(update_data))

        for key in update_data:
            self.wks.update_cell(last_row, self.DATA_POSITIONS[key],
                                 update_data[key])

    def find_last_row(self):
        datecol = self.wks.col_values(self.DATA_POSITIONS[self.DEFAULT_COLUMN])
        return(
            next(i for i, j in reversed(list(enumerate(datecol)))
                 if j != '') + 1)
