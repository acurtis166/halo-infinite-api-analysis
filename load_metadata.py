import json
from haloinfinite import auth, api, db, job


if __name__ == '__main__':

    auth_mgr = auth.AuthManager()
    # auth_mgr.generate_new_spartan_token()

    hapi = api.ApiService(auth_mgr)
    hapi.verify_or_refresh_tokens()

    pgdb = db.Database(db.TEST_DB)
    # pgdb.init()

    mdj = job.MetadataJob(hapi, pgdb)

    mdj.run()
