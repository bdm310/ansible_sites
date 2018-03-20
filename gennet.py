#!/usr/bin/python

import sys
import yaml

def domain(network):
    domain = '.' + network
    
    while 'routed' in networks[network]:
        network = networks[network]['routed']
        domain = domain + '.' + network
    return domain

if len(sys.argv) > 2:
    print("Too many arguments")
    quit()

inputfile = sys.argv[1]
inventorypath = 'inventories/production/'
playbookpath = 'local.yml'

with open(inputfile, 'r') as stream:
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
            networks[name]['subnet'] = item['subnet'].split("/")
        elif 'public' not in item:
            print("No subnet definition for network " + item['name'])
            quit()
    
    if item['type'] == 'machine':
        name = item['name']
        
        if 'network' in item:
            name = name + domain(item['network'])
        
        machines[name] = {}
        if 'network' in item:
            machines[name]['network'] = item['network']

for netname, netparams in networks.items():
    if 'routed' in netparams:
        routerip = ".".join(netparams['subnet'][0].split(".")[0:3] + ['5'])
        routernetmask = '24'
        machines['router' + domain(netname)] = {
                'roles': ['router'], 
                'networks': [netname, netparams['routed']], 
                'vars': {'router_lan_ip': routerip, 
                         'router_lan_prefix': routernetmask, 
                         'router_keepalive_state': 'MASTER', 
                         'router_keepalive_priority': '100'}}
        
hostfile = open(inventorypath + 'hosts', 'w')
hostfile.write('\n'.join(machines.keys()))
hostfile.close()

playbookfile = open(playbookpath, 'w')
for macname, macparams in machines.items():
    if 'roles' in macparams:
        playbookfile.write('- hosts: ' + macname + '\n  roles:\n    - ' + '\n    - '.join(macparams['roles']))
    if 'vars' in macparams:
        varsfile = open(inventorypath + 'host_vars/' + macname, 'w')
        varsfile.write('---\n')
        for k, v in macparams['vars'].items():
            varsfile.write(k + ': ' + v + '\n')
        varsfile.close()
playbookfile.close()

print(networks)
print(machines)