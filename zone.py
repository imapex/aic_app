import requests
import json
import sys
import os

# Note for testing - you can remove the 33:33:33:33:33:33:33:33 zone member from the MDS switch using
#
#    config t
#    zone name IMzone1 vsan 10
#    no member pwwn 33:33:33:33:33:33:33:33
#    zoneset activate name IMzoneset vsan 10

# Credentials for the MDS Switch
# Credentials are set as local Enviorment Variables.
#

username = os.getenv("AIC_USER")
password = os.getenv("AIC_PASSWORD")



# The update_zone() function below, adds tthe NewPwwn to the zone where we found the OldPwwn.
#   Two functions have been implemented:
#       1 = change zone to remove old HBA PWWN and add new HBA PWWN
#       2 = Change the PWWN associated with the device-alias. In this case no zoning changes are required, the change of device-alias is enough
#
#   DW - add checks for enhanced zoning and other things that may impact function of module

def update_zone(ipaddress, zname, vID, NPwwn, DevAlias, zset, WWNorDEVAlias):
    sys.stdout.write('DEBUG: update_zone(): Executing "update_zone" function.\n')

    header = {'content-type': 'application/json-rpc'}
    url = "http://" + ipaddress + ":8080/ins"

    if WWNorDEVAlias == 1:
        payload = [
            {"jsonrpc": "2.0", "method": "cli", "params": {"cmd": "conf t", "version": 1}, "id": 1},
            {"jsonrpc": "2.0", "method": "cli", "params": {"cmd": "zone name " + zname + " vsan " + vID, "version": 1},
             "id": 2},
            {"jsonrpc": "2.0", "method": "cli", "params": {"cmd": "member pwwn " + NPwwn, "version": 1}, "id": 3},
            {"jsonrpc": "2.0", "method": "cli",
             "params": {"cmd": "zoneset activate name " + zset + " vsan " + vID, "version": 1}, "id": 4}
        ]
    elif WWNorDEVAlias == 2:
        payload = [
            {"jsonrpc": "2.0", "method": "cli", "params": {"cmd": "conf t", "version": 1}, "id": 1},
            {"jsonrpc": "2.0", "method": "cli", "params": {"cmd": "device-alias database", "version": 1}, "id": 2},
            {"jsonrpc": "2.0", "method": "cli", "params": {"cmd": "no device-alias name " + DevAlias, "version": 1},
             "id": 3},
            {"jsonrpc": "2.0", "method": "cli",
             "params": {"cmd": "device-alias name " + DevAlias + " pwwn " + NPwwn, "version": 1}, "id": 4},
            {"jsonrpc": "2.0", "method": "cli", "params": {"cmd": "device-alias commit", "version": 1}, "id": 5}

        ]
    else:
        print ('update_zone called with invalid WWNofDEVAlias value')
        return False


    response = requests.post(url, data=json.dumps(payload), headers=header, auth=(username, password)).json()
    print "DEBUG: update_zone(): zone", zname, "added member", NPwwn, "with message:" 
    print json.dumps(response[2]['result']['msg'], indent=4)
    print json.dumps(response[3]['result']['msg'], indent=4)  

# configure_zone() takes the switch ip address, OldPwwn, Old Device Alias (future),
# and the New Pwwn.
#
# Routine first searches existing zoneset for instances of the Old Pwwn or DevAlias
# and then adds the NewPwwn to those zones or updates the DevAlias with the new Pwwn
# and then activates the new updated zoneset.
#

