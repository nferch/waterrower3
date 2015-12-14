import datetime

from twisted.internet import protocol
from twisted.python import log

class Packet(object):
    PACKET_TYPES = {
        0xfe: { "type": "distance",
                "len": 1 },
        0xff: { "type": "strokespeed",
                "len": 2 },
        0xfd: { "type": "motorvoltage",
                "len": 2 },
        0xfc: { "type": "endpowerstroke",
                "len": 0 },
    }

class SerialProtocol(protocol.Protocol):
    state = 'idle'
    datalog = []
    sum_distance = 0


    def msg_distance(self, dist):
        pass

    def msg_strokespeed(self, strokes_min, speed_m_s):
        pass

    def msg_endpowerstroke(self):
        pass

    def msg_motorvoltage(self, pre_v, cur_v):
        pass

    def pkt_distance(self, dist):
        if dist == 60:
            log.msg("ignoring large distance")
        else:
            self.sum_distance += dist
        if dist > 0:
            log.msg("got distance {0:d} cumm {1:d}".format(dist, self.sum_distance))
        self.msg_distance(dist)

    def pkt_strokespeed(self, strokes_min, speed_m_s):
        log.msg("got {0:d} strokes/min, {1:d} m/s".format(strokes_min, speed_m_s))
        self.msg_strokespeed(strokes_min, speed_m_s)

    def pkt_endpowerstroke(self):
#        log.msg("got end of power stroke")
        self.msg_endpowerstroke()

    def pkt_motorvoltage(self, pre_v, cur_v):
#        log.msg("got {0:d} previous voltage, {1:d} current voltage".format(pre_v, cur_v))
        self.msg_motorvoltage(pre_v, cur_v)

    def pkt_unimplemented(self):
        pass

    def new_packet(self, byte):
        if byte >= 0xf0:
#            print "packet type {0:x}".format(byte)
            if byte in Packet.PACKET_TYPES.keys():
                self.packet_idnum = byte
                self.packet_type = Packet.PACKET_TYPES[byte]
                self.bytes_recv = 0
                self.buf = [0] * self.packet_type["len"]
                if self.packet_type["len"] == 0:
                    self.parse_packet()
                    return('idle')
                return('inpacket')
        print "unknown packet type {0:x}".format(byte)
        return('idle')

    def state_idle(self, byte):
        return(self.new_packet(byte))

    def state_inpacket(self, byte):
        if byte >= 0xf0:
            log.msg("unexpected new packet {0:x}".format(byte))
            self.parse_packet(incomplete=True)
            return(self.new_packet(byte))

#        print "writing to %i" % self.bytes_recv
        self.buf[self.bytes_recv] = byte
        self.bytes_recv += 1

        if self.bytes_recv == self.packet_type["len"]:
            self.parse_packet()
            return('idle')
        return('inpacket')

    def parse_packet(self, incomplete=False):
        if incomplete:
            log.msg("incomplete packet "+self.dump_packet())
        self.datalogfile.write("{0}: {1}\n".format(datetime.datetime.now().isoformat(), self.dump_packet()))
        self.datalogfile.flush()
        getattr(self, 'pkt_'+self.packet_type["type"])(*self.buf)

    def dump_packet(self):
        return("{:02x}: ".format(self.packet_idnum)+
            " ".join(["{0["+str(i)+"]:02x}" for i in range(0,len(self.buf))]).format(self.buf[len(self.buf)*-1:]))

    def connectionMade(self):
        self.datalogfile = open("datalog2-{}.log".format(datetime.datetime.now().replace(microsecond=0).isoformat()),'w')

    def dataReceived(self, data):
        for c in data:
            b = ord(c)
            self.datalog.append(b)
            if len(self.datalog) % 16 == 0:
                print " ".join(["{0["+str(i)+"]:02x}" for i in range(0,16)]).format(self.datalog[-16:])
#            print "read {:02X}".format(b)
            self.state = getattr(self, 'state_'+self.state)(b)
