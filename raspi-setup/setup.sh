#!/usr/bin/env bash
sleep 10
sh -c "TERM=linux setterm -blank 0 >/dev/tty0"
sh -c "TERM=linux setterm -clear all >/dev/tty0"
sh -c "TERM=linux echo Starting Setup... >/dev/tty0"
sh -c "TERM=linux hostname -I >/dev/tty0"
mkdir /home/pi/.ssh
mkdir /etc/gst-videowall
mkdir /usr/share/raspi-setup
until curl ip4.nnev.de; do
    sh -c "TERM=linux echo no ipv4 yet... >/dev/tty0"
done
curl https://github.com/NHGmaniac.keys -o /home/pi/.ssh/authorized_keys
curl https://github.com/Felix5721.keys >> /home/pi/.ssh/authorized_keys
curl https://github.com/tynsh.keys >> /home/pi/.ssh/authorized_keys
curl https://github.com/k0rmarun.keys >> /home/pi/.ssh/authorized_keys
curl https://github.com/chrko.keys >> /home/pi/.ssh/authorized_keys
curl https://raw.githubusercontent.com/NHGmaniac/gst-videowall/master/raspi-setup/setup-cont.sh -o /usr/share/raspi-setup/setup-cont.sh
chmod +x /usr/share/raspi-setup/setup-cont.sh
exec /usr/share/raspi-setup/setup-cont.sh
