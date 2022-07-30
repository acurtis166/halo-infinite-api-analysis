import requests
import pandas as pd


def flatten_json(y):
    # https://towardsdatascience.com/flattening-json-objects-in-python-f5343c794b10
    out = {}

    def flatten(x, name=''):
        if type(x) is dict:
            for a in x:
                flatten(x[a], name + a + '_')
        elif type(x) is list:
            i = 0
            for a in x:
                flatten(a, name + str(i) + '_')
                i += 1
        else:
            out[name[:-1]] = x

    flatten(y)
    return out


def autocode_request(offset):

    url = 'https://halo.api.stdlib.com/infinite@1.4.1/stats/players/matches/'
    headers = {
        'Authorization': f'Bearer tok_dev_kwQ688yXk7ancye29mwNoQHwuMQaGMajaxeWgDJ4u24obD6jK5CoR6twLqyXGeUf',
        'Content-Type': 'application/json'
    }
    payload = {
        'gamertag': 'aCurtis X89',
        'count': 25,
        'offset': offset,
        'type': 'matchmaking',
        'language': 'en-us'
    }


def run_autocode():

    pass


def get_waypoint_matches():

    pass


def run_waypoint():

    pass