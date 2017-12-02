import json
import logging

class Config:
	def __init__(self, filename=None):
		self.log = logging.getLogger("Config")
		self.config = {}
		self.filename = filename if not filename is None else "config.json"

	def __getitem__(self, key):
		return self.config[key]

	def __setitem__(self, key, val):
		self.log.debug("set\t" + str(key) + "\t" + str(val))
		self.config[key] = val
		with open(self.filename, "w") as f:
			json.dump(self.config, f)

	def load(self):
		with open(self.filename, "r") as f:
			json_str = f.read()
			self.config = json.loads(json_str)


def loadconfig(filename):
	conf = Config(filename)
	conf.load()
	return conf

def genDefaultConf():
	conf = Config("config.json")
	macMapping = {
		"b8:27:eb:3f:3e:49": (0, 0, 1280, 1024),
		"b8:27:eb:7e:66:7d": (0, 1024, 1280, 1024),
		"b8:27:eb:94:22:1b": (0, 2048, 1280, 1024),

		"b8:27:eb:c7:e3:53": (1280, 0, 1280, 1024),
		"b8:27:eb:ab:7c:8e": (1280, 1024, 1280, 1024),
		"b8:27:eb:01:e0:da": (1280, 2048, 1280, 1024),

		"b8:27:eb:1b:99:2e": (2560, 0, 1280, 1024),
		"b8:27:eb:04:bf:2a": (2560, 1024, 1280, 1024),
		"b8:27:eb:f6:0c:00": (2560, 2048, 1280, 1024)

	}
	hostAddress = "10.128.9.121"
	conf["hostAddress"] = hostAddress
	conf["macMapping"] = macMapping
	return conf
