#!/usr/bin/env bash
gst-launch-1.0 -v videotestsrc ! videoscale ! videorate ! video/x-raw, width=1920, height=1080, framerate=25/1 ! rtpvrawpay ! udpsink host=127.0.0.1 sync=true port=9999