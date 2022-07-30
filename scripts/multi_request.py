import multiprocessing as mp
import os
import time
import requests
from itertools import chain

def f(o):
    payload = {
        'gamertag': 'aCurtis X89',
        'count': 25,
        'offset': o,
        'mode': 'matchmaking', # supposed to be type?
        'language': 'en-us'
    }
    r = requests.post('https://halo.api.stdlib.com/infinite@1.4.1/stats/players/matches/', json=payload,
                    headers={
                        'Authorization': f'Bearer tok_dev_rm16rxWeaeL7CnKbTnTCzzNxqWZLhEjyVAhkv6HSjS6ZZ2AYHfu4y7iR3fCWLXEp',
                        'Content-Type': 'application/json'
                    })
    matches = r.json()['data']['matches']
    return [g(m) for m in matches]

def g(match):
    gamevar = match['details']['gamevariant']
    mapvar = match['details']['map']
    playlist = match['details']['playlist']

    flat = {}
    # flat['response_id'] = self.id
    flat['guid'] = match['id']
    flat['gamevariant'] = gamevar['name']
    flat['gamevariant_guid'] = gamevar['asset']['id']
    flat['gamevariant_version'] = gamevar['asset']['version']
    flat['gamevariant_thumb_url'] = gamevar['asset']['thumbnail_url']
    flat['gamevariant_cat_id'] = gamevar['properties']['category_id']
    flat['map'] = mapvar['name']
    flat['map_guid'] = mapvar['asset']['id']
    flat['map_version'] = mapvar['asset']['version']
    flat['map_thumb_url'] = mapvar['asset']['thumbnail_url']
    flat['map_lvl_id'] = mapvar['properties']['level_id']
    flat['playlist'] = playlist['name']
    flat['playlist_guid'] = playlist['asset']['id']
    flat['playlist_version'] = playlist['asset']['version']
    flat['playlist_thumb_url'] = playlist['asset']['thumbnail_url']
    flat['playlist_queue'] = playlist['properties']['queue']
    flat['playlist_input'] = playlist['properties']['input']
    flat['playlist_is_ranked'] = playlist['properties']['ranked']
    flat['teams_enabled'] = match['teams']['enabled']
    flat['teams_scoring'] = match['teams']['scoring']
    flat['experience'] = match['experience']
    flat['type'] = match['type']
    flat['season_id'] = match['season']['id']
    flat['season_version'] = match['season']['version']
    # flat['played_at'] = isoparse(match['played_at'])
    flat['duration_seconds'] = match['duration']['seconds']

    return flat

def with_mp():
    start = time.time()
    with mp.Pool(mp.cpu_count()) as pool:
        results = pool.imap(f, range(0, 300, 25))
        # l = len(list(chain(*results)))
        print(next(results))
    # with mp.Pool(mp.cpu_count()) as pool:
    #     results = pool.map(f, range(300, 600, 25))
    #     l = len(list(chain(*results)))
    #     print(l)
    print('with', f'{time.time() - start}s')

def without_mp():
    start = time.time()
    for o in range(0, 150, 25):
        print(f(o))
    print('without', f'{time.time() - start}s')

if __name__ == '__main__':
    # without_mp()
    
    with_mp()