class MonitorManager:
    def __init__(self):
        self.monitors = dict()
        self.monitorHosts = dict()
        self.targetwidth = 1920

        self.addMonitor(1, 0, 0, 1280, 1024, "10.128.128.20")
        self.addMonitor(2, 1280, 0, 1280, 1024, "10.128.128.21")
        self.addMonitor(3, 2560, 0, 1280, 1024, "10.128.128.21")

    def addMonitor(self, id, x, y, w, h, host):
        self.monitors[id] = (x, y, w, h)
        self.monitorHosts[id] = host

    def delMonitor(self, id):
        self.monitors.pop(id)
        self.monitorHosts.pop(id)

    def getTotalWidth(self):
        return max(map(lambda x: x[0] + x[2], self.monitors.values()))

    def getTotalHeight(self):
        return max(map(lambda x: x[1] + x[3], self.monitors.values()))

    def getRenderTargetScreen(self):
        w = self.targetwidth
        h = self.lerp(self.targetwidth, self.getTotalWidth(), self.getTotalHeight())
        return w, h

    def lerp(self, x, width_src, width_tgt):
        return int(x * width_tgt / width_src)

    def getMonitorCropRect(self, id):
        l = self.lerp(self.monitors[id][0], self.getTotalWidth(), self.getRenderTargetScreen()[0])
        t = self.lerp(self.monitors[id][1], self.getTotalHeight(), self.getRenderTargetScreen()[1])
        r = self.getRenderTargetScreen()[0] - self.lerp(self.monitors[id][0] + self.monitors[id][2], self.getTotalWidth(), self.getRenderTargetScreen()[0])
        b = self.getRenderTargetScreen()[1] - self.lerp(self.monitors[id][1] + self.monitors[id][3], self.getTotalHeight(), self.getRenderTargetScreen()[1])
        return l, t, r, b

    def getMonitorSize(self, id):
        return self.monitors[id][2], self.monitors[id][3]


if __name__ == '__main__':
    mm = MonitorManager()
    mm.addMonitor(0, 0, 0, 1280, 1024, "127.0.0.1")
    mm.addMonitor(1, 1280, 0, 1280, 1024, "127.0.0.1")
    mm.addMonitor(2, 2560, 0, 1280, 1024, "127.0.0.1")
    print(mm.getRenderTargetScreen())
    print(mm.getMonitorCropRect(0))
    print(mm.getMonitorCropRect(1))
    print(mm.getMonitorCropRect(2))