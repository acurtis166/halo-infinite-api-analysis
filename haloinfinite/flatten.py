import json
from dateutil.parser import isoparse

from haloinfinite import util


def flatten_matches(jdata:dict) -> list[dict]:

    return [_flatten_match(m) for m in jdata['Results']]


def _flatten_match(match:dict) -> dict:

    try:
        match_info = match['MatchInfo']
        plist = match_info.get('Playlist') or {} # can be null

        m = {}
        m['guid'] = match['MatchId']
        m['started_at'] = isoparse(match_info['StartTime'])
        m['completed_at'] = isoparse(match_info['EndTime'])
        m['duration'] = util.parse_iso_duration(match_info['Duration'])
        m['map_asset_id'] = match_info['MapVariant']['AssetId']
        m['map_version_id'] = match_info['MapVariant']['VersionId']
        m['map_level_id'] = match_info['LevelId']
        m['game_variant_asset_id'] = match_info['UgcGameVariant']['AssetId']
        m['game_variant_version_id'] = match_info['UgcGameVariant']['VersionId']
        m['game_variant_category'] = match_info['GameVariantCategory']
        m['playlist_asset_id'] = plist.get('AssetId')
        m['playlist_version_id'] = plist.get('VersionId')
        m['lifecycle_mode_id'] = match_info['LifecycleMode']
        m['experience_id'] = match_info['PlaylistExperience']
        m['season_id'] = match_info['SeasonId']
        m['playable_duration'] = util.parse_iso_duration(match_info['PlayableDuration'])
        return m
    except (TypeError, KeyError) as e:
        jdata = {'ERROR': str(e), 'match': match}
        with open('match_processing_error.json', 'w') as f:
            json.dump(jdata, f)
        raise


def flatten_game_variant(jdata:dict) -> dict:

    name_components = jdata['PublicName'].split(':')

    gv = {}
    gv['asset_id'] = jdata['AssetId']
    gv['version_id'] = jdata['VersionId']
    gv['context'] = name_components[0]
    gv['name'] = name_components[1]
    return gv


def flatten_map(jdata:dict) -> dict:

    m = {}
    m['asset_id'] = jdata['AssetId']
    m['version_id'] = jdata['VersionId']
    m['name'] = jdata['PublicName']
    return m


def flatten_playlist(jdata:dict) -> dict:

    # interesting data about map-mode weights for the playlist as well
    inputs = jdata['CustomData']['AllowedDeviceInputs']

    p = {}
    p['asset_id'] = jdata['AssetId']
    p['version_id'] = jdata['VersionId']
    p['name'] = jdata['PublicName']
    p['is_ranked'] = 'Ranked' in p['name'] # hopefully this is sufficient to catch all ranked playlists
    # AllowedDeviceInputs can be [], [0], [1], [2], or [1, 2], with 1 being controller, 2 being mouse and keyboard
    # if a 1 or 2 are the only element of the list, the playlist is input-restricted, in other cases both should be true
    p['is_controller'] = not inputs or 0 in inputs or 1 in inputs # no inputs, value of 0, value of 1
    p['is_mnk'] = not inputs or 0 in inputs or 2 in inputs # no inputs, value of 0, value of 2
    p['max_fireteam_size'] = jdata['CustomData']['MaxFireteamSize']
    return p


def flatten_profiles(jdata:dict) -> list[dict]:

    return [_flatten_profile(p) for p in jdata['profileUsers']]


def _flatten_profile(prof:dict) -> dict:

    p = {}
    p['id'] = prof['id']
    # while only one setting is requested in the api call, there COULD be multiple settings
    # this grabs the first setting with "Gamertag" for the "id" and gets its value
    p['gamertag'] = next(filter(lambda p: p['id'] == 'Gamertag', prof['settings']))['value']
    return p


def flatten_match_teams(jdata:dict) -> list[dict]:

    teams = []

    for t in jdata['Teams']:
        flat = _flatten_match_team(t)
        flat['match_guid'] = jdata['MatchId']
        teams.append(flat)

    return teams


def _flatten_match_team(data:dict) -> dict:

    t = {}
    t['id'] = data['TeamId']
    t['outcome_id'] = data['Outcome']
    t['rank'] = data['Rank']
    t['stats'] = _flatten_stats(data['Stats']['CoreStats'])
    t['medals'] = _flatten_medals(data['Stats']['CoreStats']['Medals'])
    _add_mode_stats(t, data['Stats'])
    return t


def flatten_match_players(jdata:dict) -> list[dict]:

    players = []
    bots = []

    for p in jdata['Players']:
        flat = _flatten_match_player(p)
        flat['match_guid'] = jdata['MatchId']
        if p['PlayerType'] == 1:
            players.append(flat)
        else:
            flat['difficulty_id'] = p['BotAttributes']['Difficulty']
            bots.append(flat)

    return players, bots


