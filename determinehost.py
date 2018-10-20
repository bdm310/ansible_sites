#!/usr/bin/python

# Methods:
# A node comes up and gathers the following:
#  Hostname
#  DHCP assigned IP addresses and netmasks
#  For interfaces without DHCP IPs, attempt to ping the gateway for 
#    every subnet that exists in the topology to try and determine
#    if we're on a subnet without DHCP (yet)
#  

import sys
from subprocess import check_output
from loadtopology import loadtopology
from ipaddress import IPv4Network, IPv4Address
from ping import ping

if len(sys.argv) > 2:
    print("Too many arguments")
    quit()

inputfile = sys.argv[1]

networks, machines = loadtopology(inputfile)

hostname = check_output(['hostname'])

for machine in machines:
    if machine == hostname: quit()

ips = check_output(['hostname', '-I'])

ips = ips.split(' ')[:-1]
ips = [IPv4Address(unicode(ip)) for ip in ips]

localnetworks = []
for network, netparams in networks.items():
    for ip in ips:
        if 'subnet' in netparams:
            if ip in netparams['subnet'] and network not in localnetworks: localnetworks.append(network)
    

print(ips)
print(localnetworks)

