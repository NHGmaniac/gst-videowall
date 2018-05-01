#!/usr/bin/python3
from netrecv import NetRevc
import sys

raspi = True

def main():
    n = NetRevc(host=sys.argv[2], monitor_id=int(sys.argv[1]), raspi=raspi)
    n.run()


main()
