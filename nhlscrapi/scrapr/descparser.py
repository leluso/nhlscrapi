import re
from nhlscrapi.scrapr.teamnameparser import team_abbr_parser

# default parser does nothing
def default_desc_parser(event):
    pass

#############################
##
## helper funcs
##
#############################
# get int distance from 'num ft.'
def get_ft(s, def_dist = -1):
    sd = s.split(" ")[0]

    return int(sd) if sd.isdigit() else def_dist


# def team_num_name(s):
#     tnn = s.split(" ")
#     tnn[1] = tnn[1].replace('#','')
#     tnn[1] = int(tnn[1]) if tnn[1].isdigit() else -1

#     return {
#         "team": team_abbr_parser(tnn[0]),
#         "num": tnn[1],
#         "name": ' '.join(tnn[2:])
#     }
import re
__num_name_re = re.compile('([0-9]*)(.*)')

def team_num_name(s):
    # error report 600 and error report 672
    if '#' in s:
        tnn = s.split("#")
        team = team_abbr_parser(tnn[0].strip())
        m = __num_name_re.search(tnn[1])
        if m:
            name = m.group(2).strip()
            num = int(m.group(1)) if len(m.group(1)) > 0 else -1
        else:
            num = -1
            name = ''

    else:
        match_regex = r"(?P<team_abbr>[A-Z\.]{2,3})\s*(?P<player_num>[0-9]{1,2})\s*(?P<player_name>.+)"
        match = re.match(match_regex, s)
        team = match.group('team_abbr')
        num = int(match.group('player_num'))
        name = match.group('player_name')

    d = {
        "team": team,
        "num": num,
        "name": name
    }
    return d


def split_and_strip(s, by):
    return [si.strip() for si in s.split(by)]


def rem_penalty_shot_desc(s):
    return [ si for si in s if 'penalty' not in si.lower() ]




#############################
##
## parse a shot - '08 format
##
#############################
# NYR ONGOAL - #6 STRALMAN, Slap, Off. Zone, 65 ft.
# NYR ONGOAL - #62 HAGELIN, Penalty Shot, Backhand, Off. Zone, 10 ft.
# shot type might have - in it (wrap-around)
def parse_shot_desc_08(event):

    # split to get s[0] team - shooter, s[1] shot type, s[2] zone, s[3] distance
    # s[1] could read Penalty Shot
    s = split_and_strip(event.desc, ",")

    event.is_penalty_shot = 'penalty' in event.desc.lower()
    s = rem_penalty_shot_desc(s)

    # split to get team
    st = split_and_strip(s[0], " - ")
    st[0] = st[0].split(" ")[0].strip().replace('.','')

    # s[0] in form (#)num name; split by space to get num
    event.shooter = team_num_name(" ".join(st))

    # s[1] ' shottype '
    event.shot_type = s[1].strip() if len(s) > 1 else ""

    # s[2] has zone ' Off. Zone' or ' Def. Zone'
    event.zone = s[2].strip() if len(s) > 2 else ""

    # s[3] distance 'num ft.'
    event.dist = get_ft(s[3]) if len(s) > 3 else -1

    event.shooter['playerType'] = 'shooter'
    event.participants = (event.shooter,)


#############################
##
## parse a goal - '08 format
##
#############################
# NYR #13 CARCILLO(4), Wrist, Off. Zone, 11 ft. Assists: #15 DORSETT(4); #22 BOYLE(12)
# NYR #21 STEPAN(10), Penalty Shot, Wrist, Off. Zone, 10 ft.
# MTL #25 DE LA ROSE(1), Deflected, Off. Zone, 13 ft. Assists: #8 PRUST(10); #76 SUBBAN(35)

team_for_re = re.compile(r"^(?P<team_for>[A-Z\.]{2,3})")
shooter_re = re.compile(r"^(?P<team_for>[A-Z\.]{2,3})\s*#(?P<shooter_number>[0-9]{1,2})\s*(?P<shooter_name>[A-Z \.\-\']+)\(?(?P<season_goals>[0-9]*)\)")
a1_re = re.compile(r".*Assists?:\s*#(?P<a1_num>[0-9]{1,2})\s*(?P<a1_name>[A-Z \.\-\']+)\((?P<a1_a_count>\d*)\)")
a2_re = re.compile(r".*;\s*#(?P<a2_num>[0-9]{1,2})\s*(?P<a2_name>[A-Z \.\-\']+)\((?P<a2_a_count>[0-9]*)\)")
zone_re = re.compile(r".*(?P<zone>[A-z]{3})\.\s*Zone")
distance_re = re.compile(r".*(?P<distance>[0-9]+)\s* ft")
shot_type_re = re.compile(r".*, (?P<shot_type>[A-z\-]+),")

