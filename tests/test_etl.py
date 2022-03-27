"""Test the etl module."""


import unittest

import halo_infinite_api.etl as etl
import halo_infinite_api.db as db


class TestETL(unittest.TestCase):
    """Test the HaloDotAPI access functions."""


    def test_calculate_count(self):
        """Test that calculate_count calculates the correct number of rows."""

        # (offset, limit, expected count)
        data = [(0, 1, 1), (0, 10, 10), (25, 33, 8), (0, 50, 25)]
        for offset_limit in data:
            result = etl.calculate_count(offset_limit[0], offset_limit[1])
            self.assertEqual(result, offset_limit[2])


    def test_load_player_matches(self):
        """Test that matches are successfully retrieved from the API and inserted into database."""

        for n in (1, 10, 30, 100):
            with db.conn(':memory:') as conn:
                db.init(conn)
                etl.load_player_matches(conn, 'aCurtis X89', n)
                
                cur = conn.cursor()
                cur.execute('SELECT * FROM Match')
                rows = cur.fetchall()
                self.assertEqual(len(rows), n, f'Failed on {n} limit.')


    def test_load_match_details(self):
        """Test that the correct number of teams and players are retrieved for a match."""

        match_id = 'f8a12f0d-335c-421a-a392-7e38635b79e7'

        with db.conn(':memory:') as conn:
            db.init(conn)
            db.insert_matches(conn, [(match_id, '', 1, '', '', '')])
            etl.load_match_details(conn, match_id)

            cur = conn.cursor()
            cur.execute('SELECT * FROM Team')
            rows = cur.fetchall()
            self.assertEqual(len(rows), 2)

            cur.execute('SELECT * FROM Player')
            rows = cur.fetchall()
            self.assertEqual(len(rows), 8)


    def test_load_randomized_matches(self):
        """Test that matches are successfully retrieved from the API and inserted into database."""

        player_search_depth = 25
        limit = 100

        with db.conn(':memory:') as conn:
            db.init(conn)
            etl.load_randomized_matches(conn, 'aCurtis X89', player_search_depth, limit)

            cur = conn.cursor()
            cur.execute('SELECT * FROM Match')
            rows = cur.fetchall()
            self.assertGreaterEqual(len(rows), player_search_depth)
            self.assertLessEqual(len(rows), limit)

