#!/usr/bin/env bash
cd ~/videowall-videos/
while true; do
    ls |sort -R |tail -1 |while read file; do
        gst-launch-1.0 filesrc location=$file ! decodebin ! x264enc ! rtph264pay ! udpsink host=10.128.0.1 sync=true port=9999
    done
    sleep 5
done