def parse_goal_desc_08(event):
    event.is_penalty_shot = 'penalty' in event.desc.lower()
    event.participants = []

    match = team_for_re.match(event.desc)
    if match:
        team_for = team_abbr_parser(match.group('team_for'))

        match = shooter_re.match(event.desc)
        if match:
            shooter_number = int(match.group('shooter_number'))
            shooter_name = match.group('shooter_name')

            event.shooter = {
                'name': shooter_name,
                'num': shooter_number,
                'team': team_for,
                'playerType': 'scorer',
            }
            event.participants.append(event.shooter)
            event.scorer = event.shooter

        event.assists = []

        match = a1_re.match(event.desc)
        if match:
            a1_number = int(match.group('a1_num'))
            a1_name = match.group('a1_name')

            a1 = {
                'name': a1_name,
                'num': a1_number,
                'team': team_for,
                'playerType': 'assist'
            }
            event.participants.append(a1)
            event.assists.append(a1)

        match = a2_re.match(event.desc)
        if match:
            a2_number = int(match.group('a2_num'))
            a2_name = match.group('a2_name')

            a2 = {
                'name': a2_name,
                'num': a2_number,
                'team': team_for,
                'playerType': 'assist'
            }
            event.participants.append(a2)
            event.assists.append(a2)


    match = zone_re.match(event.desc)
    if match:
        event.zone = match.group('zone')

    match = distance_re.match(event.desc)
    if match:
        event.dist = int(match.group('distance'))

    match = shot_type_re.match(event.desc)
    if match:
        event.shot_type = match.group('shot_type')


def assist_from(a):
    pl = a.strip().split(" ")
    num_str = pl[0].replace('#','')

    r = []
    r.append(int(num_str) if num_str.isdigit() else -1)
    r.extend([p.strip() for p in pl[1].split("(") ])
    if len(r) == 3:
        r[2] = r[2].replace('(','').replace(')','')

    return r




#############################
##
## parse a miss - '08 format
##
#############################
# NYR #18 STAAL, Snap, Wide of Net, Off. Zone, 63 ft.
def parse_miss_08(event):

    event.is_penalty_shot = 'penalty' in event.desc

    s = split_and_strip(event.desc, ",")
    s = rem_penalty_shot_desc(s)

    event.shooter = team_num_name(s[0])
    # event.shot_type = s[1]
    # event.shot_miss_desc = s[2]
    # event.zone = s[3]
    # event.dist = get_ft(s[4])

    if s[1][-4:] == 'Zone': # error report 1090
        event.shot_type = ''
        event.shot_miss_desc = ''
        event.zone = s[1]
        event.dist = get_ft(s[2])
    elif s[2][-4:] == 'Zone': # error report 171
        event.shot_miss_desc = ''
        event.zone = s[2]
        event.dist = get_ft(s[3])
    elif s[3][-3:] == 'ft.': # error report 467
        event.shot_miss_desc = s[2]
        event.zone = ''
        event.dist = get_ft(s[3])
    else:
        event.shot_miss_desc = s[2]
        event.zone = s[3]
        event.dist = get_ft(s[4])

    event.shooter['playerType'] = 'shooter'
    event.participants = (event.shooter,)



#############################
##
## parse faceoff - '08 format
##
#############################
# VAN won Off. Zone - NYR #19 RICHARDS vs VAN #22 SEDIN
def parse_faceoff_08(event):
    s = split_and_strip(event.desc, " - ")

    w_loc = split_and_strip(s[0], "won")
    event.winner = w_loc[0]
    event.zone = w_loc[1]

    vs = s[1].split("vs")
    tnn = team_num_name(vs[0].strip())
    try:
        tnn2 = team_num_name(vs[1].strip())
        event.head_to_head = [ tnn, tnn2 ]

        if tnn.get('team') in event.winner:
            tnn['playerType'] = 'winner'
            tnn2['playerType'] = 'loser'

        else:
            tnn['playerType'] = 'winner'
            tnn2['playerType'] = 'loser'

        event.participants = (tnn, tnn2)

    except:
        print(vs)



#############################
##
## parse hit - '08 format
##
#############################
# VAN #3 BIEKSA HIT NYR #21 STEPAN, Def. Zone
def parse_hit_08(event):
    s = split_and_strip(event.desc, " HIT ")

    event.hit_by = team_num_name(s[0])
    event.team = event.hit_by['team']

    p_z = s[1].split(",")
    event.player_hit = team_num_name(p_z[0])

    event.hit_by['playerType'] = 'hitter'
    event.player_hit['playerType'] = 'hittee'

    event.participants = (event.hit_by, event.player_hit)

    event.zone = p_z[1].strip() if len(p_z) > 1 else ''




