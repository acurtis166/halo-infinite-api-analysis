import math, time, multiprocessing as mp
from tracemalloc import start

from haloinfinite import api, db, flatten as flat, util


class Job:

    MATCH_JOB_TYPE = 'match'
    METADATA_JOB_TYPE = 'metadata'

    def __init__(self, halo_api:api.ApiService, pgdb:db.Database):

        self.halo_api = halo_api
        self.db = pgdb

        self.duration = None # seconds
        self.job_type = None


    def create(self):

        if self.job_type is None:
            print('Cannot create a job without a job type specified.')
            exit(1)

        self.id = self.db.create_job(self.job_type)

        print('Created job id', self.id)


    def complete(self):

        if self.duration is None:
            print('Cannot complete a job without a duration.')
            exit(1)
            
        self.db.complete_job(self.id, self.duration)
        
        print('Completed job id', self.id)


class MatchJob(Job):
    def __init__(self, player_id:int, halo_api:api.ApiService, pgdb:db.Database=db.Database(db.PROD_DB)):

        super().__init__(halo_api, pgdb)

        print('Preparing job for player id', player_id)

        self.job_type = self.MATCH_JOB_TYPE
        self.player_id = player_id
        self.matches = []
        self.new_match_ids = []
        self.matches_retrieved = 0
        self.matches_inserted = 0
        self.player_xuid = None
        self.player_gamertag = None
        self.history_match_count = None
        self.history_last_match_at = None
        self._load_history()


    def _load_history(self):

        print('Loading historical job data')

        history = self.db.get_player_job_summary(self.player_id)
        self.player_xuid = history.xuid
        self.player_gamertag = history.gamertag
        self.history_match_count = history.match_count
        self.history_last_match_at = history.last_match_at

        print(self.history_match_count, 'matches have been previously retrieved for', self.player_gamertag or self.player_xuid)

        if self.history_last_match_at is not None:
            print('Last valid match date was', self.history_last_match_at, '(UTC)')


    def _get_total_player_match_count(self) -> int:
        """This will not include matches that were left, but those matches WILL be returned when getting match data?
        So this count is lower than what will actually be returned."""

        jdata = self.halo_api.get_player_match_count(self.player_xuid)
        # this is combined matchmade, custom, and local games, individual counts are also available
        return jdata['MatchesPlayedCount']


    def _get_expected_matches(self):

        print('Getting total matches played from the API')

        # get the total number of matches played by the player
        total_matches = self._get_total_player_match_count()

        print('At least', total_matches, 'matches played')

        # subtract the retrieved count from the total count to determine how many new matches might be collected
        expected_matches = total_matches - self.history_match_count

        print(f'Expecting about {expected_matches} new matches.')
        return expected_matches


    def _get_match_batch(self, start:int):

        jdata = self.halo_api.get_player_matches(self.player_xuid, start)
        return flat.flatten_matches(jdata)


    def _is_complete(self, match_batch:list[dict]):

        # the batch returned was less than the max count or we have passed the last valid stopping point
        return (len(match_batch) < self.halo_api.PLAYER_MATCHES_BATCH_SIZE or 
            (self.history_last_match_at and match_batch[-1]['started_at'] < self.history_last_match_at))


    def _create_matches(self, matches:list[dict]) -> None:

        new_match_ids = self.db.create_matches(matches)
        self.db.create_job_matches(self.id, new_match_ids)
        self.matches_inserted += len(new_match_ids)


    def run(self):

        # start timing
        started_at = time.time()

        # create the job
        self.create()

        # attach the player to the job
        self.db.create_job_player(self.id, self.player_id)

        # get the number of matches expected for the player
        expected_matches = self._get_expected_matches()

        cpu_count = util.get_available_cpu_count()
        
        # start a multiprocessing pool and distribute data loading processes
        offset = 0
        complete = False
        with mp.Pool(cpu_count) as pool:
            while not complete:
                results = []
                # use the service record to determine the initial number of batches, then use
                # the number of available processors to grab additional matches if the service record
                # match count is inaccurate
                num_batches = math.ceil(expected_matches / self.halo_api.PLAYER_MATCHES_BATCH_SIZE) if offset == 0 else cpu_count
                for _ in range(num_batches):
                    # queue a match request and increment the offset
                    results.append(pool.apply_async(self._get_match_batch, (offset,)))
                    offset += self.halo_api.PLAYER_MATCHES_BATCH_SIZE

                # process results as they are available
                for r in results:
                    matches = r.get()
                    self.matches_retrieved += len(matches)
                    self._create_matches(matches)
                    print(f'{self.matches_retrieved} matches retrieved, {self.matches_inserted} matches inserted...', end='\r')
                    if self._is_complete(matches):
                        # set the completion flag here so the remaining workers can finish
                        complete = True

        self.duration = time.time() - started_at

        print(f'Retrieved {self.matches_retrieved} matches in {self.duration:.1f} seconds ({(self.matches_retrieved / self.duration):.1f} matches/second)')
        print(f'Inserted {self.matches_inserted} matches into the database ({(100 * self.matches_inserted / self.matches_retrieved):.1f}% of retrieved)')

        self.complete()


