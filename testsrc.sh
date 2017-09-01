#!/usr/bin/env bash
gst-launch-1.0 videotestsrc ! videoscale ! video/x-raw, width=1280, height=720 ! jpegenc ! rtpjpegpay ! udpsink host=10.128.9.47 sync=true port=9999
