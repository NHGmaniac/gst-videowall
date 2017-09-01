#!/usr/bin/env bash
cd ../videofiles
while true; do
    ls |sort -R |tail -1 |while read file; do
        gst-launch-1.0 filesrc location=$file ! decodebin ! x264enc ! rtph264pay ! udpsink host=127.0.0.1 port=9999
    done
done