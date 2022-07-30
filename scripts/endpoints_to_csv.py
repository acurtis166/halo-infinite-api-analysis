import json
import pandas as pd


if __name__ == '__main__':

    with open('resources/endpoints.json') as f:
        js = json.load(f)

    authorities = {k: v['Hostname'] for k, v in js['Authorities'].items()}

    endpoints = []
    for k, v in js['Endpoints'].items():
        v['name'] = k
        endpoints.append(v)
    df = pd.DataFrame(endpoints)

    df['host'] = df.AuthorityId.apply(lambda aid: authorities[aid])
    df['url'] = 'https://' + df.host + df.Path

    out_cols = ['name', 'AuthorityId', 'url', 'ClearanceAware']
    df[out_cols].to_csv('endpoints.csv', index=False)
