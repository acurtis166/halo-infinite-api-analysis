"""Makes API calls, processes responses, and inserts resulting data into the database."""


from sqlite3 import Connection

import halo_infinite_api.api as hapi
import halo_infinite_api.response_processor as resp_proc
import halo_infinite_api.db as db


def load_player_matches(conn:Connection, gamertag:str, limit:int=None):
    """Request matches for a player from the Halo API and insert them into the database.

    Args:
        conn (Connection): SQLite connection.
        gamertag (str): The player to request matches for.
        limit (int, optional): The number of matches to retrieve. Defaults to None.
    """

    offset = 0

    while limit is None or limit > offset:
        count = calculate_count(offset, limit)
        matches = hapi.get_match_list(gamertag, count, offset)
        match_records = resp_proc.parse_match_list(matches)

        if len(match_records) > 0:
            db.insert_matches(conn, match_records)
        else:
            break

        offset += count


def load_match_details(conn:Connection, match_id:str):
    """Request match details from the Halo API and insert the teams and players into the database.

    Args:
        conn (Connection): SQLite connection.
        match_id (str): The GUID for the match.
    """

    match_details = hapi.get_match_details(match_id)
    teams, players = resp_proc.parse_match_details(match_details)

    db.insert_teams(conn, teams)
    db.insert_players(conn, players)


def load_many_match_details(conn:Connection):
    """Request and insert teams and players for all matches without details in the database.

    Args:
        conn (Connection): SQLite connection.
    """

    match_ids = db.get_matches_without_details(conn)

    for mid in match_ids:
        load_match_details(conn, mid)


def load_randomized_matches(conn:Connection, seed_gamertag:str, player_search_depth:int, limit:int):
    """Load matches for players, requesting matches until the limit is satisfied.

    Args:
        conn (Connection): SQLite connection.
        seed_gamertag (str): The gamertag to begin the match search with.
        player_search_depth (int): The number of matches to request for each player.
        limit (int): The total number of matches to request. Note that duplicate matches will not be inserted.
    """

    counter = 0
    gamertag = seed_gamertag

    while counter < limit:
        if counter + player_search_depth > limit:
            player_search_limit = limit - counter
        else:
            player_search_limit = player_search_depth

        load_player_matches(conn, gamertag, player_search_limit)
        load_many_match_details(conn)

        gamertag = db.get_least_frequent_player(conn)
        counter += player_search_limit

        

def calculate_count(offset:int, limit:int):
    """Calculate the count to use when requesting matches for a player when a limit is provided.

    Args:
        offset (int): The starting point for a matches request.
        limit (int): The number of matches desired.

    Returns:
        int: The count parameter to use for a matches request.
    """

    if limit is None or limit - offset >= 25:
        return 25
    else:
        return limit - offset

        