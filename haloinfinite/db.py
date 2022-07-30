"""Contains logic for inserting records into the database."""


import psycopg2
from psycopg2.extras import execute_values, NamedTupleCursor
from contextlib import contextmanager
from typing import Union

from haloinfinite import util

PROD_DB = 'halo_infinite'
TEST_DB = 'halo_infinite_test'
SYSTEM_DB = 'postgres'


class Database:
    def __init__(self, db_name:str=PROD_DB):

        db_cfg = util.load_config()['database'][db_name]
        self.host = db_cfg['host']
        self.name = db_cfg['name']
        self.user = db_cfg['user']
        self.password = db_cfg['password']

    @contextmanager
    def connect(self):
        """Create a contextual database connection.

        Yields:
            Connection: The database connection engine.
        """
        
        conn = psycopg2.connect(
            host=self.host,
            dbname=self.name,
            user=self.user,
            password=self.password
        )
        try:
            yield conn
        # except Exception as e:
        #     print(f'Error connecting to database:\n{e}')
        finally:
            conn.close()

    def execute_script(self, file_name:str) -> None:
        """Execute the SQL content of a file.

        Args:
            file_path (str): The path to the file to execute.
        """

        sql = util.get_package_data('sql/' + file_name)

        with self.connect() as conn:
            cur = conn.cursor()
            cur.execute(sql)
            conn.commit()


    def execute_values_with_str(self, sql:str, values:list[dict], template:str, **kwargs) -> Union[list[tuple], int]:

        with self.connect() as conn:
            cur = conn.cursor()
            result = execute_values(cur, sql, values, template, **kwargs)
            conn.commit()

            if result is not None:
                return result
            return cur.rowcount


    def execute_values_with_file(self, file_name:str, values:list[dict], template:str, **kwargs) -> Union[list[tuple], int]:

        sql = util.get_package_data('sql/' + file_name)
        return self.execute_values_with_str(sql, values, template, **kwargs)


    def init(self) -> None:

        prompt = 'Are you sure you want to initialize the production database? All data will be lost. (Enter "y" to confirm) '
        if self.name == PROD_DB and input(prompt).lower().strip() != 'y':
            exit()
            
        sys_conn = psycopg2.connect(
            host=self.host,
            dbname=SYSTEM_DB,
            user=self.user,
            password=self.password
        )

        # drop/create database cannot run inside a transaction block
        sys_conn.autocommit = True
        cur = sys_conn.cursor()
        # don't include semicolon termination for statements - causes OperationalError 
        # regarding not being about to run the statements in a transaction
        # make sure to close other connections before dropping database
        cur.execute(f'DROP DATABASE IF EXISTS {self.name}')
        cur.execute(f'CREATE DATABASE {self.name}')
        sys_conn.close()

        self.execute_script('init.sql')


    def create_job(self, job_type:str) -> int:
        
        with self.connect() as conn:
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO job (job_type_id)
                SELECT id
                FROM job_type
                WHERE name = %s
                RETURNING id
            ''', (job_type,))
            conn.commit()
            return cur.fetchone()[0]


    def get_player_id(self, xuid:str) -> int:

        xuid = util.unwrap_xuid(xuid)
        with self.connect() as conn:
            cur = conn.cursor()
            cur.execute('''
                SELECT id
                FROM player
                WHERE xuid = %s
            ''', (xuid,))
            row = cur.fetchone()
            if row is not None:
                return row[0]


    def create_player(self, xuid:str) -> int:

        xuid = util.unwrap_xuid(xuid)
        with self.connect() as conn:
            cur = conn.cursor()
            cur.execute('''
                DROP TABLE IF EXISTS tmp;
                CREATE TEMP TABLE tmp (xuid text);
                INSERT INTO tmp (xuid) VALUES (%s);

                INSERT INTO player (xuid)
                SELECT xuid
                FROM tmp
                WHERE NOT EXISTS (SELECT 1 FROM player WHERE xuid = tmp.xuid)
                RETURNING id;
            ''', (xuid,))
            conn.commit()
            row = cur.fetchone()
            if row is not None:
                return row[0]


    def create_job_player(self, job_id:int, player_id:int) -> None:

        with self.connect() as conn:
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO job_player (job_id, player_id)
                VALUES (%s, %s)
            ''', (job_id, player_id))
            conn.commit()


    def complete_job(self, job_id:int, duration:float) -> None:

        with self.connect() as conn:
            cur = conn.cursor()
            cur.execute('''
                UPDATE job
                SET is_valid = true, duration = %s
                WHERE id = %s
            ''', (duration, job_id))
            conn.commit()


    def get_player_job_summary(self, player_id:int) -> tuple: # namedtuple

        with self.connect() as conn:
            cur = conn.cursor(cursor_factory=NamedTupleCursor)
            cur.execute('''
                SELECT
                    p.id,
                    p.xuid,
                    p.gamertag,
                    count(jm.match_id) AS match_count,
                    max(m.started_at) AS last_match_at
                FROM player p
                LEFT JOIN job_player jp ON jp.player_id = p.id
                LEFT JOIN job j ON jp.job_id = j.id AND j.is_valid
                LEFT JOIN job_match jm ON jm.job_id = j.id
                LEFT JOIN match m ON m.id = jm.match_id
                WHERE p.id = %s
                GROUP BY p.id
            ''', (player_id,))
            return cur.fetchone()

    def create_matches(self, matches:list[dict]) -> list[int]:

        template = '''(
            %(guid)s,
            %(started_at)s,
            %(completed_at)s,
            %(duration)s,
            %(map_asset_id)s,
            %(map_version_id)s,
            %(map_level_id)s,
            %(game_variant_asset_id)s,
            %(game_variant_version_id)s,
            %(game_variant_category)s,
            %(playlist_asset_id)s,
            %(playlist_version_id)s,
            %(lifecycle_mode_id)s,
            %(experience_id)s,
            %(season_id)s,
            %(playable_duration)s
        )'''
        rows = self.execute_values_with_file('create_matches.sql', matches, template, fetch=True)
        return [r[0] for r in rows]


    def create_job_matches(self, job_id:int, match_ids:list[int]) -> None:

        values = [{'job_id': job_id, 'match_id': mid} for mid in match_ids]
        sql = '''
            INSERT INTO job_match (job_id, match_id)
            VALUES %s
        '''
        template = '(%(job_id)s, %(match_id)s)'
        self.execute_values_with_str(sql, values, template)


    def get_playlist_versions(self) -> list[tuple]: # namedtuple

        with self.connect() as conn:
            cur = conn.cursor(cursor_factory=NamedTupleCursor)
            cur.execute('''
                SELECT
                    pv.id,
                    pv.playlist_id,
                    pv.version_id,
                    p.asset_id,
                    p.name,
                    p.is_ranked,
                    p.is_controller,
                    p.is_mnk,
                    p.max_fireteam_size
                FROM playlist_version pv
                JOIN playlist p ON p.id = pv.playlist_id
            ''')
            return cur.fetchall()


    def get_map_versions(self) -> list[tuple]: # namedtuple

        with self.connect() as conn:
            cur = conn.cursor(cursor_factory=NamedTupleCursor)
            cur.execute('''
                SELECT
                    mv.id,
                    mv.map_id,
                    mv.version_id,
                    m.asset_id,
                    m.level_id,
                    m.name
                FROM map_version mv
                JOIN map m ON m.id = mv.map_id
            ''')
            return cur.fetchall()


    def get_mode_versions(self) -> list[tuple]: # namedtuple

        with self.connect() as conn:
            cur = conn.cursor(cursor_factory=NamedTupleCursor)
            cur.execute('''
                SELECT
                    mv.id,
                    mv.mode_id,
                    mv.version_id,
                    m.asset_id,
                    m.category_id,
                    m.context,
                    m.name
                FROM mode_version mv
                JOIN mode m ON m.id = mv.mode_id
            ''')
            return cur.fetchall()

        
    def get_player_xuids_missing_gamertag(self) -> list[str]:

        with self.connect() as conn:
            cur = conn.cursor()
            cur.execute('''
                SELECT xuid
                FROM player
                WHERE gamertag IS NULL
            ''')
            return [r[0] for r in cur.fetchall()]


    def update_playlists(self, playlists:list[dict]) -> None:

        # multiple records can exist for each asset_id
        # is it worth filtering? won't change result
        with self.connect() as conn:
            cur = conn.cursor()
            cur.executemany('''
                UPDATE playlist
                SET
                    name = %(name)s,
                    is_ranked = %(is_ranked)s,
                    is_controller = %(is_controller)s,
                    is_mnk = %(is_mnk)s,
                    max_fireteam_size = %(max_fireteam_size)s
                WHERE asset_id = %(asset_id)s
            ''', playlists)
            conn.commit()


    def update_maps(self, maps:list[dict]) -> None:

        # multiple records can exist for each asset_id
        # is it worth filtering? won't change result
        with self.connect() as conn:
            cur = conn.cursor()
            cur.executemany('''
                UPDATE map
                SET name = %(name)s
                WHERE asset_id = %(asset_id)s
            ''', maps)
            conn.commit()


    def update_modes(self, modes:list[dict]) -> None:

        # multiple records can exist for each asset_id
        # is it worth filtering? won't change result
        with self.connect() as conn:
            cur = conn.cursor()
            cur.executemany('''
                UPDATE mode
                SET context = %(context)s, name = %(name)s
                WHERE asset_id = %(asset_id)s
            ''', modes)
            conn.commit()


    def update_players(self, profiles:list[dict]) -> None:

        map(lambda p: p.update({'xuid': util.unwrap_xuid(p['xuid'])}), profiles)

        with self.connect() as conn:
            cur = conn.cursor()
            cur.executemany('''
                UPDATE player
                SET gamertag = %(gamertag)s
                WHERE xuid = %(id)s
            ''', profiles)
            conn.commit()


    def get_next_player_in_queue(self) -> tuple: # namedtuple

        with self.connect() as conn:
            cur = conn.cursor(cursor_factory=NamedTupleCursor)
            cur.execute('''
                SELECT p.id, max(j.created_at) AS last_job_at
                FROM player p
                LEFT JOIN job_player jp ON jp.player_id = p.id
                LEFT JOIN job j ON j.id = jp.job_id
                LEFT JOIN job_match jm ON j.id = jm.job_id
                WHERE j.is_valid
                GROUP BY p.id
                ORDER BY 2 ASC NULLS FIRST -- make it explicit that we are getting unprocessed players first, then the oldest valid job for the player
                LIMIT 1 -- only need to return one player per call
            ''')
            return cur.fetchone()
        
