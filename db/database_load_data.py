import csv
import json
import sqlite3

# Load country data
countries = []
with open("../resources/country_code.csv", "r") as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=",")
    next(csv_reader) # Skip header

    for row in csv_reader:
        # Example: Iran, Islamic Republic of -> country_name = Iran
        country_name = row[0].split(',', 1)[0]
        countries.append((country_name, row[1]))

# Load city data
json_file = json.loads(open("../resources/city_list.json", "r").read())
cities = []
for obj in json_file:
    city = (obj["id"], obj["name"], obj["country"], obj["coord"]["lat"], obj["coord"]["lon"])
    cities.append(city)
# print(cities)

con = sqlite3.connect("wether.db")
cur = con.cursor()

country_script = """
INSERT INTO country(country_name, country_code) VALUES (?, ?);
"""
cur.executemany(country_script, countries)

city_script = """
INSERT INTO city(city_id, city_name, country_code, lat, lon) VALUES (?, ?, ?, ?, ?);
"""
cur.executemany(city_script, cities)
con.commit()
con.close()
