from requests import get


def get_coordinates(object_name):
    params = {
        "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
        "geocode": object_name,
        "lang": "ru_RU",
        "format": "json"
    }
    response = get("http://geocode-maps.yandex.ru/1.x/", params=params)
    if not response:
        return None
    js = response.json()
    try:
        coords = js["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["Point"]["pos"].split()
        # bbox = '~'.join(list(map(lambda x: ','.join(x.split()), js["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]['boundedBy']["Envelope"].values())))
        return coords
    except Exception:
        return None
    return None


def write_img(idd, ll, mode='sat'):
    map_params = {
        "ll": ",".join(map(str, ll)),
        "l": mode,
        "spn": "0.03,0.03"
    }
    map_api_server = "http://static-maps.yandex.ru/1.x/"
    response = get(map_api_server, params=map_params)
    if not response:
        pass
    with open(f"static/img/{idd}.png", 'wb') as f:
        f.write(response.content)
