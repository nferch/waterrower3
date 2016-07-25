import datetime

from twisted.python import log
import waterrower3.session as wr3_session
from waterrower3.packet import Packet


class SerialProtocol(wr3_session.RowerSession):
    state = 'idle'
    datalog = []

    def __init__(self, record_datalog=True):
        self.record_datalog = record_datalog
        return(wr3_session.RowerSession.__init__(self))

    def new_packet(self, byte):
        if byte >= 0xf0:
            # print "packet type {0:x}".format(byte)
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

    def get_timestamp(self):
        return(datetime.datetime.now())

    def parse_packet(self, incomplete=False):
        if incomplete:
            log.msg("incomplete packet "+self.dump_packet())
        ts = self.get_timestamp()
        if self.record_datalog:
            self.datalogfile.write(
                "{0}: {1}\n"
                .format(
                    ts.strftime("%Y-%m-%dT%H:%M:%S.%f"), self.dump_packet()))
            self.datalogfile.flush()
        p = Packet(ts)
        p.type = self.packet_type["type"]
        p.parse(self.buf)
        self.packet_received(p)

    def dump_packet(self):
        return("{:02x}: ".format(self.packet_idnum) +
               " ".join(
                   ["{0["+str(i)+"]:02x}" for i in range(0, len(self.buf))])
               .format(self.buf[len(self.buf)*-1:]))

    def connectionMade(self):
        if self.record_datalog:
            self.datalogfilename = self.gen_datalog_filename()
            self.datalogfile = open(self.datalogfilename, 'w')

    def gen_datalog_filename(self):
        return(
            "datalog2-{}.log".format(datetime.datetime.now()
                                     .replace(microsecond=0).isoformat()))

    def dataReceived(self, data):
        for c in data:
            b = ord(c)
            self.datalog.append(b)
            if len(self.datalog) % 16 == 0:
                print " ".join(["{0["+str(i)+"]:02x}" for i in range(0, 16)]) \
                    .format(self.datalog[-16:])
#            print "read {:02X}".format(b)
            self.state = getattr(self, 'state_'+self.state)(b)
