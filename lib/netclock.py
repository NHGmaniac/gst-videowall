from gi.repository import GstNet, GObject
from lib.monitor import MonitorManager


class NetClock(object):
    def __init__(self, pipeline, address, basePort):
        self.pipeline = pipeline
        self.netprov = list()
        self.address = address
        self.basePort = int(basePort)
        self.mm = MonitorManager()

    def start(self):
        self.mm.load()
        for monitorid in self.mm.iterids():
            self.netprov.append(
                GstNet.NetTimeProvider.new(
                    self.pipeline.pipeline.get_clock(), self.address, self.basePort + monitorid))


class NetClientClock(object):
    def __init__(self, address, port):
        self.clock = None
        self.address = address
        self.port = port

    def start(self):
        self.clock = GstNet.NetClientClock.new('netclock', self.address, self.port, 0)
