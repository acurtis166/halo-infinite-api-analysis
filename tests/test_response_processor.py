"""Test the response_parse module."""


import unittest
import halo_infinite_api.response_processor as resp_parse
import halo_infinite_api.error as err


class TestResponseParse(unittest.TestCase):
    """Test the API response parsing functions."""

    def test_parse_match_valid(self):
        """Test that JSON can successfully be parsed to produce a match dict."""

        data = {
            'id': 'f8a12f0d-335c-421a-a392-7e38635b79e7',
            'details': {
                'category': {
                    'name': 'Strongholds'
                },
                'map': {
                    'name': 'Recharge'
                },
                'playlist': {
                    'name': 'Quick Play'
                }
            },
            'played_at': '2022-03-02T04:51:41.306Z',
            'duration': {
                'seconds': 511
            }
        }
        result = resp_parse.parse_match(data)
        self.assertEqual(result[0], 'f8a12f0d-335c-421a-a392-7e38635b79e7')
        self.assertEqual(result[1], '2022-03-02T04:51:41.306Z')
        self.assertEqual(result[2], 511)
        self.assertEqual(result[3], 'Quick Play')
        self.assertEqual(result[4], 'Strongholds')
        self.assertEqual(result[5], 'Recharge')


    def test_parse_match_raises_parse_error(self):
        """Test that missing match data will cause a parsing error."""

        data = {}
        with self.assertRaises(err.ParsingError):
            resp_parse.parse_match(data)


    def test_parse_match_details_filters_out_bots(self):

        self.fail('not implemented')


    def test_parse_team_valid(self):
        """Test that a team dict from JSON data can be parsed."""

        data = {
            "team": {
                "id": 0,
                "skill": {
                    "mmr": 1800.4127296666852
                }
            },
            "stats": {
                "core": {
                    "damage": {
                        "taken": 12002,
                        "dealt": 13834
                    },
                    "shots": {
                        "fired": 1910,
                        "landed": 676
                    },
                    "kda": 17,
                    "score": 6925,
                    "points": 200
                }
            },
            "rank": 1,
            "outcome": "loss"
        }
        result = resp_parse.parse_team(data)
        self.assertEqual(result[0], 0)
        self.assertEqual(result[1], 1800.4127296666852)
        self.assertEqual(result[2], 1)
        self.assertEqual(result[3], 'loss')
        self.assertEqual(result[4], 6925)
        self.assertEqual(result[5], 200)
        self.assertEqual(result[6], 17)
        self.assertEqual(result[7], 13834)
        self.assertEqual(result[8], 12002)
        self.assertEqual(result[9], 1910)
        self.assertEqual(result[10], 676)


    def test_parse_team_raises_parse_error(self):
        """Test that missing team data will cause a parsing error."""

        data = {}
        with self.assertRaises(err.ParsingError):
            resp_parse.parse_team(data)


    def test_parse_player_valid(self):
        """Test that a player dict from JSON data can be parsed."""
        
        data = {
            "gamertag": "aCurtis X89",
            "team": {
                "id": 0
            },
            "stats": {
                "core": {
                    "damage": {
                        "taken": 3000,
                        "dealt": 6000
                    },
                    "shots": {
                        "fired": 200,
                        "landed": 100
                    },
                    "kda": 10,
                    "score": 1800,
                    "points": 20
                }
            },
            "rank": 1,
            "outcome": "loss",
            "participation": {
                "joined_at": "2022-03-02T04:52:09.833Z",
                "left_at": None
            },
            "progression": {
                "csr": {
                    "pre_match": {
                        "value": 1572
                    }
                }
            }
        }
        result = resp_parse.parse_player(data)
        self.assertEqual(result[0], 0)
        self.assertEqual(result[1], 'aCurtis X89')
        self.assertEqual(result[2], 1572)
        self.assertEqual(result[3], 1800)
        self.assertEqual(result[4], 20)
        self.assertEqual(result[5], 10)
        self.assertEqual(result[6], 6000)
        self.assertEqual(result[7], 3000)
        self.assertEqual(result[8], 200)
        self.assertEqual(result[9], 100)
        self.assertEqual(result[10], "2022-03-02T04:52:09.833Z")
        self.assertEqual(result[11], None)


    def test_parse_player_raises_parse_error(self):
        """Test that missing team data will cause a parsing error."""

        data = {}
        with self.assertRaises(err.ParsingError):
            resp_parse.parse_player(data)