class MetadataJob(Job):
    def __init__(self, halo_api:api.ApiService, pgdb:db.Database=db.Database(db.PROD_DB)):

        super().__init__(halo_api, pgdb)

        self.job_type = self.METADATA_JOB_TYPE


    def _load_map(self, asset_id:str, version_id:str) -> dict:

        jdata = self.halo_api.get_map(asset_id, version_id)
        return flat.flatten_map(jdata)


    def _load_maps(self, pool):

        # get map args and filter out items that already have names
        maps = self.db.get_map_versions()
        ids = [(m.asset_id, m.version_id) for m in maps if m.name is None]
        results = pool.starmap_async(self._load_map, ids).get()
        self._validate_maps(results)
        self.db.update_maps(results)
        print(f'Updated maps.')


    def _validate_maps(self, maps:list[dict]) -> None:

        # need to make sure that all map_versions with the same asset_id/level_id have the same name
        valid = True
        assets = {}

        for m in maps:
            if m['asset_id'] not in assets:
                assets[m['asset_id']] = {'names': [], 'versions': []}
            assets[m['asset_id']]['names'].append(m['name'])
            assets[m['asset_id']]['versions'].append(m['version_id'])

        for aid, val in assets.items():
            if len(set(val['names'])) > 1:
                # TODO make a custom exception?
                print('-----------------')
                print('VALIDATION ERROR')
                print('-----------------')
                print('Multiple names found for map asset id', aid)
                print('The names found were', val['names'])
                print('The respective versions were', val['versions'])
                valid = False

        if not valid:
            exit(1)


    def _load_mode(self, asset_id:str, version_id:str):

        jdata = self.halo_api.get_gamevariant(asset_id, version_id)
        return flat.flatten_game_variant(jdata)


    def _load_modes(self, pool):

        # get game_variant args and filter out items that already have names
        mvs = self.db.get_mode_versions()
        ids = [(mv.asset_id, mv.version_id) for mv in mvs if mv.name is None]
        results = pool.starmap_async(self._load_mode, ids).get()
        self._validate_modes(results)
        self.db.update_modes(results)
        print(f'Updated modes.')


    def _validate_modes(self, modes:list[dict]):

        # need to make sure that all map_versions with the same asset_id/level_id have the same name
        valid = True
        assets = {}

        for m in modes:
            if m['asset_id'] not in assets:
                assets[m['asset_id']] = {'names': [], 'contexts': [], 'versions': []}
            assets[m['asset_id']]['names'].append(m['name'])
            assets[m['asset_id']]['contexts'].append(m['context'])
            assets[m['asset_id']]['versions'].append(m['version_id'])

        for aid, val in assets.items():
            if len(set(val['names'])) > 1 or len(set(val['contexts'])) > 1:
                # TODO make a custom exception?
                print('-----------------')
                print('VALIDATION ERROR')
                print('-----------------')
                print('Multiple names and/or contexts found for mode asset id', aid)
                print('The names found were', val['names'])
                print('The contexts found were', val['contexts'])
                print('The respective versions were', val['versions'])
                valid = False

        if not valid:
            exit(1)


    def _load_playlist(self, asset_id:str, version_id:str) -> dict:

        jdata = self.halo_api.get_playlist(asset_id, version_id)
        return flat.flatten_playlist(jdata)


    def _load_playlists(self, pool):

        # get playlist args and filter out items that already have names
        pvs = self.db.get_playlist_versions()
        ids = [(pv.asset_id, pv.version_id) for pv in pvs if pv.name is None]
        results = pool.starmap_async(self._load_playlist, ids).get()
        self._validate_playlists(results)
        self.db.update_playlists(results)
        print(f'Updated playlists.')


    def _validate_playlists(self, playlists:list[dict]):

        # need to make sure that all map_versions with the same asset_id/level_id have the same name
        valid = True
        assets = {}

        for p in playlists:
            if p['asset_id'] not in assets:
                assets[p['asset_id']] = {'names': [], 'versions': []}
            assets[p['asset_id']]['names'].append(p['name'])
            assets[p['asset_id']]['versions'].append(p['version_id'])

        for aid, val in assets.items():
            if len(set(val['names'])) > 1:
                # TODO make a custom exception?
                print('-----------------')
                print('VALIDATION ERROR')
                print('-----------------')
                print('Multiple names found for playlist asset id', aid)
                print('The names found were', val['names'])
                print('The respective versions were', val['versions'])
                valid = False

        if not valid:
            exit(1)


    def _load_gamertag_batch(self, xuids:list[str]) -> int:

        jdata = self.halo_api.get_profiles(xuids)
        profiles = flat.flatten_profiles(jdata)
        self.db.update_players(profiles)
        return profiles


    def _load_gamertags(self, pool):

        batch_size = 100
        xuids = self.db.get_player_xuids_missing_gamertag()
        batched = [b for b in util.batch(xuids, batch_size)]
        pool.map_async(self._load_gamertag_batch, batched).get()
        print('Updated players')


    def run(self) -> None:

        # create job
        self.create()

        # start timer
        started_at = time.time()

        # create mp pool
        with mp.Pool(util.get_available_cpu_count()) as pool:
            self._load_maps(pool)
            self._load_modes(pool)
            self._load_playlists(pool)
            self._load_gamertags(pool)

        # stop timer
        self.duration = time.time() - started_at

        # complete
        self.complete()


class MatchDetailsJob:
    def __init__(self, pgdb:db.Database):

        self.db = pgdb

        # self.id = pgdb.insert_match_details_job()

