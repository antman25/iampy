#!/usr/bin/env python3

# export AWS_CSM_ENABLED=true

import socket
import json

UDP_IP = "127.0.0.1"
UDP_PORT = 31000

iamMap = {}
iamDef = {}

def handle_api_call(msg):
    service = msg['Service']
    api = msg['Api']
    print('ApiMsg %s:%s' % (service,api))

def loadMaps():
   with open('map.json') as f:
       iamMap = json.loads(f.read())
   with open('iam_definition.json') as f:
       iamDef = json.loads(f.read())

def getDependantActions(actions):
   result = actions.copy()
   for base_action in actions:
       split_base = base_action.split(':')
       if len(split_base) != 2:
           continue
       base_service = split_base[0]
       base_method = split_base[1]

       for service in iamDef:
           if service['prefix'].lower() == base_service.lower():
               for priv in service['privileges']:
                   if priv['privileges'].lower() == base_method.lower():
                       for resource_type in priv['resource_type']:
                           for dependent_action in resource_type['dependent_actions']:
                               result.append(dependent_action)
   return result
        

def main():
    loadMaps()
    print(getDependantActions(['S3:PutObject']))
    log_file = open('csm.log', 'w')

    sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
    sock.bind((UDP_IP, UDP_PORT))

    while True:
        data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
        data_str = data.decode('utf-8')
        data_json = json.loads(data_str)
        log_file.write(data_str)
        #print("received message: %s" % data_json)

        if 'Type' in data_json:
            if data_json['Type'] == 'ApiCall':
                handle_api_call(data_json)
            else:
                print(data_str)

if __name__ == '__main__':
    main()
