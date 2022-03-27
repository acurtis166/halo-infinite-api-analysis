import unittest
import halo_infinite_api.api as api
import halo_infinite_api.error as err

import requests


class TestApi(unittest.TestCase):
    """Test the HaloDotAPI access functions."""

    def test_post_raises_api_request_error_bad_endpoint(self):
        """Test that a bad endpoint raises an ApiRequestError"""

        endpoint = 'bad_endpoint/'
        with self.assertRaises(err.ApiRequestError):
            api._post(endpoint)


    def test_post_raises_api_request_error_missing_params(self):
        """Test that having missing parameters raises an ApiRequestError"""

        endpoint = 'appearance/'
        data = {'gamertag': None}
        with self.assertRaises(err.ApiRequestError):
            api._post(endpoint, data)


    def test_get_match_list_count_25(self):
        """Test that valid gamertag returns a JSON response with 25 matches."""

        gamertag = 'aCurtis X89'
        count = 25
        resp = api.get_match_list(gamertag, count)
        self.assertIsInstance(resp, requests.Response)
        try:
            data = resp.json()
        except requests.exceptions.JSONDecodeError:
            self.fail('Response.json() failed to decode the response.')
        self.assertEqual(len(data['data']), 25)


    def test_get_match_list_count_5(self):
        """Test that valid gamertag returns a JSON response with 5 matches."""

        gamertag = 'aCurtis X89'
        count = 5
        resp = api.get_match_list(gamertag, count)
        self.assertIsInstance(resp, requests.Response)
        try:
            data = resp.json()
        except requests.exceptions.JSONDecodeError:
            self.fail('Response.json() failed to decode the response.')
        self.assertEqual(len(data['data']), count)


    def test_get_match_list_offset(self):
        """Test that changing the offset parameter changes the retrieved data for get_match_list."""

        gamertag = 'aCurtis X89'
        resp_zero = api.get_match_list(gamertag, 1, 0)
        id_zero = resp_zero.json()['data'][0]['id']
        resp_one = api.get_match_list(gamertag, 1, 1)
        id_one = resp_one.json()['data'][0]['id']
        self.assertNotEqual(id_zero, id_one)


    def test_get_match_details_valid(self):
        """Test that valid match id returns a JSON response with appropriate data."""

        match_id = 'f8a12f0d-335c-421a-a392-7e38635b79e7'
        resp = api.get_match_details(match_id)
        self.assertIsInstance(resp, requests.Response)
        try:
            data = resp.json()
        except requests.exceptions.JSONDecodeError:
            self.fail('Response.json() failed to decode the response.')
        self.assertEqual(data['data']['id'], 'f8a12f0d-335c-421a-a392-7e38635b79e7')

