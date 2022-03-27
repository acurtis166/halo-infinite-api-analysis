"""Test the db_insert module."""


import unittest

import halo_infinite_api.db as db


MATCHES = [
    ('f8a12f0d-335c-421a-a392-7e38635b79e7', '2022-03-02T04:51:41.306Z', 511, 'Quick Play', 'Strongholds', 'Recharge'),
    ('a37b3a4b-2f2a-4eec-9919-463e3c87c16c', '2022-03-02T04:38:29.534Z', 632, 'Quick Play', 'CTF', 'Aquarius')
]

TEAMS = [
    ('f8a12f0d-335c-421a-a392-7e38635b79e7', 0, 1800, 1, 'win', 6000, 50, 13.66, 12000, 10000, 1000, 400),
    ('f8a12f0d-335c-421a-a392-7e38635b79e7', 1, 1500, 2, 'loss', 5000, 40, -6, 10000, 12000, 1100, 410),
    ('a37b3a4b-2f2a-4eec-9919-463e3c87c16c', 0, 1500, 2, 'loss', 5000, 40, -6, 10000, 12000, 1100, 410)
]

PLAYERS = [
    ('f8a12f0d-335c-421a-a392-7e38635b79e7', 0, 'TwiningIsland83', 1000, 1200, 12, 2.66, 2500, 2300, 400, 160, '2022-03-02T04:51:41.306Z', None),
    ('f8a12f0d-335c-421a-a392-7e38635b79e7', 0, 'aCurtis X89', 1500, 2000, 20, 10.33, 4000, 2000, 300, 160, '2022-03-02T04:51:41.306Z', None),
    ('a37b3a4b-2f2a-4eec-9919-463e3c87c16c', 0, 'TwiningIsland83', 1100, 1200, 13, 3.66, 2500, 2300, 400, 160, '2022-03-02T04:51:41.306Z', None)
]


class TestDb(unittest.TestCase):
    """Test the HaloDotAPI access functions."""


    def test_insert_matches_success(self):
        """Test that matches are successfully inserted into database."""

        with db.conn(':memory:') as conn:
            db.init(conn)
            db.insert_matches(conn, MATCHES)

            cur = conn.cursor()
            cur.execute('SELECT * FROM Match')
            rows = cur.fetchall()
            self.assertEqual(len(rows), 2)
            self.assertEqual(rows[0][0], 'f8a12f0d-335c-421a-a392-7e38635b79e7')


    def test_insert_matches_ignore(self):
        """Test that duplicate match inserts are ignored."""

        with db.conn(':memory:') as conn:
            db.init(conn)
            db.insert_matches(conn, MATCHES)
            db.insert_matches(conn, MATCHES)

            cur = conn.cursor()
            cur.execute('SELECT * FROM Match')
            rows = cur.fetchall()
            self.assertEqual(len(rows), 2)


    def test_insert_teams_success(self):
        """Test that teams are successfully inserted into database."""

        with db.conn(':memory:') as conn:
            db.init(conn)
            db.insert_matches(conn, MATCHES)
            db.insert_teams(conn, TEAMS)

            cur = conn.cursor()
            cur.execute('SELECT * FROM Team')
            rows = cur.fetchall()
            self.assertEqual(len(rows), len(TEAMS))
            self.assertEqual(rows[0][4], 'win')
            self.assertEqual(rows[1][7], -6)


    def test_insert_teams_ignore(self):
        """Test that duplicate team inserts are ignored."""

        with db.conn(':memory:') as conn:
            db.init(conn)
            db.insert_matches(conn, MATCHES)
            db.insert_teams(conn, TEAMS)
            db.insert_teams(conn, TEAMS)

            cur = conn.cursor()
            cur.execute('SELECT * FROM Team')
            rows = cur.fetchall()
            self.assertEqual(len(rows), (len(TEAMS)))


    def test_insert_players_success(self):
        """Test that players are successfully inserted into database."""

        with db.conn(':memory:') as conn:
            db.init(conn)
            db.insert_matches(conn, MATCHES)
            db.insert_teams(conn, TEAMS)
            db.insert_players(conn, PLAYERS)

            cur = conn.cursor()
            cur.execute('SELECT * FROM Player')
            rows = cur.fetchall()
            self.assertEqual(len(rows), len(PLAYERS))
            self.assertEqual(rows[1][2], 'aCurtis X89')
            self.assertEqual(rows[0][7], 2500)


    def test_insert_players_ignore(self):
        """Test that duplicate player inserts are ignored."""

        with db.conn(':memory:') as conn:
            db.init(conn)
            db.insert_matches(conn, MATCHES)
            db.insert_teams(conn, TEAMS)
            db.insert_players(conn, PLAYERS)
            db.insert_players(conn, PLAYERS)

            cur = conn.cursor()
            cur.execute('SELECT * FROM Player')
            rows = cur.fetchall()
            self.assertEqual(len(rows), len(PLAYERS))


    def test_get_least_frequent_player(self):
        """Test that the least frequent player is retrieved from the database."""

        with db.conn(':memory:') as conn:
            db.init(conn)
            db.insert_matches(conn, MATCHES)
            db.insert_teams(conn, TEAMS)
            db.insert_players(conn, PLAYERS)

            result = db.get_least_frequent_player(conn)

        self.assertEqual(result, 'aCurtis X89')


    def test_get_least_frequent_player_raises_exception(self):

        self.fail('not implemented')


    def test_get_matches_without_details(self):
        """Test that the correct MatchIds are found."""

        with db.conn(':memory:') as conn:
            db.init(conn)
            db.insert_matches(conn, MATCHES)
            db.insert_teams(conn, TEAMS[:1])
            db.insert_players(conn, PLAYERS[:1])

            result = db.get_matches_without_details(conn)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], 'a37b3a4b-2f2a-4eec-9919-463e3c87c16c')

