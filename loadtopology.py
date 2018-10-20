#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 31 22:55:33 2018

@author: glados
"""

import yaml
from ipaddress import IPv4Network, IPv4Address

def domain(network, networks):
    domain = '.' + network
    
    while 'routed' in networks[network]:
        network = networks[network]['routed']
        domain = domain + '.' + network
    return domain

def loadtopology(filepath):
    with open(filepath, 'r') as stream:
        try:
            inputdata = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
    
    networks = {}
    machines = {}
    
    for item in inputdata:
        if item['type'] == 'network':
            name = item['name']
            networks[name] = {}
            if 'routed' in item:
                networks[name]['routed'] = item['routed']
            if 'subnet' in item:
                networks[name]['subnet'] = IPv4Network(unicode(item['subnet']))
            elif 'public' not in item:
                print("No subnet definition for network " + item['name'])
                quit()
    
    #Iterate for machines afterward so we know we have all the networks already            
    for item in inputdata:
        if item['type'] == 'machine':
            name = item['name']
            
            if 'network' in item:
                name = name + domain(item['network'], networks)
            
            machines[name] = {}
            if 'network' in item:
                machines[name]['network'] = item['network']
            if 'ip' in item:
                machines[name]['ip'] = IPv4Address(unicode(item['ip']))
    
    for netname, netparams in networks.items():
        if 'routed' in netparams:
            routerip = str(netparams['subnet'][5])
            virtip = str(netparams['subnet'][1])
            routernetmask = '24'
            machines['router' + domain(netname, networks)] = {
                    'roles': ['router'], 
                    'networks': [netname, netparams['routed']], 
                    'vars': {'ip': routerip, 
                             'router_virt_ip': virtip, 
                             'router_lan_prefix': routernetmask, 
                             'router_keepalive_state': 'MASTER', 
                             'router_keepalive_priority': '100'}}
            
    return networks, machines