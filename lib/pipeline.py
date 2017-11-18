#!/usr/bin/python3
import os, logging, subprocess

from gi.repository import Gst

# import library components
from lib.monitor import MonitorManager

#        udpsrc port=9999 caps="application/x-rtp, media=(string)video, clock-rate=(int)90000, encoding-name=(string)H264, packetization-mode=(string)1, profile-level-id=(string)640028, payload=(int)96, ssrc=(uint)3042026353, timestamp-offset=(uint)1763490137, seqnum-offset=(uint)614, a-framerate=(string)25"
#        ! rtph264depay
#        ! decodebin
#        udpsrc port=9999 caps="application/x-rtp, media=(string)video, clock-rate=(int)90000, encoding-name=(string)RAW, sampling=(string)YCbCr-4:2:0, depth=(string)8, width=(string)1920, height=(string)1080, colorimetry=(string)BT709-2, payload=(int)96, ssrc=(uint)2100997544, timestamp-offset=(uint)3604836381, seqnum-offset=(uint)15493, a-framerate=(string)25"
#        ! rtpvrawdepay

class Pipeline(object):
    def __init__(self):
        self.log = logging.getLogger('Pipeline')
        self.mm = MonitorManager()
        self.mm.load()
        self.speed = "fast"
        self.option_string = "keyint=1"

    def configure(self):
        self.pipeline = None
        pipelineTemplate = """
        rtpbin name=rtpbin 
        
        filesrc location=/mnt/media/videowall-videos/19.mp4
        ! decodebin
        ! queue max-size-time=0 max-size-buffers=0 max-size-bytes=1073741274
        ! videoconvert
        ! videoscale
        ! capsfilter caps="video/x-raw, width={width}, height={height}"
        ! tee name=t
        ! multiqueue name=mq
        ! x264enc speed-preset={speed} option-string="{option_string}" tune=zerolatency
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
        ! x264enc speed-preset={speed} option-string="{option_string}" tune=zerolatency intra-refresh=true quantizer=30 pass=5
        ! rtph264pay 
        ! queue max-size-buffers=0 max-size-time=0 max-size-bytes=1048576000
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
                                           preview_rtcp_recv_port="30000")
        for monitorid in self.mm.monitors.keys():
            rect = self.mm.getMonitorCropRect(monitorid)
            size = self.mm.getMonitorSize(monitorid)
            pipeline += monitorTemplate.format(left=rect[0], top=rect[1], right=rect[2], bottom=rect[3],
                                               width=size[0], height=size[1], speed=self.speed,
                                               option_string=self.option_string,
                                               host=self.mm.monitorHosts[monitorid][1],
                                               rtp_port="{}".format(10000+monitorid),
                                               rtcp_send_port="{}".format(20000+monitorid),
                                               rtcp_recv_port="{}".format(30000+monitorid),
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
