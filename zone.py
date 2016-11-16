import requests
import json

#print "enter ip address"
#ip=raw_input()
ip="172.22.163.35:8080"
OldPwwn = u'11:11:11:11:11:11:11:11'
OldDevAlias = 'OldDeviceAlias'
NewPwwn = '33:33:33:33:33:33:33:33'

#print "enter vsan to be configured"
#vlanId=raw_input()
#vsanId=raw_input()

myheaders = {'content-type': 'application/json-rpc'}
url = "http://"+ip+"/ins"
username = "danwms"
password = "AICteam"


payload=[
  {"jsonrpc": "2.0","method": "cli","params": {"cmd": "show zoneset active","version": 1},"id": 1},
]
response = requests.post(url,data=json.dumps(payload), headers=myheaders,auth=(username,password)).json()

vsan_table = response['result']['body']['TABLE_zoneset']['ROW_zoneset']
v1=vsan_table[0]

rezone={}
for zoneset_vsan in vsan_table:
    for zones in zoneset_vsan['TABLE_zone']['ROW_zone']:
        if isinstance(zones,dict):
            try:
                for zone_member in zones['TABLE_zone_member']['ROW_zone_member']:
                    try:
                        if zone_member.get('wwn') is not None and zone_member.get('wwn') is OldPwwn:
                            pwwn = zone_member.get('wwn')
                            zonename = zones['zone_name']
                            vsanID = zones['zone_vsan_id']
                            zoneset = zoneset_vsan['zoneset_name']
                    except:
                        print ('top loop debug')
            except:
                print ('debug: do not need this print')
        else:
            try:
                zones = zoneset_vsan['TABLE_zone']['ROW_zone']
                for zone_member in zones['TABLE_zone_member']['ROW_zone_member']:
                    if zone_member.get('wwn') is not None and zone_member.get('wwn') == OldPwwn:
                        pwwn = zone_member.get('wwn')
                        zonename = zones['zone_name']
                        vsanID = zones['zone_vsan_id']
                        zoneset = zoneset_vsan['zoneset_name']
            except:
                print "debug: failed zones assignmend, bottom loop"


# this creates vsan 5
payload=[
 {"jsonrpc": "2.0","method": "cli","params": {"cmd": "conf t","version": 1},"id": 1},
 {"jsonrpc": "2.0","method": "cli","params": {"cmd": "zone name "+zonename+" vsan "+vsanID,"version": 1},"id": 2},
 {"jsonrpc": "2.0","method": "cli","params": {"cmd": "member pwwn "+NewPwwn,"version": 1},"id": 3},
 {"jsonrpc": "2.0","method": "cli","params": {"cmd": "zoneset activate name "+zoneset+" vsan "+vsanID,"version": 1},"id": 4}
]
response = requests.post(url,data=json.dumps(payload), headers=myheaders,auth=(username,password)).json()
print (json.dumps(response[3]['result']['msg'], indent=4))
