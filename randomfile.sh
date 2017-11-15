#!/usr/bin/env bash
cd /mnt/media/videowall-videos
while true; do
    ls |sort -R |tail -1 |while read file; do
        gst-launch-1.0 -v filesrc location=$file ! decodebin name=demux ! fakesink demux. ! video/x-raw ! videorate ! videoscale ! video/x-raw, format=I420, width=1920, height=1080, framerate=25/1 ! rtpvrawpay ! udpsink port=9999 host=127.0.0.1
    done
    sleep 5
done
