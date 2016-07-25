import gspread
from googleapiclient import discovery
from googleapiclient import http
from oauth2client.service_account import ServiceAccountCredentials


SCOPES = ['https://www.googleapis.com/auth/devstorage.read_write',
          'https://spreadsheets.google.com/feeds']


class GoogleSheetsConnector(object):
    def __init__(self, creds_file):

        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            creds_file, SCOPES)
        self.gc = gspread.authorize(credentials)
        self.storage_service = discovery.build('storage', 'v1',
                                               credentials=credentials)


class GoogleSheetsUpdater(object):
    MAX_HEADER_ROW_SEARCH = 5

    def __init__(self, gc, sheet, bucket_name):
        self.gc = gc
        self.wks = self.gc.gc.open(sheet).sheet1
        self.bucket_name = bucket_name

    def upload_datalog(self, filename):
        body = {'name': filename, }

        with open(filename, 'rb') as f:
            req = self.gc.storage_service.objects().insert(
                bucket=self.bucket_name, body=body,
                media_body=http.MediaIoBaseUpload(f,
                                                  'application/octet-stream'))
            resp = req.execute()

        return(resp)

    def update_spreadsheet(self, update_data):
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
