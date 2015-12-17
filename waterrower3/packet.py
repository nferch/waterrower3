from twisted.python import log


class Packet(object):
    PACKET_TYPES = {
        0xfe: {"type": "distance",
               "len": 1},
        0xff: {"type": "strokespeed",
               "len": 2},
        0xfd: {"type": "motorvoltage",
               "len": 2},
        0xfc: {"type": "endpowerstroke",
               "len": 0},
    }
    args = None

    def __init__(self, timestamp):
        self.timestamp = timestamp

    def parse_bin(self, data):
        self.type = self.PACKET_TYPES[data[0]]["type"]

        if len(data) > 1:
            self.parse(data[1:])

    def parse_type(self, byte):
        self.type = self.PACKET_TYPES[byte]["type"]

    def parse(self, data):
        getattr(self, 'pkt_'+self.type)(*data)

    def pkt_distance(self, dist):
        if dist == 60:
            log.msg("ignoring large distance")
            self.args = 0
        else:
            self.args = dist
        return(self)

    def pkt_strokespeed(self, strokes_min, speed_m_s):
        self.args = {"strokes_min": strokes_min,
                     "speed": speed_m_s}
        return(self)

    def pkt_endpowerstroke(self):
        return(self)

    def pkt_motorvoltage(self, pre_v, cur_v):
        self.args = {"previous": pre_v,
                     "current": cur_v}
        return(self)

    def __eq__(self, other):
        if self.type == other.type:
            return(self.args == other.args and
                   self.timestamp == other.timestamp)
        else:
            return(False)
