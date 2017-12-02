import argparse
from lib.config import loadconfig

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("mac", type=str, help="Mac Address of Raspi of connected Monitor")
	parser.add_argument("x", type=int, help="x position in grid. 0 is left")
	parser.add_argument("y", type=int, help="y position in grid. 0 is top")
	parser.add_argument("-pW", type=int, default=1280, help="pixel width")
	parser.add_argument("-pH", type=int, default=1024, help="pixel height")
	parser.add_argument("-phyW", type=float, default=41, help="physical width")
	parser.add_argument("-phyH", type=float, default=34, help="physical height")
	parser.add_argument("-bW", type=float, default=1.5, help="border width")
	parser.add_argument("-bH", type=float, default=2, help="border height")
	args = parser.parse_args()

	conf = loadconfig("config.json")
	macMapping = conf["macMapping"]
	vals = {}
	vals["physicalWidth"] = args.phyW
	vals["physicalHeight"] = args.phyH
	vals["physicalBorderWidth"] = args.bW
	vals["physicalBorderHeight"] = args.bH
	vals["virtualWidth"] = args.pW
	vals["virtualHeight"] = args.pH
	vals["physicalOffsetX"] = x * 1280 
	vals["physicalOffsetX"] = y * 1024 
	macMapping[args.mac] = vals
	conf["macMapping"] = macMapping


if __name__ == "__main__":
	main()
