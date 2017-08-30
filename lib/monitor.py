import json
import os


class MonitorManager:
    def __init__(self):
        self.monitors = dict()
        self.monitorHosts = dict()
        self.targetwidth = 2560

        # self.addMonitor(1, 0, 0, 1280, 1024, "10.128.9.86")
        # self.addMonitor(2, 1280, 0, 1280, 1024, "10.128.9.106")
        # self.addMonitor(3, 0, 1024, 1280, 1024, "10.128.9.27")
        # self.addMonitor(4, 1280, 1024, 1280, 1024, "10.128.9.26")
        # self.addMonitor(5, 1280, 1024, 1280, 1024, "10.128.10.1")
        #        self.addMonitor(6, 2560, 1024, 1280, 1024, "10.128.10.1")                                                     #
        #        self.addMonitor(7, 0, 2048, 1280, 1024, "10.128.10.1")
        #        self.addMonitor(8, 1280, 2048, 1280, 1024, "10.128.10.1")
        #        self.addMonitor(9, 2560, 2048, 1280, 1024, "10.128.10.1")

    def addMonitor(self, id, x, y, w, h, host):
        self.monitors[id] = (x, y, w, h)
        self.monitorHosts[id] = host

    def delMonitor(self, id):
        self.monitors.pop(id)
        self.monitorHosts.pop(id)

    def getTotalWidth(self):
        return 1920 if len(self.monitors) is 0 else max(map(lambda x: x[0] + x[2], self.monitors.values()))

    def getTotalHeight(self):
        return 1080 if len(self.monitors) is 0 else max(map(lambda x: x[1] + x[3], self.monitors.values()))

    def getRenderTargetScreen(self):
        w = self.targetwidth
        h = self.lerp(self.targetwidth, self.getTotalWidth(), self.getTotalHeight())
        return w, h

    def lerp(self, x, width_src, width_tgt):
        return int(x * width_tgt / width_src)

    def getMonitorCropRect(self, id):
        l = self.lerp(self.monitors[id][0], self.getTotalWidth(), self.getRenderTargetScreen()[0])
        t = self.lerp(self.monitors[id][1], self.getTotalHeight(), self.getRenderTargetScreen()[1])
        r = self.getRenderTargetScreen()[0] - self.lerp(self.monitors[id][0] + self.monitors[id][2],
                                                        self.getTotalWidth(), self.getRenderTargetScreen()[0])
        b = self.getRenderTargetScreen()[1] - self.lerp(self.monitors[id][1] + self.monitors[id][3],
                                                        self.getTotalHeight(), self.getRenderTargetScreen()[1])
        return l, t, r, b

    def getMonitorSize(self, id):
        return self.monitors[id][2], self.monitors[id][3]

    def save(self):
        if not os.path.exists("./config"):
            os.mkdir("./config")
        with open("./config/monitors", "w") as f:
            json.dump(self.monitors, f)
        with open("./config/monitorHosts", "w") as f:
            json.dump(self.monitorHosts, f)

    def load(self):
        with open("./config/monitors") as f:
            data = json.load(f)
            self.monitors = {int(k): v for k, v in data.items()}

        with open("./config/monitorHosts") as f:
            data = json.load(f)
            self.monitorHosts = {int(k): v for k, v in data.items()}


if __name__ == '__main__':
    mm = MonitorManager()
    mm.addMonitor(0, 0, 0, 1280, 1024, "127.0.0.1")
    mm.addMonitor(1, 1280, 0, 1280, 1024, "127.0.0.1")
    mm.addMonitor(2, 2560, 0, 1280, 1024, "127.0.0.1")
    print(mm.getRenderTargetScreen())
    print(mm.getMonitorCropRect(0))
    print(mm.getMonitorCropRect(1))
    print(mm.getMonitorCropRect(2))
