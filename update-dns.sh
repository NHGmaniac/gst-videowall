#!/usr/bin/env bash
id=$1
ipv4=$(curl http://ip4.nnev.de)
ipv6=$(curl http://ip6.nnev.de)
domain=videowall.krautsal.at

ttl=10

######
send_dns_update() {
echo "server tethys.hosts.c9n.de"
echo "del $id.$domain"
if [ -n "$ipv4" ]; then
  echo "add $id.$domain $ttl a $ipv4"
fi
if [ -n "$ipv6" ]; then
  echo "add $id.$domain $ttl aaaa $ipv6"
fi
echo "send"
}
send_dns_update | nsupdate -k video-wall-tsig.krautsal.at.tsig-key
