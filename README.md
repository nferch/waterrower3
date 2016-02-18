#WaterRower Monitor III tools

Discovered that the Monitor III had a serial port that was documented on their [website](https://www.waterrower.com/pccablespec.php). Got sick of manually entering my row sessions to a Google Spreadsheet, so I decided to gin up some Python to do it automatically.

#Install

`pip install .`

#Setup

1. Connect your WaterRower Monitor III to your computer's serial port. I use a PL2303 USB serial adapter with a Raspberry Pi, but I have at times used it with Ubuntu and OS X.
2. Identify your system's serial port device. On my Raspberry Pi it's /dev/ttyUSB0.

## Google Spreadsheets support.

1. [Per the gspread documentation](https://github.com/burnash/gspread/blob/master/README.md), [Obtain OAuth2 credentials from Google Developers Console](http://gspread.readthedocs.org/en/latest/oauth2.html)
2. Copy the JSON file for the service account to wherever you'll run this.
2. Create a Google Spreadsheet for the data to go into. [Here's an example](https://docs.google.com/spreadsheets/d/1X9kUckCAQ2aC0F07AMe7TiXw3uIQGkMhAqN1I1DxPRI/edit?usp=sharing)
3. Give the account you created in step 1 write access to the Google Spreadsheet.

#Example Usage
1. `sudo collector -c ~/google-oauth-creds.json -g "Rowing Python Test"`
2. Start rowing.
3. Break yo neck
4. Hit 'e' to end your rowing session.
4. If you elected to use Google Spreadsheets support, the results of your row sesssion will be uploaded to the Google Spreadsheet.

#Hacking/Development
Developing with real WaterRower Monitor is a PITA, so I created a datalog replayer.

By default the collector writes a datalog file which you can use replay through a `socat` pipe to simulate a rowing session.

1. `socat PTY,link=foo PTY,link=bar`
2. `replay datalog2-2015-12-13T11:39:01.log bar`
3. `collector -p foo -n -c ~/google-oauth-creds.json -g "Rowing Python Test"`
