#!/usr/bin/env bash
cd ~/videowall-videos/
while true; do
    ls |sort -R |tail -1 |while read file; do
        gst-launch-1.0 -v filesrc location=$file ! decodebin ! videocsale ! video/x-raw, width=1920, height=1080 ! x264enc ! rtph264pay ! udpsink host=127.0.0.1 port=9999
    done
    sleep 5
done