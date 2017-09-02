#!/usr/bin/env bash
gst-launch-1.0 -v videotestsrc ! videoscale ! video/x-raw ! rtpvrawpay ! udpsink host=127.0.0.1 sync=true port=9999