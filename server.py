#!/usr/bin/python3
import logging, sys
import http.server
import subprocess
from lib.loghandler import LogHandler
from lib.args import Args
from lib.monitor import MonitorManager
macMapping = {
            "b8:27:eb:3f:3e:49": (0, 0, 1280, 1024),
            "b8:27:eb:04:bf:2a": (0, 1024, 1280, 1024),

            "b8:27:eb:36:46:29": (1280, 0, 1280, 1024),
            "b8:27:eb:1b:99:2e": (1280, 1024, 1280, 1024),

            "b8:27:eb:7e:66:7d": (2560, 0, 1280, 1024),
            "b8:27:eb:ff:f5:b0": (2560, 1024, 1280, 1024)

        }



hostAddress = "138.201.80.211"
monitorManager = MonitorManager()
monitorManager.load()

syncstream = None


def add_device(mac, ip):
    if monitorManager.hasMonitor(mac):
        return monitorManager.replaceMonitor(mac, ip)
    id = len(monitorManager.monitors) + 1
    monitorManager.addMonitor(id, *macMapping[mac], mac, ip)
    return id

def startProcess():
    global syncstream
    if syncstream:
        syncstream.kill()
    monitorManager.save()
    syncstream = subprocess.Popen(["./syncstream.py"])


class auto_configure_RequestHandler(http.server.BaseHTTPRequestHandler):
    # GET
    def do_GET(self):


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

        startProcess()

        return


def run_server():
    logging.getLogger('ConfigServer').info('starting server...')

    server_address = ("127.0.0.1", 8081)
    httpd = http.server.HTTPServer(server_address, auto_configure_RequestHandler)

    logging.getLogger('ConfigServer').info('running server...')
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
    startProcess()
    run_server()

if __name__ == '__main__':
    main()
