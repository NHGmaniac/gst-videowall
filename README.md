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

# TODO
- Better documentation
- Remove config files + make it portable
- Setup tuning options in config

# Say hi
- If you're currently on 34C3 say hi to NHG/Kormarun/Tynsh at the NoName assembly
- Hack it
