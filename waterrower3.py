import datetime

from twisted.internet import protocol
from twisted.python import log

class WaterRower3(protocol.Protocol):
    state = 'idle'
    datalog = []

    packet_types = {
        0xfe: { "type": "distance",
                "len": 1 },
        0xff: { "type": "strokespeed",
                "len": 2 },
        0xfd: { "type": "motorvoltage",
                "len": 2 },
        0xfc: { "type": "endpowerstroke",
                "len": 0 },
    }

    def msg_distance(self, dist):
        pass

    def msg_strokespeed(self, strokes_min, speed_m_s):
        pass

    def msg_endpowerstroke(self):
        pass

    def msg_motorvoltage(self, pre_v, cur_v):
        pass

    def pkt_distance(self, dist):
        log.msg("got distance {0:d}".format(dist))
        self.msg_distance(dist)

    def pkt_strokespeed(self, strokes_min, speed_m_s):
        log.msg("got {0:d} strokes/min, {1:d} m/s".format(strokes_min, speed_m_s))
        self.msg_strokespeed(strokes_min, speed_m_s)

    def pkt_endpowerstroke(self):
        log.msg("got end of power stroke")
        self.msg_endpowerstroke()

    def pkt_motorvoltage(self, pre_v, cur_v):
        log.msg("got {0:d} previous voltage, {1:d} current voltage".format(pre_v, cur_v))
        self.msg_motorvoltage(pre_v, cur_v)

    def pkt_unimplemented(self):
        pass

    def state_idle(self, byte):
        if byte & 0xf0:
            print "packet type {0:x}".format(byte)
            if byte in self.packet_types.keys():
                self.packet_type = self.packet_types[byte]
                self.bytes_recv = 0
                if self.packet_type["len"] == 0:
                    self.parse_packet()
                    return('idle')
                self.buf = [0] * self.packet_type["len"]
                return('inpacket')
        print "unknown packet type {0:x}".format(byte)
        return('idle')

    def state_inpacket(self, byte):
#        print "writing to %i" % self.bytes_recv
        self.buf[self.bytes_recv] = byte
        self.bytes_recv += 1

        if self.bytes_recv == self.packet_type["len"]:
            self.parse_packet()
            return('idle')
        return('inpacket')

    def parse_packet(self):
        args = [self.buf[i] for i in range(0, self.packet_type["len"], 1)]
        getattr(self, 'pkt_'+self.packet_type["type"])(*args)

    def connectionMade(self):
        self.datalogfile = open("datalog-{}.log".format(datetime.datetime.now().replace(microsecond=0).isoformat()),'w')

    def dataReceived(self, data):
        for c in data:
            b = ord(c)
            self.datalogfile.write("{:02x} ".format(b))
            self.datalogfile.flush()
            self.datalog.append(b)
            if len(self.datalog) % 16 == 0:
                print " ".join(["{0["+str(i)+"]:02x}" for i in range(0,16)]).format(self.datalog[-16:])
                self.datalogfile.write("\n")
                self.datalogfile.flush()
#            print "read {:02X}".format(b)
            self.state = getattr(self, 'state_'+self.state)(b)