#############################
##
## parse blocked shot - '08 format
##
#############################
# VAN #14 BURROWS BLOCKED BY NYR #27 MCDONAGH, Snap, Def. Zone
def parse_block_08(event):
    s = split_and_strip(event.desc, "BLOCKED BY")
    event.shooter = team_num_name(s[0])

    s = split_and_strip(s[1], ",")
    event.blocked_by = team_num_name(s[0])

    if len(s) == 3:  # Normal number of items found (expected case)
        event.shot_type = s[1]
        event.zone = s[2]
    else:  # Something is missing - shot or zone
        if 'Zone' in s[1]:  # We have zone, not shot.
            event.shot_type = ''
            event.zone = s[1]
        else:  # Shot, not zone.
            event.shot_type = s[1]
            event.zone = ''

    event.shooter['playerType'] = 'shooter'
    event.blocked_by['playerType'] = 'blocker'
    event.participants = (event.shooter, event.blocked_by)




#############################
##
## parse takeaway - '08 format
##
#############################
# NYR TAKEAWAY - #27 MCDONAGH, Def. Zone
def parse_takeaway_08(event):
    s = split_and_strip(event.desc, " - ")

    s[0] = s[0].replace('?', ' ')
    event.team = team_abbr_parser(s[0].split(" ")[0].strip())

    s = split_and_strip(s[1], ",")
    tnn = team_num_name(str('team ' + s[0]))
    event.player_num = tnn["num"]
    event.player_name = tnn["name"]

    if len(s) > 1:
        event.zone = s[1]

    event.participants = (dict(
        name=event.player_name,
        num=event.player_num,
        team=event.team,
        playerType='playerID', # Butchering this for nhlscraper
    ),)



#############################
##
## parse giveaway - '08 format
## same form as takeaway
##
#############################
# NYR GIVEAWAY - #21 STEPAN, Def. Zone
def parse_giveaway_08(event):
    parse_takeaway_08(event)


# These are not being used but I want to remember them
penalty_with_drawn_re = r"(?P<team_against>[A-Z\.]{2,3})\s*#(?P<against_player_number>[0-9]{1,2})\s*(?P<against_player_name>[A-Z \.\-\']+)\W+(?P<offence>[A-z\s\.\-]+)(\((?P<penalty_class>\w+)\))?\((?P<penalty_length>\d+)\s*min\),?\s*((?P<zone>Def|Off|Neu)\.\s*Zone)?.*(Drawn By: (?P<drawn_team>[A-Z\.]{2,3})\s*#(?P<drawn_player_number>[0-9]{1,2})\s*(?P<drawn_player_name>[A-Z \.\-\']+).*).*"
penalty_without_drawn_re = r"(?P<team_against>[A-Z\.]{2,3})\s*#(?P<against_player_number>[0-9]{1,2})\s*(?P<against_player_name>[A-Z \.\-\']+)\W+(?P<offence>[A-z\s\.\-]+)(\((?P<penalty_class>\w+)\))?\((?P<penalty_length>\d+)\s*min\),?\s*((?P<zone>Def|Off|Neu)\.\s*Zone)?.*"
bench_penalty_re = r"(?P<team_against>[A-Z\.]{2,3})\s*TEAM\W+(?P<offence>[A-z\s\.\-\/]+)(\((\w+)\))?\((?P<penalty_length>\d+)\s*min\)\s*Served By: \#(?P<serving_player_number>[0-9]{1,2})\s*(?P<serving_player_name>[A-Z \.\-\']+),?\s*((?P<zone>Def|Off|Neu)\.\s*Zone)?.*"
served_and_drawn_re = r"(?P<team_against>[A-Z\.]{2,3})\s*#(?P<against_player_number>[0-9]{1,2})\s*(?P<against_player_name>[A-Z \.\-\']+)\W+(?P<offence>[A-z\s\.\-\']+)(\((?P<penalty_class>\w+)\))?\((?P<penalty_length>\d+)\s*min\)\s*Served By:\s*\#(?P<serving_player_number>[0-9]{1,2})\s*(?P<serving_player_name>[A-Z \.\-\']+),\s*((?P<zone>Def|Off|Neu)\.\s*Zone)?\s*(Drawn By:\s*(?P<drawn_team>[A-Z\.]{2,3})\s*#(?P<drawn_player_number>[0-9]{1,2})\s*(?P<drawn_player_name>[A-Z \.\-\']+).*).*"
served_and_drawn_bench_re = r"(?P<team_against>[A-Z\.]{2,3})\s*TEAM\W+(?P<offence>[A-z\s\.\-\/]+)(\((\w+)\))?\((?P<penalty_length>\d+)\s*min\)\s*Served By: \#(?P<serving_player_number>[0-9]{1,2})\s*(?P<serving_player_name>[A-Z \.\-\']+),?((?P<zone>Def|Off|Neu)\.\s*Zone)?\s*(Drawn By:\s*(?P<drawn_team>[A-Z\.]{2,3})\s*#(?P<drawn_player_number>[0-9]{1,2})\s*(?P<drawn_player_name>[A-Z \.\-\']+).*).*"
penalty_without_drawn_with_served_re = r"(?P<team_against>[A-Z\.]{2,3})\s*#(?P<against_player_number>[0-9]{1,2})\s*(?P<against_player_name>[A-Z \.\-\']+)\W+(?P<offence>[A-z\s\.\-]+)(\((?P<penalty_class>\w+)\))?\((?P<penalty_length>\d+)\s*min\),?\s*Served By: \#(?P<serving_player_number>[0-9]{1,2})\s*(?P<serving_player_name>[A-Z \.\-\']+),?\s*((?P<zone>Def|Off|Neu)\.\s*Zone)?.*"

