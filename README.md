# gst-videowall

This project is used to display any video across multiple monitors using commodity hardware and software.
Playback and syncronisation is mostly done using GStreamer.

# Requirements

- Python 3
- GStreamer 1.0 + pygst
- Raspi only: omx-player + gst omx extensions

# Running it

## Render server

- Setup your monitor config file (config.json)
- Start server.py
- Stream some video to port 9999 (see testsrc.sh or randomfile.sh)
- Start receivers 

## Receivers
- Run receiver scripts gst-recv.sh or gst-recv-pi.sh (on raspi)

### Raspi-Autostart
- Get an raspbian stretch image onto your sd card
- ssh onto your raspi
- clone this repo
- execute raspi-setup/setup.py

# How is it working?

1. Send some data (i.e. testsrc/randomfile.sh) to the uninteruptable input handler (Port 9999)
2. The handler than proceeds to resize the input to fit a virtual canvas spanning all registered monitors (config.json).
3. Then the render server crops the correct area for each monitor from the virtual canvas (leaving out borders).
4. Encode the n sub videos in h264 (best format for raspi) and send via RTP
5. Clients and Server sync them selves via RTCP (sending current frame + timestamp + length of queue)
6. Clients buffer video for some time
7.1. Native clients decode and play directly on framebuffer
7.2. Rapi clients pass the video for accelerated decoding/playback to OMX-Player (where we can no longer guarantee sync)


TestSrc => Port 9999
RandomFile => Port 9999

Uninteruptable Input (9999) => Split + Resize to virtual canvas + Cut out display area => Send to raspi via rtp
Raspi + Server Sync via RTCP

# TODO
- Better documentation
- Remove config files + make it portable
- Setup tuning options in config

# Say hi
- If you're currently on 34C3 say hi to NHG/Kormarun/Tynsh at the NoName assembly
- Hack it
