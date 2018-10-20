#!/usr/bin/python

import sys
import loadtopology.py

if len(sys.argv) > 2:
    print("Too many arguments")
    quit()

inputfile = sys.argv[1]
inventorypath = 'inventories/production/'
playbookpath = 'local.yml'

networks, machines = loadtopology(inputfile)
     
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