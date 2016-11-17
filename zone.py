#
# take ip, Old Pwwn, New Pwwn as inputs to program. Given fixed values here for testing
# add device alias option if time permits
#
# note for testing - you can remove the 33:33:33:33:33:33:33:33 zone member from the MDS switch using
#          a tcl script on the MDS. From MDS cli run:   tclsh boothflash:tclzone
#       it does these commands:
#               config t
#               zone name IMzone1 vsan 10
#               no member pwwn 33:33:33:33:33:33:33:33
#               zoneset activate name IMzoneset vsan 10

import requests
import json

#
# global credentials for switch - need to encrypt these
#
username = "danwms"
password = "AICteam"

#
#   add zone member to zone and activate the zoneset
#

def update_zone(url, myheaders, zname, vID, NPwwn, zset):

    # Here we add the NewPwwn to the zone where we found the OldPwwn


    payload = [
        {"jsonrpc": "2.0", "method": "cli", "params": {"cmd": "conf t", "version": 1}, "id": 1},
        {"jsonrpc": "2.0", "method": "cli", "params": {"cmd": "zone name " + zname + " vsan " + vID, "version": 1},
         "id": 2},
        {"jsonrpc": "2.0", "method": "cli", "params": {"cmd": "member pwwn " + NPwwn, "version": 1}, "id": 3},
        {"jsonrpc": "2.0", "method": "cli",
         "params": {"cmd": "zoneset activate name " + zset + " vsan " + vID, "version": 1}, "id": 4}
    ]
    response = requests.post(url, data=json.dumps(payload), headers=myheaders, auth=(username, password)).json()
    print "zone",zname,"added member",NPwwn,"with message:",json.dumps(response[3]['result']['msg'], indent=4)

def configure_zone(ip, OldPwwn, OldDevAlias, NewPwwn):
    #
    # configure_zone() takes the switch ip address, OldPwwn, searches existing zoneset for instances of
    # that Pwwn and adds the NewPwwn to those zones and activates the new updated zoneset.
    #    DW - As time permits, Device Alias capability will also be added
    #    DW - also check for enhanced zoning and do commit before activate
    #    DW - clean up corner case of one zone in a zoneset.
    #
    #   NOTE FOR TESTING - you can remove the 33:33:33:33:33:33:33:33 zone member from the MDS switch using
    #       these commands:
    #               config t
    #               zone name IMzone1 vsan 10
    #               no member pwwn 33:33:33:33:33:33:33:33
    #               zoneset activate name IMzoneset vsan 10


    #
    # get current zoneset info from switch
    #
    myheaders = {'content-type': 'application/json-rpc'}
    url = "http://" + ip + "/ins"

    payload=[
      {"jsonrpc": "2.0","method": "cli","params": {"cmd": "show zoneset active","version": 1},"id": 1},
    ]
    response = requests.post(url,data=json.dumps(payload), headers=myheaders,auth=(username,password)).json()
    zone_table = response['result']['body']['TABLE_zoneset']['ROW_zoneset']

    #
    # check current zoneset for the old pwwn. If found, add the new pwwn to all zones that contain the old one and activate the zoneset
    #
    #
    # start by parsing the zoneset table
    #
    for zoneset_vsan in zone_table:
        for zones in zoneset_vsan['TABLE_zone']['ROW_zone']:
    #
    #	parsing inconsistant json structure. If single zone in zoneset, ROW_zone is type dict rather than list. testing type and proceeding accordingly
    #
            if isinstance(zoneset_vsan['TABLE_zone']['ROW_zone'],dict):
                # single zone in zoneset, type dict rather than list so assign directly to avoid error
                zones = zoneset_vsan['TABLE_zone']['ROW_zone']
                # more than one zone, cycle through them
            for zone_member in zones['TABLE_zone_member']['ROW_zone_member']:
                try:
                    if zone_member.get('wwn') is not None and zone_member.get('wwn') == OldPwwn:
                        pwwn = zone_member.get('wwn')
                        zonename = zones['zone_name']
                        vsanID = zones['zone_vsan_id']
                        zoneset = zoneset_vsan['zoneset_name']
                        # Call update_zone to add new pwwn to zone and activate
                        update_zone(url, myheaders, zonename, vsanID, NewPwwn, zoneset)
                except:
                    print ('top loop debug')



def main():

    # print "enter ip address"
    # ip=raw_input()
    ip = "172.22.163.35:8080"

    OPwwn = u'11:11:11:11:11:11:11:11'
    ODevAlias = 'OldDeviceAlias'
    NPwwn = '33:33:33:33:33:33:33:33'

    configure_zone(ip, OPwwn, ODevAlias, NPwwn)

main()