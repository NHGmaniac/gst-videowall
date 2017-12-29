#!/usr/bin/env bash
cd /mnt/media/videowall-videos
while true; do
    ls |sort -R |tail -1 |while read file; do
        gst-launch-1.0 -v filesrc location=$file ! decodebin ! video/x-raw ! videorate ! videoscale ! video/x-raw, format=I420, width=1920, height=1080, framerate=25/1 ! compositor name=mix sink_1::ypos=100 sink_1::xpos=1500 sink_1::width=320 sink_1::height=100! matroskamux ! tcpclientsink port=9999 host=127.0.0.1 filesrc location=/home/server/gst-videowall/nnev.png ! decodebin ! imagefreeze ! videoconvert ! videoscale ! capsfilter caps="video/x-raw, format=I420,width=1920, framerate=1/1" ! mix.
    done
    sleep 5
done
