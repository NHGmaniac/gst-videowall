#!/usr/bin/python3
import logging, sys, time, shutil, signal
import http.server
import threading
import gi


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

from lib.config import loadconfig
from lib.args import Args
from lib.monitor import MonitorManager
from lib.pipeline import Pipeline, TCPSource
from lib.netclock import NetClock
from lib.loghandler import LogHandler
from lib.mainloop import MainLoop
macMapping = {}

monitorManager = MonitorManager()


conf = None
stop = False
t = None
ready = False
ncdict = None

clearOnStart = True

def add_device(mac, ip):
    if monitorManager.hasMonitor(mac):
        return monitorManager.replaceMonitor(mac, ip)
    monitorconf = macMapping[mac]
    monitorconf["ip"] = ip
    monitorconf["mac"] = mac
    return monitorManager.addMonitor(monitorconf)


class auto_configure_RequestHandler(http.server.BaseHTTPRequestHandler):
    # GET
    def do_GET(self):
        conf.load()
        macMapping = conf["macMapping"]
        data = self.path
        if not data:
            self.send_response(418, "I'm a teapot")
            return
        data = data.split("/")
        if not len(data) == 3 or len(data[1]) != 17:
            self.send_response(418, "I'm a teapot")
            return
        mac = data[1]
        ip = data[2]
        if mac not in macMapping.keys():
            self.send_response(418, "I'm a teapot")
            return
        if monitorManager.hasMonitor(mac):
            print("Client already registered")
        client_id = add_device(mac, ip)
        if client_id is None:
            self.send_response(418, "I'm a teapot")
            return

        if ready:
            self.send_response(200, "OK")

            # Send headers
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            # Send message back to client
            # Write content as utf-8 data
            self.wfile.write(bytes("{} {} {}".format(client_id, hostAddress, ncdict[client_id][1]), "utf8"))
        else:
            self.send_response(418, 'not ready')
        monitorManager.save()

        return


def run_server():
    logging.getLogger('ConfigServer').info('starting server...')

    server_address = ("10.128.9.47", 8082)
    httpd = http.server.HTTPServer(server_address, auto_configure_RequestHandler)

    logging.getLogger('ConfigServer').info('running server...')
    httpd.serve_forever()

# run mainclass
def main():
    global conf, macMapping, hostAddress, t, ready, ncdict
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




    #load config
    conf = loadconfig("config.json")
    macMapping = conf["macMapping"]
    hostAddress = conf["hostAddress"]

    #start server
    t = threading.Thread(target=run_server)
    t.start()
    if clearOnStart:
        try:
            shutil.rmtree("./config")
        except FileNotFoundError:
            pass
    while not ready:
        try:
            time.sleep(2)
            print("\x1b[2J\x1b[H")
            monitorManager.load()
            print('syncstream ready')
            print('- registered clients -')
            for mon in monitorManager.monitors:
                print('{}: {} ({})'.format(mon.index, mon.ip, mon.mac))
            print('press ctrl+c to start')
        except KeyboardInterrupt:
            print('Starting!')
            # make killable by ctrl-c
            logging.debug('setting SIGINT handler')
            signal.signal(signal.SIGINT, signal.SIG_DFL)
            # init main-class and main-loop
            logging.debug('Creating Pipeline')
            pipeline = Pipeline()
            source = TCPSource(9999)
            netclock = NetClock(pipeline, None, 10000)
            pipeline.configure()
            pipeline.start()
            netclock.start()
            ncdict = netclock.netprov
            ready = True
            logging.info('running GObject MainLoop')
            MainLoop.run()


if __name__ == '__main__':
    main()
