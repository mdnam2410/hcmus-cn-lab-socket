
-- User and admin information
-- Admin's username contains all numbers
CREATE TABLE IF NOT EXISTS user (
    username TEXT PRIMARY KEY,
    password TEXT,
    name     TEXT
);

-- Country code using Alpha-2 format from ISO 3166-1
CREATE TABLE IF NOT EXISTS country (
    country_code TEXT PRIMARY KEY,
    country_name TEXT
);

-- City information
CREATE TABLE IF NOT EXISTS city (
    city_id      INTEGER PRIMARY KEY,
    city_name    TEXT,
    country_code TEXT,
    lat          REAL, -- Latitude
    lon          REAL, -- Longitude

    FOREIGN KEY(country_code) REFERENCES country(country_code)
);

-- User's favorite city (admin does not have this feature)
CREATE TABLE IF NOT EXISTS favorite_city (
    username TEXT,
    city_id  INTEGER,

    PRIMARY KEY(username, city_id),
    FOREIGN KEY(username) REFERENCES user(username),
    FOREIGN KEY(city_id) REFERENCES city(city_id)
);

CREATE TABLE IF NOT EXISTS weather_condition (
    weather_id  TEXT PRIMARY KEY,
    main        TEXT,
    description TEXT,
    icon        TEXT
);

CREATE TABLE IF NOT EXISTS city_weather (
    city_id       INTEGER,
    report_date   TEXT,
    weather_id    TEXT,
    min_degree    REAL,
    max_degree    REAL,
    precipitation REAL,

    PRIMARY KEY(city_id, report_date, weather_id),
    FOREIGN KEY(city_id) REFERENCES city(city_id),
    FOREIGN KEY(weather_id) REFERENCES weather_info(weather_id)
);
