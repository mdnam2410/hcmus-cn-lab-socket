Bulk download weather information from http://bulk.openweathermap.org/sample/

Weather condition code: https://openweathermap.org/weather-conditions
* Thunderstorm: 200
* Drizzle: 300
* Rain: 500
* Snow: 600
* Atmosphere: 7xx
    * Mist: 701
    * Smoke: 711
    * Haze: 721
    * Dust: 731
    * Fog: 741
    * Sand: 751
    * Dust: 761
    * Ash: 762
    * Squall: 771
    * Tornado: 781
* Clear: 800
* Clouds: 801

Database schemas to consider:
user(username, password, name)
country(country_code, country_name)
city(city_id, city_name, country_code, lat, lon)
favorite_city(username, city_id)
weather_type(weather_id, description, weather_icon)
city_weather(city_id, date, weather_id, min_degree, max_degree, precipitation)

Resources:
* resources/country_code.csv: https://datahub.io/core/country-list#resource-data
* resources/country_list.json: http://bulk.openweathermap.org/sample/