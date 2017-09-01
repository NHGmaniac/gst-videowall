#!/usr/bin/env bash
id=$1
host=$2
if [ -z "$host" ]; then host="127.0.0.1"; fi
rtp_port=$(echo "10000 + $id" | bc)
rtcp_send_port=$(echo "30000 + $id" | bc)
rtcp_recv_port=$(echo "20000 + $id" | bc)
while true; do \
gst-launch-1.0 -v rtpbin name=rtpbin \
	udpsrc caps="application/x-rtp,media=(string)video,clock-rate=(int)90000,encoding-name=(string)JPEG" \
	port=$rtp_port ! rtpbin.recv_rtp_sink_0 \
        rtpbin. ! rtpjpegdepay ! decodebin ! autovideosink \
	udpsrc port=$rtcp_recv_port ! rtpbin.recv_rtcp_sink_0 \
	rtpbin.send_rtcp_src_0 ! udpsink port=$rtcp_send_port host=$host sync=false async=false
	sleep 2
	done

