import datetime
import sqlite3
import time

class DatabaseConnectionError(Exception):
    pass

class Database:
    """Class that provides encapsulation for basic queries needed for the app"""

    def __init__(self, database_path):
        self.today = datetime.date.today()
        self.con = None
        try:
            self.con = sqlite3.connect(database_path)
            self.con.row_factory = sqlite3.Row
            self.cur = self.con.cursor()
            self.cur.execute('PRAGMA foreign_keys = 1')
        except sqlite3.Error:
            raise DatabaseConnectionError(f'Cannot connect to {database_path}')
    
    def __del__(self):
        self.con.close()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        if type is None:
            self.con.commit()
        else:
            self.con.rollback()

    def execute_query(self, query):
        self.cur.execute(query)
        return self.cur.fetchall()

    def commit(self):
        self.con.commit()

    # User and admin methods

    def authenticate(self, username, password):
        """Authenticate a user with given username and password
        
        Parameters
        ----------
        username : str
        password : str

        Returns
        -------
        list
            A list of (username, name) (maximum one element).

        """

        query = """
        SELECT user.username, user.name
        FROM user
        WHERE user.username = ? AND user.password = ?;
        """
        self.cur.execute(query, (username, password))
        return self.cur.fetchall()

    def sign_up(self, username, password, name) -> bool:
        """Register a user

        Parameters
        ----------
        username : str
        password : str
        name : str

        Returns
        -------
        bool
            True if successful, False otherwise.
        """

        # Check if username already existed
        self.cur.execute("SELECT username FROM user WHERE username = ?", (username,))
        r = self.cur.fetchall()
        if len(r) != 0:
            return False
        else:
            query = """
            INSERT INTO user VALUES (?, ?, ?);
            """
            self.cur.execute(query, (username, password, name))
            self.con.commit()
            return True

    # Weather query methods

    def weather_by_date(self, date: str):
        """Retrieve weather condition of all cities in a given date

        Parameters
        ----------
        date : str
            In ISO 8601 format (YYYY-MM-DD).

        Returns
        -------
        list
            A list of (city_id, city_name, country_name, report_date, main, min_degree, max_degree, precipitaion).
        """

        query = """
        SELECT c.city_id, c.city_name, ct.country_name, cw.report_date, 
               wc.main, cw.min_degree, cw.max_degree, cw.precipitation
        FROM   city_weather AS cw JOIN city AS c
               ON cw.city_id = c.city_id
               JOIN weather_condition AS wc
               ON cw.weather_id = wc.weather_id
               JOIN country AS ct
               ON c.country_code = ct.country_code
        WHERE  cw.report_date = ?;
        """
        self.cur.execute(query, (date,))
        return self.cur.fetchall()

    def today_weather(self):
        """Retrieve today weather information of all cities

        Returns
        -------
        list
            A list of (city_id, city_name, country_name, report_date, main, min_degree, max_degree, precipitaion).
        """

        return self.weather_by_date(self.today.isoformat())

    def weather_by_date_range(self, city_id, start, end):
        """Retrieve weather information of a city in a date range [start, end]

        Parameters
        ----------
        city_id : int
            ID of the city to query.
        start : str
            Start date, in ISO 8601 format (YYYY-MM-DD).
        end : str
            End date, in ISO 8601 format (YYYY-MM-DD), required that start <= end

        Returns
        -------
        list
            A list of (city_id, city_name, country_name, report_date, main, min_degree, max_degree, precipitaion).
        None
            Returns if start > date
        """

        query = """
        SELECT c.city_id, c.city_name, ct.country_name, cw.report_date, 
               wc.main, cw.min_degree, cw.max_degree, cw.precipitation
        FROM   city_weather AS cw JOIN city AS c
               ON cw.city_id = c.city_id
               JOIN weather_condition AS wc
               ON cw.weather_id = wc.weather_id
               JOIN country AS ct
               ON c.country_code = ct.country_code
        WHERE  c.city_id = ? AND cw.report_date BETWEEN ? AND ?;"""

        s = datetime.date.fromisoformat(start)
        e = datetime.date.fromisoformat(end)
        if s <= e:
            self.cur.execute(query, (city_id, start, end))
            return self.cur.fetchall()
        else:
            return None

    def forecast(self, city_id):
        """Retrieve 7-day weather forecast information for a given city
        
        Parameters
        ----------
        city_id : int

        Returns
        -------
        list
            A list of (city_id, city_name, country_name, report_date, main, min_degree, max_degree, precipitaion),
            sorted by report_date
        """

        return self.weather_by_date_range(
            city_id,
            start=self.today.isoformat(),
            end=(self.today + datetime.timedelta(days=6)).isoformat()
        )

    # Searching

    def search_city(self, name):
        """Search city by name
        
        Parameters
        ----------
        name : str

        Returns
        -------
        list
            A list of (city_id, city_name, country_name).
        """

        query = """
        SELECT c.city_id, c.city_name, ct.country_name
        FROM city AS c JOIN country AS ct ON c.country_code = ct.country_code
        WHERE city_name LIKE ?;
        """
        name = name.lower()
        name = '%' + name + '%'
        self.cur.execute(query, (name,))
        return self.cur.fetchall()

    def add_city(self, city_info):
        """Insert a new city

        Parameters
        ----------
        city_info : tuple
            A 5-tuple of (city_id, city_name, country_code, lat, lon)

        Returns
        -------
        bool
            True if successful, False otherwise
        """

        query = '''
        INSERT INTO city VALUES (?, ?, ?, ?, ?);
        '''
        try:
            self.cur.execute(query, city_info)
            self.con.commit()
            return True
        except sqlite3.DatabaseError:
            return False

    def update_weather_by_city(self, city_id, weather_info):
        """Update the weather information of a given city

        Parameters
        ----------
        city_id : int
        weather_info : tuple
            A 5-tuple of (day, weather_id, min_degree, max_degree, precipitation)

        Returns
        -------
        bool
            True if successful, False otherwise
        """
        
        query = '''
        UPDATE city_weather
        SET report_date = ?, weather_id = ?, min_degree = ?, max_degree = ?, precipitation = ?
        WHERE city_id = ?;
        '''
        
        t = [x for x in weather_info]
        t.append(city_id)
        pack = tuple(t)
        try:
            self.cur.execute(query, parameters=pack)
            self.cur.commit()
            return True
        except sqlite3.DatabaseError:
            return False

if __name__ == '__main__':
    with Database('db/wether.db') as db:
        city_id = input('City ID: ')
        city_name = input('City name: ')
        country_code = input('Country code: ')
        lat = float(input('Latitude: '))
        lon = float(input('Longitude: '))

        print('OK' if db.add_city((city_id, city_name, country_code, lat, lon)) else 'Not OK')
