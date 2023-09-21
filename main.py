import uvicorn
from fastapi import FastAPI
import pyproj
import requests
import csv


def address_coordinates(q):
    url = 'https://api-adresse.data.gouv.fr/search/?' + 'q=' + q.replace(' ', '+')
    res = requests.get(url)
    features_list = res.json()['features']
    return features_list[1]['geometry']['coordinates']


def lamber93_to_gps(x, y):
    lambert = pyproj.Proj(
        '+proj=lcc +lat_1=49 +lat_2=44 +lat_0=46.5 +lon_0=3 +x_0=700000 +y_0=6600000 +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs')
    wgs84 = pyproj.Proj('+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs')
    long, lat = pyproj.transform(lambert, wgs84, x, y)
    return long, lat


def search_coverage(x_lamb, y_lamb):
    switcher_operator = {
        '20801': 'Orange',
        '20810': 'SFR',
        '20815': 'Free',
        '20820': 'Bouygue'
    }

    check_truefalse = lambda x: x == '1'

    with open('2018_01_Sites_mobiles_2G_3G_4G_France_metropolitaine_L93.csv') as file:
        csv_reader = csv.reader(file, delimiter=';')
        next(csv_reader)
        net_cover_dict = dict()
        for row in csv_reader:
            operateur_num, xx, yy, cober2G, cober3G, cober4G = row
            if xx == x_lamb:  # and yy == y_lamb:
                print(switcher_operator.get(operateur_num, "Not found"), xx, yy, cober2G, cober3G, cober4G)
                net_cover_G = dict()
                net_cover_G['2G'] = check_truefalse(cober2G)
                net_cover_G['3G'] = check_truefalse(cober3G)
                net_cover_G['4G'] = check_truefalse(cober4G)
                net_cover_dict[switcher_operator.get(operateur_num, "Not found")] = net_cover_G

    return net_cover_dict


app = FastAPI()


@app.get("/")
async def read_root():
    return {"result": "API Running!"}


@app.get("/netcover_api")
def net_cover(q=None):
    if q is None:
        answer = "No textual address!"
    else:
        [x, y] = address_coordinates(q)
        print('address_coordinates(q)', x, y)

        [x_lamb, y_lamb] = lamber93_to_gps(x, y)
        print('lamber93_to_gps(x, y)', x_lamb, y_lamb)

        x_lamb = '135264'
        y_lamb = '6852783'
        answer = search_coverage(x_lamb, y_lamb)

    return answer


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
