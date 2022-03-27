"""Contains logic for retrieving API data from the Halo Infinite API resource."""


import requests
import config

import halo_infinite_api.error as error


def _post(endpoint:str, data:dict=None):
    """Make a POST request to the specified API endpoint and return the response.

    Args:
        endpoint (str): the URL to make the request to
        params (dict, optional): parameters for the request. Defaults to None.

    Raises:
        halo_match_prediction.error.ApiRequestError: if a request to the API fails

    Returns:
        Response: the response object
    """

    r = requests.post(f'https://halo.api.stdlib.com/infinite@{config.API_VERSION}/{endpoint}', 
                    headers={
                        'Authorization': f'Bearer {config.API_KEY}',
                        'Content-Type': 'application/json'
                    }, 
                    json=data)

    # make sure the request was successful, otherwise raise an exception
    if r.status_code != requests.codes.ok:
        raise error.ApiRequestError(r, data)

    return r


def get_match_list(gamertag:str, count:int=25, offset:int=1, mode:str='matchmade'):
    """Get targeted player's match history.

    Args:
        gamertag (str): Player's gamertag
        count (int, optional): Retrieve this many rows. Min 1, max 25. Defaults to 25.
        offset (int, optional): Start at this record number. Defaults to 1.
        mode (str, optional): Enumerated game mode - 'matchmade' or 'custom'. Defaults to 'matchmade'.

    Returns:
        Response: the Response from the API request.
    """

    endpoint = 'stats/matches/list/'
    data = {
        'gamertag': gamertag,
        'limit': {
            'count': count,
            'offset': offset
        },
        'mode': mode
    }
    return _post(endpoint, data)


def get_match_details(match_id:str):
    """Get the details of a particular match.

    Args:
        match_id (str): The GUID that identifies the match.

    Returns:
        Response: the Response from the API request.
    """

    endpoint = 'stats/matches/retrieve/'
    params = {
        'id': match_id
    }
    return _post(endpoint, params)

    