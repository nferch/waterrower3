import datetime

import unittest2
import mock
import waterrower3.serial_interface as wr3_serial_interface


class SerialInterfaceTest(unittest2.TestCase):
    def test_distance_packet(self):
        """Ensure we can parse a distance packet."""
        faketime = datetime.datetime(1950, 4, 13, 13, 50)
        tsp = wr3_serial_interface.SerialProtocol()
        tsp.packet_received = mock.MagicMock()
        tsp.get_timestamp = mock.MagicMock(return_value=faketime)
        tsp.connectionMade()
        tsp.dataReceived(['\xfe', '\x00'])
        p = wr3_serial_interface.Packet(faketime)
        p.type = 'distance'
        p.args = 0
        tsp.packet_received.assert_called_with(p)
