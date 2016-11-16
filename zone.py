#
# configure_zone() takes the switch ip address, OldPwwn, searches existing zoneset for instances of
# that Pwwn and adds the NewPwwn to those zones and activates the new updated zoenset.
# As time permits, Device Alias capability will also be added
#

def configure_zone(ipaddr, OldPwwn, OldDevAlias, NewPwwn):

    #
    # credentials for switch - need to encrypt these
    #
    myheaders = {'content-type': 'application/json-rpc'}
    url = "http://" + ipaddr + "/ins"
    username = "danwms"
    password = "AICteam"

    # get current zoneset info from switch
    #
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
            if isinstance(zones,dict):
                try:
                    for zone_member in zones['TABLE_zone_member']['ROW_zone_member']:
                        try:
                            if zone_member.get('wwn') is not None and zone_member.get('wwn') is OldPwwn:
                                pwwn = zone_member.get('wwn')
                                zonename = zones['zone_name']
                                vsanID = zones['zone_vsan_id']
                                zoneset = zoneset_vsan['zoneset_name']
    # DW- should make a call here to add pwwn to zone here to account for case where pwwn exists in multiple zones
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
    # DW- should make a call here to add pwwn to zone here to account for case where pwwn exists in multiple zones
                except:
                    print "debug: failed zones assignmend, bottom loop"


    # Here we add the NewPwwn to the zone where we found the OldPwwn
    #
    # DW- make this subroutine called when match is found
    payload=[
     {"jsonrpc": "2.0","method": "cli","params": {"cmd": "conf t","version": 1},"id": 1},
     {"jsonrpc": "2.0","method": "cli","params": {"cmd": "zone name "+zonename+" vsan "+vsanID,"version": 1},"id": 2},
     {"jsonrpc": "2.0","method": "cli","params": {"cmd": "member pwwn "+NewPwwn,"version": 1},"id": 3},
     {"jsonrpc": "2.0","method": "cli","params": {"cmd": "zoneset activate name "+zoneset+" vsan "+vsanID,"version": 1},"id": 4}
    ]
    response = requests.post(url,data=json.dumps(payload), headers=myheaders,auth=(username,password)).json()
    print (json.dumps(response[3]['result']['msg'], indent=4))


def main():
    # print "enter ip address"
    # ip=raw_input()
    ip = "172.22.163.35:8080"

    OPwwn = u'11:11:11:11:11:11:11:11'
    ODevAlias = 'OldDeviceAlias'
    NPwwn = '33:33:33:33:33:33:33:33'

    configure_zone(ip, OPwwn, ODevAlias, NPwwn)



main()