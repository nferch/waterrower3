import json


import gspread
import oauth2client.client as oauth2_client


class GoogleSheetsConnector(object):
    def __init__(self, creds_file):
        json_key = json.load(open(creds_file))
        scope = ['https://spreadsheets.google.com/feeds']

        creds = oauth2_client.SignedJwtAssertionCredentials(
            json_key['client_email'],
            json_key['private_key'].encode(),
            scope)

        self.gc = gspread.authorize(creds)


class GoogleSheetsUpdater(object):
    MAX_HEADER_ROW_SEARCH = 5

    def __init__(self, gc, sheet):
        self.gc = gc
        self.wks = self.gc.gc.open(sheet).sheet1

    def update(self, update_data):
        header_cols = self.find_column_headers(update_data.keys())
        last_row = self.find_last_row(header_cols.iteritems().next()[1]) + 1

        if last_row > self.wks.row_count:
            self.wks.add_rows(10)
            return(self.update(update_data))

        for key in update_data:
            self.wks.update_cell(last_row, header_cols[key],
                                 update_data[key])

    def find_last_row(self, column):
        """last non-empty row for given column starting from bottom of sheet."""
        col_vals = self.wks.col_values(column)
        return(
            next(i for i, j in reversed(list(enumerate(col_vals)))
                 if j != '') + 1)

    def find_column_headers(self, headers):
        """Find column ids based on a header row.

        :param headers: columns to find
        :type headers: list
        :returns: dict of headers/column ids
        """
        for j in range(1, self.MAX_HEADER_ROW_SEARCH+1):
            try:
                row = self.wks.row_values(j)
            except gspread.exceptions.HTTPError as e:
                if e.code == 400:
                    raise LookupError("Can't find header row")
                else:
                    raise(e)
            if set(headers) < set(row):
                return({h: row.index(h)+1 for h in headers})
        raise LookupError("Can't find header row")
