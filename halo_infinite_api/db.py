"""Contains logic for inserting records into the SQLite database."""


import sqlite3
from contextlib import contextmanager
import config


@contextmanager
def conn(database:str=config.DATABASE):
    """Create a contextual database connection.

    Args:
        database (str, optional): The database for storing and retrieving API data. Defaults to config.DATABASE.

    Yields:
        Connection: The SQLite connection.
    """
    
    conn = sqlite3.connect(database)
    try:
        yield conn
    finally:
        conn.close()


def init(conn:sqlite3.Connection):
    """Initialize a database for the Halo Infinite API application.

    Args:
        conn (Connection): A SQLite connection.
    """

    with open('init.sql') as f:
        sql = f.read()

    cur = conn.cursor()
    cur.executescript(sql)
    conn.commit()


def insert_matches(conn:sqlite3.Connection, matches:list[tuple]):
    """Insert match data into the database.

    Args:
        conn (Connection): A SQLite connection.
        matches (list[tuple]): The match data to insert.
    """

    cur = conn.cursor()
    cur.executemany("""
        INSERT OR IGNORE INTO Match (MatchId, PlayedAt, Duration, Playlist, GameType, Map) 
        VALUES (?, ?, ?, ?, ?, ?)""", matches)
    conn.commit()


def insert_teams(conn:sqlite3.Connection, teams:list[tuple]):
    """Insert team data from match details into the database.

    Args:
        conn (Connection): A SQLite connection.
        teams (list[tuple]): The team data to insert.
    """

    cur = conn.cursor()
    cur.executemany("""
        INSERT OR IGNORE INTO Team (MatchId, TeamId, MMR, Rank, Outcome, Score, Points, KDA, DamageDealt, DamageTaken, ShotsFired, ShotsLanded)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", teams)
    conn.commit()


def insert_players(conn:sqlite3.Connection, players:list[tuple]):
    """Insert player data from match details into the database.

    Args:
        conn (Connection): A SQLite connection.
        teams (list[tuple]): The team data to insert.
    """

    cur = conn.cursor()
    cur.executemany("""
        INSERT OR IGNORE INTO Player (MatchId, TeamId, Gamertag, PreMatchCsr, Score, Points, KDA, DamageDealt, DamageTaken, ShotsFired, ShotsLanded, JoinedAt, LeftAt)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", players)
    conn.commit()


def get_least_frequent_player(conn:sqlite3.Connection):
    """Get the gamertag of the player that occurs least frequently in the Player table."""

    cur = conn.cursor()
    cur.execute("""
        SELECT Gamertag, COUNT(Gamertag)
        FROM Player
        GROUP BY Gamertag
        ORDER BY 2
        LIMIT 1
    """)
    row = cur.fetchone()

    if row is None:
        raise Exception('No player records exist in the database.')

    return row[0]


def get_matches_without_details(conn:sqlite3.Connection):
    """Get matches which haven't had teams and/or players inserted into the database.

    Args:
        conn (Connection): SQLite connection.
    """

    cur = conn.cursor()
    cur.execute("""
        SELECT MatchId
        FROM Match
        WHERE MatchId NOT IN (
            SELECT DISTINCT MatchId
            FROM (
                SELECT MatchId
                FROM Team
                UNION
                SELECT MatchId
                FROM Player
            )
        )
    """)
    rows = cur.fetchall()

    return tuple(r[0] for r in rows)

    