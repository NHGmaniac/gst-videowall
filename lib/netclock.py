from gi.repository import GstNet, GObject


class NetClock(object):
    def __init__(self, pipeline, address, port):
        self.pipeline = pipeline
        self.netprov = None
        self.address = address
        self.port = port

    def start(self):
        self.netprov = GstNet.NetTimeProvider.new(self.pipeline.pipeline.get_clock(), self.address, self.port)


class NetClientClock(object):
    def __init__(self, address, port):
        self.clock = None
        self.address = address
        self.port = port

    def start(self):
        self.clock = GstNet.NetClientClock.new('netclock', self.address, self.port, 0)
