from twisted.internet import protocol
from twisted.python import log


class RowerSession(protocol.Protocol):
    def __init__(self):
        self.distance = 0
        self.first_stroke = None
        self.last_stroke = None
        self.interval_started = None
        self.lulls = []
        self.intervals = []

    def packet_received(self, packet):
        if not self.last_stroke:
            self.first_stroke = packet.timestamp
            self.last_stroke = packet.timestamp
        getattr(self, 'pkt_'+packet.type)(packet)

    def session_end(self):
        longest_lull = [0]
        longest_interval = [0]
        for l in self.lulls:
            if l[0] > longest_lull[0]:
                longest_lull = l
        for l in self.intervals:
            if l[0] > longest_interval[0]:
                longest_interval = l
        log.msg("longest lull: {} at {}".format(*longest_lull))
        log.msg("longest interval: {} at {}".format(*longest_interval))
        log.msg("total time: {}".format(self.last_stroke - self.first_stroke))
        log.msg("total distance: {}".format((self.distance/4000.0)))

    def pkt_motorvoltage(self, packet):
        pass

    def pkt_strokespeed(self, packet):
        stroke_delay = (packet.timestamp - self.last_stroke).seconds
        if stroke_delay > 5:
            log.msg("detected lull of {}".format(stroke_delay))
            self.lulls.append([stroke_delay, packet.timestamp])
            interval_time = (self.last_stroke - self.interval_started).seconds
            log.msg("last interval time {}".format(interval_time))
            self.intervals.append([interval_time, self.last_stroke])
            self.interval_started = None
        elif not self.interval_started:
            self.interval_started = packet.timestamp
        self.last_stroke = packet.timestamp

    def pkt_endpowerstroke(self, packet):
        pass

    def pkt_distance(self, packet):
        if packet.args == 60:
            log.msg("ignoring large distance")
        else:
            self.distance += packet.args
        if packet.args > 0:
            log.msg("got distance {0:d} cumm {1:d}"
                    .format(packet.args, self.distance))
