#!/usr/bin/python3
import gi, signal, logging, sys

# import GStreamer and GLib-Helper classes
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GObject
import threading
import http.server

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
from lib.pipeline import Pipeline
from lib.loghandler import LogHandler
from lib.mainloop import MainLoop


# main class
class SyncStream(object):
    macMapping = {
        "aa:bb:cc:dd:ee:ff": (0, 0, 1280, 1024)
    }
    hostAddress = "10.128.9.47"
    def __init__(self):
        self.log = logging.getLogger('SyncStream')

        # initialize subsystem
        self.log.debug('creating A/V-Pipeline')
        self.pipeline = Pipeline()

    def run(self):
        self.pipeline.configure()
        self.pipeline.start()

        try:
            self.log.info('running GObject-MainLoop')
            MainLoop.run()
        except KeyboardInterrupt:
            self.log.info('Terminated via Ctrl-C')

    def add_device(self, mac, ip):
        id = len(self.pipeline.mm.monitors) + 1
        self.pipeline.mm.addMonitor(id, *self.macMapping[mac], ip)
        self.pipeline.restart()
        return id

    def quit(self):
        self.log.info('quitting GObject-MainLoop')
        MainLoop.quit()


from http.server import BaseHTTPRequestHandler, HTTPServer


def createHandler(syncstream):
    class auto_configure_RequestHandler(BaseHTTPRequestHandler):
        # GET
        def do_GET(self):
            # Send response status code
            self.send_response(200)

            mac = self.path
            if not mac or len(mac) is not 18:
                self.send_error(418, "I'm a teapot")
                return
            mac = mac[1:]
            if mac not in syncstream.macMapping:
                self.send_error(418, "I'm a teapot")
                return
            ip = self.client_address
            client_id = syncstream.add_device(mac, ip)

            # Send headers
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            # Send message back to client
            # Write content as utf-8 data
            self.wfile.write(bytes("{} {}".format(client_id, syncstream.hostAddress), "utf8"))
            return

    return auto_configure_RequestHandler


def run_server(syncstream):
    print('starting server...')

    # Server settings
    # Choose port 8080, for port 80, which is normally used for a http server, you need root access
    server_address = ('127.0.0.1', 8081)
    httpd = HTTPServer(server_address, createHandler(syncstream))
    print('running server...')
    httpd.serve_forever()


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

    server = threading.Thread(target=run_server, args=(syncstream,))
    server.daemon = True
    server.start()

    logging.debug('running SyncStream')
    syncstream.run()


if __name__ == '__main__':
    main()
