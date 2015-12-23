import datetime

import waterrower3.packet as wr3_packet


class ReplayFile(object):
    def __init__(self, protocol, filename):
        self.file = open(filename, "r")
        self.proto = protocol

    def run(self):
        for l in self.file.readlines():
            sl = l.rstrip().split(" ")
            ts = datetime.datetime.strptime(sl[0], "%Y-%m-%dT%H:%M:%S.%f:")
            bin_data = bytearray([int("0x"+c[0:2], 0) for c in sl[1:]])
            p = wr3_packet.Packet(ts)
            p.parse_bin(bin_data)
            self.proto.packet_received(p)
        self.proto.session_end()
