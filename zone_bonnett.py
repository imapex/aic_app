import requests
import json
import sys

# Note for testing - you can remove the 33:33:33:33:33:33:33:33 zone member from the MDS switch using
#
#    config t
#    zone name IMzone1 vsan 10
#    no member pwwn 33:33:33:33:33:33:33:33
#    zoneset activate name IMzoneset vsan 10

# Credentials for switch - need to encrypt these
username = "danwms"
password = "AICteam"

# The update_zone() function below, adds tthe NewPwwn to the zone where we found the OldPwwn.

def update_zone(ipaddress, zname, vID, NPwwn, zset):
    sys.stdout.write('DEBUG: update_zone(): Executing "update_zone" function.\n')

    header = {'content-type': 'application/json-rpc'}
    url = "http://" + ipaddress + ":8080/ins"

    payload = [
        {"jsonrpc": "2.0", "method": "cli", "params": {"cmd": "conf t", "version": 1}, "id": 1},
        {"jsonrpc": "2.0", "method": "cli", "params": {"cmd": "zone name " + zname + " vsan " + vID, "version": 1}, "id": 2},
        {"jsonrpc": "2.0", "method": "cli", "params": {"cmd": "member pwwn " + NPwwn, "version": 1}, "id": 3},
        {"jsonrpc": "2.0", "method": "cli", "params": {"cmd": "zoneset activate name " + zset + " vsan " + vID, "version": 1}, "id": 4}
    ]

    response = requests.post(url, data=json.dumps(payload), headers=header, auth=(username, password)).json()
    print "DEBUG: update_zone(): zone",zname,"added member",NPwwn,"with message:",json.dumps(response[3]['result']['msg'], indent=4)
    print 'DEBUG: update_zone(): NX-APIs Response 2:'
    print (json.dumps(response[2]['result']['msg'], indent=4))
    print 'DEBUG: update_zone(): NX-APIs Response 3:'
    print (json.dumps(response[3]['result']['msg'], indent=4))

# configure_zone() takes the switch ip address, OldPwwn, Old Device Alias (future),
# and the New Pwwn.
#
# Routine first searches existing the zoneset for instances of the Old Pwwn
# and then adds the NewPwwn to those zones and activates the new updated zoneset.
# As time permits, Device Alias capability will also be added

def configure_zone(ipaddress, OldPwwn, OldDevAlias, NewPwwn):
    # Write DEBUG output to stdout.
    sys.stdout.write('DEBUG: configure_zone(): Executing "configure_zone" function.\n')
    sys.stdout.write('DEBUG: configure_zone(): IP address is: '+ipaddress+'\n')
    sys.stdout.write('DEBUG: configure_zone(): OldPwwn is: '+OldPwwn+'\n')
    sys.stdout.write('DEBUG: configure_zone(): OldDevAlias is: '+OldDevAlias+'\n')
    sys.stdout.write('DEBUG: configure_zone(): NewPwwn is: '+NewPwwn+'\n')
    
    header = {'content-type': 'application/json-rpc'}
    url = "http://" + ipaddress + ":8080/ins"

    # Get current zoneset info from switch.
    payload=[
      {"jsonrpc": "2.0","method": "cli","params": {"cmd": "show zoneset active","version": 1},"id": 1},
    ]

    response = requests.post(url,data=json.dumps(payload), headers=header,auth=(username,password)).json()
    zone_table = response['result']['body']['TABLE_zoneset']['ROW_zoneset']
    # Print DEBUG output.
    print 'DEBUG: configure_zone(): Output of "show zoneset active" command:'
    print json.dumps(response, sort_keys=True, indent=4, separators=(',', ': '))
    print 'DEBUG: configure_zone(): Output of "zone_table" variable:'
    print json.dumps(zone_table, sort_keys=True, indent=4, separators=(',', ': '))

    # check current zoneset for the old pwwn. If found, add the new pwwn to all zones that contain the old one
    # and activate the zoneset
    #
    # start by parsing the zoneset table
    for zoneset_vsan in zone_table:
        for zones in zoneset_vsan['TABLE_zone']['ROW_zone']:#
         # Parsing inconsistant json structure. If single zone in zoneset, 
         # ROW_zone is type dict rather than list. 
         # Testing type and proceeding accordingly.
            if isinstance(zoneset_vsan['TABLE_zone']['ROW_zone'],dict):
                # single zone in zoneset, type dict rather than list so assign directly to avoid error
                zones = zoneset_vsan['TABLE_zone']['ROW_zone']
                print 'DEBUG: configure_zone(): ROW_zone: appears to be a "dict":'
                print json.dumps(zones, sort_keys=True, indent=4, separators=(',', ': '))
                # more than one zone, cycle through them
            for zone_member in zones['TABLE_zone_member']['ROW_zone_member']:
                print 'DEBUG: configure_zone(): zone_member:'
                print json.dumps(zone_member, sort_keys=True, indent=4, separators=(',', ': '))
                try:
                    if zone_member.get('wwn') is not None and zone_member.get('wwn') == OldPwwn:
                        print 'DEBUG: configure_zone(): We have a match! Setting variables needed for the NX-API call to the MDS.'
                        pwwn = zone_member.get('wwn')
                        zonename = zones['zone_name']
                        vsanID = zones['zone_vsan_id']
                        zoneset = zoneset_vsan['zoneset_name']
                        print 'DEBUG: configure_zone(): Calling and passing variables to update_zone().'
                        # Call update_zone to add new pwwn to zone and activate
                        update_zone(ipaddress, zonename, vsanID, NewPwwn, zoneset)
                except:
                    print ('top loop debug')

def zone():

    # print "enter ip address"
    # ip=raw_input()
    ip = "172.22.163.35:8080"

    OPwwn = u'11:11:11:11:11:11:11:11'
    ODevAlias = 'OldDeviceAlias'
    NPwwn = '33:33:33:33:33:33:33:33'

    configure_zone(sw_url, header, OPwwn, ODevAlias, NPwwn)
    return


# zone()