import requests
import psycopg2
from psycopg2 import Error
import time 
# TimezoneDB API details
API_KEY = "JZ45JV2R8WBZ"
LIST_ENDPOINT = f"http://api.timezonedb.com/v2.1/list-time-zone?key={API_KEY}"
TIME_ZONE_ENDPOINT = f"http://api.timezonedb.com/v2.1/get-time-zone?key={API_KEY}"

#PostgreSQLdb details
DB_HOST = "localhost"
DB_NAME = "timezones_db" 
DB_USER = "pelaez"
DB_PASSWORD = "admin"


# get zone_names from the DB and put them into a list[] in order to use the codes to make requests to the get-time-zone endpoint
def get_zone_names():
    try:
        # Establish database connection
        connection = psycopg2.connect(
            user='pelaez',
            password='admin',
            host='localhost',
            database='timezones_db'
        )

        # Create a cursor object to execute SQL queries
        cursor = connection.cursor()

        # Execute SQL query to select zone_name from TZDB_TIMEZONES table
        cursor.execute("SELECT zone_name FROM TZDB_TIMEZONES")

        # Fetch all rows (zone names) from the query result
        rows = cursor.fetchall()

        # Extract zone names from the rows and store them in a list
        zone_names = [row[0] for row in rows]

        # Close the cursor and connection
        cursor.close()
        connection.close()

        return zone_names
    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL or fetching zone names:", error)
        return []

