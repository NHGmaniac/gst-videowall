#!/usr/bin/env bash
id=$1
host=$2
if [ -z "$host" ]; then host="127.0.0.1"; fi
rtp_port=$(echo "10000 + $id" | bc)
rtcp_send_port=$(echo "30000 + $id" | bc)
rtcp_recv_port=$(echo "20000 + $id" | bc)
mkfifo gst-omx-pipe
while true; do \
omxplayer --live --win "0 0 1280 1024" gst-omx-pipe &
gst-launch-1.0 rtpbin name=rtpbin \
	udpsrc caps="application/x-rtp,media=(string)video,clock-rate=(int)90000,encoding-name=(string)H264" \
	port=$rtp_port ! rtpbin.recv_rtp_sink_0 \
        rtpbin. ! rtph264depay ! queue flush-on-eos=true max-size-buffers=0 max-size-time=0 max-size-bytes=104857600 ! h264parse ! mpegtsmux ! filesink buffer-mode=2 location=gst-omx-pipe  \
	udpsrc port=$rtcp_recv_port ! rtpbin.recv_rtcp_sink_0 \
	rtpbin.send_rtcp_src_0 ! udpsink port=$rtcp_send_port host=$host sync=false async=false
	sleep 2
	done

