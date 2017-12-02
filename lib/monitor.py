import json
import os


class Monitor:
    def __init__(self, **kwargs):
        self.load(kwargs)

    def load(self, data):
        self.index = data.get("index", 0)
        self.mac = data.get("mac", "")
        self.ip = data.get("ip", "")

        self.physicalWidth = data.get("physicalWidth", 0)
        self.physicalHeight = data.get("physicalHeight", 0)
        self.physicalOffsetX = data.get("physicalOffsetX", 0)
        self.physicalOffsetY = data.get("physicalOffsetY", 0)
        self.physicalBorderWidth = data.get("physicalBorderWidth", 0)
        self.physicalBorderHeight = data.get("physicalBorderHeight", 0)

        self.virtualWidth = data.get("virtualWidth", 0)
        self.virtualHeight = data.get("virtualHeight", 0)

    def save(self):
        return self.__dict__

    def lerp(self, x, src, target):
        return int(float(x) * (float(target) / float(src)))

    def getCrop(self, physicalMonitorSize, virtualMonitorSize):
        physicalMonitorWidth = physicalMonitorSize[0]
        physicalMonitorHeight = physicalMonitorSize[1]

        renderWidth = virtualMonitorSize[0]
        renderHeight = virtualMonitorSize[1]

        dpiX = renderWidth/self.physicalWidth
        dpiY = renderHeight/self.physicalHeight

        borderWidth = self.physicalBorderWidth*dpiX
        borderHeight = self.physicalBorderHeight*dpiY
        (l, t, r, b) = self.getCropWithoutBorders(physicalMonitorSize, virtualMonitorSize)

        return (int(l + borderWidth), int(t + borderHeight), int(r + borderWidth), int(b + borderHeight))

    def getCropWithoutBorders(self, physicalMonitorSize, virtualMonitorSize):
        physicalMonitorWidth = physicalMonitorSize[0]
        physicalMonitorHeight = physicalMonitorSize[1]

        renderWidth = virtualMonitorSize[0]
        renderHeight = virtualMonitorSize[1]

        l = self.lerp(self.physicalOffsetX, physicalMonitorWidth, renderWidth)
        t = self.lerp(self.physicalOffsetY, physicalMonitorHeight, renderHeight)
        r = renderWidth - self.lerp(self.physicalOffsetX, physicalMonitorWidth, renderWidth)
        b = renderHeight - self.lerp(self.physicalOffsetY, physicalMonitorHeight, renderHeight)
        return l, t, r, b

    def getVirtualOffset(self):
        dpiX = self.virtualWidth/self.physicalWidth
        dpiY = self.virtualHeight/self.physicalHeight

        return (
            dpiX*(self.physicalOffsetX + self.physicalBorderWidth),
            dpiY*(self.physicalOffsetY + self.physicalBorderHeight)
        )


class MonitorManager:
    def __init__(self):
        self.monitors = []
        self.targetwidth = 1920

    def addMonitor(self, monitor):
        if not isinstance(monitor, Monitor):
            monitor["index"] = len(self.monitors) + 1
            monitor = Monitor(**monitor)
        self.monitors.append(monitor)
        return monitor.index

    def replaceMonitor(self, mac, ip):
        for monitor in self.monitors:
            if monitor.mac == mac:
                monitor.ip = ip
                return monitor.index

    def delMonitor(self, id):
        for monitor in self.monitors:
            if monitor.index == id:
                self.monitors.remove(monitor)
                return

    def hasMonitor(self, mac):
        for monitor in self.monitors:
            if monitor.mac == mac:
                return True
        return False

    def getMonitor(self, id):
        for monitor in self.monitors:
            if monitor.index == id:
                return monitor

    def getMaxKey(self, func, default=1):
        if not self.monitors:
            return default
        return max(map(func, self.monitors))

    def getPhysicalWidth(self):
        return self.getMaxKey(lambda m: m.physicalWidth + m.physicalOffsetX, 1920)

    def getPhysicalHeight(self):
        return self.getMaxKey(lambda m: m.physicalHeight + m.physicalOffsetY, 1080)

    def getRenderTargetScreen(self):
        w = self.targetwidth
        h = self.lerp(self.targetwidth, self.getPhysicalWidth(), self.getPhysicalHeight())
        return w, h

    def lerp(self, x, width_src, width_tgt):
        return int(x * (width_tgt / width_src))

    def getMonitorCropRect(self, id):
        monitor = self.getMonitor(id)
        physicalWidth = self.getMaxKey(lambda m: m.physicalOffsetX + m.physicalWidth + m.physicalBorderWidth)
        physicalHeight = self.getMaxKey(lambda m: m.physicalOffsetY + m.physicalHeight + m.physicalBorderHeight)
        virtualWidth, virtualHeight = self.getRenderTargetScreen()

        return monitor.getCrop((physicalWidth, physicalHeight), (virtualWidth, virtualHeight))

    def getMonitorResolution(self, id):
        monitor = self.getMonitor(id)
        return monitor.virtualWidth, monitor.virtualHeight

    def save(self):
        if not os.path.exists("./config"):
            os.mkdir("./config")
        with open("./config/monitors", "w") as f:
            data = list(map(lambda m: m.save(), self.monitors))
            json.dump(data, f)

    def load(self):
        if os.path.exists("./config"):
            with open("./config/monitors") as f:
                data = json.load(f)
                self.monitors = list(map(lambda m: Monitor(**m), data))

    def iterids(self):
        for monitor in self.monitors:
            yield monitor.index


if __name__ == '__main__':
    mm = MonitorManager()
    mm.load()
    print(mm.monitors)
    # mm.addMonitor({
    #     "index":0,
    #     "ip":"127.0.0.1",
    #     "physicalWidth":20,
    #     "physicalHeight": 10,
    #     "physicalOffsetX":0,
    #     "physicalOffsetY":0,
    #     "physicalBorderWidth":1,
    #     "physicalBorderHeight":1,
    #     "virtualWidth":1280,
    #     "virtualHeight":1024,
    # })
    # mm.addMonitor({
    #     "index":1,
    #     "ip":"127.0.0.1",
    #     "physicalWidth":20,
    #     "physicalHeight": 10,
    #     "physicalOffsetX":0,
    #     "physicalOffsetY":10,
    #     "physicalBorderWidth":1,
    #     "physicalBorderHeight":1,
    #     "virtualWidth":1280,
    #     "virtualHeight":1024,
    # })
    print(mm.getRenderTargetScreen())
    for m in mm.iterids():
        print(mm.getMonitorCropRect(m))