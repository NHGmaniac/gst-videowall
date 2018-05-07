#!/usr/bin/python3
from netrecv import NetRevc
import sys, logging

from lib.loghandler import LogHandler

raspi = True

def main():
    # configure logging
    docolor = sys.stderr.isatty()

    handler = LogHandler(docolor)
    logging.root.addHandler(handler)

    level = logging.DEBUG

    logging.root.setLevel(level)

    # init main-class and main-loop
    logging.debug('initializing NetRecv')
    n = NetRevc(host=sys.argv[2], monitor_id=int(sys.argv[1]), raspi=raspi, base_time=int(sys.argv[3]))
    n.run()


main()
