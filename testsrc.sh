#!/usr/bin/env bash
gst-launch-1.0 videotestsrc ! videoscale ! video/x-raw ! rtprawpay ! udpsink host=127.0.0.1 sync=true port=9999