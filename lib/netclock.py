from gi.repository import GstNet, GObject
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
            self.netprov.append(
                GstNet.NetTimeProvider.new(
                    self.pipeline.pipeline.get_clock(), self.address, self.basePort + monitorid))


class NetClientClock(object):
    def __init__(self, address, port):
        self.clock = None
        self.address = address
        self.port = port
        self.log = logging.getLogger('NetClientClock')
        self.log.info('initialized NetClientClock')
        self.log.info('time provider: {}:{}'.format(self.address, self.port))

    def start(self):
        self.log.info('starting NetClientClock...')
        self.clock = GstNet.NetClientClock.new('netclock', self.address, self.port, 0)
