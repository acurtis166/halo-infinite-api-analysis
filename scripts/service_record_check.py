from cmath import exp
from haloinfinite import api, response_process as rp


if __name__ == '__main__':
    hapi = api.AutocodeHaloAPI()
    expected = 0
    actual = 0
    ids = [
        ('Entrenched', '3facc347-6e49-40c9-b9e7-503d26092eed', 10),
        ('Tactical Slayer', '7f2b4f8f-c2f3-4ad4-a250-b55214fa4111', 6),
        ('Last Spartan Standing', '0299adc1-f07a-4b6c-8126-0c35ac2fa08d', 4),
        ('Tactical Slayer', '70bb9184-e674-4307-8846-239ab4a30cb6', 2),
        ('Cyber Showdown - Attrition', '0c47c724-3625-4243-a3fd-29b66a2aea6d', 2),
        ('Team Snipers', '325c18a5-d85b-4ba6-b98f-21465d9c19e2', 20),
        ('Land Grab', '14352c39-a409-4d34-9ded-1c280bb4f868', 5),
        ('Fracture: Tenrai - Fiesta', '4af0b113-8696-4f22-9e09-596d473de933', 23),
        ('FFA Slayer', 'f6c93ddd-a623-41b1-b9e3-81632ff73cfb', 9),
        ('Team Slayer', 'aa41f6a9-51be-4f25-a53f-48192ce14de7', 41),
        ('Quick Play', 'bdceefb3-1c52-4848-a6b7-d49acd13109d', 436),
        ('Big Team Battle', 'dc4929de-216c-43bc-b207-1702253f4576', 38),
        ('Rumble Pit', '7d9828c7-8184-4421-ad14-824fce8f7ebe', 3),
        ('Ranked Arena', 'f7f30787-f607-436b-bdec-44c65bc2ecef', 12),
        ('Fiesta', '4829f027-a9af-4b2f-86dd-7b290d6bb0a4', 38),
        ('Bot Bootcamp', 'a446725e-b281-414c-a21e-31b8700e95a1', 16),
        ('Ranked Arena', 'edfef3ac-9cbe-4fa2-b949-8f29deafd483', 77)
    ]
    for name, id, ct in ids:
        data = hapi.get_service_record('aCurtis X89', playlist_id=id)
        sr = rp.flatten_service_record(data)
        expected += ct
        actual += sr['total_matches']
        print(name, id, ct, sr['total_matches'])

    print('expected', expected)
    print('actual', actual)