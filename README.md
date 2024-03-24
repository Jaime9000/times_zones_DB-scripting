## Documenting step process of accessing [timezonedb](http://api.timezonedb.com/v2.1/list-time-zone) data-sets  [](http://api.timezonedb.com/v2.1/list-time-zone)via API endpoint, creating a DB (data-base) to store the data and managing the data.

### Goal:

1. Create a python script to query the TimezoneDB API and populate the tables —TZDB_TIMEZONES and —TZDB_ZONE_DETAILS
2. **Requirement:** Python script should handle errors when retrieving the API and log them into the table —TZDB_ERROR_LOG.
3. **Requirement:** —TZDB_TIMEZONES is to be deleted every time the script runs prior to populating the table with data from the API. (ensures the table is fresh each time the script runs. * Process should be DROP TABLE(Delete) —TZDB_TIMEZONES, CREATE TABLE(recreate) —TZDB_TIMEZONES, INSERT INTO(populate) —TZDB_TIMEZONES. *Leaving the table freshly populated after each run of the script.* 

### Let’s begin:

- Create an account w/ [timezonedb](http://api.timezonedb.com/v2.1/list-time-zone) via https://timezonedb.com/register.
    - Once registered you should receive a personal API-key via email
    - store this key as it is necessary for authentication when accessing the API-endpoints
- We will be using two different API endpoints from [timezonedb](https://timezonedb.com/api):
    
    you can find the endpoints here: https://timezonedb.com/api
    

- List Time Zone: http://api.timezonedb.com/v2.1/list-time-zone  —> Use for TZDB_TIMEZONES

- Get Time Zone: http://api.timezonedb.com/v2.1/get-time-zone —> Use for TZDB_ZONE_DETAILS

---

### *DB creation and configuration:*

- We’ll be using PostegreSQL for our DB, others could have been chosen, but I’ve chosen Postgres because of its python integration and cli interface.
    - For the database, we’ll be using PostgreSQL:
        1. verify if installed psql --version
            1. if installed should return version and pakagemanager like so:  ‘psql (PostgreSQL) 14.11 (Homebrew)’
        2. if not installed: 
            1. Install via homebrew:
                1. *`brew install Postgre`* 
                
                *—> start the service*: `brew services start postgresql`
                
            2. install via apt: 
                1. `sudo apt install postgresql` 
                
                —> start the service: `sudo systemctl restart postgresql`
                
    - Once installation is verified and the service is running:
        - Enter the psql shell: `psql -U postgres`
        - once you have entered the shell create a new super-user and server:
            - `create user alex with superuser password 'admin976!';`
        - Now let's create a new DB:
            - `CREATE DATABASE your_database_name;`
            - then use `\l` to list all DBs to verify your DB has been created
            - use `\q` to quit shell now
        - Now reenter  the shell using your new DB_name and user
            - `psql -U your_username your_database_name`
                
                —> print your DB connection info with `\conninfo`
                
            - Now we can use the connection info in our script

### *Writing the python-script:*

- Now we can begin writing our script:
    - [ ]  Open up your preferred text editor(I’m using nvim)
    - [ ]  
-
