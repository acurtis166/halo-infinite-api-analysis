
from haloinfinite.api import AutocodeHaloAPI


def get_match_summary(gamertag:str) -> dict:

    api = AutocodeHaloAPI()
    match_batches = api.get_matches(gamertag, 2)
    m = next(match_batches)[1]
    print(m)


def get_match_details(match_guid:str) -> dict:

    api = AutocodeHaloAPI()
    gen = api.get_match_details([match_guid])
    return next(gen)


if __name__ == '__main__':

    match_guid = '60893ed9-7144-42e0-8831-ce854ba975ae'
    for mt, mp, mpm in get_match_details(match_guid):
        # print(mt)
        print(mp)
        # print(mpm)