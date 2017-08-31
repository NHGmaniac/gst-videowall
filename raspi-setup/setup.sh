#!/usr/bin/env bash
sh -c "TERM=linux setterm -blank 0 >/dev/tty0"
sh -c "TERM=linux setterm -clear all >/dev/tty0"
sh -c "TERM=linux echo Starting Setup... >/dev/tty0"
sh -c "TERM=linux hostname -I >/dev/tty0"
mkdir /home/pi/.ssh
mkdir /etc/gst-videowall
mkdir /usr/share/raspi-setup
curl https://github.com/NHGmaniac.keys -o /home/pi/.ssh/authorized_keys
curl https://raw.githubusercontent.com/NHGmaniac/gst-videowall/master/raspi-setup/setup-cont.sh -o /usr/share/raspi-setup/setup-cont.sh
chmod +x /usr/share/raspi-setup/setup-cont.sh
exec /usr/share/raspi-setup/setup-cont.sh