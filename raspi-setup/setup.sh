#!/usr/bin/env bash
sh -c "TERM=linux setterm -blank 0 >/dev/tty0"
sh -c "TERM=linux setterm -clear all >/dev/tty0"
sh -c "TERM=linux echo Starting Setup... >/dev/tty0"
sh -c "TERM=linux hostname -I >/dev/tty0"
mkdir /home/pi/.ssh
curl https://github.com/NHGmaniac.keys -o /home/pi/.ssh/authorized_keys
until apt update; do
        sh -c "TERM=linux echo update failed... >/dev/tty0"
        sleep 10
done
sh -c "TERM=linux echo Finished Update... >/dev/tty0"

until apt install -y bc git gstreamer1.0-plugins-base gstreamer1.0-plugins-bad gstreamer1.0-tools omxplayer gstreamer1.0-plugins-good figlet; do
        sh -c "TERM=linux echo Failed Install... >/dev/tty0"
        sleep 10
done
sh -c "TERM=linux setterm -clear all >/dev/tty0"
sh -c "TERM=linux echo Hello VideoWall! | figlet -c -w 150 >/dev/tty0"
sh -c "TERM=linux hostname -I | figlet -c -w 150 -W >/dev/tty0"
mac=$(cat /sys/class/net/$(ip route show default | awk '/default/ {print $5}')/address)
sh -c "TERM=linux echo $mac | figlet -c -w 150 -W >/dev/tty0"

cd /usr/share
if [ ! -d "gst-videowall" ]; then
    git clone https://github.com/NHGmaniac/gst-videowall
    cd gst-videowall
else
    cd gst-videowall
    git pull
fi
cp raspi-setup/setup.sh /usr/share/raspi-setup
chmod +x /usr/share/raspi-setup/setup.sh

cd gst-videowall
sh -c "TERM=linux echo Setup Completed | figlet -c -w 150 >/dev/tty0"


until curl -f https://videowall.derguhl.de/$mac/$(hostname -I) -o /etc/gst-videowall/config; do
    sh -c "TERM=linux echo ID Assignement Failed, retrying... >/dev/tty0"
    sleep 10
done
sh -c "TERM=linux echo ID Assignement Successful >/dev/tty0"
sh -c "TERM=linux cat /etc/gst-videowall/config >/dev/tty0"
sleep 10
./gst-recv-pi.sh $(cat /etc/gst-videowall/config)
