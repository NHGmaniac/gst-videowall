#!/usr/bin/python3
import logging, sys
import http.server
import subprocess
from lib.loghandler import LogHandler
from lib.args import Args
from lib.monitor import MonitorManager

macMapping = {
    "aa:bb:cc:dd:ee:ff": (0, 0, 1280, 1024)
}
hostAddress = "10.128.9.47"
monitorManager = MonitorManager()
syncstream = None

def add_device(mac, ip):
    if monitorManager.hasMonitor(ip):
        return None
    id = len(monitorManager.monitors) + 1
    monitorManager.addMonitor(id, *macMapping[mac], ip)
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
        # Send response status code
        self.send_response(200)

        data = self.path
        if not data:
            self.send_error(418, "I'm a teapot")
            return
        data = data.split("/")
        if not len(data) == 3 or len(data[1]) != 17:
            self.send_error(418, "I'm a teapot")
            return
        mac = data[1]
        ip = data[2]
        client_id = add_device(mac, ip)
        if client_id is None:
            self.send_error(418, "I'm a teapot")
            return

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

    server_address = (hostAddress, 8081)
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

    run_server()

if __name__ == '__main__':
    main()
