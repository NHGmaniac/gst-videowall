#!/usr/bin/python3
import gi, signal, logging, sys

# import GStreamer and GLib-Helper classes
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GObject, GstNet

# check min-version
minGst = (1, 0)
minPy = (3, 0)

Gst.init([])
if Gst.version() < minGst:
    raise Exception("GStreamer version", Gst.version(), 'is too old, at least', minGst, 'is required')

if sys.version_info < minPy:
    raise Exception("Python version", sys.version_info, 'is too old, at least', minPy, 'is required')

# init GObject & Co. before importing local classes
GObject.threads_init()

from lib.netclock import NetClientClock
from lib.pipeline import RecvPipeline
from lib.loghandler import LogHandler

import subprocess


MainLoop = GObject.MainLoop()

class NetRevc(object):
    def __init__(self, host, monitor_id, raspi=False, base_time=None):
        self.log = logging.getLogger('NetRecv')

        # initialize subsystem
        self.log.debug('creating A/V-Pipeline')
        self.pipeline = RecvPipeline(host, monitor_id, raspi=raspi)
        self.netclientclock = None
        self.host = host
        self.id = monitor_id
        self.raspi = raspi
        self.base_time = base_time

    def run(self):
        if self.raspi:
            subprocess.call(['mkfifo', 'gst-omx-pipe'])
            subprocess.Popen(['omxplayer', '--live', '--win', '"0 0 1280 1024"', '--aspect-mode', 'stretch', 'gst-omx-pipe'])
        self.pipeline.configure()
        self.pipeline.pipeline.set_start_time(Gst.CLOCK_TIME_NONE)
        self.pipeline.pipeline.set_base_time(self.base_time)
        self.netclientclock = NetClientClock(self.host, 10000 + int(self.id), self.base_time)
        self.netclientclock.start()
        self.pipeline.setclock(self.netclientclock.clock)
        self.pipeline.start()

        try:
            while True:
                self.log.info('running GObject-MainLoop')
                MainLoop.run()
        except KeyboardInterrupt:
            self.log.info('Terminated via Ctrl-C')

    def quit(self):
        self.log.info('quitting GObject-MainLoop')
        MainLoop.quit()

# run mainclass
def main():
    # configure logging
    docolor = sys.stderr.isatty()

    handler = LogHandler(docolor)
    logging.root.addHandler(handler)

    level = logging.DEBUG

    logging.root.setLevel(level)

    # make killable by ctrl-c
    logging.debug('setting SIGINT handler')
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    logging.info('Python Version: %s', sys.version_info)
    logging.info('GStreamer Version: %s', Gst.version())

    # init main-class and main-loop
    logging.debug('initializing NetRecv')
    netrecv = NetRevc('127.0.0.1', 2)

    logging.debug('running SyncStream')
    netrecv.run()


if __name__ == '__main__':
    main()
