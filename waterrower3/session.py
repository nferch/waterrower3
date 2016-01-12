from twisted.internet import protocol
from twisted.python import log


class RowerSession(protocol.Protocol):
    updatecallback = None

    def __init__(self):
        self.reset()

    def reset(self):
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
        if self.updatecallback:
            self.updatecallback.update_session()

    def longest(self, thing):
        thing = self.lulls if thing == 'lull' else self.intervals
        longest = [0]
        for l in thing:
            if l[0] > longest[0]:
                longest = l
        return(longest if longest != [0] else [])

    def total_time(self):
        return((self.last_stroke - self.first_stroke).seconds)

    def total_distance(self):
        return(self.distance/4000.0)

    def session_end(self):
        log.msg("longest lull: {} at {}".format(*self.longest("lull")))
        log.msg("longest interval: {} at {}".format(*self.longest("interval")))
        log.msg("total time: {}".format(self.total_time()))
        log.msg("total distance: {}".format(self.total_distance()))

    def pkt_motorvoltage(self, packet):
        pass

    def pkt_strokespeed(self, packet):
        stroke_delay = (packet.timestamp - self.last_stroke).seconds
        if stroke_delay > 5:
            log.msg("detected lull of {}".format(stroke_delay))
            self.lulls.append([stroke_delay, packet.timestamp])
            if self.interval_started:
                interval_time = (self.last_stroke -
                                 self.interval_started).seconds
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
