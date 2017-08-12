## Setting up the application

 1. Use psql to create the tournament database if it doesn't exist.
    - `psql`
    - `CREATE DATABASE tournament;`
    - `\q`
 
 2. Execute the command `psql tournament <tournament.sql` to execute the sql file on the tournament database to create the tables for the application.

 3. Run `python tournement_test.py`