from flask import Flask, Response
import json


app = Flask(__name__)
app.json.sort_keys = False


# Создание словаря для красивой подачи информации
def beautiful_view(any_list):
    id_keys = ["geonameid", "name", "asciiname", "alternatenames", "latitude", "longitude", "feature class",
               "feature code", "country code", "cc2", "admin1 code", "admin2 code", "admin3 code", "admin4 code",
               "population", "elevation", "dem", "timezone", "modification date"]
    dict_back = {}
    for key, value in zip(id_keys, any_list):
        dict_back[key] = value
    return dict_back


city_list = []
with open(r'RU.txt', 'r', encoding='utf-8') as file:
    for line in file:
        line = line.rstrip().split('\t')
        if 'PPL' in line[7]:
            city_list.append(line)


@app.route("/api/cities/<int:geonameid>", methods=['GET'])
def get_info_by_id(geonameid):
    for city_info in city_list:
        if int(city_info[0]) == geonameid:
            city_info = json.dumps(beautiful_view(city_info), ensure_ascii=False, indent=4)
            return Response(city_info, content_type="application/json; charset=utf-8")


@app.route("/api/cities/page=<int:num_page>&count=<int:count_cities>", methods=['GET'])
def get_info_for_page(num_page, count_cities):
    page = []
    for i in range(count_cities * (num_page - 1), count_cities * num_page):
        page.append(beautiful_view(city_list[i]))
    page = json.dumps(page, ensure_ascii=False, indent=4)
    return Response(page, content_type="application/json; charset=utf-8")


@app.route("/api/cities/<city_1>&<city_2>", methods=['GET'])
def get_two_cities(city_1, city_2):
    info_cities = []
    for city in (city_1, city_2):
        cities = []
        for element in city_list:
            if city.lower() in element[3].lower():
                cities.append(beautiful_view(element))
        cities = sorted(cities, key=lambda x: int(x['population']), reverse=True)
        info_cities.append(cities[0])

    # Определение ближестоящего к северу города
    northern = [int(x['latitude'].split('.')[0]) for x in info_cities]
    northern = northern.index(max(northern))

    # Определение часового пояса и их разность
    difference = [x['timezone'] for x in info_cities]
    if difference[0] == difference[1]:
        difference = 0
    else:
        timezones = {"Asia/Anadyr": 12, "Asia/Barnaul": 7, "Asia/Chita": 9, "Asia/Irkutsk": 8, "Asia/Kamchatka": 12,
                     "Asia/Khandyga": 9, "Asia/Krasnoyarsk": 7, "Asia/Magadan": 11, "Asia/Novokuznetsk": 7,
                     "Asia/Novosibirsk": 7, "Asia/Omsk": 6, "Asia/Sakhalin": 11, "Asia/Srednekolymsk": 11,
                     "Asia/Tomsk": 7, "Asia/Ust-Nera": 10, "Asia/Vladivostok": 10, "Asia/Yakutsk": 9,
                     "Asia/Yekaterinburg": 5, "Europe/Astrakhan": 4, "Europe/Kaliningrad": 2, "Europe/Kirov": 3,
                     "Europe/Moscow": 3, "Europe/Samara": 4, "Europe/Saratov": 4, "Europe/Ulyanovsk": 4,
                     "Europe/Volgograd": 3}
        difference = [timezones[x] for x in difference]
        difference = abs(difference[0] - difference[1])

    info_cities.append({'Northern': info_cities[northern]["asciiname"], 'Time Difference': difference})
    info_cities = json.dumps(info_cities, ensure_ascii=False, indent=4)
    return Response(info_cities, content_type="application/json; charset=utf-8")


@app.route("/api/cities/<letters>", methods=['GET'])
def get_city_by_some_letters(letters):
    cities = {}
    letters = letters.lower()
    length = len(letters)
    for element in city_list:
        if letters in element[2][:length].lower():
            if element[1] not in cities.values():
                cities[len(cities) + 1] = element[1]
            else:
                continue
    cities = json.dumps(cities, ensure_ascii=False, indent=4)
    return Response(cities, content_type="application/json; charset=utf-8")


if __name__ == "__main__":
    app.run(debug=True, port=8000, host="127.0.0.1")
