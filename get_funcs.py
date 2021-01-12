from requests import request

# GET URL for stats using NHL API. {0} must be replaced with a valid game ID.
stats_path = 'https://statsapi.web.nhl.com/api/v1/game/{0}/feed/live'

# GET URL for schedules using NHL API. {0} must be replaced with a valid team ID.
# {1}, {2} must be replaced with a start date(1)/end date(2) formatted 'YYYY-MM-DD'.
schedule_path = 'https://statsapi.web.nhl.com/api/v1/schedule?teamId={0}&startDate={1}&endDate={2}'

# GET URL for rosters using NHP API. {0} must be replaced with a valid team ID.
roster_path = 'https://statsapi.web.nhl.com/api/v1/teams/{0}?expand=team.roster'


def get_conferences() -> {}:
    """ Returns a dict with all active NHL Conference ID's, and Names """
    conferences = {}
    conf_json = request(
        url='https://statsapi.web.nhl.com/api/v1/conferences',
        method='get'
    ).json()
    for conf in conf_json['conferences']:
        conferences[conf['id']] = conf['name']
    return conferences


def get_divisions() -> {}:
    """ Returns a dict with all active NHL Division ID's, Names, and Conference """
    divisions = {}
    div_json = request(
        url='https://statsapi.web.nhl.com/api/v1/divisions',
        method='get'
    ).json()
    for div in div_json['divisions']:
        divisions[div['id']] = {
            'division_key': div['id'],
            'name': div['name'],
            # 'conference': div['conference']['id']  (not being used this year?)
        }
    return divisions


def get_team_ids() -> [int]:
    team_ids = []
    teams_json = request(
        url='https://statsapi.web.nhl.com/api/v1/teams',
        method='get'
    ).json()
    for team in teams_json['teams']:
        team_ids.append(team['id'])
    return team_ids


def get_teams() -> {}:
    """ Returns a dict with all active NHL Team ID's, Names, Abbreviation, and Division """
    teams = {}
    teams_json = request(
        url='https://statsapi.web.nhl.com/api/v1/teams',
        method='get'
    ).json()
    for team in teams_json['teams']:
        teams[team['id']] = {
            'id': team['id'],
            'name': team['name'],
            'abbreviation': team['abbreviation'],
            'division': team['division']['id']
        }
    return teams


def get_game_ids(team_ids: [int], start_date: str, end_date: str) -> [int]:
    game_ids = []
    for team in team_ids:  # Getting each teams list of games from start_date to end_date
        schedule = request(
            url=schedule_path.format(team, start_date, end_date),
            method='get'
        ).json()
        for game in schedule['dates']:
            game_id = str(game['games'][0]['gamePk'])
            if game_id not in game_ids:  # Adding unique game_ids only
                game_ids.append(game_id)
    return game_ids


def get_games(team_ids: [int], start_date: str, end_date: str) -> {}:
    """ Returns a dict with all game info for all teams in team_ids between start_date and end_date including
     Home Team, Away Team, Home Team Score, Away Team Score, and Puck Drop"""
    games = {}
    for team in team_ids:  # Getting each teams list of games from start_date to end_date
        schedule = request(
            url=schedule_path.format(team, start_date, end_date),
            method='get'
        ).json()
        for game in schedule['dates']:
            game_id = str(game['games'][0]['gamePk'])
            if game_id not in games:  # Adding unique games only
                games[game_id] = {
                    'game_id': game_id,
                    'home_team': game['games'][0]['teams']['home']['team']['id'],
                    'away_team': game['games'][0]['teams']['away']['team']['id'],
                    'home_team_score': game['games'][0]['teams']['home']['score'],
                    'away_team_score': game['games'][0]['teams']['away']['score'],
                    'puck_drop': game['games'][0]['gameDate']
                }
    return games


def get_players(team_ids: [int]) -> {}:
    """ Returns a dict of all Players for teams specified with team_ids """
    players = {}
    for team in team_ids:
        roster_json = request(
            url=roster_path.format(team),
            method='get'
        ).json()

        for person in roster_json['teams'][0]['roster']['roster']:
            # Some players don't have jersey numbers, validate and make None if needed
            try:
                jersey_number = person['jerseyNumber']
            except KeyError:
                jersey_number = None

            players[person['person']['id']] = {
                'player_id': person['person']['id'],
                'first_name': person['person']['fullName'].split(' ')[0],
                'last_name': person['person']['fullName'].split(' ')[1],
                'number': jersey_number,
                'team': team
            }
    return players


def get_events(game_ids: [int]) -> {}:
    """ Returns a dict of all events for all games specified with game_ids """
    events = {}
    for game in game_ids:
        game_json = request(
            url=stats_path.format(game),
            method='get'
        ).json()

        all_events = game_json['liveData']['plays']['allPlays']
        for event in all_events:

            # Getting all needed data assigned, checking for presence / absence of fields
            event_id = event['result']['eventCode']
            description = event['result']['description']
            event_type = event['result']['event']
            # Not every event has a secondary type, need to check to see if it exists
            try:
                secondary_type = event['result']['secondaryType']
            except KeyError:  # The event only features a primary event type.
                secondary_type = None
            period = event['about']['period']
            time_remaining = event['about']['periodTimeRemaining']

            # 0-4 players may be involved in an event, need to check to see how many exist
            try:  # Not every event features a player
                player_1 = event['players'][0]['player']['id']
                player_1_type = event['players'][0]['playerType']
                try:  # Not every event features two or more players
                    player_2 = event['players'][1]['player']['id']
                    player_2_type = event['players'][1]['playerType']
                    try:  # Not every event features three or more players
                        player_3 = event['players'][2]['player']['id']
                        player_3_type = event['players'][2]['playerType']
                        try:  # Not every event features four players
                            player_4 = event['players'][3]['player']['id']
                            player_4_type = event['players'][3]['playerType']
                        except IndexError:  # Only 3 players involved
                            player_4 = None
                            player_4_type = None
                    except IndexError:  # Only 2 players involved
                        player_4 = None
                        player_4_type = None
                        player_3 = None
                        player_3_type = None
                except IndexError:  # Only 1 player involved
                    player_4 = None
                    player_4_type = None
                    player_3 = None
                    player_3_type = None
                    player_2 = None
                    player_2_type = None
            except KeyError:  # No players involved
                player_4 = None
                player_4_type = None
                player_3 = None
                player_3_type = None
                player_2 = None
                player_2_type = None
                player_1 = None
                player_1_type = None

            # Adding record to events dict
            events[(game, event_id)] = {
                'game': game,
                'event_id': event_id,
                'description': description,
                'primary_type': event_type,
                'secondary_type': secondary_type,
                'player_1': player_1,
                'player_1_type': player_1_type,
                'player_2': player_2,
                'player_2_type': player_2_type,
                'player_3': player_3,
                'player_3_type': player_3_type,
                'player_4': player_4,
                'player_4_type': player_4_type,
                'period': period,
                'time_remaining': time_remaining
            }

    return events
