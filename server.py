#!/usr/bin/python3
import logging, sys, time, shutil
import http.server
import subprocess
import threading
import lib.config as config
from lib.config import loadconfig
from lib.loghandler import LogHandler
from lib.args import Args
from lib.monitor import MonitorManager
from syncstream import SyncStream
macMapping = {}

monitorManager = MonitorManager()

syncstream = None
conf = None
stop = False
t = None

clearOnStart = True

def add_device(mac, ip):
    if monitorManager.hasMonitor(mac):
        return monitorManager.replaceMonitor(mac, ip)
    monitorconf = macMapping[mac]
    monitorconf["ip"] = ip
    return monitorManager.addMonitor(monitorconf)


def startProcess():
    global syncstream
    if syncstream:
        syncstream.reload()
    else:
        syncstream = SyncStream()
        syncstream.run()


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

        self.send_response(200, "OK")

        # Send headers
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        # Send message back to client
        # Write content as utf-8 data
        self.wfile.write(bytes("{} {}".format(client_id, hostAddress), "utf8"))
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
    global conf, macMapping, hostAddress, t
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
        shutil.rmtree("./config")
    while True:
        time.sleep(2)
        print("\x1b[2J\x1b[H")
        monitorManager.load()
        print('syncstream ready')
        print('- registered clients -')
        for mon in monitorManager.monitors:
            print('{}: {} ({})'.format(mon.index, mon.ip, mon.mac))

if __name__ == '__main__':
    main()