def populate_zone_details_stage(data):
    try:
        # Establish database connection
        connection = psycopg2.connect(
            user='pelaez',
            password='admin',
            host='localhost',
            database='timezones_db'
        )
        print("about to attempt stage table creation")
        # Create a cursor object to execute SQL queries
        cursor = connection.cursor()

        # Create the TZDB_ZONE_DETAILS_STAGE table if it doesn't exist
        print("attempting to create TZDB_ZONE_DETAILS_STAGE table")
        create_stage_table = '''
            CREATE TEMP TABLE IF NOT EXISTS TZDB_ZONE_DETAILS_STAGE (
                COUNTRYCODE VARCHAR(2) NOT NULL,
                COUNTRYNAME VARCHAR(100) NOT NULL,
                ZONENAME VARCHAR(100) PRIMARY KEY,
                GMTOFFSET INT NOT NULL,
                DST INT NOT NULL,
                ZONESTART INT NOT NULL,
                ZONEEND INT,
                FORMATTED DATE

            )'''

        cursor.execute(create_stage_table)
        print("Stage table created successfully ")
        connection.commit()
                # Insert data into the staging table
        cursor.execute("""
            INSERT INTO TZDB_ZONE_DETAILS_STAGE (COUNTRYCODE, COUNTRYNAME, ZONENAME, GMTOFFSET, DST, ZONESTART, ZONEEND, FORMATTED)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (data['countryCode'], data['countryName'], data['zoneName'], data['gmtOffset'], data['dst'], data['zoneStart'], data['zoneEnd'], data['formatted']))

        # Commit the transaction
        connection.commit()

        print("Data inserted into TZDB_ZONE_DETAILS_STAGE successfully.")

        # Close the cursor and connection
        cursor.close()
        connection.close()

    except (Exception, psycopg2.Error) as error:
        print("Error while populating TZDB_ZONE_DETAILS_STAGE table:", error)



def populate_timezones_table_stable(data):
    try:
        # Establish database connection
        connection = psycopg2.connect(
            user= 'pelaez',
            password='admin',
            host='localhost',
            database='timezones_db'
        )

        # Create a cursor object to execute SQL queries
        cursor = connection.cursor()

        # Drop and recreate TZDB_TIMEZONES table
        cursor.execute("DROP TABLE IF EXISTS TZDB_TIMEZONES")
        cursor.execute("""
            CREATE TABLE TZDB_TIMEZONES (
                country_code VARCHAR(2),
                country_name VARCHAR(255),
                zone_name VARCHAR(255),
                gmt_offset INT,
                timestamp BIGINT
            )
        """)

        # Populate TZDB_TIMEZONES table with data from API response
        for zone in data['zones']:
            cursor.execute("""
                INSERT INTO TZDB_TIMEZONES (country_code, country_name, zone_name, gmt_offset, timestamp)
                VALUES (%s, %s, %s, %s, %s)
            """, (zone['countryCode'], zone['countryName'], zone['zoneName'], zone['gmtOffset'], zone['timestamp']))

        # Commit the transaction
        connection.commit()

        # Close the cursor and connection
        cursor.close()
        connection.close()

        print("TZDB_TIMEZONES table populated successfully.")
    except psycopg2.Error as error:
        print("Error while connecting to PostgreSQL or populating TZDB_TIMEZONES table:", error)



# Function to fetch data from TimezoneDB API
def fetch_list_data():
    try:
        response = requests.get('http://api.timezonedb.com/v2.1/list-time-zone?key=JZ45JV2R8WBZ&format=json')
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error fetching data from API: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error fetching data from API: {str(e)}")
        return None

# to be used in conjunction with get_zone_names()
def fetch_timezone_data(zone_names):
    for zone in zone_names: 
        try:
            response = requests.get(f'http://api.timezonedb.com/v2.1/get-time-zone?key=JZ45JV2R8WBZ&format=json&by=zone&zone={zone}')
            if response.status_code == 200:
                populate_zone_details_stage(response.json())
                print(response.json())
                time.sleep(1.5)
                #return response.json()
            else:
                print(f"Error fetching data from API: {response.status_code}")
                return None
        except Exception as e:
            print(f"Error fetching data from API: {str(e)}")
            return None

# Function to create database connection
def create_connection():
    try:
        connection = psycopg2.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            database=DB_NAME
        )
        if connection:
            print(connection)
            print("Connected to the PostgreSQL database")
            return connection
    except (Exception, Error) as error:
        print("Error while connecting to PostgreSQL", error)
        return False, None
def recreate_timezones_table():
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        try:
            # Drop the TZDB_TIMEZONES table if it exists
            cursor.execute("DROP TABLE IF EXISTS TZDB_TIMEZONES")
            
            # Create the TZDB_TIMEZONES table
            cursor.execute("""
                CREATE TABLE TZDB_TIMEZONES (
                    zoneName VARCHAR(100) PRIMARY KEY,
                    countryCode VARCHAR(2) NOT NULL
                )
            """)
            connection.commit()
            print("TZDB_TIMEZONES table recreated successfully.")
        except Exception as e:
            print("Error recreating TZDB_TIMEZONES table:", e)
            connection.rollback()
        finally:
            cursor.close()
            connection.close()

def create_error_log_table():
    try:
        connection = create_connection()
        if connection:
            cursor = connection.cursor()
            # Check if TZDB_ERROR_LOG table exists
            cursor.execute("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'tzdb_error_log')")
            exists = cursor.fetchone()[0]
            if not exists:
                # Create TZDB_ERROR_LOG table if it doesn't exist
                cursor.execute("""
                    CREATE TABLE TZDB_ERROR_LOG (
                        id SERIAL PRIMARY KEY,
                        error_message TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                connection.commit()
                print("TZDB_ERROR_LOG table created successfully.")
            else:
                print("TZDB_ERROR_LOG table already exists.")
            cursor.close()
            connection.close()
    except Exception as e:
        print("Error creating TZDB_ERROR_LOG table:", e)

# get zone_names from the DB and put them into a list[] in order to use the codes to make requests to the get-time-zone endpoint
def get_zone_names():
    try:
        # Establish database connection
        connection = psycopg2.connect(
            user='pelaez',
            password='admin',
            host='localhost',
            database='timezones_db'
        )

        # Create a cursor object to execute SQL queries
        cursor = connection.cursor()

        # Execute SQL query to select zone_name from TZDB_TIMEZONES table
        cursor.execute("SELECT zone_name FROM TZDB_TIMEZONES")

        # Fetch all rows (zone names) from the query result
        rows = cursor.fetchall()

        # Extract zone names from the rows and store them in a list
        zone_names = [row[0] for row in rows]

        # Close the cursor and connection
        cursor.close()
        connection.close()

        return zone_names
    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL or fetching zone names:", error)
        return []

# Function to execute SQL commands
def execute_query(connection, query):
    try:
        cursor = connection.cursor()
        cursor.execute(query)
        connection.commit()
        cursor.close()
    except (Exception, Error) as error:
        print("Error executing query:", error)

# helper Function to handle errors and log them into TZDB_ERROR_LOG table
def log_error(error_message):
    connection = create_connection()
    if connection:
        query = f"INSERT INTO TZDB_ERROR_LOG (error_message) VALUES ('{error_message}')"
        execute_query(connection, query)
        connection.close()

def populate_timezones_table_err():
    try:
        list_data = fetch_list_data()
        if list_data:
            connection = create_connection()
            if connection:
                recreate_timezones_table()  # Recreate the table each time before populating
                cursor = connection.cursor()
                for zone in data["zones"]:
                    query = f"INSERT INTO TZDB_TIMEZONES (zone_name, country_code) VALUES ('{zone['zoneName']}', '{zone['countryCode']}')"
                    try:
                        cursor.execute(query)
                        connection.commit()
                    except Exception as e:
                        error_message = f"Error populating TZDB_TIMEZONES table: {str(e)}"
                        log_error(error_message)
                cursor.close()
                connection.close()
    except Exception as e:
        error_message = f"Error fetching data from API or populating TZDB_TIMEZONES table: {str(e)}"
        log_error(error_message)


def populate_timezones_table_full():
    # Fetch data from the list API endpoint
    response = requests.get(LIST_ENDPOINT)
    if response.status_code == 200:
        data = response.json()
        if "zones" in data:
            zones = data["zones"]
            if zones:
                connection = create_connection()
                if connection:
                    try:
                        cursor = connection.cursor()
                        # Truncate the TZDB_TIMEZONES table before insertion
                        cursor.execute("TRUNCATE TABLE TZDB_TIMEZONES")
                        # Insert data into the TZDB_TIMEZONES table
                        for zone in zones:
                            cursor.execute("INSERT INTO TZDB_TIMEZONES (zoneName, countryCode) VALUES (%s, %s)", (zone["zoneName"], zone["countryCode"]))
                        connection.commit()
                        print("TZDB_TIMEZONES table populated successfully.")
                    except Exception as e:
                        print("Error populating TZDB_TIMEZONES table:", e)
                        connection.rollback()
                    finally:
                        cursor.close()
                        connection.close()
            else:
                print("No zones data found in the API response.")
        else:
            print("Missing 'zones' key in the API response.")
    else:
        print(f"Failed to fetch data from API: {response.status_code}")

def fetch_data_from_api(endpoint):
    try:
        response = requests.get(endpoint)
        if response.status_code == 200:
            return response.json()
        else:
            log_error(f"API Error: {response.status_code}")
            return None
    except Exception as e:
        log_error(f"Error fetching data from API: {str(e)}")
        return None

def populate_timezones_table():
    try:
        data = fetch_data_from_api(LIST_ENDPOINT)
        print(data)
        if data:
            connection = create_connection()
            if connection:
                recreate_timezones_table()  # Recreate the table each time before populating
                cursor = connection.cursor()
                for zone in data["zones"]:
                    query = f"INSERT INTO TZDB_TIMEZONES (zone_name, country_code) VALUES ('{zone['zoneName']}', '{zone['countryCode']}')"
                    cursor.execute(query)
                    connection.commit()
                cursor.close()
                connection.close()
    except Exception as e:
        print("Error populating TZDB_TIMEZONES table:", e)


# Main function to fetch and print data from API
def main():
    list_data = fetch_list_data()
    if list_data:
        print("Response from List endpoint of TimezoneDB API:")
        print(list_data)

    else:
        print("Failed to fetch list data from TimezoneDB API")
    print("END OF LIST DATA\n")
    zones = get_zone_names() 
    tz_data = fetch_timezone_data(zones)
    if tz_data:
        print("Response from Timezone endpoint of TimezoneDB API:")
        print(tz_data)
    else:
        print("Failed to fetch timezone data from TimezoneDB API")
    print("END OF TIMEZONE DATA\n")
    print("Attempting to connect to PostgreSQL database...")
    create_connection()
    print("Attempting creation of TZDB_TIMEZONES table...\n")
    recreate_timezones_table()
    print("Attempting creation of TZDB_ERROR_LOG table if it is not already created...\n")
    create_error_log_table()
    print("Attempting to populate TZDB_TIMEZONES table...\n")
    populate_timezones_table_stable(list_data)
    #zones = get_zone_names()
    #fetch_timezone_data(zones)
    print(zones)
if __name__ == "__main__":
    main()

