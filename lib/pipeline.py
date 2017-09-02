#!/usr/bin/python3
import os, logging, subprocess

import gi

gi.require_version("Gst", "1.0")

from gi.repository import Gst

# import library components
from lib.monitor import MonitorManager


class Pipeline(object):
    def __init__(self):
        self.log = logging.getLogger('Pipeline')
        self.mm = MonitorManager()
        self.mm.load()
        self.speed = "ultrafast"
        self.source = None
        self.dummysrc = None
        self.linked = False

    def configure(self):
        self.pipeline = None
        pipelineTemplate = """
        rtpbin name=rtpbin 
        
        queue name=input
        ! rtph264depay
        ! decodebin
        ! videoconvert
        ! videoscale
        ! capsfilter caps="video/x-raw, width={width}, height={height}"
        ! tee name=t 
        ! queue 
        ! x264enc speed-preset={speed} 
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
        ! queue
        ! videocrop left={left} top={top} right={right} bottom={bottom}
        ! x264enc speed-preset={speed} 
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
                                           preview_host="10.128.10.11",
                                           preview_rtp_port="10000",
                                           preview_rtcp_send_port="20000",
                                           preview_rtcp_recv_port="30000")
        for monitorid in self.mm.monitors.keys():
            rect = self.mm.getMonitorCropRect(monitorid)
            size = self.mm.getMonitorSize(monitorid)
            pipeline += monitorTemplate.format(left=rect[0], top=rect[1], right=rect[2], bottom=rect[3],
                                               width=size[0], height=size[1], speed=self.speed,
                                               host=self.mm.monitorHosts[monitorid][1],
                                               rtp_port="{}".format(10000 + monitorid),
                                               rtcp_send_port="{}".format(20000 + monitorid),
                                               rtcp_recv_port="{}".format(30000 + monitorid),
                                               id=monitorid)

        self.log.debug("Generated Pipeline")
        self.log.debug(pipeline)

        self.pipeline = Gst.parse_launch(pipeline)

        self.source = Gst.ElementFactory.make("udpsrc", "video-source")
        self.source.set_property("port", 9999)
        self.source.set_property("caps",
                                 Gst.Caps.from_string(
                                     "application/x-rtp"
                                 )
                                 )

        self.dummysrc = Gst.ElementFactory.make("videotestsrc", "video-source")

        self.pipeline.add(self.source)
        self.source.link(self.pipeline.get_by_name("input"))

        bus = self.pipeline.get_bus()
        bus.add_signal_watch()
        bus.enable_sync_message_emission()
        bus.connect("message", self.on_message)

        self.linked = True

    def on_message(self, bus, message):
        t = message.type
        if t == Gst.MessageType.EOS:
            self.dummysrc.link(self.pipeline.get_by_name("input"))
            self.source.unlink()
            self.linked = False
            self.log.info("Pipeline linked to dummy source")

        elif t == Gst.MessageType.STREAM_START:
            if not self.linked:
                self.source.link(self.pipeline.get_by_name("input"))
                self.dummysrc.unlink()
                self.linked = True
                self.log.info("Pipeline linked to real source")

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