def _flatten_match_player(data:dict) -> dict:

    p = {}
    p['id'] = data['PlayerId']
    p['team_id'] = data['LastTeamId']
    p['outcome_id'] = data['Outcome']
    p['rank'] = data['Rank']
    p['joined_at'] = data['FirstJoinedTime']
    p['left_at'] = data['LastLeaveTime']
    p['present_at_beginning'] = data['PresentAtBeginning']
    p['joined_in_progress'] = data['JoinedInProgress']
    p['left_in_progress'] = data['LeftInProgress']
    p['present_at_completion'] = data['PresentAtCompletion']
    p['time_played'] = data['TimePlayed']
    return p


def _flatten_stats(core_stats:dict) -> dict:

    s = {}
    s['score'] = core_stats['Score']
    s['personal_score'] = core_stats['PersonalScore']
    s['rounds_won'] = core_stats['RoundsWon']
    s['rounds_lost'] = core_stats['RoundsLost']
    s['rounds_tied'] = core_stats['RoundsTied']
    s['kills'] = core_stats['Kills']
    s['deaths'] = core_stats['Deaths']
    s['assists'] = core_stats['Assists']
    s['suicides'] = core_stats['Suicides']
    s['betrayals'] = core_stats['Betrayals']
    s['grenade_kills'] = core_stats['GrenadeKills']
    s['headshot_kills'] = core_stats['HeadshotKills']
    s['melee_kills'] = core_stats['MeleeKills']
    s['power_weapon_kills'] = core_stats['PowerWeaponKills']
    s['shots_fired'] = core_stats['ShotsFired']
    s['shots_hit'] = core_stats['ShotsHit']
    s['damage_dealt'] = core_stats['DamageDealt']
    s['damage_taken'] = core_stats['DamageTaken']
    s['callout_assists'] = core_stats['CalloutAssists']
    s['vehicle_destroys'] = core_stats['VehicleDestroys']
    s['driver_assists'] = core_stats['DriverAssists']
    s['hijacks'] = core_stats['Hijacks']
    s['emp_assists'] = core_stats['EmpAssists']
    s['max_killing_spree'] = core_stats['MaxKillingSpree']
    return s


def _flatten_medals(medals:dict) -> list[dict]:

    return [{'id': m['NameId'], 'count': m['Count']} for m in medals]


def _add_mode_stats(owner:dict, stats:dict) -> None:

    if len(stats.keys()) > 9:
        print('More than expected (9) stats keys found for match')
        with open('too_many_stats_keys.json', 'w') as f:
            json.dump(stats, f)

    modes = (
        ('bomb', 'BombStats', _flatten_bomb),
        ('ctf', 'CaptureTheFlagStats', _flatten_ctf),
        ('elimination', 'EliminationStats', _flatten_elimination),
        ('extraction', 'ExtractionStats', _flatten_extraction),
        ('infection', 'InfectionStats', _flatten_infection),
        ('oddball', 'OddballStats', _flatten_oddball),
        ('zones', 'ZonesStats', _flatten_zones),
        ('stockpile', 'StockpileStats', _flatten_stockpile)
    )
    for m in modes:
        mode_stats = stats.get(m[1])
        if mode_stats is not None:
            owner[m[0]] = m[2](mode_stats)
            # return b/c there can only be one mode stats
            return


def _flatten_bomb(mode_stats:dict):

    print('bomb mode not implemented')
    with open('bomb.json', 'w') as f:
        json.dump(mode_stats, f)
    raise NotImplementedError()


def _flatten_ctf(mode_stats:dict):

    raise NotImplementedError()


def _flatten_elimination(mode_stats:dict):

    e = {}
    e['allies_revived'] = mode_stats['AlliesRevived']
    e['elimination_assists'] = mode_stats['EliminationAssists']
    e['eliminations'] = mode_stats['Eliminations']
    e['enemy_revives_denied'] = mode_stats['EnemyRevivesDenied']
    e['executions'] = mode_stats['Executions']
    e['kills_as_last_player_standing'] = mode_stats['KillsAsLastPlayerStanding']
    e['last_players_standing_killed'] = mode_stats['LastPlayersStandingKilled']
    e['rounds_survived'] = mode_stats['RoundsSurvived']
    e['times_revived_by_ally'] = mode_stats['TimesRevivedByAlly']
    e['lives_remaining'] = mode_stats['LivesRemaining']
    e['elimination_order'] = mode_stats['EliminationOrder']
    return e


def _flatten_extraction(mode_stats:dict):

    print('extraction mode not implemented')
    with open('extraction.json', 'w') as f:
        json.dump(mode_stats, f)
    raise NotImplementedError()


def _flatten_infection(mode_stats:dict):

    print('infection mode not implemented')
    with open('infection.json', 'w') as f:
        json.dump(mode_stats, f)
    raise NotImplementedError()


def _flatten_oddball(mode_stats:dict):

    pass


def _flatten_zones(mode_stats:dict):

    pass


def _flatten_stockpile(mode_stats:dict):

    pass

