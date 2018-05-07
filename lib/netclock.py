from gi.repository import GstNet, GObject, Gst
from lib.monitor import MonitorManager
import logging


class NetClock(object):
    def __init__(self, pipeline, address, basePort):
        self.pipeline = pipeline
        self.netprov = list()
        self.address = address
        self.basePort = int(basePort)
        self.mm = MonitorManager()
        self.log = logging.getLogger('NetClock')
        self.log.info('initialized NetClock (Time Provider) on address {}'.format(self.address))
        self.log.debug('base port: {}'.format(self.basePort))

    def start(self):
        self.mm.load()
        self.log.info('starting NetClock (Time Provider)')
        for monitorid in self.mm.iterids():
            self.log.debug('new netclock on port {}'.format(self.basePort + monitorid))
            clock_prov = GstNet.NetTimeProvider.new(
                    self.pipeline.pipeline.get_clock(), self.address, self.basePort + monitorid)
            base_time = self.pipeline.get_clock().get_time()
            self.pipeline.pipeline.set_start_time(Gst.CLOCK_TIME_NONE)
            self.pipeline.pipeline.set_base_time(base_time)
            self.netprov.append((clock_prov, base_time))


class NetClientClock(object):
    def __init__(self, address, port, base_time=None):
        self.clock = None
        self.address = address
        self.port = port
        self.log = logging.getLogger('NetClientClock')
        self.log.info('initialized NetClientClock')
        self.log.info('time provider: {}:{}'.format(self.address, self.port))
        self.base_time = base_time

    def start(self):
        self.log.info('starting NetClientClock...')
        if self.base_time:
            self.log.debug('initial clock time was: {}'.format(self.base_time))
            self.clock = GstNet.NetClientClock.new('netclock', self.address, self.port, self.base_time)
        else:
            self.clock = GstNet.NetClientClock.new('netclock', self.address, self.port, 0)
