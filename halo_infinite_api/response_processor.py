"""Contains logic for converting API responses to tuples of selected data for storage."""


import requests
import halo_infinite_api.error as err


def parse_match(match:dict):
    """Convert a dict of match data to a database-insertable tuple.

    Args:
        match (dict): Match data.

    Raises:
        err.ParsingError: Occurs if the provided data doesn't match the necessary schema.

    Returns:
        tuple: Selected match data for storage.
    """

    try:
        id = match['id']
        played_at = match['played_at']
        duration = match['duration']['seconds']
        playlist = match['details']['playlist']['name']
        game_type = match['details']['category']['name']
        map_name = match['details']['map']['name']
        return (id, played_at, duration, playlist, game_type, map_name)
    except KeyError:
        raise err.ParsingError('match', match)


def parse_match_list(resp:requests.Response):
    """Convert an API response into a list of database-insertable tuples.

    Args:
        resp (requests.Response): The API response to parse.

    Returns:
        list[tuple]: The list of selected match data.
    """

    data = resp.json()['data']
    return [parse_match(m) for m in data]

    
def parse_match_details(resp:requests.Response):
    """Convert an API response into team and player data.

    Args:
        resp (requests.Response): The API response to parse.

    Returns:
        tuple[list[tuple]]: A tuple of two lists. The first list contains tuples of match-team data. The second list contains tuples of match-player data.
    """

    match_details = resp.json()
    
    match_id = match_details['data']['id']
    teams = match_details['data']['teams']['details']
    players = match_details['data']['players']

    team_tuples = [(match_id,) + parse_team(t) for t in teams]
    player_tuples = [(match_id,) + parse_player(p) for p in players if p['type'] == 'player']

    return team_tuples, player_tuples


def parse_team(team:dict):
    """Convert a dict of team data from match details into a tuple of selected information.

    Args:
        team (dict): The dict containing the data to extract.

    Raises:
        err.ParsingError: Occurs if the provided data doesn't match the necessary schema.

    Returns:
        tuple: Selected team data.
    """

    try:
        id = team['team']['id']
        mmr = team['team']['skill']['mmr']
        rnk = team['rank']
        outcome = team['outcome']
        score = team['stats']['core']['score']
        points = team['stats']['core']['points']
        kda = team['stats']['core']['kda']
        dmg_dealt = team['stats']['core']['damage']['dealt']
        dmg_taken = team['stats']['core']['damage']['taken']
        shots_fired = team['stats']['core']['shots']['fired']
        shots_landed = team['stats']['core']['shots']['landed']
        return (id, mmr, rnk, outcome, score, points, kda, dmg_dealt, dmg_taken, shots_fired, shots_landed)
    except KeyError:
        raise err.ParsingError('team', team)


def parse_player(player:dict):
    """Convert a dict of player data from match details into a tuple of selected information.

    Args:
        player (dict): The dict containing the data to extract.

    Raises:
        err.ParsingError: Occurs if the provided data doesn't match the necessary schema.

    Returns:
        tuple: Selected player data.
    """

    try:
        team_id = player['team']['id']
        gamertag = player['gamertag']
        if player['progression'] is not None:
            pre_match_csr = player['progression']['csr']['pre_match']['value']
        else:
            pre_match_csr = None
        score = player['stats']['core']['score']
        points = player['stats']['core']['points']
        kda = player['stats']['core']['kda']
        dmg_dealt = player['stats']['core']['damage']['dealt']
        dmg_taken = player['stats']['core']['damage']['taken']
        shots_fired = player['stats']['core']['shots']['fired']
        shots_landed = player['stats']['core']['shots']['landed']
        joined_at = player['participation']['joined_at']
        left_at = player['participation']['left_at']
        return (team_id, gamertag, pre_match_csr, score, points, kda, dmg_dealt, dmg_taken, shots_fired, shots_landed, joined_at, left_at)
    except KeyError:
        raise err.ParsingError('player', player)

