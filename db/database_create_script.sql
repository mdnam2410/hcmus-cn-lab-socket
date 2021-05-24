
-- User and admin information
CREATE TABLE user (
    username TEXT PRIMARY KEY,
    password TEXT NOT NULL,
    name     TEXT NOT NULL
);

-- Country code using Alpha-2 format from ISO 3166-1
CREATE TABLE country (
    country_code TEXT PRIMARY KEY,
    country_name TEXT NOT NULL
);

-- City information
CREATE TABLE city (
    city_id      INTEGER PRIMARY KEY,
    city_name    TEXT NOT NULL,
    country_code TEXT NOT NULL,
    lat          REAL, -- Latitude
    lon          REAL, -- Longitude

    FOREIGN KEY(country_code) REFERENCES country(country_code) ON DELETE CASCADE
);

CREATE TABLE weather_condition (
    weather_id  INTEGER PRIMARY KEY,
    main        TEXT NOT NULL,
    description TEXT,
    icon        TEXT
);

CREATE TABLE city_weather (
    city_id       INTEGER,
    report_date   TEXT,
    weather_id    TEXT,
    min_degree    REAL CHECK(min_degree > -273.15),
    max_degree    REAL CHECK(max_degree > -273.15 AND max_degree >= min_degree),
    precipitation REAL CHECK(precipitation BETWEEN 0 AND 1),

    PRIMARY KEY(city_id, report_date),
    FOREIGN KEY(city_id) REFERENCES city(city_id) ON DELETE CASCADE,
    FOREIGN KEY(weather_id) REFERENCES weather_condition(weather_id) ON DELETE SET NULL
);
