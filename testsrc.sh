#!/usr/bin/env bash
gst-launch-1.0 -v videotestsrc ! video/x-raw, format=I420, width=1920, height=1080, framerate=25/1 ! matroskamux ! tcpclientsink port=9999 host=127.0.0.1
