# see https://den.dev/blog/halo-api-authentication

import requests, json, pytz
from dateutil.parser import isoparse
from datetime import datetime as dt

from haloinfinite import util, api


class AuthManager:
    '''Manages acquisition and refresh of spartan tokens for authentication when calling the API.
        See https://den.dev/blog/halo-api-authentication'''

    AUTH_SCOPES = ' '.join(['Xboxlive.signin', 'Xboxlive.offline_access'])
    APPROVAL_PROMPT = 'auto'


    def __init__(self, config_file:str='config.yaml'):

        try:
            cfg = util.load_config(config_file)['azure_aad']
            self.client_id = cfg['client_id']
            self.client_secret = cfg['client_secret']
            self.redirect_uri = cfg['redirect_uri']
        except KeyError:
            print('Make sure your config file has "azure_aad" as a top level key and "client_id", "client_secret", and "redirect_url" under it.')
            exit(1)

        self.auth_code = None
        self.oauth_token = None
        self.refresh_token = None
        self.user_token = None
        self.user_hash = None
        self.halo_xsts_token = None
        self.xbox_xsts_token = None
        self.spartan_token = None
        self.expires_at = None


    def generate_new_spartan_token(self, use_refresh_token:bool=False):

        if use_refresh_token:
            self.refresh_oauth_token()
        else:
            # get an authentication code from the user
            url = self.generate_auth_url()
            print('Navigate to the below URL, confirm permissions, and copy the "code" parameter in the return URL (starts with "M.R3_")')
            print(url)
            self.auth_code = input('Paste code...')
            self.request_oauth_token()

        self.request_user_token()
        self.request_xsts_token()
        self.request_xsts_token(False)
        self.request_spartan_token()

        # finally, store the data
        self.save()


    def load_from_json(self):

        try:
            with open('token.json') as f:
                js = json.load(f)
        except FileNotFoundError:
            print('No "token.json" file found in the current directory.')
            return

        self.auth_code = js['auth_code']
        self.oauth_token = js['oauth_token']
        self.refresh_token = js['refresh_token']
        self.user_token = js['user_token']
        self.user_hash = js['user_hash']
        self.halo_xsts_token = js['halo_xsts_token']
        self.xbox_xsts_token = js['xbox_xsts_token']
        self.spartan_token = js['spartan_token']
        self.expires_at = isoparse(js['expires_at'])

        print('Loaded spartan token from file.')


    def save(self):

        if self.spartan_token is None:
            print('Unable to save the authentication info without a "spartan_token" provided.')
            exit(1)

        data = {
            'client_id': self.client_id,
            'auth_code': self.auth_code,
            'oauth_token': self.oauth_token,
            'refresh_token': self.refresh_token,
            'user_token': self.user_token,
            'user_hash': self.user_hash,
            'halo_xsts_token': self.halo_xsts_token,
            'xbox_xsts_token': self.xbox_xsts_token,
            'spartan_token': self.spartan_token,
            'expires_at': self.expires_at.isoformat()
        }

        with open('token.json', 'w') as f:
            json.dump(data, f)

        print('Saved "token.json" to the current directory.')


    def token_time_remaining(self) -> float:

        utcnow = pytz.utc.localize(dt.utcnow())
        return (self.expires_at - utcnow).total_seconds()


    def get_spartan_token(self):

        # if prop isn't set, try loading from file
        if not self.spartan_token:
            self.load_from_json()

        if self.spartan_token:
            # refresh if less than 10 minutes remaining for token
            if self.token_time_remaining() < 600:
                print('Refreshing spartan token.')
                self.generate_new_spartan_token(True)
            print('Valid spartan token from file.')
            return self.spartan_token
        
        # if no file data could be loaded, do full auth flow
        print('No spartan token available. Requesting new token.')
        self.generate_new_spartan_token()
        return self.spartan_token


    def generate_auth_url(self):

        url = 'https://login.live.com/oauth20_authorize.srf'
        params = {
            'client_id': self.client_id,
            'response_type': 'code',
            'approval_prompt': self.APPROVAL_PROMPT,
            'scope': self.AUTH_SCOPES,
            'redirect_uri': self.redirect_uri
        }
        # use Request to encode the url appropriately
        p = requests.Request('GET', url, params=params).prepare()
        return p.url


    def request_oauth_token(self):

        url = 'https://login.live.com/oauth20_token.srf'
        params = {
            'grant_type': 'authorization_code',
            'code': self.auth_code,
            'approval_prompt': self.APPROVAL_PROMPT,
            'scope': self.AUTH_SCOPES,
            'redirect_uri': self.redirect_uri,
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }
        resp = requests.post(url, params)
        resp.raise_for_status()
        js = resp.json()

        try:
            self.oauth_token = js['access_token']
        except KeyError:
            print('No "access_token" key in the oauth token response. Response text:')
            print(resp.text)
            exit(1)


    def refresh_oauth_token(self):
        '''See https://docs.microsoft.com/en-us/azure/active-directory/develop/v2-oauth2-auth-code-flow#refresh-the-access-token'''

        url = 'https://login.live.com/oauth20_token.srf'
        params = {
            'grant_type': 'refresh_token',
            'refresh_token': self.refresh_token,
            'scope': self.AUTH_SCOPES,
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }
        resp = requests.post(url, params)
        resp.raise_for_status()
        js = resp.json()

        try:
            self.oauth_token = js['access_token']
        except KeyError:
            print('No "access_token" key in the oauth token response. Response text:')
            print(resp.text)
            exit(1)


    def request_user_token(self):

        url = 'https://user.auth.xboxlive.com/user/authenticate'
        headers = {
            'x-xbl-contract-version': '1'
        }
        js = {
            'Properties': {
                'AuthMethod': 'RPS',
                'RpsTicket': 'd=' + self.oauth_token,
                'SiteName': 'user.auth.xboxlive.com'
            },
            'RelyingParty': 'http://auth.xboxlive.com',
            'TokenType': 'JWT'
        }
        resp = requests.post(url, headers=headers, json=js)
        resp.raise_for_status()
        rjson = resp.json()

        try:
            self.user_token = rjson['Token']
        except KeyError:
            print('No "Token" key in the user token response. Response text:')
            print(resp.text)
            exit(1)

        self.user_hash = rjson['DisplayClaims']['xui'][0]['uhs']


    def request_xsts_token(self, use_halo_relying_party:bool=True):
        '''Xbox Security Token Service (XSTS)'''

        url = 'https://xsts.auth.xboxlive.com/xsts/authorize'
        headers = {
            'x-xbl-contract-version': '1'
        }
        relying_party = 'https://prod.xsts.halowaypoint.com/' if use_halo_relying_party else 'http://xboxlive.com'
        js = {
            'Properties': {
                'SandboxId': 'RETAIL',
                'UserTokens': [self.user_token]
            },
            'RelyingParty': relying_party,
            'TokenType': 'JWT'
        }
        resp = requests.post(url, headers=headers, json=js)
        resp.raise_for_status()
        js = resp.json()

        try:
            if use_halo_relying_party:
                self.halo_xsts_token = js['Token']
            else:
                self.xbox_xsts_token = js['Token']
        except KeyError:
            print('No "Token" key in the xsts token response. Response text:')
            print(resp.text)
            exit(1)


    def get_xbox_live_v3_token(self):
        '''Not currently used.'''

        return f'XBL3.0 x={self.user_hash};{self.xbox_xsts_token}'


    def request_spartan_token(self):

        url = 'https://settings.svc.halowaypoint.com/spartan-token'
        headers = {
            'User-Agent': api.HALO_WAYPOINT_USER_AGENT,
            'Accept': 'application/json'
        }
        js = {
            'Audience': 'urn:343:s3:services',
            'MinVersion': '4',
            'Proof': [{
                'Token': self.halo_xsts_token,
                'TokenType': 'Xbox_XSTSv3'
            }]
        }
        resp = requests.post(url, headers=headers, json=js)
        resp.raise_for_status()
        rjson = resp.json()

        try:
            self.spartan_token = rjson['SpartanToken']
        except KeyError:
            print('No "Token" key in the spartan token response. Response text:')
            print(resp.text)
            exit(1)
        
        isodate = rjson['ExpiresUtc']['ISO8601Date']
        self.expires_at = isoparse(isodate)


    def request_clearance_token(self):
        '''Not currently used.'''

        url = f'https://settings.svc.halowaypoint.com/oban/flight-configurations/titles/hi/audiences/RETAIL/active'
        headers = {
            'x-343-authorization-spartan': self.spartan_token,
            'User-Agent': api.HALO_PC_USER_AGENT
        }
        params = {
            'sandbox': 'UNUSED',
            'build': '222249.22.06.08.1730-0'
        }
        resp = requests.get(url, params, headers=headers)
        resp.raise_for_status()
        rjson = resp.json()

        try:
            return rjson['FlightConfigurationId']
        except KeyError:
            print('No "FlightConfigurationId" key in the clearance token response. Response text:')
            print(resp.text)
            exit(1)