def configure_zone(ipaddress, OldPwwn, DevAlias, NewPwwn):
    # Write DEBUG output to stdout.
    sys.stdout.write('DEBUG: configure_zone(): Executing "configure_zone" function.\n')
    #    sys.stdout.write('DEBUG: configure_zone(): IP address is: '+ipaddress+'\n')
    #    sys.stdout.write('DEBUG: configure_zone(): OldPwwn is: '+OldPwwn+'\n')
    #    sys.stdout.write('DEBUG: configure_zone(): DevAlias is: '+DevAlias+'\n')
    #    sys.stdout.write('DEBUG: configure_zone(): NewPwwn is: '+NewPwwn+'\n')

    header = {'content-type': 'application/json-rpc'}
    url = "http://" + ipaddress + ":8080/ins"

    # Get current zoneset info from switch.
    payload = [
        {"jsonrpc": "2.0", "method": "cli", "params": {"cmd": "show zoneset active", "version": 1}, "id": 1},
    ]

    response = requests.post(url, data=json.dumps(payload), headers=header, auth=(username, password)).json()
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
    print 'DEBUG: configure_zone(): Parsing the zoneset table.'
    print 'DEBUG: configure_zone(): For each zone in the switch, loop through each zone member searching for an Old WWN match.'
    for zoneset_vsan in zone_table:
        print 'DEBUG: configure_zone(): Starting zone set search.'
        for zones in zoneset_vsan['TABLE_zone']['ROW_zone']:  #
            print 'DEBUG: configure_zone(): Starting zone search.'
            # Parsing inconsistant json structure. If single zone in zoneset,
            # ROW_zone is type dict rather than list.
            # Testing type and proceeding accordingly.
            if isinstance(zoneset_vsan['TABLE_zone']['ROW_zone'], dict):
                # single zone in zoneset, type dict rather than list so assign directly to avoid error
                zones = zoneset_vsan['TABLE_zone']['ROW_zone']
                print 'DEBUG: configure_zone(): ROW_zone: appears to be a "dict":'
                print json.dumps(zones, sort_keys=True, indent=4, separators=(',', ': '))
                # more than one zone, cycle through them
            for zone_member in zones['TABLE_zone_member']['ROW_zone_member']:
                print 'DEBUG: configure_zone(): Searching zone member:'
                print json.dumps(zone_member, sort_keys=True, indent=4, separators=(',', ': '))
                try:
                    # Check for target Pwwn in this zone. If zone_member.get('wwn') is not None and zone_member.get('wwn') == OldPwwn:
                    if zone_member.get('wwn') is not None and zone_member.get('wwn') == OldPwwn:
                        print 'DEBUG: configure_zone(): PWWN, We have a match! Setting variables needed for the NX-API call to the MDS.'
                        pwwn = zone_member.get('wwn')
                        zonename = zones['zone_name']
                        vsanID = zones['zone_vsan_id']
                        zoneset = zoneset_vsan['zoneset_name']
                        WWNorDEVAlias = 1  # 1 indicates zone by PWWN
                        print 'DEBUG: configure_zone(): Calling and passing variables to update_zone().'
                        # Call update_zone to add new pwwn to zone and activate
                        update_zone(ipaddress, zonename, vsanID, NewPwwn, DevAlias, zoneset, WWNorDEVAlias)

                        # Check for target device alias in this zone
                    elif zone_member.get('dev_alias') is not None and zone_member.get('dev_alias') == DevAlias:
                        print 'DEBUG: configure_zone(): DevAlias, We have a match! Setting variables needed for the NX-API call to the MDS.'
                        pwwn = zone_member.get('wwn')
                        zonename = zones['zone_name']
                        vsanID = zones['zone_vsan_id']
                        zoneset = zoneset_vsan['zoneset_name']
                        WWNorDEVAlias = 2  # 2 indicates zone by Device Alias
                        print 'DEBUG: configure_zone(): Calling and passing variables to update_zone().'
                        # Call update_zone to add new pwwn to zone and activate
                        update_zone(ipaddress, zonename, vsanID, NewPwwn, DevAlias, zoneset, WWNorDEVAlias)
                except:
                    print ('top loop debug')
            print 'DEBUG: configure_zone(): Searched all zone members in this zone. If more zones exisit, we will search those next.'
        print 'DEBUG: configure_zone(): Searched all zones in this zone set. If more zone sets exist, we will search those next.'
    print 'DEBUG: configure_zone(): Searched all zones sets.'


def zone():
    # print "enter ip address"
    # ip=raw_input()
    ip = "172.22.163.35"

#   Test data until monitoring &/or GUI input is working.
    OPwwn = u'11:11:11:11:11:11:11:11'
    DevAlias = 'AICda'
    NPwwn = '33:33:33:33:33:33:33:33'

    configure_zone(ip, OPwwn, DevAlias, NPwwn)
    return


#zone()