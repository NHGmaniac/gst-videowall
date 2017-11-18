#!/usr/bin/python3
import gi, signal, logging, sys

# import GStreamer and GLib-Helper classes
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GObject

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

# import local classes
from lib.args import Args
from lib.pipeline import Pipeline,TCPSource
from lib.loghandler import LogHandler
from lib.mainloop import MainLoop


# main class
class SyncStream(object):
    def __init__(self):
        self.log = logging.getLogger('SyncStream')

        # initialize subsystem
        self.log.debug('creating A/V-Pipeline')
        self.pipeline = Pipeline()
        self.source = TCPSource(9999)

    def run(self):
        self.pipeline.configure()
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
    docolor = (Args.color == 'always') or (Args.color == 'auto' and sys.stderr.isatty())

    handler = LogHandler(docolor)
    logging.root.addHandler(handler)

    if Args.verbose >= 2:
        level = logging.DEBUG
    elif Args.verbose == 1:
        level = logging.INFO
    else:
        level = logging.WARNING
    level = logging.DEBUG

    logging.root.setLevel(level)

    # make killable by ctrl-c
    logging.debug('setting SIGINT handler')
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    logging.info('Python Version: %s', sys.version_info)
    logging.info('GStreamer Version: %s', Gst.version())

    # init main-class and main-loop
    logging.debug('initializing SyncStream')
    syncstream = SyncStream()

    logging.debug('running SyncStream')
    syncstream.run()


if __name__ == '__main__':
    main()
