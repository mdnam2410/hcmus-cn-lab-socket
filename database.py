import datetime
import sqlite3

class DatabaseConnectionError(Exception):
    pass

class Database:
    """Providing access to the server database
    """

    def __init__(self, database_path):
        self.today = datetime.date.today()
        self.con = None
        try:
            self.con = sqlite3.connect(database_path)
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


    # ---------- Utility methods ----------

    def execute_query(self, query):
        self.cur.execute(query)
        return self.cur.fetchall()

    def commit(self):
        self.con.commit()


    # ---------- User-identity-related methods ----------

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

        query = '''
        SELECT user.username, user.name
        FROM user
        WHERE user.username = ? AND user.password = ?;
        '''

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


    # ---------- Weather querying methods ----------

    def query_weather_by_date(self, date: str):
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

        return self.query_weather_by_date(self.today.isoformat())

    def query_weather_by_date_range(self, city_id, start, end):
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

        query = '''
        SELECT c.city_id, c.city_name, ct.country_name, cw.report_date, 
               wc.main, cw.min_degree, cw.max_degree, cw.precipitation
        FROM   city_weather AS cw JOIN city AS c
               ON cw.city_id = c.city_id
               JOIN weather_condition AS wc
               ON cw.weather_id = wc.weather_id
               JOIN country AS ct
               ON c.country_code = ct.country_code
        WHERE  c.city_id = ? AND cw.report_date BETWEEN ? AND ?;
        '''

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

        return self.query_weather_by_date_range(
            city_id,
            start=self.today.isoformat(),
            end=(self.today + datetime.timedelta(days=6)).isoformat()
        )


    # ---------- Searching methods ----------

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

        query = '''
        SELECT c.city_id, c.city_name, ct.country_name
        FROM city AS c JOIN country AS ct ON c.country_code = ct.country_code
        WHERE city_name LIKE ?;
        '''

        name = name.lower()
        name = '%' + name + '%'
        self.cur.execute(query, (name,))
        return self.cur.fetchall()


    # ---------- Database modification methods ----------

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

    def update_weather(self, city_id, date, weather_info):
        """Add or update weather information of a given city.

        Add a new weather_info of the city with ID city_id if the given date is not present in the database.
        Overwrite the current weather_info if date is present.

        Parameters
        ----------
        city_id : int

        date : str
            In YYYY-MM-DD format
        weather_info : tuple
            A 4-tuple of (weather_id, min_degree, max_degree, precipitation)

        Returns
        -------
        bool
            True if successful, False otherwise
        """
        
        update_query = '''
        UPDATE city_weather
        SET weather_id = ?, min_degree = ?, max_degree = ?, precipitation = ?
        WHERE city_id = ? AND report_date = ?;
        '''

        add_query = '''
        INSERT INTO city_weather(weather_id, min_degree, max_degree, precipitation, city_id, report_date)
            VALUES (?, ?, ?, ?, ?, ?);
        '''

        self.cur.execute('SELECT * FROM city_weather WHERE city_id = ? AND report_date = ?', (city_id, date))
        add = True if len(self.cur.fetchall()) else False
        
        p = [x for x in weather_info]
        p.append(city_id)
        p.append(date)

        try:
            if add:
                self.cur.execute(update_query, p)
            else:
                self.cur.execute(add_query, p)
            return True
        except sqlite3.DatabaseError:
            return False

if __name__ == '__main__':
    with Database('db/temp.db') as db:
        r = db.today_weather()
        print(r)