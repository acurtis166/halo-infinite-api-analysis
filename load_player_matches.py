from haloinfinite import auth, api, db, job


if __name__ == '__main__':

    auth_mgr = auth.AuthManager()
    # auth_mgr.generate_new_spartan_token()

    hapi = api.ApiService(auth_mgr)
    hapi.verify_or_refresh_tokens()

    pgdb = db.Database(db.TEST_DB)
    pgdb.init()

    pid = pgdb.create_player('xuid(2535445291321133)')

    mj = job.MatchJob(pid, hapi, pgdb)

    mj.run()