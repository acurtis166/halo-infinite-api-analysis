import requests

from haloinfinite import util

# haven't tested if these are actually necessary or not
HALO_WAYPOINT_USER_AGENT = "HaloWaypoint/2021112313511900 CFNetwork/1327.0.4 Darwin/21.2.0"
HALO_PC_USER_AGENT = "SHIVA-2043073184/6.10021.18539.0 (release; PC)"


class ApiService:
    '''Wrapper for select endpoints servicing Halo Infinite.'''

    PLAYER_MATCHES_BATCH_SIZE = 25

    def __init__(self, auth_mgr):

        self.auth_mgr = auth_mgr


    def verify_or_refresh_tokens(self):

        self.auth_mgr.get_spartan_token()

    
    def _get_json(self, url:str, user_agent:str, params:dict=None):

        headers = {
            'x-343-authorization-spartan': self.auth_mgr.spartan_token,
            'User-Agent': user_agent,
            'Accept': 'application/json'
        }
        resp = requests.get(url, params, headers=headers)
        resp.raise_for_status()
        return resp.json()


    def get_match_stats(self, match_guid:str):

        # match_guid = '21416434-4717-4966-9902-af7097469f74'
        # match_guid = '8d641322-8553-44f0-b991-89d028377c62'
        url = f'https://halostats.svc.halowaypoint.com:443/hi/matches/{match_guid}/stats'
        return self._get_json(url, HALO_PC_USER_AGENT)


    def get_player_matches(self, player_xuid:str, start:int=0, count:int=25):

        xuid = util.wrap_xuid(player_xuid)
        url = f'https://halostats.svc.halowaypoint.com:443/hi/players/{xuid}/matches'
        params = {
            'start': start, # offset starting at 0
            'count': count # max 25
        }
        return self._get_json(url, HALO_WAYPOINT_USER_AGENT, params)


    def get_player_match_count(self, player_xuid:str):

        xuid = util.wrap_xuid(player_xuid)
        url = f'https://halostats.svc.halowaypoint.com:443/hi/players/{xuid}/matches/count'
        return self._get_json(url, HALO_WAYPOINT_USER_AGENT)


    def get_player_match_skill(self, match_guid:str, player_xuids:list[str]):

        url = f'https://skill.svc.halowaypoint.com:443/hi/matches/{match_guid}/skill'
        params = {
            'players': [util.wrap_xuid(x) for x in player_xuids]
        }
        return self._get_json(url, HALO_PC_USER_AGENT, params)


    def get_player_privacy(self, player_xuid:str):

        xuid = util.wrap_xuid(player_xuid)
        url = f'https://halostats.svc.halowaypoint.com:443/hi/players/{xuid}/matches-privacy'
        return self._get_json(url, HALO_WAYPOINT_USER_AGENT)


    def get_map(self, asset_id:str, version_id:str):

        url = f'https://discovery-infiniteugc.svc.halowaypoint.com/hi/maps/{asset_id}/versions/{version_id}'
        return self._get_json(url, HALO_WAYPOINT_USER_AGENT)


    def get_playlist(self, asset_id:str, version_id:str):

        # only works with version-dependent url?
        url = f'https://discovery-infiniteugc.svc.halowaypoint.com/hi/playlists/{asset_id}/versions/{version_id}'
        return self._get_json(url, HALO_WAYPOINT_USER_AGENT)


    def get_gamevariant(self, asset_id:str, version_id:str):

        url = f'https://discovery-infiniteugc.svc.halowaypoint.com/hi/ugcGameVariants/{asset_id}/versions/{version_id}'
        return self._get_json(url, HALO_WAYPOINT_USER_AGENT)


    def get_map_mode_pair(self, asset_id:str, version_id:str):

        # only works with version-dependent url?
        # this one has both map and playlist
        url = f'https://discovery-infiniteugc.svc.halowaypoint.com/hi/mapModePairs/{asset_id}/versions/{version_id}'
        return self._get_json(url, HALO_WAYPOINT_USER_AGENT)


    def get_profiles(self, player_xuids:list[str]):
        '''See https://docs.microsoft.com/en-us/gaming/gdk/_content/gc/reference/live/rest/uri/profilev2/uri-usersbatchprofilesettingspost
        players: xuids just the number
        '''

        # not technically part of halo endpoints but logically makes sense here
        url = 'https://profile.xboxlive.com/users/batch/profile/settings'
        headers = {
            'x-xbl-contract-version': '2',
            'Content-Type': 'application/json',
            'Authorization': self.auth_mgr.get_xbox_live_v3_token()
        }
        js = {
            'settings': ['Gamertag'],
            'userIds': [util.unwrap_xuid(x) for x in player_xuids]
        }
        resp = requests.post(url, headers=headers, json=js)
        resp.raise_for_status()
        return resp.json()