against_team_re = re.compile(r"^(?P<team_against>[A-Z\.]{2,3})")
against_player_re = re.compile(r"^(?P<team_against>[A-Z\.]{2,3})\s*#(?P<against_player_number>[0-9]{1,2})\s*(?P<against_player_name>[A-Z \.\-\']+)")
penalty_info_re = re.compile(r".*(?P<offence>[A-Z][a-z\s\.\-\'\/]+)(\((?P<penalty_class>\w+)\))?\((?P<penalty_length>\d+)\s*min\)")
serving_player_re = re.compile(r".*Served By:\s*\#(?P<serving_player_number>[0-9]{1,2})\s*(?P<serving_player_name>[A-Z \.\-\']+)")
drawn_player_re = re.compile(r".*Drawn By:\s*(?P<drawn_team>[A-Z\.]{2,3})\s*#(?P<drawn_player_number>[0-9]{1,2})\s*(?P<drawn_player_name>[A-Z \.\-\']+)")
zone_re = re.compile(r".*((?P<zone>Def|Off|Neu)\.\s*Zone)")

def parse_penalty_08(event):
    desc = event.desc.replace('\\', '')

    match = against_team_re.match(desc)
    against_team_abbr = team_abbr_parser(match.group('team_against'))

    event.participants = []
    match = against_player_re.match(desc)
    if match:
        event.participants.append({
            'name': match.group('against_player_name'),
            'num': int(match.group('against_player_number')),
            'team': against_team_abbr,
            'playerType': 'penaltyOn',
        })

    match = serving_player_re.match(desc)
    if match:
        event.participants.append({
            'name': match.group('serving_player_name'),
            'num': int(match.group('serving_player_number')),
            'team': against_team_abbr,
            'playerType': 'servedBy',
        })

    match = drawn_player_re.match(desc)
    if match:
        event.participants.append({
            'name': match.group('drawn_player_name'),
            'num': int(match.group('drawn_player_number')),
            'team': team_abbr_parser(match.group('drawn_team')),
            'playerType': 'drewBy',
        })

    match = penalty_info_re.match(desc)
    if match:
        event.offence = match.group('offence').strip()
        event.length = int(match.group('penalty_length'))
    else:
        event.offence = 'Unknown'
        event.length = 2

    try:
        event.severity = (match.group('penalty_class') or 'min') + 'or'
    except:
        event.severity = 'minor'

    match = zone_re.match(desc)
    if match:
        event.zone = match.group('zone')



#############################
##
## parse shootout
##
#############################
def parse_shootout(event):
    s = split_and_strip(event.desc, ',')

    d_str = s[-1].split(' ')[0]
    event.dist = int(d_str) if d_str.isdigit() else 0

    event.shot_type = s[1]

    tnn = split_and_strip(s[0], ' ')
    if len(tnn) == 3:
        event.shooter = team_num_name(' '.join(tnn))
    elif len(tnn) == 5:
        event.shooter = team_num_name(' '.join([tnn[0], tnn[3], tnn[4]]))

    event.shooter['playerType'] = 'shooter'
    event.participants = (event.shooter,)
