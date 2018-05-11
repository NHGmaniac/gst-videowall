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
        ! decodebin
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
        self.speed = "ultrafast"
        self.option_string = "keyint=1"
        self.clock = None
        self.pipeline = None

    def configure(self):
        self.mm.load()
        pipelineTemplate = """
        rtpbin name=rtpbin max-rtcp-rtp-time-diff=50 latency=2000
        

        intervideosrc channel=video
        ! queue max-size-time=0 max-size-buffers=0 max-size-bytes=173741274 min-threshold-bytes=1000000
        ! videoconvert
        ! videoscale
        ! capsfilter caps="video/x-raw, width={width}, height={height}, framerate=25/1"
        ! textoverlay text="github.com/\r\nNHGmaniac/\r\ngst-videowall" valignment=top halignment=left xpad=100 ypad=100 font-desc="Sans, 12" shaded-background=yes
        ! tee name=t     
        
        multiqueue name=mq
        t.
        ! mq.
        mq.
        ! queue max-size-time=0 max-size-buffers=0 max-size-bytes=1073741274
        ! x264enc speed-preset=medium option-string="keyint=1" tune=zerolatency intra-refresh=true quantizer=30 pass=5
        ! rtph264pay 
        ! rtpbin.send_rtp_sink_0
        
        rtpbin.send_rtp_src_0
        ! udpsink port={preview_rtp_port} host={preview_host}
        
        rtpbin.send_rtcp_src_0
        ! udpsink port={preview_rtcp_send_port} sync=false async=false host={preview_host}
        
        udpsrc port={preview_rtcp_recv_port}
        ! rtpbin.recv_rtcp_sink_0
        """

        monitorTemplate = """
        t.
        ! mq.
        mq.
        ! videocrop left={left} top={top} right={right} bottom={bottom}
        ! queue max-size-time=0 max-size-buffers=0 max-size-bytes=1073741274
        ! x264enc speed-preset={speed} option-string="{option_string}" tune=fastdecode intra-refresh=true quantizer=30 pass=5
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
                                           preview_host="127.0.0.1",
                                           preview_rtp_port="11000",
                                           preview_rtcp_send_port="12000",
                                           preview_rtcp_recv_port="13000",
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
                                               rtp_port="{}".format(11000 + monitorid),
                                               rtcp_send_port="{}".format(12000 + monitorid),
                                               rtcp_recv_port="{}".format(13000 + monitorid),
                                               id=monitorid)

        self.log.debug("Generated Pipeline")
        self.log.debug(pipeline)

        self.pipeline = Gst.parse_launch(pipeline)
        self.clock = self.pipeline.get_clock()
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


class RecvPipeline(object):
    def __init__(self, host, monitor_id, raspi=False):
        self.log = logging.getLogger('RecvPipeline')
        self.clock = None
        self.pipeline = None
        self.id = monitor_id
        self.host = host
        self.raspi = raspi

    def setclock(self, clock):
        self.clock = clock
        self.pipeline.set_clock(clock)

    def configure(self):

        pipelineTemplate = """
        rtpbin name=rtpbin
        
        udpsrc caps="application/x-rtp, media=video, clock-rate=90000, encoding-name=H264"
        port={rtp_port} ! rtpbin.recv_rtp_sink_0
        
        
        udpsrc port={rtcp_recv_port} ! rtpbin.recv_rtcp_sink_0
        
        rtpbin.send_rtcp_src_0 ! udpsink port={rtcp_send_port} host={host} sync=false async=false
        """
        if self.raspi:
            pipelineTemplate += """
            rtpbin. ! rtph264depay
            ! queue flush-on-eos=true max-size-buffers=0 max-size-time=0 max-size-bytes=404857600 min-threshold-bytes=50000000 ! h264parse 
            ! mpegtsmux ! filesink location=gst-omx-pipe 
            """
        else:
            pipelineTemplate += """
            rtpbin. ! decodebin ! autovideosink
            """

        pipeline = pipelineTemplate.format(host=self.host,
                                           rtp_port=11000 + self.id,
                                           rtcp_recv_port=12000 + self.id,
                                           rtcp_send_port=13000 + self.id)
        self.log.debug("Generated Pipeline")
        self.log.debug(pipeline)

        self.pipeline = Gst.parse_launch(pipeline)
        self.clock = self.pipeline.get_clock()

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