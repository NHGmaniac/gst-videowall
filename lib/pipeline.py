#!/usr/bin/python3
import os, logging, subprocess

from gi.repository import Gst
from lib.tcpsingleconnection import TCPSingleConnection

# import library components
from lib.monitor import MonitorManager


#        udpsrc port=9999 caps="application/x-rtp, media=(string)video, clock-rate=(int)90000, encoding-name=(string)H264, packetization-mode=(string)1, profile-level-id=(string)640028, payload=(int)96, ssrc=(uint)3042026353, timestamp-offset=(uint)1763490137, seqnum-offset=(uint)614, a-framerate=(string)25"
#        ! rtph264depay
#        ! decodebin
#        udpsrc port=9999 caps="application/x-rtp, media=(string)video, clock-rate=(int)90000, encoding-name=(string)RAW, sampling=(string)YCbCr-4:2:0, depth=(string)8, width=(string)1920, height=(string)1080, colorimetry=(string)BT709-2, payload=(int)96, ssrc=(uint)2100997544, timestamp-offset=(uint)3604836381, seqnum-offset=(uint)15493, a-framerate=(string)25"
#        ! rtpvrawdepay


class TCPSource(TCPSingleConnection):
    def __init__(self, port):
        self.log = logging.getLogger("TCPSource")
        super().__init__(port)
        self.fd = None
        self.pipeline = None

    def on_accepted(self, conn, addr):
        self.fd = conn.fileno()
        pipeline = """
        fdsrc fd={fd} blocksize=1048576
        ! queue
        ! matroskademux name=demux
        ! intervideosink channel=video
        """
        self.pipeline = Gst.parse_launch(pipeline.format(fd=self.fd))
        self.pipeline.bus.add_signal_watch()
        self.pipeline.bus.connect("message::eos", self.on_eos)
        self.pipeline.bus.connect("message::error", self.on_error)
        self.pipeline.set_state(Gst.State.PLAYING)

    def disconnect(self):
        self.pipeline.set_state(Gst.State.NULL)
        self.pipeline = None
        self.close_connection()

    def on_eos(self, bus, message):
        if self.currentConnection is not None:
            self.disconnect()

    def on_error(self, bus, message):
        if self.currentConnection is not None:
            self.disconnect()


class Pipeline(object):
    def __init__(self):
        self.log = logging.getLogger('Pipeline')
        self.mm = MonitorManager()
        self.mm.load()
        self.speed = "medium"
        self.option_string = "keyint=1"

    def configure(self):
        self.pipeline = None
        pipelineTemplate = """
        rtpbin name=rtpbin max-rtcp-rtp-time-diff=50 latency=2000
        
        
        
        intervideosrc channel=video
        ! decodebin
        ! queue max-size-time=0 max-size-buffers=0 max-size-bytes=173741274 min-threshold-bytes=1000000
        ! videoconvert
        ! videoscale
        ! capsfilter caps="video/x-raw, width={width}, height={height}"
        ! textoverlay text="github.com/\r\nNHGmaniac/\r\ngst-videowall" valignment=top halignment=left xpad=100 ypad=100 font-desc="Sans, 12" shaded-background=yes
        ! compositor name=mix sink_1::ypos=100 sink_1::xpos={offsetlogo} sink_0::alpha=1 sink_1::alpha=0.7 sink_1::width=320 sink_1::height=100
        ! tee name=t
        
        filesrc location={logo}
        ! decodebin
        ! imagefreeze
        ! videoconvert
        ! videoscale
        ! capsfilter caps="video/x-raw, format=I420, width=1920, framerate=1/1"
        ! mix.        
        
        multiqueue name=mq        
        """

        monitorTemplate = """
        t.
        ! mq.
        mq.
        ! videocrop left={left} top={top} right={right} bottom={bottom}
        ! queue max-size-time=0 max-size-buffers=0 max-size-bytes=1073741274
        ! x264enc speed-preset={speed} option-string="{option_string}" tune=zerolatency intra-refresh=true quantizer=30 pass=5
        ! rtph264pay 
        ! rtpbin.send_rtp_sink_{id}
        
        rtpbin.send_rtp_src_{id}
        ! udpsink port={rtp_port} host={host}
        
        rtpbin.send_rtcp_src_{id}
        ! udpsink port={rtcp_send_port} sync=false async=false host={host}
        
        udpsrc port={rtcp_recv_port}
        ! rtpbin.recv_rtcp_sink_{id}
        """
        pipeline = pipelineTemplate.format(width=self.mm.getRenderTargetScreen()[0],
                                           height=self.mm.getRenderTargetScreen()[1],
                                           speed=self.speed,
                                           option_string=self.option_string,
                                           preview_host="10.128.9.47",
                                           preview_rtp_port="10000",
                                           preview_rtcp_send_port="20000",
                                           preview_rtcp_recv_port="30000",
                                           offsetlogo=self.mm.getRenderTargetScreen()[0]-420,
                                           logo="nnev.png"
                                           )
        for monitorid in self.mm.iterids():
            l, t, r, b = self.mm.getMonitorCropRect(monitorid)
            self.log.debug("" + str(l) + " " + str(t) + " " + str(r) + " " + str(b) + " " + str(monitorid))
            size = self.mm.getMonitorResolution(monitorid)
            pipeline += monitorTemplate.format(left=l, top=t, right=r, bottom=b,
                                               width=size[0], height=size[1], speed=self.speed,
                                               option_string=self.option_string,
                                               host=self.mm.getMonitor(monitorid).ip,
                                               rtp_port="{}".format(10000 + monitorid),
                                               rtcp_send_port="{}".format(20000 + monitorid),
                                               rtcp_recv_port="{}".format(30000 + monitorid),
                                               id=monitorid)

        self.log.debug("Generated Pipeline")
        self.log.debug(pipeline)

        self.pipeline = Gst.parse_launch(pipeline)

    def start(self):
        self.log.info('Starting Pipeline')
        self.pipeline.set_state(Gst.State.PLAYING)

    def stop(self):
        self.log.info('Stopping Pipeline')
        self.pipeline.set_state(Gst.State.NULL)

    def restart(self):
        self.stop()
        self.configure()
        self.start()
