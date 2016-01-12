import gspread.exceptions
import unittest2
import mock
import waterrower3.google_sheets as wr3_google_sheets


class GoogleSheetsUpdaterTest(unittest2.TestCase):
    def test_instantiate(self):
        gc = mock.MagicMock()
        wr3_google_sheets.GoogleSheetsUpdater(gc,
                                              "Test Sheet")
        gc.gc.open.assert_called_with("Test Sheet")

    def test_find_column_headers(self):
        gc = mock.MagicMock()
        gs = wr3_google_sheets.GoogleSheetsUpdater(gc, "fakesheet")
        gs.wks = mock.MagicMock()

        gs.wks.row_values.side_effect = [
            ["poop", "asdf"],
            ["nothing", "header2", "poop", "header1"],
            [],
            [],
            []]

        self.assertEqual(
            gs.find_column_headers(["header1", "header2"]),
            {"header1": 4, "header2": 2})
        gs.wks.row_values.assert_has_calls([
            mock.call(1),
            mock.call(2)
            ])

    def test_find_last_row(self):
        gc = mock.MagicMock()
        gs = wr3_google_sheets.GoogleSheetsUpdater(gc, "fakesheet")
        gs.wks = mock.MagicMock()

        gs.wks.col_values.side_effect = [
            ["", "Date", "1/2/2014", "1/4/2014", "", ""]]

        self.assertEqual(
            gs.find_last_row(3),
            4)
        gs.wks.col_values.assert_called_with(3)

    def test_missing_headers(self):
        """ensure exception raised if header row is not found."""
        gc = mock.MagicMock()
        gs = wr3_google_sheets.GoogleSheetsUpdater(gc, "fakesheet")
        gs.wks = mock.MagicMock()
        gs.wks.row_values.side_effect = [
            ["poop", "asdf"],
            ["nothing", "header2", "poop", "header1"],
            [],
            [],
            []]

        with self.assertRaises(LookupError):
            gs.find_column_headers(["homer"])

    def test_short_worksheet(self):
        """ensure we don't explode if the sheet contains few rows."""
        gc = mock.MagicMock()
        gs = wr3_google_sheets.GoogleSheetsUpdater(gc, "fakesheet")
        gs.wks = mock.MagicMock()
        gs.wks.row_values.side_effect = [
            ["poop", "asdf"],
            gspread.exceptions.HTTPError(
                400,
                "Invalid query parameter value for range.")]

        with self.assertRaises(LookupError):
            gs.find_column_headers(["homer"])

    def test_gsapi_failure(self):
        """but do if the api fails."""
        gc = mock.MagicMock()
        gs = wr3_google_sheets.GoogleSheetsUpdater(gc, "fakesheet")
        gs.wks = mock.MagicMock()
        gs.wks.row_values.side_effect = [
            gspread.exceptions.HTTPError(503, "bar")]

        with self.assertRaises(gspread.exceptions.HTTPError):
            gs.find_column_headers(["homer"])

    @mock.patch("waterrower3.google_sheets.GoogleSheetsUpdater.find_last_row")
    @mock.patch(
        "waterrower3.google_sheets.GoogleSheetsUpdater.find_column_headers")
    def test_update(self, find_column_headers, find_last_row):
        gc = mock.MagicMock()
        gs = wr3_google_sheets.GoogleSheetsUpdater(gc, "fakesheet")
        gs.wks = mock.MagicMock()

        find_column_headers.side_effect = [{"Bar": 2, "Toot": 4}]
        find_last_row.side_effect = [1]

        gs.update({"Bar": "poop"})
        gs.wks.update_cell.assert_called_with(2, 2, "poop")

    @mock.patch("waterrower3.google_sheets.GoogleSheetsUpdater.find_last_row")
    @mock.patch(
        "waterrower3.google_sheets.GoogleSheetsUpdater.find_column_headers")
    def test_update_add_rows(self, find_column_headers, find_last_row):
        gc = mock.MagicMock()
        gs = wr3_google_sheets.GoogleSheetsUpdater(gc, "fakesheet")
        gs.wks = mock.MagicMock()

        find_column_headers.side_effect = [{"Bar": 2, "Toot": 4}]
        find_last_row.side_effect = [3]
        gs.wks.row_count = 1

        _update = gs.update
        with mock.patch("waterrower3.google_sheets.GoogleSheetsUpdater.update"):
            _update({"Bar": "poop"})
        gs.wks.add_rows.assert_called_with(10)
