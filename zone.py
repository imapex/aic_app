"""
 NX-API-BOT 
"""
import requests
import json

"""
Modify these please
"""
url='http://172.22.163.35:8080/ins'
switchuser='danwms'
switchpassword='AICteam'

# Pwwns will be passed in
OldPwwn = '11:11:11:11:11:11:11:11'
NewPwwn = '33:33:33:33:33:33:33:33'
# the following will be derived from show zoneset active once I figure out how to parse the return string
zone = 'IMzone1'
zoneset = 'IMzoneset'
vsan = 10

debug=0

myheaders={'content-type':'application/json-rpc'}
payload=[
  {
    "jsonrpc": "2.0",
    "method": "cli",
    "params": {
      "cmd": "show zoneset active",
      "version": 1.2
    },
    "id": 1
  }
]
response = requests.post(url,data=json.dumps(payload), headers=myheaders,auth=(switchuser,switchpassword)).json()

#
# DW: add logic to check if OldPwwn is in exising active zoneset, extract Zoneset name, Zone name and VSAN number
# DW: also determine if enhanced zoning is being used - if so, a commit is required before activating zoneset
#
# now add new member to existing zoneset
#

myheaders={'content-type':'application/json-rpc'}
payload=[
  {
    "jsonrpc": "2.0",
    "method": "cli",
    "params": {
      "cmd": "zone name IMzone1 vsan 10",
      "version": 1.2
    },
    "id": 1
  },
  {
    "jsonrpc": "2.0",
    "method": "cli",
    "params": {
      "cmd": "member pwwn 33:33:33:33:33:33:33:33",
      "version": 1.2
    },
    "id": 2
  },
]
response = requests.post(url,data=json.dumps(payload), headers=myheaders,auth=(switchuser,switchpassword)).json()

#
# if enhanced zoning, commit changes
#
myheaders={'content-type':'application/json-rpc'}
payload=[
  {
    "jsonrpc": "2.0",
    "method": "cli",
    "params": {
      "cmd": "zone commit vsan 10",
      "version": 1.2
    },
    "id": 1
  }
]
response = requests.post(url,data=json.dumps(payload), headers=myheaders,auth=(switchuser,switchpassword)).json()

#
# and activate zoneset
#
myheaders={'content-type':'application/json-rpc'}
payload=[
  {
    "jsonrpc": "2.0",
    "method": "cli",
    "params": {
      "cmd": "zoneset activate name IMzoneset vsan 10",
      "version": 1.2
    },
    "id": 1
  }
]
response = requests.post(url,data=json.dumps(payload), headers=myheaders,auth=(switchuser,switchpassword)).json()

#print (json.dumps(response, indent=4))
