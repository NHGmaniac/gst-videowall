#!/usr/bin/env bash

apt update
apt install bc git gstreamer1.0-plugins-base gstreamer1.0-plugins-bad gstreamer1.0-tools omxplayer gstreamer1.0-plugins-good figlet
sh -c "TERM=linux echo Hello VideoWall! | figlet -c -w 150 >/dev/tty0"
mkdir /home/pi/.ssh
curl https://github.com/NHGmaniac.keys -o /home/pi/.ssh/authorized_keys
cd /usr/share
git clone https://github.com/NHGmaniac/gst-videowall
cd gst-videowall
git pull
sh -c "TERM=linux echo Setup Completed | figlet -c -w 150 >/dev/tty0"
sh -c "TERM=linux hostname -I | figlet -c -w 150 >/dev/tty0"
id=$(cat /etc/gst-videowall/id)
host=$(cat /etc/gst-videowall/host)
sh -c "TERM=linux echo \"$id : $host\" | figlet -c -w 150 >/dev/tty0"
./gst-recv-pi.sh $id $host